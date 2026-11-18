
import csv
import hashlib
import os
import shutil
import sqlite3

DB_PATH = "network_security.db"
CSV_PATH = "network_events_sample.csv"
DB_COPY_PATH = "network_security_plan_test.db"


def compute_event_key(row):
    values = [
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
        str(row["duration_ms"])
    ]
    return hashlib.sha256("|".join(values).encode()).hexdigest()


def inspect_database(conn):
    print("\n=== DATABASE STRUCTURE ===")
    cur = conn.cursor()

    cur.execute("""
        SELECT type, name, tbl_name, sql
        FROM sqlite_schema
        WHERE name NOT LIKE 'sqlite_%'
        ORDER BY type, name;
    """)

    for obj in cur.fetchall():
        print(f"\n{obj[0].upper()}: {obj[1]} ({obj[2]})")
        print(obj[3])


def load_batch(conn, path):
    cur = conn.cursor()
    cur.execute("SELECT sensor_name, sensor_id FROM sensors")
    sensors = dict(cur.fetchall())

    records = []

    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            records.append((
                compute_event_key(row),
                row["timestamp"],
                sensors[row["sensor_name"]],
                row["src_ip"],
                row["dst_ip"],
                int(row["src_port"]) if row["src_port"] else None,
                int(row["dst_port"]),
                row["protocol"],
                row["event_type"],
                row["action"],
                int(row["bytes"]),
                int(row["duration_ms"])
            ))

    return records


def import_events(conn, path):
    print("\n=== IMPORT AND IDEMPOTENCY TEST ===")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM network_events")
    initial = cur.fetchone()[0]

    records = load_batch(conn, path)

    extra_1 = (
        hashlib.sha256(
            b"2026-09-18T11:00:01|edge-fw-01|198.51.100.66|10.0.0.10|54321|443|TCP|CONNECTION|BLOCK|512|15"
        ).hexdigest(),
        "2026-09-18T11:00:01", 2, "198.51.100.66",
        "10.0.0.10", 54321, 443, "TCP", "CONNECTION",
        "BLOCK", 512, 15
    )

    extra_2 = (
        hashlib.sha256(
            b"2026-09-18T11:00:02|core-sensor-02|203.0.113.23|10.0.0.14|54322|22|TCP|AUTH_FAILURE|BLOCK|256|5"
        ).hexdigest(),
        "2026-09-18T11:00:02", 1, "203.0.113.23",
        "10.0.0.14", 54322, 22, "TCP", "AUTH_FAILURE",
        "BLOCK", 256, 5
    )

    records.extend([extra_1, extra_2])

    sql = """
        INSERT INTO network_events (
            event_key, timestamp, sensor_id, src_ip, dst_ip,
            src_port, dst_port, protocol, event_type,
            action, bytes, duration_ms
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(event_key) DO NOTHING;
    """

    with conn:
        cur.executemany(sql, records)

    cur.execute("SELECT COUNT(*) FROM network_events")
    first_count = cur.fetchone()[0]

    print("Initial records:", initial)
    print("After first import:", first_count)

    with conn:
        cur.executemany(sql, records)

    cur.execute("SELECT COUNT(*) FROM network_events")
    second_count = cur.fetchone()[0]

    print("After second import:", second_count)

    assert first_count == second_count, "Idempotency test failed"

    print("Idempotency verified successfully.")


def test_audit(conn):
    print("\n=== AUDIT AND ROLLBACK TEST ===")

    conn.isolation_level = None
    cur = conn.cursor()

    cur.execute("""
        SELECT alert_id, source_ip, rule_name, status
        FROM alerts
        WHERE alert_id = 1
    """)
    print("Before:", cur.fetchone())

    cur.execute("SELECT COUNT(*) FROM alert_status_history")
    history_before = cur.fetchone()[0]

    cur.execute("BEGIN TRANSACTION")

    cur.execute("""
        UPDATE alerts
        SET status = 'INVESTIGATING'
        WHERE alert_id = 1
    """)

    cur.execute("""
        SELECT alert_id, status
        FROM alerts
        WHERE alert_id = 1
    """)
    print("During transaction:", cur.fetchone())

    cur.execute("""
        SELECT history_id, alert_id, old_status,
               new_status, changed_at
        FROM alert_status_history
    """)

    print("History records:", cur.fetchall())

    cur.execute("ROLLBACK")

    cur.execute("""
        SELECT alert_id, status
        FROM alerts
        WHERE alert_id = 1
    """)
    print("After rollback:", cur.fetchone())

    cur.execute("SELECT COUNT(*) FROM alert_status_history")
    history_after = cur.fetchone()[0]

    assert history_before == history_after, "Rollback failed"

    print("Rollback verified successfully.")


def compare_query_plans(source, copy):
    print("\n=== QUERY PLAN COMPARISON ===")

    shutil.copyfile(source, copy)

    conn = sqlite3.connect(copy)
    cur = conn.cursor()

    query = """
        EXPLAIN QUERY PLAN
        SELECT event_id, timestamp, dst_ip,
               dst_port, event_type, action
        FROM network_events
        WHERE src_ip = '198.51.100.66'
          AND timestamp >= '2026-09-18T10:10:00'
          AND timestamp <= '2026-09-18T10:15:00'
        ORDER BY timestamp;
    """

    cur.execute("DROP INDEX IF EXISTS idx_events_src_time")
    cur.execute(query)

    before = cur.fetchall()

    print("\nPlan before index:")
    for item in before:
        print(item)

    cur.execute("""
        CREATE INDEX idx_events_src_time
        ON network_events(src_ip, timestamp)
    """)

    cur.execute(query)
    after = cur.fetchall()

    print("\nPlan after index:")
    for item in after:
        print(item)

    conn.close()
    os.remove(copy)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    inspect_database(conn)
    import_events(conn, CSV_PATH)
    test_audit(conn)

    conn.close()

    compare_query_plans(DB_PATH, DB_COPY_PATH)


if __name__ == "__main__":
    main()
