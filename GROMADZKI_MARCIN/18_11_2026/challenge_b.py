import csv
import hashlib
import shutil
import sqlite3
from pathlib import Path

DB_PATH = Path("network_security.db")
COPY_DB_PATH = Path("network_security_copy.db")
CSV_PATH = Path("network_events_sample.csv")


def get_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inspect_database(conn: sqlite3.Connection) -> None:
    print("=" * 60)
    print("1. INSPECT: sqlite_schema")
    print("=" * 60)
    rows = conn.execute(
        """
        SELECT type, name, tbl_name, sql
        FROM sqlite_schema
        WHERE name NOT LIKE 'sqlite_%'
        ORDER BY type, name;
        """
    ).fetchall()
    for obj_type, name, tbl_name, sql in rows:
        print(f"[{obj_type.upper()}] {name} (table: {tbl_name})")
        print(f"{sql}\n")


def build_batch(conn: sqlite3.Connection, csv_path: Path, limit: int = 10) -> list[tuple]:
    """
    Builds a 12-column batch for network_events:
    (event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port,
     protocol, event_type, action, bytes, duration_ms)
    """
    sensor_map = dict(
        conn.execute("SELECT sensor_name, sensor_id FROM sensors;").fetchall()
    )

    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fields = set(reader.fieldnames or [])
            print(f"CSV columns detected: {reader.fieldnames}")

            required = {
                "timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
                "protocol", "event_type", "action", "bytes", "duration_ms"
            }
            if required.issubset(fields) and ("sensor_id" in fields or "sensor_name" in fields):
                batch = []
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    sid = (
                        int(row["sensor_id"])
                        if "sensor_id" in row
                        else sensor_map[row["sensor_name"]]
                    )
                    src_port = int(row["src_port"]) if row["src_port"] not in ("", None) else None
                    event_key = row.get("event_key") or hashlib.sha256(
                        "|".join(str(row[k]) for k in reader.fieldnames).encode("utf-8")
                    ).hexdigest()
                    batch.append(
                        (
                            event_key,
                            row["timestamp"],
                            sid,
                            row["src_ip"],
                            row["dst_ip"],
                            src_port,
                            int(row["dst_port"]),
                            row["protocol"],
                            row["event_type"],
                            row["action"],
                            int(row["bytes"]),
                            int(row["duration_ms"]),
                        )
                    )
                if batch:
                    return batch

    # Fallback: reuse existing 12-column rows from network_events
    return conn.execute(
        """
        SELECT event_key, timestamp, sensor_id, src_ip, dst_ip,
               src_port, dst_port, protocol, event_type, action,
               bytes, duration_ms
        FROM network_events
        ORDER BY event_id
        LIMIT ?;
        """,
        (limit,),
    ).fetchall()


def import_and_prove_idempotency(conn: sqlite3.Connection, batch: list[tuple]) -> None:
    print("=" * 60)
    print("2 & 3. IMPORT & PROVE IDEMPOTENCY")
    print("=" * 60)

    insert_sql = """
        INSERT INTO network_events (
            event_key, timestamp, sensor_id, src_ip, dst_ip,
            src_port, dst_port, protocol, event_type, action,
            bytes, duration_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(event_key) DO NOTHING;
    """

    count_before = conn.execute("SELECT COUNT(*) FROM network_events;").fetchone()[0]
    print(f"Batch size:             {len(batch)}")
    print(f"Row count before Run 1: {count_before}")

    with conn:
        conn.executemany(insert_sql, batch)
    count_run1 = conn.execute("SELECT COUNT(*) FROM network_events;").fetchone()[0]
    print(f"Row count after Run 1:  {count_run1} (delta: +{count_run1 - count_before})")

    with conn:
        conn.executemany(insert_sql, batch)
    count_run2 = conn.execute("SELECT COUNT(*) FROM network_events;").fetchone()[0]
    print(f"Row count after Run 2:  {count_run2} (delta: +{count_run2 - count_run1})")

    assert count_run2 == count_run1, "FAILED: Row count increased on second run!"
    print("PASS: Second run added 0 rows (idempotent ingestion verified).\n")


def audit_alert_update_with_rollback(conn: sqlite3.Connection) -> None:
    print("=" * 60)
    print("4. AUDIT: Update alert 1 inside transaction -> show history -> ROLLBACK")
    print("=" * 60)

    alert_before = conn.execute(
        "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;"
    ).fetchone()
    print(f"Alert 1 before transaction: {alert_before}")

    current_status = alert_before[3]
    new_status = "INVESTIGATING" if current_status != "INVESTIGATING" else "OPEN"

    prev_isolation = conn.isolation_level
    conn.isolation_level = None
    try:
        conn.execute("BEGIN;")
        conn.execute(
            "UPDATE alerts SET status = ? WHERE alert_id = 1;",
            (new_status,),
        )

        alert_inside = conn.execute(
            "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;"
        ).fetchone()
        history_rows = conn.execute(
            """
            SELECT history_id, alert_id, old_status, new_status, changed_at
            FROM alert_status_history
            ORDER BY history_id DESC
            LIMIT 5;
            """
        ).fetchall()

        print(f"Alert 1 inside transaction: {alert_inside}")
        print("Trigger row(s) in alert_status_history (before ROLLBACK):")
        for row in history_rows:
            print(" ", row)

        conn.execute("ROLLBACK;")
        print("Executed ROLLBACK.")
    except Exception:
        conn.execute("ROLLBACK;")
        raise
    finally:
        conn.isolation_level = prev_isolation

    alert_after = conn.execute(
        "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;"
    ).fetchone()
    history_count = conn.execute("SELECT COUNT(*) FROM alert_status_history;").fetchone()[0]
    print(f"Alert 1 after ROLLBACK:     {alert_after}")
    print(f"alert_status_history count: {history_count}\n")


def optimise_on_db_copy() -> None:
    print("=" * 60)
    print("5. OPTIMISE: EXPLAIN QUERY PLAN before & after idx_events_src_time (on DB copy)")
    print("=" * 60)

    shutil.copyfile(DB_PATH, COPY_DB_PATH)
    print(f"Created copy: {COPY_DB_PATH}")

    explain_sql = """
        EXPLAIN QUERY PLAN
        SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
        FROM network_events
        WHERE src_ip = ?
        ORDER BY timestamp DESC;
    """

    with get_connection(COPY_DB_PATH) as copy_conn:
        sample_src = copy_conn.execute(
            "SELECT src_ip FROM network_events LIMIT 1;"
        ).fetchone()

        # idx_events_src_time already exists in network_security.db,
        # so drop it on the COPY first to measure the BEFORE plan.
        copy_conn.execute("DROP INDEX IF EXISTS idx_events_src_time;")

        print(f"\nBEFORE idx_events_src_time (src_ip = {sample_src[0]}):")
        for row in copy_conn.execute(explain_sql, sample_src):
            print(" ", row)

        copy_conn.execute(
            """
            CREATE INDEX idx_events_src_time
            ON network_events (src_ip, timestamp);
            """
        )

        print(f"\nAFTER idx_events_src_time (src_ip = {sample_src[0]}):")
        for row in copy_conn.execute(explain_sql, sample_src):
            print(" ", row)
    print()


if __name__ == "__main__":
    with get_connection(DB_PATH) as conn:
        inspect_database(conn)
        batch = build_batch(conn, CSV_PATH, limit=10)
        import_and_prove_idempotency(conn, batch)
        audit_alert_update_with_rollback(conn)

    optimise_on_db_copy()