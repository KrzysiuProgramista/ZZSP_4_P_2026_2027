PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id   INTEGER PRIMARY KEY,
    sensor_name TEXT NOT NULL UNIQUE,
    location    TEXT NOT NULL DEFAULT 'unknown'
);

CREATE TABLE IF NOT EXISTS network_events (
    event_id    INTEGER PRIMARY KEY,
    event_key   TEXT NOT NULL UNIQUE,
    timestamp   TEXT NOT NULL,
    sensor_id   INTEGER NOT NULL REFERENCES sensors(sensor_id) ON DELETE RESTRICT,
    src_ip      TEXT NOT NULL,
    dst_ip      TEXT NOT NULL,
    src_port    INTEGER CHECK(src_port BETWEEN 1 AND 65535),
    dst_port    INTEGER NOT NULL CHECK(dst_port BETWEEN 1 AND 65535),
    protocol    TEXT NOT NULL CHECK(protocol IN ('TCP', 'UDP', 'ICMP')),
    event_type  TEXT NOT NULL,
    action      TEXT NOT NULL CHECK(action IN ('ALLOW', 'BLOCK')),
    bytes       INTEGER NOT NULL DEFAULT 0 CHECK(bytes >= 0),
    duration_ms INTEGER NOT NULL DEFAULT 0 CHECK(duration_ms >= 0)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id   INTEGER PRIMARY KEY,
    source_ip  TEXT NOT NULL,
    rule_name  TEXT NOT NULL,
    status     TEXT NOT NULL CHECK(status IN ('OPEN','INVESTIGATING','CLOSED','FALSE_POSITIVE')),
    first_seen TEXT NOT NULL,
    last_seen  TEXT NOT NULL,
    event_count INTEGER NOT NULL CHECK(event_count > 0),
    UNIQUE(source_ip, rule_name, first_seen)
);

CREATE TABLE IF NOT EXISTS alert_status_history (
    history_id INTEGER PRIMARY KEY,
    alert_id   INTEGER NOT NULL REFERENCES alerts(alert_id) ON DELETE RESTRICT,
    old_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_statistics (
    source_ip   TEXT PRIMARY KEY,
    event_count INTEGER NOT NULL CHECK(event_count >= 0),
    last_seen   TEXT NOT NULL
);

-- Index for the common source-IP + time-range query in the lecture.
CREATE INDEX IF NOT EXISTS idx_events_src_time
    ON network_events(src_ip, timestamp);

-- Useful for filtering by event type and time during detection/reporting.
CREATE INDEX IF NOT EXISTS idx_events_type_time
    ON network_events(event_type, timestamp);

-- Useful for alert history lookups by alert.
CREATE INDEX IF NOT EXISTS idx_alert_history_alert_time
    ON alert_status_history(alert_id, changed_at);

CREATE TRIGGER IF NOT EXISTS log_alert_status_change
AFTER UPDATE OF status ON alerts
FOR EACH ROW
WHEN OLD.status <> NEW.status
BEGIN
    INSERT INTO alert_status_history (alert_id, old_status, new_status)
    VALUES (NEW.alert_id, OLD.status, NEW.status);
END;
