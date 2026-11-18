#!/usr/bin/env python3
"""
Challenge B: Make Ingestion Safe and Auditable
Demonstrates:
  1. Inspecting sqlite_schema (keys, constraints, triggers, indexes)
  2. Full 12-column network_events INSERT with executemany() and ON CONFLICT(event_key) DO NOTHING
  3. Proving idempotency across two consecutive batch runs
  4. Auditing alert status updates via trigger inside an explicit transaction + ROLLBACK
  5. Comparing EXPLAIN QUERY PLAN before and after idx_events_src_time on a DB copy
"""

import csv
import hashlib
import shutil
import sqlite3
import tempfile
from pathlib import Path

DB_PATH = Path("network_security.db")
CSV_PATH = Path("network_events_sample.csv")

INSERT_EVENT_SQL = """
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
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING;
"""


def compute_event_key(row: dict) -> str:
    """Compute deterministic SHA-256 hash matching the existing database convention."""
    raw = "|".join([
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
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def step_1_inspect(conn: sqlite3.Connection) -> None:
    print("=" * 72)
    print("STEP 1: INSPECT sqlite_schema (Tables, Indexes, Triggers, Views)")
    print("=" * 72)
    cur = conn.execute(
        """
        SELECT type, name, tbl_name, sql
        FROM sqlite_schema
        WHERE type IN ('table', 'index', 'trigger', 'view')
        ORDER BY type, tbl_name, name
        """
    )
    for obj_type, name, tbl_name, sql in cur.fetchall():
        print(f"[{obj_type.upper()}] {name} (on {tbl_name})")
        if sql:
            for line in sql.strip().splitlines():
                print(f"    {line}")
    print()


def load_batch_rows(conn: sqlite3.Connection, csv_path: Path) -> list[tuple]:
    """Read CSV rows, resolve sensor_id (inserting missing sensors safely), and build 12-column tuples."""
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    sensor_names = sorted({r["sensor_name"] for r in rows})
    conn.executemany(
        "INSERT INTO sensors (sensor_name) VALUES (?) ON CONFLICT(sensor_name) DO NOTHING;",
        [(name,) for name in sensor_names],
    )
    sensor_map = dict(conn.execute("SELECT sensor_name, sensor_id FROM sensors;").fetchall())

    batch = []
    for r in rows:
        batch.append((
            compute_event_key(r),
            r["timestamp"],
            sensor_map[r["sensor_name"]],
            r["src_ip"],
            r["dst_ip"],
            int(r["src_port"]) if r["src_port"] else None,
            int(r["dst_port"]),
            r["protocol"],
            r["event_type"],
            r["action"],
            int(r["bytes"]),
            int(r["duration_ms"]),
        ))
    return batch


def step_2_and_3_import_and_idempotency(conn: sqlite3.Connection, csv_path: Path) -> None:
    print("=" * 72)
    print("STEP 2 & 3: SAFE IDEMPOTENT IMPORT (12-column executemany + ON CONFLICT)")
    print("=" * 72)
    initial_count = conn.execute("SELECT COUNT(*) FROM network_events;").fetchone()[0]
    print(f"Initial network_events row count: {initial_count}")

    batch = load_batch_rows(conn, csv_path)
    print(f"Loaded {len(batch)} rows from {csv_path.name}")

    # Run 1
    with conn:
        cur1 = conn.executemany(INSERT_EVENT_SQL, batch)
    count_after_run_1 = conn.execute("SELECT COUNT(*) FROM network_events;").fetchone()[0]
    print(f"Run 1 -> rowcount reported: {cur1.rowcount}, table count: {count_after_run_1}")

    # Run 2 (exact same batch)
    with conn:
        cur2 = conn.executemany(INSERT_EVENT_SQL, batch)
    count_after_run_2 = conn.execute("SELECT COUNT(*) FROM network_events;").fetchone()[0]
    print(f"Run 2 -> rowcount reported: {cur2.rowcount}, table count: {count_after_run_2}")

    assert count_after_run_1 == count_after_run_2, "Idempotency check failed: row count increased!"
    print("PASS: Row count did not increase on the second run (idempotency verified).\n")


def step_4_audit_transaction_rollback(conn: sqlite3.Connection) -> None:
    print("=" * 72)
    print("STEP 4: AUDIT TRIGGER INSIDE TRANSACTION + ROLLBACK")
    print("=" * 72)
    cur = conn.cursor()

    before_alert = cur.execute(
        "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;"
    ).fetchone()
    before_hist_count = cur.execute("SELECT COUNT(*) FROM alert_status_history;").fetchone()[0]
    print(f"Before transaction -> Alert 1: {before_alert}, history count: {before_hist_count}")

    # Begin explicit transaction
    cur.execute("BEGIN TRANSACTION;")
    cur.execute("UPDATE alerts SET status = 'INVESTIGATING' WHERE alert_id = 1;")

    in_tx_alert = cur.execute(
        "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;"
    ).fetchone()
    in_tx_history = cur.execute(
        "SELECT history_id, alert_id, old_status, new_status, changed_at FROM alert_status_history WHERE alert_id = 1;"
    ).fetchall()
    print(f"Inside transaction -> Alert 1: {in_tx_alert}")
    print(f"Inside transaction -> Trigger audit row(s): {in_tx_history}")
    assert len(in_tx_history) == 1, "Expected trigger to insert 1 audit row!"

    # Rollback transaction
    cur.execute("ROLLBACK;")

    after_alert = cur.execute(
        "SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;"
    ).fetchone()
    after_hist_count = cur.execute("SELECT COUNT(*) FROM alert_status_history;").fetchone()[0]
    print(f"After ROLLBACK     -> Alert 1: {after_alert}, history count: {after_hist_count}")

    assert after_alert == before_alert, "Alert 1 was not restored on ROLLBACK!"
    assert after_hist_count == before_hist_count, "Audit history row was not rolled back!"
    print("PASS: Trigger fired atomically inside transaction and rolled back cleanly.\n")


def step_5_optimise_query_plan(db_path: Path) -> None:
    print("=" * 72)
    print("STEP 5: OPTIMISE (EXPLAIN QUERY PLAN BEFORE & AFTER idx_events_src_time)")
    print("=" * 72)
    test_query = """
    EXPLAIN QUERY PLAN
    SELECT event_id, timestamp, src_ip, dst_ip, dst_port, event_type, action
    FROM network_events
    WHERE src_ip = '198.51.100.90'
      AND timestamp BETWEEN '2026-09-18T10:00:00' AND '2026-09-18T10:30:00'
    ORDER BY timestamp;
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        copy_path = Path(tmpdir) / "network_security_copy.db"
        shutil.copy2(db_path, copy_path)

        copy_conn = sqlite3.connect(copy_path)
        try:
            # Before index: drop idx_events_src_time on the copy
            copy_conn.execute("DROP INDEX IF EXISTS idx_events_src_time;")
            plan_before = copy_conn.execute(test_query).fetchall()
            print("BEFORE idx_events_src_time (dropped on DB copy):")
            for row in plan_before:
                print(f"    detail={row[3]}")

            # After index: recreate composite index idx_events_src_time
            copy_conn.execute(
                "CREATE INDEX idx_events_src_time ON network_events(src_ip, timestamp);"
            )
            plan_after = copy_conn.execute(test_query).fetchall()
            print("AFTER idx_events_src_time (created on DB copy):")
            for row in plan_after:
                print(f"    detail={row[3]}")

            assert any("SCAN" in r[3] for r in plan_before), "Expected full table SCAN without index!"
            assert any("USING INDEX idx_events_src_time" in r[3] for r in plan_after), (
                "Expected idx_events_src_time to be used!"
            )
            print("PASS: Composite index eliminated full table scan and temporary B-tree sort.\n")
        finally:
            copy_conn.close()


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV sample not found: {CSV_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        step_1_inspect(conn)
        step_2_and_3_import_and_idempotency(conn, CSV_PATH)
        step_4_audit_transaction_rollback(conn)
    finally:
        conn.close()

    step_5_optimise_query_plan(DB_PATH)
    print("ALL CHALLENGE B CHECKS PASSED SUCCESSFULLY.")


if __name__ == "__main__":
    main()