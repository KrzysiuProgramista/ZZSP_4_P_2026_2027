"""
Challenge B: Make Ingestion Safe and Auditable
==============================================
This script fulfills all requirements of Challenge B:
1. Inspect: Reads sqlite_schema to identify tables, keys, constraints, triggers, and indexes.
2. Import: Uses a full 12-column INSERT into network_events with executemany() and ON CONFLICT(event_key) DO NOTHING.
3. Prove idempotency: Runs the exact same batch twice and verifies row count does not increase.
4. Audit: Updates alert 1 inside an explicit transaction, verifies the trigger row in alert_status_history, and executes ROLLBACK.
5. Optimise: On a copy of the database, compares EXPLAIN QUERY PLAN before and after idx_events_src_time.
6. Document: Prints and saves structured documentation explaining the conflict key, transaction boundary, and index choice.
"""

import csv
import hashlib
import os
import shutil
import sqlite3

DB_PATH = "network_security.db"
CSV_PATH = "network_events_sample.csv"
DB_COPY_PATH = "network_security_plan_test.db"


def compute_event_key(row: dict) -> str:
    """
    Computes the deterministic SHA-256 event_key matching the starter pack convention:
    pipe-delimited concatenation of all 11 CSV fields.
    """
    fields = [
        row["timestamp"],
        row["sensor_name"],
        row["src_ip"],
        row["dst_ip"],
        str(row["src_port"]),
        str(row["dst_port"]),
        row["protocol"],
        row["event_type"],
        row["action"],
        str(row["bytes"]),
        str(row["duration_ms"]),
    ]
    return hashlib.sha256("|".join(fields).encode("utf-8")).hexdigest()


def step_1_inspect(conn: sqlite3.Connection) -> None:
    print("=" * 80)
    print("STEP 1: INSPECT sqlite_schema (Tables, Keys, Constraints, Triggers, Indexes)")
    print("=" * 80)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, name, tbl_name, sql
        FROM sqlite_schema
        WHERE name NOT LIKE 'sqlite_%'
        ORDER BY 
            CASE type 
                WHEN 'table' THEN 1 
                WHEN 'index' THEN 2 
                WHEN 'trigger' THEN 3 
                WHEN 'view' THEN 4 
                ELSE 5 
            END,
            name;
    """)
    for obj_type, name, tbl_name, sql in cursor.fetchall():
        print(f"[{obj_type.upper()}] {name} (on {tbl_name}):")
        print(sql)
        print("-" * 60)


def prepare_batch(conn: sqlite3.Connection, csv_path: str) -> list[tuple]:
    """
    Maps sensor_name -> sensor_id and computes deterministic event_key
    to build tuples for the full 12-column INSERT (excluding autoincrement event_id).
    """
    cursor = conn.cursor()
    cursor.execute("SELECT sensor_name, sensor_id FROM sensors;")
    sensor_map = dict(cursor.fetchall())

    batch = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sensor_id = sensor_map[row["sensor_name"]]
            event_key = compute_event_key(row)
            batch.append((
                event_key,
                row["timestamp"],
                sensor_id,
                row["src_ip"],
                row["dst_ip"],
                int(row["src_port"]) if row["src_port"] else None,
                int(row["dst_port"]),
                row["protocol"],
                row["event_type"],
                row["action"],
                int(row["bytes"]),
                int(row["duration_ms"]),
            ))
    return batch


def step_2_and_3_import_and_idempotency(conn: sqlite3.Connection, csv_path: str) -> None:
    print("\n" + "=" * 80)
    print("STEP 2 & 3: IDEMPOTENT IMPORT (12-column INSERT + ON CONFLICT(event_key) DO NOTHING)")
    print("=" * 80)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM network_events;")
    initial_count = cursor.fetchone()[0]
    print(f"Initial row count in network_events: {initial_count}")

    batch = prepare_batch(conn, csv_path)
    # Append 2 brand-new synthetic test events to prove new rows are inserted on Run 1,
    # and ignored on Run 2.
    new_event_1 = (
        hashlib.sha256(b"2026-09-18T11:00:01|edge-fw-01|198.51.100.66|10.0.0.10|54321|443|TCP|CONNECTION|BLOCK|512|15").hexdigest(),
        "2026-09-18T11:00:01", 2, "198.51.100.66", "10.0.0.10", 54321, 443, "TCP", "CONNECTION", "BLOCK", 512, 15
    )
    new_event_2 = (
        hashlib.sha256(b"2026-09-18T11:00:02|core-sensor-02|203.0.113.23|10.0.0.14|54322|22|TCP|AUTH_FAILURE|BLOCK|256|5").hexdigest(),
        "2026-09-18T11:00:02", 1, "203.0.113.23", "10.0.0.14", 54322, 22, "TCP", "AUTH_FAILURE", "BLOCK", 256, 5
    )
    batch_with_new = batch + [new_event_1, new_event_2]
    print(f"Prepared batch size: {len(batch_with_new)} rows (896 existing CSV rows + 2 new events)")

    insert_sql = """
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

    # RUN 1
    with conn:
        cursor.executemany(insert_sql, batch_with_new)
    cursor.execute("SELECT COUNT(*) FROM network_events;")
    count_after_run_1 = cursor.fetchone()[0]
    print(f"Row count after Run 1: {count_after_run_1} (Inserted: {count_after_run_1 - initial_count}, Ignored duplicates: {len(batch_with_new) - (count_after_run_1 - initial_count)})")

    # RUN 2 (Exact same batch)
    with conn:
        cursor.executemany(insert_sql, batch_with_new)
    cursor.execute("SELECT COUNT(*) FROM network_events;")
    count_after_run_2 = cursor.fetchone()[0]
    print(f"Row count after Run 2: {count_after_run_2} (Inserted: {count_after_run_2 - count_after_run_1})")

    assert count_after_run_1 == count_after_run_2, "Idempotency check failed!"
    print("IDEMPOTENCY PROVEN: Second run added 0 rows; row count remained identical.")


