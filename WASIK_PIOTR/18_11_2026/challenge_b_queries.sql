-- ============================================================================
-- CHALLENGE B: MAKE INGESTION SAFE AND AUDITABLE (SQL REFERENCE & VERIFICATION)
-- ============================================================================
-- Note: Extends/queries the existing schema without recreating existing tables
-- or triggers.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. INSPECT: Read sqlite_schema to identify keys, constraints, triggers, indexes
-- ----------------------------------------------------------------------------
SELECT 
    type,
    name,
    tbl_name,
    sql
FROM sqlite_schema
WHERE name NOT LIKE 'sqlite_%'
ORDER BY 
    CASE type 
        WHEN 'table' THEN 1 
        WHEN 'index' THEN 2 
        WHEN 'trigger' THEN 3 
        WHEN 'view' THEN 4 
        ELSE 5 
    END,
    name;


-- ----------------------------------------------------------------------------
-- 2. IMPORT & IDEMPOTENCY: Full 12-column INSERT with ON CONFLICT(event_key)
-- ----------------------------------------------------------------------------
-- Executed via Python cursor.executemany() using deterministic SHA-256 event_key:
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

-- Verification query (run before, after Run 1, and after Run 2):
SELECT COUNT(*) AS total_network_events FROM network_events;


-- ----------------------------------------------------------------------------
-- 3. AUDIT: Update alert 1 inside an explicit transaction, verify trigger, ROLLBACK
-- ----------------------------------------------------------------------------
BEGIN TRANSACTION;

UPDATE alerts
SET status = 'INVESTIGATING'
WHERE alert_id = 1;

-- Verify alert status changed inside transaction:
SELECT alert_id, source_ip, rule_name, status
FROM alerts
WHERE alert_id = 1;

-- Verify trigger log_alert_status_change automatically inserted audit row:
SELECT history_id, alert_id, old_status, new_status, changed_at
FROM alert_status_history
WHERE alert_id = 1;

-- Revert both the alert update and the trigger-generated audit entry:
ROLLBACK;

-- Confirm state is restored after ROLLBACK:
SELECT alert_id, status FROM alerts WHERE alert_id = 1;
SELECT COUNT(*) AS audit_rows_after_rollback FROM alert_status_history;


-- ----------------------------------------------------------------------------
-- 4. OPTIMISE: Compare EXPLAIN QUERY PLAN before and after idx_events_src_time
-- ----------------------------------------------------------------------------
-- (Run on a copy of network_security.db)

-- A. Plan BEFORE idx_events_src_time:
DROP INDEX IF EXISTS idx_events_src_time;

EXPLAIN QUERY PLAN
SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.66'
  AND timestamp >= '2026-09-18T10:10:00'
  AND timestamp <= '2026-09-18T10:15:00'
ORDER BY timestamp;

-- B. Plan AFTER idx_events_src_time:
CREATE INDEX idx_events_src_time
    ON network_events(src_ip, timestamp);

EXPLAIN QUERY PLAN
SELECT event_id, timestamp, dst_ip, dst_port, event_type, action
FROM network_events
WHERE src_ip = '198.51.100.66'
  AND timestamp >= '2026-09-18T10:10:00'
  AND timestamp <= '2026-09-18T10:15:00'
ORDER BY timestamp;


-- ----------------------------------------------------------------------------
-- 5. DOCUMENTATION: CONFLICT KEY, TRANSACTION BOUNDARY & INDEX CHOICE
-- ----------------------------------------------------------------------------
/*
1. CONFLICT KEY CHOICE (event_key):
   - `event_id` is an internal surrogate primary key (INTEGER PRIMARY KEY) generated
     by SQLite upon insertion, so it cannot detect duplicate source events across
     re-imports.
   - `event_key` has a UNIQUE constraint and stores a deterministic SHA-256 hash
     of all 11 natural attributes of a network event (timestamp, sensor_name,
     src_ip, dst_ip, src_port, dst_port, protocol, event_type, action, bytes,
     duration_ms).
   - Using `ON CONFLICT(event_key) DO NOTHING` guarantees idempotent ingestion:
     re-running the same CSV batch safely skips already-ingested events while
     inserting any newly arrived events without raising IntegrityError.

2. TRANSACTION BOUNDARY:
   - Batch Ingestion: Wrapping `executemany()` in a single transaction (`with conn:`)
     ensures all-or-nothing batch atomicity (preventing partial CSV loads on
     failure) and avoids per-row fsync overhead (orders of magnitude faster).
   - Alert Status Audit: SQLite executes triggers inside the same transaction as
     the firing `UPDATE` statement. Updating `alerts` inside an explicit
     `BEGIN TRANSACTION ... ROLLBACK` block proves that the audit trail in
     `alert_status_history` is strictly atomic with the parent state change—if
     the alert update rolls back, no orphaned audit log row remains.

3. INDEX CHOICE (idx_events_src_time ON network_events(src_ip, timestamp)):
   - Incident investigation queries filter by an exact `src_ip` (`=`) and a
     contiguous time window (`timestamp >= ... AND timestamp <= ...`), ordered by
     `timestamp`.
   - Placing the equality column (`src_ip`) first and the range/sort column
     (`timestamp`) second follows the B-tree leftmost-prefix rule:
     * BEFORE index: SQLite performs a full table scan (`SCAN network_events`)
       followed by an expensive temporary sort (`USE TEMP B-TREE FOR ORDER BY`).
     * AFTER index: SQLite jumps directly to the matching `src_ip` slice and
       scans the `timestamp` range in order (`SEARCH network_events USING INDEX
       idx_events_src_time (src_ip=? AND timestamp>? AND timestamp<?)`),
       eliminating both the full table scan and the temporary sort pass.
*/
