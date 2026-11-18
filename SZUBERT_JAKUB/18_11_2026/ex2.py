import sqlite3

conn = sqlite3.connect('network_security.db')
try:
    conn.execute('PRAGMA foreign_keys = ON')

    insert_sql = """
    INSERT INTO network_events (
        event_key, timestamp, sensor_id, src_ip, dst_ip,
        src_port, dst_port, protocol, event_type, action,
        bytes, duration_ms
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(event_key) DO NOTHING;
    """

    sample_batch = [
        ('test-key-999', '2026-09-18T12:00:00', 1, '192.0.2.50', '10.0.0.5',
         54321, 443, 'TCP', 'CONNECTION', 'ALLOW', 1024, 50)
    ]

    with conn:
        conn.executemany(insert_sql, sample_batch)
    count_after_first = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]

    with conn:
        conn.executemany(insert_sql, sample_batch)
    count_after_second = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]

    print(f"Amount of row after first import: {count_after_first}")
    print(f"Amount of rows after second import: {count_after_second}")

    conn.execute("BEGIN")
    conn.execute("UPDATE alerts SET status = 'INVESTIGATING' WHERE alert_id = 1")
    
    history = conn.execute(
        "SELECT alert_id, old_status, new_status FROM alert_status_history WHERE alert_id = 1"
    ).fetchall()
    print("Input in history inside of trasnsaction:", history)

    conn.execute("ROLLBACK")
    
    history_after = conn.execute("SELECT COUNT(*) FROM alert_status_history WHERE alert_id = 1").fetchone()[0]
    print(f"History' rows after ROLLBACK: {history_after}")

finally:
    conn.close()