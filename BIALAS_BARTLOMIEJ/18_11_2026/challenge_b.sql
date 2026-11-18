/*
CHALLENGE B — SAFE AND AUDITABLE EVENT INGESTION
Target: the supplied network_security.db schema.

This SQL file accompanies challenge_b.py. It documents and provides the SQL
statements used by the Python importer and the manual verification steps.

The Python script:
- validates CSV fields and resolves sensor_name -> sensor_id;
- calculates event_key as SHA-256 of the 11 original CSV values joined by "|";
- calls the 12-column INSERT below with sqlite3.executemany();
- runs tests against a disposable copy of the starter database.
*/

PRAGMA foreign_keys = ON;

-- 1) Inspect existing schema objects. Tables and trigger already exist:
SELECT type, name, sql
FROM sqlite_schema
WHERE type IN ('table', 'index', 'view', 'trigger')
ORDER BY type, name;

-- 2) Resolve sensor IDs used by the imported CSV rows:
SELECT sensor_id, sensor_name
FROM sensors
ORDER BY sensor_id;

-- 3) Full 12-column idempotent event insert.
-- Python binds values in this exact order for every CSV row.
INSERT INTO network_events (
    event_key, timestamp, sensor_id, src_ip, dst_ip,
    src_port, dst_port, protocol, event_type, action, bytes, duration_ms
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING;

-- 4) Idempotency evidence: execute the INSERT batch twice from Python,
-- then compare the row counts. The second execution must insert zero rows.
SELECT COUNT(*) AS event_rows,
       COUNT(DISTINCT event_key) AS distinct_event_keys
FROM network_events;

-- 5) Audit trigger test. Run as one transaction on a disposable DB copy.
-- The trigger should insert OPEN -> INVESTIGATING into the history table.
BEGIN;

UPDATE alerts
SET status = 'INVESTIGATING'
WHERE alert_id = 1;

SELECT alert_id, old_status, new_status, changed_at
FROM alert_status_history
WHERE alert_id = 1
ORDER BY history_id DESC;

ROLLBACK;

-- After ROLLBACK, alert 1 must be OPEN and no new history row may remain.
SELECT alert_id, status
FROM alerts
WHERE alert_id = 1;

SELECT COUNT(*) AS history_rows
FROM alert_status_history
WHERE alert_id = 1;

-- 6) Query-plan comparison. Run both EXPLAIN statements on a disposable copy.
-- The first plan is measured without the composite index.
DROP INDEX IF EXISTS idx_events_src_time;

EXPLAIN QUERY PLAN
SELECT timestamp, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.77'
  AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;

-- Create the composite index matching WHERE src_ip = ? and timestamp >= ?.
CREATE INDEX idx_events_src_time
ON network_events(src_ip, timestamp);

-- The second plan should use idx_events_src_time.
EXPLAIN QUERY PLAN
SELECT timestamp, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.77'
  AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;

-- 7) Final integrity checks:
PRAGMA foreign_key_check;
