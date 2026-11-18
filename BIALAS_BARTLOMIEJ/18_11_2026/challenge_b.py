#!/usr/bin/env python3
"""Challenge B: safe, idempotent and auditable SQLite event ingestion.

Usage:
    python challenge_b.py network_security.db network_events_sample.csv

The script creates a disposable copy of the supplied DB for its demonstration.
It leaves the original database untouched.
"""
import csv
import hashlib
import ipaddress
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

CSV_FIELDS = [
    "timestamp", "sensor_name", "src_ip", "dst_ip", "src_port",
    "dst_port", "protocol", "event_type", "action", "bytes", "duration_ms",
]
INSERT_SQL = """
INSERT INTO network_events (
    event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port,
    protocol, event_type, action, bytes, duration_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING
"""
PLAN_SQL = """
SELECT timestamp, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.77'
  AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC
"""

def as_int(row, field, line_no, low=0, high=None):
    try:
        value = int(row[field])
    except (TypeError, ValueError):
        raise ValueError(f"CSV line {line_no}: {field} must be an integer")
    if value < low or (high is not None and value > high):
        raise ValueError(f"CSV line {line_no}: {field} outside allowed range")
    return value

def prepare_rows(csv_path, conn):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != CSV_FIELDS:
            raise ValueError("CSV header/column order does not match expected 11 fields")
        raw_rows = list(reader)

    sensors = dict(conn.execute("SELECT sensor_name, sensor_id FROM sensors"))
    prepared = []
    for line_no, row in enumerate(raw_rows, start=2):
        missing = [name for name in CSV_FIELDS if not row.get(name)]
        if missing:
            raise ValueError(f"CSV line {line_no}: missing {', '.join(missing)}")
        try:
            datetime.fromisoformat(row["timestamp"])
            ipaddress.ip_address(row["src_ip"])
            ipaddress.ip_address(row["dst_ip"])
        except ValueError as exc:
            raise ValueError(f"CSV line {line_no}: invalid timestamp or IP: {exc}") from exc
        if row["sensor_name"] not in sensors:
            raise ValueError(f"CSV line {line_no}: unknown sensor {row['sensor_name']}")
        protocol = row["protocol"].upper()
        action = row["action"].upper()
        if protocol not in {"TCP", "UDP", "ICMP"}:
            raise ValueError(f"CSV line {line_no}: invalid protocol {protocol}")
        if action not in {"ALLOW", "BLOCK"}:
            raise ValueError(f"CSV line {line_no}: invalid action {action}")
        src_port = as_int(row, "src_port", line_no, 1, 65535)
        dst_port = as_int(row, "dst_port", line_no, 1, 65535)
        byte_count = as_int(row, "bytes", line_no)
        duration = as_int(row, "duration_ms", line_no)

        # README convention: SHA-256 over the 11 source CSV values joined by "|".
        event_key = hashlib.sha256(
            "|".join(row[field] for field in CSV_FIELDS).encode("utf-8")
        ).hexdigest()

        prepared.append((
            event_key, row["timestamp"], sensors[row["sensor_name"]],
            row["src_ip"], row["dst_ip"], src_port, dst_port, protocol,
            row["event_type"], action, byte_count, duration,
        ))
    return prepared

