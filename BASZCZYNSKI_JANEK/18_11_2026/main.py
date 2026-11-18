
import csv
import hashlib
import shutil
import sqlite3
from pathlib import Path

DB_PATH = Path("network_security.db")
COPY_DB_PATH = Path("network_security_test_copy.db")
CSV_PATH = Path("network_events_sample.csv")

INSERT_12_COL_SQL = """
INSERT INTO network_events (
    event_key,
    timestamp,
    sensor_id,
    src_ip,
    dst_ip,
    src_port,
    dst_port,
    protocol,
    event_type,
    action,
    bytes,
    duration_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING;
"""

BENCHMARK_QUERY = """
SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.66'
  AND timestamp >= '2026-09-18T10:10:00'
  AND timestamp <  '2026-09-18T10:20:00'
ORDER BY timestamp;
"""


def make_event_key(row: dict[str, str]) -> str:
    """Compute a deterministic SHA-256 deduplication key from CSV fields."""
    payload = "|".join([
        row["timestamp"],
        row["sensor_name"],
        row["src_ip"],
        row["dst_ip"],
        row["src_port"],
        row["dst_port"],
        row["protocol"],
        row["event_type"],
        row["action"],
        row["bytes"],
        row["duration_ms"],
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_csv_batch(conn: sqlite3.Connection, csv_path: Path) -> list[tuple]:
    """Load network_events_sample.csv into 12-column tuples for executemany()."""
    sensor_map = dict(
        conn.execute("SELECT sensor_name, sensor_id FROM sensors").fetchall()
    )
    batch: list[tuple] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            batch.append((
                make_event_key(row),
                row["timestamp"],
                sensor_map[row["sensor_name"]],
                row["src_ip"],
                row["dst_ip"],
                int(row["src_port"]),
                int(row["dst_port"]),
                row["protocol"],
                row["event_type"],
                row["action"],
                int(row["bytes"]),
                int(row["duration_ms"]),
            ))
    return batch


def step_1_inspect(conn: sqlite3.Connection) -> None:
    print("\n=== STEP 1: INSPECT sqlite_schema ===")
    rows = conn.execute("""
        SELECT type, name, tbl_name, sql
        FROM sqlite_schema
        WHERE name NOT LIKE 'sqlite_%'
        ORDER BY type, name;
    """).fetchall()
    for obj_type, name, tbl_name, sql in rows:
        print(f"[{obj_type.upper()}] {name} (table: {tbl_name})")
        print(f"  {sql}\n")


def step_2_and_3_import_idempotency(copy_db: Path) -> None:
    print("\n=== STEP 2 & 3: IMPORT (12-COL executemany) + PROVE IDEMPOTENCY ===")
    print(f"Working on copy: {copy_db}")
    conn = sqlite3.connect(copy_db)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        batch = load_csv_batch(conn, CSV_PATH)
        print(f"Prepared CSV batch size: {len(batch)} rows")

        count_before = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]

        # Run 1 (single atomic transaction)
        with conn:
            conn.executemany(INSERT_12_COL_SQL, batch)
        count_after_1 = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]

        # Run 2 (exact same batch -> ON CONFLICT(event_key) DO NOTHING)
        with conn:
            conn.executemany(INSERT_12_COL_SQL, batch)
        count_after_2 = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]

        print(f"Row count before import : {count_before}")
        print(f"Row count after run 1   : {count_after_1} (delta: +{count_after_1 - count_before})")
        print(f"Row count after run 2   : {count_after_2} (delta: +{count_after_2 - count_after_1})")

        assert count_after_2 == count_after_1, "Idempotency check failed!"
        print("PASS: Second run added 0 rows (idempotent).")
    finally:
        conn.close()


def step_4_audit_rollback(conn: sqlite3.Connection) -> None:
    print("\n=== STEP 4: AUDIT TRIGGER INSIDE TRANSACTION + ROLLBACK ===")
    # Use a connection with explicit transaction control (isolation_level=None)
    audit_conn = sqlite3.connect(DB_PATH, isolation_level=None)
    try:
        audit_conn.execute("PRAGMA foreign_keys = ON")

        alert_before = audit_conn.execute(
            "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1"
        ).fetchone()
        if alert_before is None:
            raise RuntimeError("Alert 1 not found in alerts table.")

        history_before = audit_conn.execute(
            "SELECT COUNT(*) FROM alert_status_history"
        ).fetchone()[0]

        current_status = alert_before[3]
        new_status = "INVESTIGATING" if current_status != "INVESTIGATING" else "OPEN"

        print(f"Before txn -> alert 1: {alert_before}, history count: {history_before}")

        audit_conn.execute("BEGIN;")
        audit_conn.execute(
            "UPDATE alerts SET status = ? WHERE alert_id = 1;",
            (new_status,),
        )

        trigger_rows = audit_conn.execute("""
            SELECT history_id, alert_id, old_status, new_status, changed_at
            FROM alert_status_history
            WHERE alert_id = 1
            ORDER BY history_id DESC;
        """).fetchall()
        print(f"Inside txn -> updated status to '{new_status}', trigger rows: {trigger_rows}")
        assert len(trigger_rows) >= 1, "Expected trigger to insert an audit row!"

        audit_conn.execute("ROLLBACK;")

        alert_after = audit_conn.execute(
            "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1"
        ).fetchone()
        history_after = audit_conn.execute(
            "SELECT COUNT(*) FROM alert_status_history"
        ).fetchone()[0]

        print(f"After ROLLBACK -> alert 1: {alert_after}, history count: {history_after}")
        assert alert_after == alert_before, "Alert 1 did not roll back!"
        assert history_after == history_before, "Audit history did not roll back!"
        print("PASS: Trigger fired inside transaction and ROLLBACK reverted both tables.")
    finally:
        audit_conn.close()


def step_5_optimise(copy_db: Path) -> None:
    print("\n=== STEP 5: OPTIMISE (EXPLAIN QUERY PLAN BEFORE vs AFTER idx_events_src_time) ===")
    print(f"Working on copy: {copy_db}")
    conn = sqlite3.connect(copy_db)
    try:
        conn.execute("DROP INDEX IF EXISTS idx_events_src_time;")
        plan_before = conn.execute(f"EXPLAIN QUERY PLAN {BENCHMARK_QUERY}").fetchall()
        print("Plan BEFORE idx_events_src_time:")
        for row in plan_before:
            print(f"  {row}")

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_src_time
                ON network_events(src_ip, timestamp);
        """)
        conn.commit()

        plan_after = conn.execute(f"EXPLAIN QUERY PLAN {BENCHMARK_QUERY}").fetchall()
        print("Plan AFTER idx_events_src_time:")
        for row in plan_after:
            print(f"  {row}")
    finally:
        conn.close()


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Missing {DB_PATH}")
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Missing {CSV_PATH}")

    # Create a clean working copy for mutating/index-dropping tests
    shutil.copy2(DB_PATH, COPY_DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        step_1_inspect(conn)
    finally:
        conn.close()

    step_2_and_3_import_idempotency(COPY_DB_PATH)
    step_4_audit_rollback(conn=None)  # uses its own explicit-txn connection
    step_5_optimise(COPY_DB_PATH)


if __name__ == "__main__":
    main()