PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    location    TEXT    NOT NULL DEFAULT 'unspecified'
);

CREATE TABLE IF NOT EXISTS ip_addresses (
    ip_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    address     TEXT    NOT NULL UNIQUE,
    is_private  INTEGER NOT NULL CHECK (is_private IN (0, 1))
);

CREATE TABLE IF NOT EXISTS event_types (
    event_type_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    code             TEXT    NOT NULL UNIQUE,
    default_severity TEXT    NOT NULL CHECK (default_severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE TABLE IF NOT EXISTS network_events (
    event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    event_hash    TEXT    NOT NULL UNIQUE,
    sensor_id     INTEGER NOT NULL REFERENCES sensors(sensor_id) ON DELETE RESTRICT,
    event_type_id INTEGER NOT NULL REFERENCES event_types(event_type_id) ON DELETE RESTRICT,
    src_ip_id     INTEGER NOT NULL REFERENCES ip_addresses(ip_id) ON DELETE RESTRICT,
    dst_ip_id     INTEGER NOT NULL REFERENCES ip_addresses(ip_id) ON DELETE RESTRICT,
    event_time    TEXT    NOT NULL,
    src_port      INTEGER CHECK (src_port IS NULL OR (src_port BETWEEN 1 AND 65535)),
    dst_port      INTEGER CHECK (dst_port IS NULL OR (dst_port BETWEEN 1 AND 65535)),
    protocol      TEXT    NOT NULL CHECK (protocol IN ('TCP', 'UDP', 'ICMP')),
    action        TEXT    NOT NULL CHECK (action IN ('ALLOW', 'BLOCK')),
    bytes         INTEGER NOT NULL CHECK (bytes >= 0),
    duration_ms   INTEGER NOT NULL CHECK (duration_ms >= 0)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code     TEXT    NOT NULL,
    source_ip_id  INTEGER NOT NULL REFERENCES ip_addresses(ip_id) ON DELETE RESTRICT,
    target_ip_id  INTEGER NOT NULL REFERENCES ip_addresses(ip_id) ON DELETE RESTRICT,
    dst_port      INTEGER NOT NULL DEFAULT -1,
    window_start  TEXT    NOT NULL,
    window_end    TEXT    NOT NULL,
    severity      TEXT    NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    event_count   INTEGER NOT NULL CHECK (event_count >= 1),
    description   TEXT    NOT NULL,
    status        TEXT    NOT NULL DEFAULT 'NEW' CHECK (status IN ('NEW', 'INVESTIGATING', 'CLOSED')),
    created_at    TEXT    NOT NULL,
    UNIQUE (rule_code, source_ip_id, target_ip_id, dst_port, window_start)
);

CREATE TABLE IF NOT EXISTS alert_events (
    alert_id INTEGER NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES network_events(event_id) ON DELETE CASCADE,
    PRIMARY KEY (alert_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_events_time        ON network_events(event_time);
CREATE INDEX IF NOT EXISTS idx_events_src_dst     ON network_events(src_ip_id, dst_ip_id, event_time);
CREATE INDEX IF NOT EXISTS idx_events_type_time   ON network_events(event_type_id, event_time);
CREATE INDEX IF NOT EXISTS idx_events_dst_port    ON network_events(dst_port);
CREATE INDEX IF NOT EXISTS idx_alerts_status_sev  ON alerts(status, severity);