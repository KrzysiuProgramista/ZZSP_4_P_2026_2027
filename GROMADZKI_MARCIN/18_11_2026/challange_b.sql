PRAGMA foreign_keys = ON;

-- 1. Inspect existing schema (keys, constraints, triggers, indexes)
SELECT type, name, tbl_name, sql
FROM sqlite_schema
WHERE name NOT LIKE 'sqlite_%'
ORDER BY type, name;

-- 2. Full 12-column network_events idempotent INSERT template
INSERT INTO network_events (
    event_key, timestamp, sensor_id, src_ip, dst_ip,
    src_port, dst_port, protocol, event_type, action,
    bytes, duration_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING;

-- 3. Prove idempotency check
SELECT COUNT(*) AS network_events_count FROM network_events;

-- 4. Audit: Update alert 1 inside a transaction, inspect trigger row, ROLLBACK
BEGIN;
    SELECT alert_id, source_ip, rule_name, status
    FROM alerts
    WHERE alert_id = 1;

    UPDATE alerts
    SET status = 'INVESTIGATING'
    WHERE alert_id = 1;

    SELECT history_id, alert_id, old_status, new_status, changed_at
    FROM alert_status_history
    ORDER BY history_id DESC
    LIMIT 5;
ROLLBACK;

-- Confirm rollback restored alert 1 and left alert_status_history clean
SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;
SELECT COUNT(*) AS history_count_after_rollback FROM alert_status_history;

-- 5. Optimise (run ONLY on a copy: network_security_copy.db)
DROP INDEX IF EXISTS idx_events_src_time;

EXPLAIN QUERY PLAN
SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
FROM network_events
WHERE src_ip = '192.168.1.10'
ORDER BY timestamp DESC;

CREATE INDEX idx_events_src_time
ON network_events (src_ip, timestamp);

EXPLAIN QUERY PLAN
SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
FROM network_events
WHERE src_ip = '192.168.1.10'
ORDER BY timestamp DESC;