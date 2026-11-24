-- ============================================================================
-- Challenge B: Make Ingestion Safe and Auditable
-- Target DB: network_security.db (extends existing schema without recreating
-- existing tables/triggers).
-- ============================================================================

-- 1. Inspect existing schema (keys, constraints, triggers, indexes)
SELECT type, name, tbl_name, sql
FROM sqlite_schema
WHERE sql IS NOT NULL
ORDER BY type, name;

-- 2. Idempotent 12-column INSERT pattern for network_events
-- (event_id is AUTOINCREMENT/PRIMARY KEY; the 12 explicit columns are:
--  event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port,
--  protocol, event_type, action, bytes, duration_ms)
-- Executed via executemany() in ingest_network_events.py:
-- INSERT INTO network_events (
--     event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port,
--     protocol, event_type, action, bytes, duration_ms
-- ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
-- ON CONFLICT(event_key) DO NOTHING;

-- 3. Audit test on alert 1 inside a transaction, showing trigger history row, then ROLLBACK
BEGIN TRANSACTION;

UPDATE alerts
SET status = 'INVESTIGATING'
WHERE alert_id = 1;

-- Verify trigger inserted an audit record into alert_status_history
SELECT history_id, alert_id, old_status, new_status, changed_at
FROM alert_status_history
WHERE alert_id = 1
ORDER BY history_id DESC;

ROLLBACK;

-- Confirm alert 1 reverted and no uncommitted history row remains
SELECT alert_id, source_ip, rule_name, status FROM alerts WHERE alert_id = 1;
SELECT COUNT(*) AS alert_1_history_rows_after_rollback FROM alert_status_history WHERE alert_id = 1;

-- 4. Query plan comparison for source-IP + time-range lookup
EXPLAIN QUERY PLAN
SELECT event_id, timestamp, dst_ip, dst_port, event_type, action, bytes
FROM network_events
WHERE src_ip = '198.51.100.66'
  AND timestamp BETWEEN '2026-09-18T10:00:00' AND '2026-09-18T11:00:59';