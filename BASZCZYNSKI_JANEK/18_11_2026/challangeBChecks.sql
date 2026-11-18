-- =============================================================================
-- Challenge B: Make Ingestion Safe and Auditable
-- Database: network_security.db (SQLite)
-- Note: Do NOT recreate existing tables or triggers.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. INSPECT: Read sqlite_schema for keys, constraints, triggers, and indexes
-- -----------------------------------------------------------------------------
SELECT
    type,
    name,
    tbl_name,
    sql
FROM sqlite_schema
WHERE name NOT LIKE 'sqlite_%'
ORDER BY type, name;


-- -----------------------------------------------------------------------------
-- 2. IMPORT (Template): Full 12-column idempotent INSERT
--    (Executed via Python executemany() with parameter placeholders below;
--     event_id is omitted so SQLite assigns the INTEGER PRIMARY KEY.)
-- -----------------------------------------------------------------------------
-- INSERT INTO network_events (
--     event_key, timestamp, sensor_id, src_ip, dst_ip,
--     src_port, dst_port, protocol, event_type, action,
--     bytes, duration_ms
-- ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
-- ON CONFLICT(event_key) DO NOTHING;


-- -----------------------------------------------------------------------------
-- 3. AUDIT: Test log_alert_status_change trigger inside a transaction, then ROLLBACK
--    (Adjust target status if alert 1 is not currently 'OPEN'.)
-- -----------------------------------------------------------------------------
BEGIN;

UPDATE alerts
SET status = CASE
    WHEN status <> 'INVESTIGATING' THEN 'INVESTIGATING'
    ELSE 'OPEN'
END
WHERE alert_id = 1;

-- Inspect the audit row written by the AFTER UPDATE trigger inside this txn:
SELECT
    history_id,
    alert_id,
    old_status,
    new_status,
    changed_at
FROM alert_status_history
WHERE alert_id = 1
ORDER BY history_id DESC;

ROLLBACK;

-- Confirm both tables reverted cleanly:
SELECT alert_id, status FROM alerts WHERE alert_id = 1;
SELECT COUNT(*) AS history_count_after_rollback FROM alert_status_history;


-- -----------------------------------------------------------------------------
-- 4. OPTIMISE: Compare EXPLAIN QUERY PLAN before and after idx_events_src_time
--    IMPORTANT: Run this section ONLY on a COPY of network_security.db!
-- -----------------------------------------------------------------------------
DROP INDEX IF EXISTS idx_events_src_time;

-- BEFORE index (expects SCAN network_events + TEMP B-TREE for ORDER BY):
EXPLAIN QUERY PLAN
SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.66'
  AND timestamp >= '2026-09-18T10:10:00'
  AND timestamp <  '2026-09-18T10:20:00'
ORDER BY timestamp;

CREATE INDEX IF NOT EXISTS idx_events_src_time
    ON network_events(src_ip, timestamp);

-- AFTER index (expects SEARCH network_events USING INDEX idx_events_src_time):
EXPLAIN QUERY PLAN
SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.66'
  AND timestamp >= '2026-09-18T10:10:00'
  AND timestamp <  '2026-09-18T10:20:00'
ORDER BY timestamp;