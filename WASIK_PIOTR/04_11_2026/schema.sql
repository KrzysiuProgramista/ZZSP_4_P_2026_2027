-- Database Schema for Network Security Event Analyzer

PRAGMA foreign_keys = ON;

-- 1. Sensors Table
CREATE TABLE IF NOT EXISTS sensors (
    sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    location TEXT
);

-- 2. IP Addresses Table
CREATE TABLE IF NOT EXISTS ip_addresses (
    ip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE,
    is_private INTEGER NOT NULL CHECK (is_private IN (0, 1))
);

-- 3. Event Types Table
CREATE TABLE IF NOT EXISTS event_types (
    event_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    default_severity TEXT NOT NULL DEFAULT 'INFO' CHECK (default_severity IN ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
);

-- 4. Network Events Table
CREATE TABLE IF NOT EXISTS network_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL REFERENCES sensors(sensor_id),
    event_type_id INTEGER NOT NULL REFERENCES event_types(event_type_id),
    src_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    dst_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    event_time TEXT NOT NULL,
    src_port INTEGER CHECK (src_port IS NULL OR src_port BETWEEN 1 AND 65535),
    dst_port INTEGER CHECK (dst_port IS NULL OR dst_port BETWEEN 1 AND 65535),
    protocol TEXT NOT NULL CHECK (protocol IN ('TCP', 'UDP', 'ICMP')),
    action TEXT NOT NULL CHECK (action IN ('ALLOW', 'BLOCK')),
    bytes INTEGER NOT NULL CHECK (bytes >= 0),
    duration_ms INTEGER NOT NULL CHECK (duration_ms >= 0),
    event_hash TEXT NOT NULL UNIQUE
);

-- 5. Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code TEXT NOT NULL,
    source_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    target_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    dst_port INTEGER,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    event_count INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW' CHECK (status IN ('NEW', 'INVESTIGATING', 'CLOSED')),
    created_at TEXT NOT NULL,
    UNIQUE(rule_code, source_ip_id, target_ip_id, window_start)
);

-- Indexes for optimal query performance
CREATE INDEX IF NOT EXISTS idx_events_time ON network_events(event_time);
CREATE INDEX IF NOT EXISTS idx_events_src_ip ON network_events(src_ip_id);
CREATE INDEX IF NOT EXISTS idx_events_dst_ip ON network_events(dst_ip_id);
CREATE INDEX IF NOT EXISTS idx_alerts_rule ON alerts(rule_code);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
