import hashlib
import os
import shutil
import sqlite3
import pandas as pd


def build_event_key(row) -> str:
    """Deterministic natural key derived from event attributes."""
    raw = "|".join([
        str(row["timestamp"]),
        str(row["sensor_name"]),
        str(row["src_ip"]),
        str(row["dst_ip"]),
        str(row["src_port"]),
        str(row["dst_port"]),
        str(row["protocol"]),
        str(row["event_type"]),
        str(row["action"]),
        str(row["bytes"]),
        str(row["duration_ms"]),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def inspect_schema(conn: sqlite3.Connection) -> None:
    print("=== 1. SCHEMA INSPECTION (sqlite_schema) ===")
    rows = conn.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_schema WHERE sql IS NOT NULL ORDER BY type, name"
    ).fetchall()
    for obj_type, name, tbl_name, sql in rows:
        print(f"[{obj_type.upper()}] {name} (on {tbl_name})")
        print(sql)
        print("-" * 60)


def ensure_sensors(conn: sqlite3.Connection, sensor_names) -> dict:
    sensor_map = {}
    for s_name in sorted(set(sensor_names)):
        conn.execute(
            "INSERT OR IGNORE INTO sensors (sensor_name) VALUES (?)",
            (s_name,),
        )
    for sensor_id, s_name in conn.execute("SELECT sensor_id, sensor_name FROM sensors"):
        sensor_map[s_name] = sensor_id
    return sensor_map


def ingest_batch(conn: sqlite3.Connection, csv_path: str) -> int:
    df = pd.read_csv(csv_path)
    sensor_map = ensure_sensors(conn, df["sensor_name"])

    records = []
    for _, row in df.iterrows():
        event_key = build_event_key(row)
        sensor_id = sensor_map[row["sensor_name"]]
        records.append((
            event_key,
            str(row["timestamp"]),
            int(sensor_id),
            str(row["src_ip"]),
            str(row["dst_ip"]),
            int(row["src_port"]) if pd.notna(row["src_port"]) else None,
            int(row["dst_port"]),
            str(row["protocol"]),
            str(row["event_type"]),
            str(row["action"]),
            int(row["bytes"]),
            int(row["duration_ms"]),
        ))

    insert_sql = """
        INSERT INTO network_events (
            event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port,
            protocol, event_type, action, bytes, duration_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(event_key) DO NOTHING
    """
    with conn:
        conn.executemany(insert_sql, records)

    return conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]


def prove_idempotency(conn: sqlite3.Connection, csv_path: str) -> None:
    print("=== 2 & 3. IDEMPOTENT IMPORT & PROVE IDEMPOTENCY ===")
    before_run_1 = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
    after_run_1 = ingest_batch(conn, csv_path)
    after_run_2 = ingest_batch(conn, csv_path)
    print(f"Row count before Run 1 : {before_run_1}")
    print(f"Row count after  Run 1 : {after_run_1}")
    print(f"Row count after  Run 2 : {after_run_2}")
    assert after_run_1 == after_run_2, "Idempotency check failed: row count changed on second run!"
    print("IDEMPOTENCY VERIFIED: Row count did not increase on second run.")
    print("-" * 60)


def test_audit_rollback(conn: sqlite3.Connection) -> None:
    print("=== 4. AUDIT TRIGGER & TRANSACTION ROLLBACK TEST ===")
    alert_before = conn.execute(
        "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1"
    ).fetchone()
    print("Alert 1 before transaction:", alert_before)

    conn.execute("BEGIN TRANSACTION")
    conn.execute("UPDATE alerts SET status = 'INVESTIGATING' WHERE alert_id = 1")
    history_inside_tx = conn.execute(
        "SELECT history_id, alert_id, old_status, new_status, changed_at "
        "FROM alert_status_history WHERE alert_id = 1 ORDER BY history_id DESC"
    ).fetchall()
    print("Trigger history rows INSIDE transaction after UPDATE:", history_inside_tx)
    conn.execute("ROLLBACK")

    alert_after = conn.execute(
        "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1"
    ).fetchone()
    history_after_rollback = conn.execute(
        "SELECT COUNT(*) FROM alert_status_history WHERE alert_id = 1"
    ).fetchone()[0]
    print("Alert 1 AFTER ROLLBACK:", alert_after)
    print("Alert 1 history row count AFTER ROLLBACK:", history_after_rollback)
    print("-" * 60)


def compare_query_plan(source_db: str, csv_path: str) -> None:
    print("=== 5. EXPLAIN QUERY PLAN: BEFORE vs AFTER idx_events_src_time ===")
    temp_db = "temp_plan_check.db"
    if os.path.exists(temp_db):
        os.remove(temp_db)
    shutil.copy2(source_db, temp_db)

    query = """
        SELECT event_id, timestamp, dst_ip, dst_port, event_type, action, bytes
        FROM network_events
        WHERE src_ip = '198.51.100.66'
          AND timestamp BETWEEN '2026-09-18T10:00:00' AND '2026-09-18T11:00:59'
    """

    conn_no_idx = sqlite3.connect(temp_db)
    conn_no_idx.execute("DROP INDEX IF EXISTS idx_events_src_time")
    plan_before = conn_no_idx.execute(f"EXPLAIN QUERY PLAN {query}").fetchall()
    print("Plan WITHOUT idx_events_src_time:")
    for row in plan_before:
        print(" ", row)
    conn_no_idx.close()

    conn_with_idx = sqlite3.connect(temp_db)
    conn_with_idx.execute(
        "CREATE INDEX IF NOT EXISTS idx_events_src_time ON network_events(src_ip, timestamp)"
    )
    plan_after = conn_with_idx.execute(f"EXPLAIN QUERY PLAN {query}").fetchall()
    print("Plan WITH idx_events_src_time:")
    for row in plan_after:
        print(" ", row)
    conn_with_idx.close()

    if os.path.exists(temp_db):
        os.remove(temp_db)
    print("-" * 60)


def main() -> None:
    base_db = "network_security.db"
    csv_path = "network_events_sample.csv"
    working_db = "challenge_b_test.db"

    shutil.copy2(base_db, working_db)
    conn = sqlite3.connect(working_db)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        inspect_schema(conn)
        prove_idempotency(conn, csv_path)
        test_audit_rollback(conn)
        compare_query_plan(working_db, csv_path)
    finally:
        conn.close()
        if os.path.exists(working_db):
            os.remove(working_db)


if __name__ == "__main__":
    main()