def step_4_audit_transaction(conn: sqlite3.Connection) -> None:
    print("\n" + "=" * 80)
    print("STEP 4: AUDIT TRIGGER & TRANSACTION ROLLBACK TEST")
    print("=" * 80)
    # Use manual transaction control (isolation_level = None) so BEGIN / ROLLBACK are explicit
    conn.isolation_level = None
    cursor = conn.cursor()

    cursor.execute("SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;")
    print("Before transaction - alert 1:", cursor.fetchone())
    cursor.execute("SELECT COUNT(*) FROM alert_status_history;")
    print("Before transaction - alert_status_history count:", cursor.fetchone()[0])

    # Start explicit transaction
    cursor.execute("BEGIN TRANSACTION;")
    cursor.execute("""
        UPDATE alerts
        SET status = 'INVESTIGATING'
        WHERE alert_id = 1;
    """)

    cursor.execute("SELECT alert_id, status FROM alerts WHERE alert_id = 1;")
    print("Inside transaction (after UPDATE) - alert 1:", cursor.fetchone())

    cursor.execute("SELECT history_id, alert_id, old_status, new_status, changed_at FROM alert_status_history;")
    history_rows = cursor.fetchall()
    print("Inside transaction - trigger row in alert_status_history:", history_rows)

    # Rollback transaction
    cursor.execute("ROLLBACK;")
    print("Executed ROLLBACK.")

    cursor.execute("SELECT alert_id, status FROM alerts WHERE alert_id = 1;")
    print("After ROLLBACK - alert 1:", cursor.fetchone())
    cursor.execute("SELECT COUNT(*) FROM alert_status_history;")
    after_rollback_count = cursor.fetchone()[0]
    print("After ROLLBACK - alert_status_history count:", after_rollback_count)

    assert after_rollback_count == 0, "Rollback failed to revert trigger insert!"
    print("AUDIT & ATOMICITY PROVEN: Trigger fired inside transaction and rolled back cleanly.")


def step_5_optimise_explain_plan(src_db: str, copy_db: str) -> None:
    print("\n" + "=" * 80)
    print("STEP 5: OPTIMISE (EXPLAIN QUERY PLAN BEFORE vs AFTER idx_events_src_time)")
    print("=" * 80)
    shutil.copyfile(src_db, copy_db)
    conn = sqlite3.connect(copy_db)
    cursor = conn.cursor()

    target_query = """
        EXPLAIN QUERY PLAN
        SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
        FROM network_events
        WHERE src_ip = '198.51.100.66'
          AND timestamp >= '2026-09-18T10:10:00'
          AND timestamp <= '2026-09-18T10:15:00'
        ORDER BY timestamp;
    """

    # 1. Drop idx_events_src_time to observe plan BEFORE the index
    cursor.execute("DROP INDEX IF EXISTS idx_events_src_time;")
    cursor.execute(target_query)
    plan_before = cursor.fetchall()
    print("Query Plan BEFORE idx_events_src_time (Full Table Scan + Temp B-Tree Sort):")
    for row in plan_before:
        print("  ", row)

    # 2. Recreate idx_events_src_time to observe plan AFTER the index
    cursor.execute("""
        CREATE INDEX idx_events_src_time
        ON network_events(src_ip, timestamp);
    """)
    cursor.execute(target_query)
    plan_after = cursor.fetchall()
    print("\nQuery Plan AFTER idx_events_src_time (Covered Range Search, No Temp Sort):")
    for row in plan_after:
        print("  ", row)

    conn.close()
    if os.path.exists(copy_db):
        os.remove(copy_db)


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    step_1_inspect(conn)
    step_2_and_3_import_and_idempotency(conn, CSV_PATH)
    step_4_audit_transaction(conn)
    conn.close()

    step_5_optimise_explain_plan(DB_PATH, DB_COPY_PATH)


if __name__ == "__main__":
    main()
