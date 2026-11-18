/*
  Advanced SQL & Database Engineering
  SQL component of the reliable event-ingestion pipeline (slide 38).

  Database: network_security.db
  Existing schema objects are reused; do not recreate the tables or trigger.

  IMPORTANT:
  - Python performs CSV parsing/validation and computes the deterministic
    SHA-256 event_key from the 11 source CSV fields.
  - This file contains the SQLite statements used by the ingestion pipeline.
  - Run with SQLite. Parameterized INSERT is intended to be called from
    Python sqlite3.executemany(); its 12 values are supplied by the importer.
*/

PRAGMA foreign_keys = ON;

-- 1. INSPECT THE EXISTING DATABASE (read-only)
SELECT type, name, sql
FROM sqlite_schema
WHERE type IN ('table', 'index', 'view', 'trigger')
ORDER BY type, name;

PRAGMA table_info(network_events);
PRAGMA foreign_key_list(network_events);
PRAGMA index_list(network_events);

-- 2. LOOK UP SENSOR IDS
-- Python uses this result to map CSV sensor_name to the required sensor_id.
SELECT sensor_id, sensor_name
FROM sensors
ORDER BY sensor_id;

-- 3. IDEMPOTENT EVENT INSERT
-- Bind the 12 values in this order:
-- event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port,
-- protocol, event_type, action, bytes, duration_ms.
-- Repeated event_key values are ignored by the UNIQUE constraint.
INSERT INTO network_events (
    event_key, timestamp, sensor_id, src_ip, dst_ip,
    src_port, dst_port, protocol, event_type, action, bytes, duration_ms
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING;

-- 4. VERIFY IDEMPOTENCY
-- Capture this count before and after importing the same batch twice.
SELECT COUNT(*) AS event_rows
FROM network_events;

SELECT COUNT(DISTINCT event_key) AS distinct_event_keys
FROM network_events;

-- Expected for the supplied starter database before any new import:
-- event_rows = 896
-- distinct_event_keys = 896

-- 5. REPORT / OBSERVABILITY
-- The existing view is queried, not recreated.
SELECT *
FROM suspicious_sources
ORDER BY failed_logins DESC;

-- Recent events for a source IP (uses idx_events_src_time).
SELECT timestamp, event_type, action, dst_ip, dst_port
FROM network_events
WHERE src_ip = ?
  AND timestamp >= ?
ORDER BY timestamp DESC;

-- 6. AUDIT-TRIGGER TEST
-- Alert 1 starts as OPEN. The trigger inserts an audit row when the
-- status genuinely changes. ROLLBACK leaves the starter database unchanged.
BEGIN;

UPDATE alerts
SET status = 'INVESTIGATING'
WHERE alert_id = 1;

SELECT alert_id, old_status, new_status, changed_at
FROM alert_status_history
WHERE alert_id = 1
ORDER BY history_id DESC;

-- Expected inside this transaction: OPEN -> INVESTIGATING.
ROLLBACK;

-- Verify that both the alert update and its trigger-generated history row
-- were rolled back.
SELECT alert_id, status
FROM alerts
WHERE alert_id = 1;

SELECT COUNT(*) AS history_rows
FROM alert_status_history
WHERE alert_id = 1;

-- Expected after ROLLBACK: status = OPEN; history_rows = 0.

-- 7. QUERY-PLAN CHECK
-- The starter database already has idx_events_src_time.
EXPLAIN QUERY PLAN
SELECT timestamp, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.77'
  AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;

-- Expected: SQLite should use idx_events_src_time for the source/time lookup.
-- Exact EXPLAIN QUERY PLAN wording varies by SQLite version.

-- 8. FINAL INTEGRITY CHECKS
PRAGMA foreign_key_check;

SELECT
    (SELECT COUNT(*) FROM network_events) AS event_count,
    (SELECT COUNT(DISTINCT event_key) FROM network_events) AS unique_event_keys,
    (SELECT COUNT(*) FROM alert_status_history) AS audit_history_rows;
