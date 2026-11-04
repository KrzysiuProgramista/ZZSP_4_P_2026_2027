-- Network Security Event Analyzer | Python stdlib + SQLite
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK(length(trim(name)) > 0),
    location TEXT
);

CREATE TABLE IF NOT EXISTS ip_addresses (
    ip_id INTEGER PRIMARY KEY,
    address TEXT NOT NULL UNIQUE CHECK(length(address) > 0),
    is_private INTEGER NOT NULL CHECK(is_private IN (0,1))
);

CREATE TABLE IF NOT EXISTS event_types (
    event_type_id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    default_severity TEXT NOT NULL CHECK(default_severity IN ('INFO','LOW','MEDIUM','HIGH','CRITICAL'))
);

CREATE TABLE IF NOT EXISTS network_events (
    event_id INTEGER PRIMARY KEY,
    event_hash TEXT NOT NULL UNIQUE,
    sensor_id INTEGER NOT NULL REFERENCES sensors(sensor_id),
    event_type_id INTEGER NOT NULL REFERENCES event_types(event_type_id),
    src_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    dst_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    event_time TEXT NOT NULL,
    raw_timestamp TEXT NOT NULL,
    src_port INTEGER CHECK(src_port BETWEEN 1 AND 65535),
    dst_port INTEGER CHECK(dst_port BETWEEN 1 AND 65535),
    protocol TEXT NOT NULL CHECK(protocol IN ('TCP','UDP','ICMP')),
    action TEXT NOT NULL CHECK(action IN ('ALLOW','BLOCK')),
    bytes INTEGER NOT NULL CHECK(bytes >= 0),
    duration_ms INTEGER NOT NULL CHECK(duration_ms >= 0)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY,
    rule_code TEXT NOT NULL CHECK(rule_code IN ('PORT_SCAN','BRUTE_FORCE','TRAFFIC_FLOOD')),
    source_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    target_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    dst_port INTEGER CHECK(dst_port BETWEEN 1 AND 65535),
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('HIGH','CRITICAL')),
    status TEXT NOT NULL DEFAULT 'NEW' CHECK(status IN ('NEW','INVESTIGATING','CLOSED')),
    event_count INTEGER NOT NULL CHECK(event_count >= 1),
    metric_count INTEGER NOT NULL CHECK(metric_count >= 1),
    description TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    CHECK(window_end > window_start)
);

-- COALESCE ensures nullable dst_port cannot create duplicate alerts.
CREATE UNIQUE INDEX IF NOT EXISTS ux_alert_identity ON alerts(
    rule_code, source_ip_id, target_ip_id, COALESCE(dst_port, -1), window_start, window_end
);

CREATE TABLE IF NOT EXISTS alert_events (
    alert_id INTEGER NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES network_events(event_id) ON DELETE CASCADE,
    PRIMARY KEY(alert_id, event_id)
);

CREATE TABLE IF NOT EXISTS import_rejections (
    rejection_id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK(line_number >= 2),
    reason TEXT NOT NULL,
    raw_row TEXT NOT NULL,
    rejected_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);

CREATE INDEX IF NOT EXISTS idx_events_time ON network_events(event_time);
CREATE INDEX IF NOT EXISTS idx_events_endpoints_time ON network_events(src_ip_id,dst_ip_id,event_time);
CREATE INDEX IF NOT EXISTS idx_events_type_port_time ON network_events(event_type_id,dst_port,event_time);
CREATE INDEX IF NOT EXISTS idx_events_dst_port_time ON network_events(dst_ip_id,dst_port,event_time);
CREATE INDEX IF NOT EXISTS idx_alerts_severity_status ON alerts(severity,status);