def run_demo(source_db, csv_path):
    with tempfile.TemporaryDirectory(prefix="challenge_b_") as temp_dir:
        demo_db = Path(temp_dir) / "challenge_b_demo.db"
        shutil.copy2(source_db, demo_db)

        conn = sqlite3.connect(demo_db)
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            if conn.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
                raise RuntimeError("SQLite foreign-key enforcement is not enabled")

            batch = prepare_rows(csv_path, conn)
            # Use an isolated copy and empty only the event table so the test
            # demonstrates first import (896 inserts) and retry (0 inserts).
            with conn:
                conn.execute("DELETE FROM network_events")

            start_count = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
            with conn:
                conn.executemany(INSERT_SQL, batch)
            after_first = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
            first_inserted = after_first - start_count

            with conn:
                conn.executemany(INSERT_SQL, batch)
            after_second = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
            second_inserted = after_second - after_first

            print("=== IMPORT / IDEMPOTENCY ===")
            print(f"CSV rows validated:                 {len(batch)}")
            print(f"Rows before first import:           {start_count}")
            print(f"Rows after first import:             {after_first}")
            print(f"Rows inserted on first import:      {first_inserted}")
            print(f"Rows after second import:            {after_second}")
            print(f"Rows inserted on second import:     {second_inserted}")
            print("IDEMPOTENCY TEST:                  PASS" if after_first == after_second and second_inserted == 0 else "IDEMPOTENCY TEST: FAIL")

            # Audit trigger test: show the row inside the transaction, then roll back.
            print("\n=== AUDIT TRIGGER / ROLLBACK ===")
            initial_status = conn.execute(
                "SELECT status FROM alerts WHERE alert_id = 1"
            ).fetchone()[0]
            conn.execute("BEGIN")
            conn.execute(
                "UPDATE alerts SET status = 'INVESTIGATING' WHERE alert_id = 1"
            )
            audit_rows = conn.execute("""
                SELECT alert_id, old_status, new_status
                FROM alert_status_history
                WHERE alert_id = 1
                ORDER BY history_id DESC
            """).fetchall()
            print(f"Status before transaction:           {initial_status}")
            print(f"Trigger history inside transaction:  {audit_rows}")
            conn.rollback()
            final_status = conn.execute(
                "SELECT status FROM alerts WHERE alert_id = 1"
            ).fetchone()[0]
            history_count = conn.execute(
                "SELECT COUNT(*) FROM alert_status_history WHERE alert_id = 1"
            ).fetchone()[0]
            print(f"Status after ROLLBACK:                {final_status}")
            print(f"History rows after ROLLBACK:          {history_count}")
            audit_pass = (
                initial_status == "OPEN"
                and audit_rows == [(1, "OPEN", "INVESTIGATING")]
                and final_status == "OPEN"
                and history_count == 0
            )
            print("AUDIT / ROLLBACK TEST:              " + ("PASS" if audit_pass else "FAIL"))

            # Query-plan comparison on the disposable DB copy.
            print("\n=== QUERY PLAN / COMPOSITE INDEX ===")
            conn.execute("DROP INDEX IF EXISTS idx_events_src_time")
            before_plan = conn.execute("EXPLAIN QUERY PLAN " + PLAN_SQL).fetchall()
            print("Before index:")
            for row in before_plan:
                print("  " + row[3])
            conn.execute(
                "CREATE INDEX idx_events_src_time ON network_events(src_ip, timestamp)"
            )
            after_plan = conn.execute("EXPLAIN QUERY PLAN " + PLAN_SQL).fetchall()
            print("After index:")
            for row in after_plan:
                print("  " + row[3])
            before_text = " ".join(row[3] for row in before_plan).upper()
            after_text = " ".join(row[3] for row in after_plan).upper()
            plan_pass = "SCAN NETWORK_EVENTS" in before_text and "USING INDEX IDX_EVENTS_SRC_TIME" in after_text
            print("QUERY PLAN TEST:                    " + ("PASS" if plan_pass else "CHECK PLAN OUTPUT"))

            fk_issues = conn.execute("PRAGMA foreign_key_check").fetchall()
            print("\n=== FINAL CHECKS ===")
            print(f"Foreign-key check:                  {'OK' if not fk_issues else fk_issues}")
            print(f"Unique event keys:                  {conn.execute('SELECT COUNT(DISTINCT event_key) FROM network_events').fetchone()[0]}")
            all_pass = after_first == len(batch) and after_second == after_first and audit_pass and plan_pass and not fk_issues
            print("OVERALL:                            " + ("ALL TESTS PASSED" if all_pass else "REVIEW REQUIRED"))
            if not all_pass:
                raise SystemExit(1)
        finally:
            conn.close()

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python challenge_b.py network_security.db network_events_sample.csv")
    db_path, csv_path = map(Path, sys.argv[1:])
    if not db_path.is_file() or not csv_path.is_file():
        raise SystemExit("Database or CSV file not found.")
    run_demo(db_path, csv_path)

if __name__ == "__main__":
    main()
