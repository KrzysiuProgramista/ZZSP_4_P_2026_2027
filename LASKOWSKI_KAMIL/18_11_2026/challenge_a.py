import sqlite3

def run_challenge_a():
    db_path = "network_security.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    print("=== 1. Initializing Schema & Sample Data ===")
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS sensors (
        sensor_id INTEGER PRIMARY KEY,
        sensor_name TEXT UNIQUE NOT NULL,
        location TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS network_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_key TEXT UNIQUE NOT NULL,
        timestamp TEXT NOT NULL,
        sensor_id INTEGER NOT NULL,
        src_ip TEXT NOT NULL,
        dst_ip TEXT NOT NULL,
        src_port INTEGER NOT NULL,
        dst_port INTEGER NOT NULL,
        protocol TEXT NOT NULL,
        event_type TEXT NOT NULL,
        action TEXT NOT NULL,
        bytes INTEGER NOT NULL,
        duration_ms INTEGER NOT NULL,
        FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
    );
    """)

    cursor.executescript("""
    INSERT OR IGNORE INTO sensors (sensor_id, sensor_name, location) VALUES 
    (1, 'perimeter-fw-01', 'Data Center North'),
    (2, 'internal-fw-02', 'Data Center South');

    -- Brute-force / Auth failure burst from 203.0.113.23
    INSERT OR IGNORE INTO network_events (event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port, protocol, event_type, action, bytes, duration_ms) VALUES
    ('ev-101', '2026-09-18T10:20:00', 1, '203.0.113.23', '10.0.0.5', 51000, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 50),
    ('ev-102', '2026-09-18T10:20:15', 1, '203.0.113.23', '10.0.0.5', 51001, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 45),
    ('ev-103', '2026-09-18T10:20:30', 1, '203.0.113.23', '10.0.0.5', 51002, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 60),
    ('ev-104', '2026-09-18T10:20:45', 1, '203.0.113.23', '10.0.0.5', 51003, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 55),
    ('ev-105', '2026-09-18T10:21:00', 1, '203.0.113.23', '10.0.0.5', 51004, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 50),
    ('ev-106', '2026-09-18T10:21:30', 1, '203.0.113.23', '10.0.0.5', 51005, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 52),
    ('ev-107', '2026-09-18T10:22:00', 1, '203.0.113.23', '10.0.0.5', 51006, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 48),
    ('ev-108', '2026-09-18T10:22:30', 1, '203.0.113.23', '10.0.0.5', 51007, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 50),
    ('ev-109', '2026-09-18T10:23:00', 1, '203.0.113.23', '10.0.0.5', 51008, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 60),
    ('ev-110', '2026-09-18T10:24:33', 1, '203.0.113.23', '10.0.0.5', 51009, 22, 'TCP', 'AUTH_FAILURE', 'BLOCK', 120, 49),

    -- General blocked probes from 198.51.100.66
    ('ev-120', '2026-09-18T10:10:00', 1, '198.51.100.66', '10.0.0.10', 40000, 80, 'TCP', 'CONNECTION', 'BLOCK', 40, 10),
    ('ev-121', '2026-09-18T10:10:01', 1, '198.51.100.66', '10.0.0.10', 40001, 443, 'TCP', 'CONNECTION', 'BLOCK', 40, 10),
    ('ev-122', '2026-09-18T10:10:02', 1, '198.51.100.66', '10.0.0.10', 40002, 8080, 'TCP', 'CONNECTION', 'BLOCK', 40, 10),
    ('ev-123', '2026-09-18T10:10:03', 1, '198.51.100.66', '10.0.0.10', 40003, 3306, 'TCP', 'CONNECTION', 'BLOCK', 40, 10),
        -- Allowlisted / Benign traffic from 10.0.0.15
    ('ev-130', '2026-09-18T10:21:00', 2, '10.0.0.15', '10.0.0.50', 50100, 443, 'TCP', 'CONNECTION', 'ALLOW', 1500, 120),
    ('ev-131', '2026-09-18T10:22:00', 2, '10.0.0.15', '10.0.0.50', 50101, 443, 'TCP', 'CONNECTION', 'ALLOW', 1500, 110);
    """)
    conn.commit()

    print("=== 2. Creating View: source_activity_report ===")
    cursor.execute("DROP VIEW IF EXISTS source_activity_report;")

    create_view_sql = """
    CREATE VIEW source_activity_report AS
    WITH recent_events AS (
        -- Grain: One row per event within the 30-minute analytical window
        SELECT 
            src_ip, 
            event_type, 
            action, 
            dst_port,
            timestamp
        FROM network_events
        WHERE timestamp >= '2026-09-18T10:00:00'
          AND timestamp <  '2026-09-18T10:30:00'
    ),
    source_summary AS (
        -- Grain: One row per source IP aggregating metrics via conditional aggregation
        SELECT 
            src_ip,
            COUNT(*) AS total_events,
            SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS failed_logins,
            SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS blocked_events,
            COUNT(DISTINCT dst_port) AS unique_ports
        FROM recent_events
        GROUP BY src_ip
    )
    -- Grain: One row per source IP with calculated metrics and threat classification
    SELECT 
        src_ip,
        total_events,
        failed_logins,
        blocked_events,
        unique_ports,
        CASE 
            WHEN failed_logins >= 5 OR unique_ports >= 10 THEN 'INVESTIGATE'
            WHEN blocked_events >= 5 OR total_events >= 20 THEN 'WATCH'
            ELSE 'NORMAL'
        END AS threat_classification
    FROM source_summary;
    """
    cursor.execute(create_view_sql)
    conn.commit()

    print("\n=== 3. Querying View (`source_activity_report`) ===")
    cursor.execute("SELECT * FROM source_activity_report ORDER BY total_events DESC;")
    print(f"{'Source IP':<18} | {'Total':<6} | {'Failed':<6} | {'Blocked':<8} | {'Ports':<6} | {'Classification':<15}")
    print("-" * 75)
    for row in cursor.fetchall():
        print(f"{row[0]:<18} | {row[1]:<6} | {row[2]:<6} | {row[3]:<8} | {row[4]:<6} | {row[5]:<15}")

    print("\n=== 4. Set Operations: EXCEPT with Allowlist CTE ===")
    set_op_sql = """
    WITH allowlist(src_ip) AS (
        VALUES ('10.0.0.15'), ('10.0.0.20')
    )
    SELECT src_ip, threat_classification 
    FROM source_activity_report
    EXCEPT
    SELECT r.src_ip, r.threat_classification 
    FROM source_activity_report r
    JOIN allowlist a ON r.src_ip = a.src_ip;
    """
    cursor.execute(set_op_sql)
    print(f"{'Source IP':<18} | {'Classification':<15}")
    print("-" * 36)
    for row in cursor.fetchall():
        print(f"{row[0]:<18} | {row[1]:<15}")

    conn.close()

if __name__ == "__main__":
    run_challenge_a()