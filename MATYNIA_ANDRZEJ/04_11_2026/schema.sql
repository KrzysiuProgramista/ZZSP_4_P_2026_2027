PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    location TEXT
);

CREATE TABLE IF NOT EXISTS ip_addresses (
    ip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE,
    is_private INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS event_types (
    event_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    default_severity TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS network_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    event_type_id INTEGER NOT NULL,
    src_ip_id INTEGER NOT NULL,
    dst_ip_id INTEGER NOT NULL,
    event_time TEXT NOT NULL,
    src_port INTEGER CHECK(src_port BETWEEN 1 AND 65535),
    dst_port INTEGER CHECK(dst_port BETWEEN 1 AND 65535),
    protocol TEXT NOT NULL CHECK(protocol IN ('TCP','UDP','ICMP')),
    bytes INTEGER NOT NULL CHECK(bytes >= 0),
    FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id),
    FOREIGN KEY (event_type_id) REFERENCES event_types(event_type_id),
    FOREIGN KEY (src_ip_id) REFERENCES ip_addresses(ip_id),
    FOREIGN KEY (dst_ip_id) REFERENCES ip_addresses(ip_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code TEXT NOT NULL,
    source_ip_id INTEGER,
    target_ip_id INTEGER,
    severity TEXT NOT NULL,
    event_count INTEGER NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW',
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_ip_id) REFERENCES ip_addresses(ip_id),
    FOREIGN KEY (target_ip_id) REFERENCES ip_addresses(ip_id),
    UNIQUE(rule_code, source_ip_id, target_ip_id, window_start)
);
