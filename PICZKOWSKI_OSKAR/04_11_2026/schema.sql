-- Network Security Event Analyzer schema.
-- Timestamps are ISO 8601 strings in UTC: YYYY-MM-DDTHH:MM:SS.

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id  INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0),
    location   TEXT
);

CREATE TABLE IF NOT EXISTS ip_addresses (
    ip_id      INTEGER PRIMARY KEY,
    address    TEXT NOT NULL UNIQUE,
    is_private INTEGER NOT NULL CHECK (is_private IN (0, 1))
);

CREATE TABLE IF NOT EXISTS event_types (
    event_type_id    INTEGER PRIMARY KEY,
    code             TEXT NOT NULL UNIQUE,
    default_severity TEXT NOT NULL
        CHECK (default_severity IN ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

CREATE TABLE IF NOT EXISTS network_events (
    event_id      INTEGER PRIMARY KEY,
    event_key     TEXT NOT NULL UNIQUE,              -- SHA-256 of the normalised record (dedup)
    sensor_id     INTEGER NOT NULL REFERENCES sensors(sensor_id),
    event_type_id INTEGER NOT NULL REFERENCES event_types(event_type_id),
    src_ip_id     INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    dst_ip_id     INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    event_time    TEXT NOT NULL,
    src_port      INTEGER CHECK (src_port IS NULL OR src_port BETWEEN 1 AND 65535),
    dst_port      INTEGER CHECK (dst_port IS NULL OR dst_port BETWEEN 1 AND 65535),
    protocol      TEXT NOT NULL CHECK (protocol IN ('TCP', 'UDP', 'ICMP')),
    action        TEXT NOT NULL CHECK (action IN ('ALLOW', 'BLOCK')),
    bytes         INTEGER NOT NULL CHECK (bytes >= 0),
    duration_ms   INTEGER NOT NULL CHECK (duration_ms >= 0)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id     INTEGER PRIMARY KEY,
    rule_code    TEXT NOT NULL CHECK (rule_code IN ('PORT_SCAN', 'BRUTE_FORCE', 'TRAFFIC_FLOOD')),
    source_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    target_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    service_port INTEGER NOT NULL DEFAULT 0 CHECK (service_port BETWEEN 0 AND 65535), -- 0 = not port-specific
    window_start TEXT NOT NULL,
    window_end   TEXT NOT NULL,
    severity     TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status       TEXT NOT NULL DEFAULT 'NEW' CHECK (status IN ('NEW', 'INVESTIGATING', 'CLOSED')),
    event_count  INTEGER NOT NULL CHECK (event_count >= 0),
    description  TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    -- Uniqueness strategy: one alert per rule, endpoint pair, service and window.
    UNIQUE (rule_code, source_ip_id, target_ip_id, service_port, window_start)
);

CREATE INDEX IF NOT EXISTS idx_events_time     ON network_events(event_time);
CREATE INDEX IF NOT EXISTS idx_events_pair     ON network_events(src_ip_id, dst_ip_id, event_time);
CREATE INDEX IF NOT EXISTS idx_events_dst_port ON network_events(dst_port);
CREATE INDEX IF NOT EXISTS idx_alerts_status   ON alerts(status, severity);
