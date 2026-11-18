-- ============================================================================
-- Challenge B: Make Ingestion Safe and Auditable
-- Database: network_security.db (SQLite)
-- Note: Extends/uses existing schema without recreating existing tables/triggers.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. INSPECT: Read sqlite_schema to identify keys, constraints, triggers, indexes
-- ----------------------------------------------------------------------------
SELECT type, name, tbl_name, sql
FROM sqlite_schema
WHERE type IN ('table', 'index', 'trigger', 'view')
ORDER BY type, tbl_name, name;

PRAGMA index_list('network_events');
PRAGMA index_info('idx_events_src_time');
PRAGMA foreign_key_list('network_events');
PRAGMA foreign_key_list('alert_status_history');

-- ----------------------------------------------------------------------------
-- 2. IMPORT & 3. PROVE IDEMPOTENCY (Full 12-column INSERT with ON CONFLICT)
-- ----------------------------------------------------------------------------
-- Parameterized statement used in Python executemany():
/*
INSERT INTO network_events (
    event_key,
    timestamp,
    sensor_id,
    src_ip,
    dst_ip,
    src_port,
    dst_port,
    protocol,
    event_type,
    action,
    bytes,
    duration_ms
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING;
*/

SELECT COUNT(*) AS total_network_events FROM network_events;

-- ----------------------------------------------------------------------------
-- 4. AUDIT: Update alert 1 inside a transaction, show trigger history, ROLLBACK
-- ----------------------------------------------------------------------------
BEGIN TRANSACTION;

SELECT alert_id, source_ip, rule_name, status
FROM alerts
WHERE alert_id = 1;

-- Trigger log_alert_status_change fires AFTER UPDATE OF status ON alerts
UPDATE alerts
SET status = 'INVESTIGATING'
WHERE alert_id = 1;

SELECT history_id, alert_id, old_status, new_status, changed_at
FROM alert_status_history
WHERE alert_id = 1;

ROLLBACK;

SELECT alert_id, source_ip, rule_name, status
FROM alerts
WHERE alert_id = 1;

SELECT COUNT(*) AS history_rows_after_rollback
FROM alert_status_history;

-- ----------------------------------------------------------------------------
-- 5. OPTIMISE: Compare EXPLAIN QUERY PLAN before and after idx_events_src_time
-- (Executed on a temporary copy of network_security.db)
-- ----------------------------------------------------------------------------
EXPLAIN QUERY PLAN
SELECT event_id, timestamp, src_ip, dst_ip, dst_port, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.90'
  AND timestamp BETWEEN '2026-09-18T10:00:00' AND '2026-09-18T10:30:00'
ORDER BY timestamp;