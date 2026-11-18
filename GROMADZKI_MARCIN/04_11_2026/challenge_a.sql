--------------------------------------------------------------------------------
-- Challenge A: Build an Analytical Report
-- Deliverable: One SQL file with comments, grain explanations, and rule justifications.
--------------------------------------------------------------------------------

-- ==============================================================================
-- 1. EXPLANATION OF GRAIN AT EVERY STEP
-- ==============================================================================
-- * filtered_events CTE: One row represents a single individual network event 
--   (log entry) recorded within the specified time range.
-- * summarised_sources CTE: One row represents a unique source IP (src_ip) 
--   aggregated across all events matching the time window.
-- * source_activity_report View: One row represents a unique source IP paired with 
--   its summary statistics and calculated risk classification.
-- * Set Comparison Queries (EXCEPT / INTERSECT): One row represents a filtered 
--   source IP evaluated against the allowlist set operations.

-- ==============================================================================
-- 2. CLASSIFICATION RULES & THRESHOLD JUSTIFICATION
-- ==============================================================================
-- * INVESTIGATE: Triggered if auth_failure_count >= 5, block_count >= 15, or 
--   distinct_dst_ports >= 15. 
--   -> Justification: High thresholds signify potential brute-force attacks, 
--      aggressive port scanning, or malicious automated activity.
-- * WATCH: Triggered if auth_failure_count >= 1 or block_count >= 8.
--   -> Justification: Moderate anomalous behavior that warrants active monitoring 
--      without immediate escalation.
-- * NORMAL: Default state for all other sources with baseline or benign patterns.

-- ==============================================================================
-- 3. SQL IMPLEMENTATION
-- ==============================================================================

DROP VIEW IF EXISTS source_activity_report;

CREATE VIEW source_activity_report AS
WITH filtered_events AS (
    -- Grain: One row per single network event
    SELECT
        event_id,
        timestamp,
        src_ip,
        dst_port,
        event_type,
        action
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <= '2026-09-18T10:59:59'
),

summarised_sources AS (
    -- Grain: One row per unique source IP (src_ip)
    SELECT
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS auth_failure_count,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS block_count,
        COUNT(DISTINCT dst_port) AS distinct_dst_ports
    FROM filtered_events
    GROUP BY src_ip
)

-- Grain: One row per source IP with risk classification
SELECT
    src_ip,
    total_events,
    auth_failure_count,
    block_count,
    distinct_dst_ports,
    CASE
        WHEN auth_failure_count >= 5
          OR block_count >= 15
          OR distinct_dst_ports >= 15
            THEN 'INVESTIGATE'

        WHEN auth_failure_count >= 1
          OR block_count >= 8
            THEN 'WATCH'

        ELSE 'NORMAL'
    END AS risk_classification
FROM summarised_sources;


-- ==============================================================================
-- 4. REPORT QUERIES & SET COMPARISONS
-- ==============================================================================

-- 4.1. Main Report Output (Sorted by Risk Severity & Volume)
SELECT *
FROM source_activity_report
ORDER BY
    CASE risk_classification
        WHEN 'INVESTIGATE' THEN 1
        WHEN 'WATCH' THEN 2
        ELSE 3
    END,
    total_events DESC;


-- 4.2. Set Comparison: EXCEPT (Suspicious IPs not on the allowlist)
WITH allowlist AS (
    SELECT '10.0.0.14' AS src_ip
    UNION ALL
    SELECT '10.0.0.15'
    UNION ALL
    SELECT '10.0.0.20'
)

SELECT src_ip
FROM source_activity_report
WHERE risk_classification IN ('WATCH', 'INVESTIGATE')

EXCEPT

SELECT src_ip
FROM allowlist

ORDER BY src_ip;


-- 4.3. Set Comparison: INTERSECT (Allowlisted IPs flagged as WATCH/INVESTIGATE)
WITH allowlist AS (
    SELECT '10.0.0.14' AS src_ip
    UNION ALL
    SELECT '10.0.0.15'
    UNION ALL
    SELECT '10.0.0.20'
)

SELECT src_ip
FROM source_activity_report
WHERE risk_classification IN ('WATCH', 'INVESTIGATE')

INTERSECT

SELECT src_ip
FROM allowlist

ORDER BY src_ip;