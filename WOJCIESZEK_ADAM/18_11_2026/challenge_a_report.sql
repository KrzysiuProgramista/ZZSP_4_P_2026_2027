-- ============================================================================
-- Challenge A: Build an Analytical Report (source_activity_report)
-- Grain of final output: One row per source IP (src_ip) in the chosen window.
-- ============================================================================

-- 1. Standalone analytical query using CTEs
WITH filtered_events AS (
    -- Grain: One row per network_event within the chosen time range
    SELECT
        event_id,
        timestamp,
        src_ip,
        dst_port,
        event_type,
        action
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <= '2026-09-18T11:00:59'
),
ip_summary AS (
    -- Grain: One row per distinct src_ip in the filtered time range
    SELECT
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS auth_failure_count,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS block_count,
        COUNT(DISTINCT dst_port) AS distinct_dst_ports
    FROM filtered_events
    GROUP BY src_ip
),
classified_ips AS (
    -- Grain: One row per src_ip with risk classification applied
    SELECT
        src_ip,
        total_events,
        auth_failure_count,
        block_count,
        distinct_dst_ports,
        CASE
            WHEN auth_failure_count >= 3
              OR block_count >= 10
              OR distinct_dst_ports >= 15
              OR total_events >= 100 THEN 'INVESTIGATE'
            WHEN auth_failure_count >= 1
              OR block_count >= 4
              OR distinct_dst_ports >= 8 THEN 'WATCH'
            ELSE 'NORMAL'
        END AS risk_tier
    FROM ip_summary
),
allowlist AS (
    -- Grain: One row per allowlisted IP address
    SELECT '10.0.0.14' AS src_ip
    UNION ALL SELECT '10.0.0.15'
    UNION ALL SELECT '10.0.0.20'
    UNION ALL SELECT '10.0.0.25'
    UNION ALL SELECT '10.0.1.10'
),
allowlisted_flagged_ips AS (
    -- Set comparison:
    -- INTERSECT finds IPs present in both classified_ips and allowlist.
    -- EXCEPT finds IPs in classified_ips that are NOT in allowlist.
    SELECT src_ip, 1 AS is_allowlisted
    FROM classified_ips
    INTERSECT
    SELECT src_ip, 1 AS is_allowlisted
    FROM allowlist
),
non_allowlisted_ips AS (
    SELECT src_ip
    FROM classified_ips
    EXCEPT
    SELECT src_ip
    FROM allowlist
)
SELECT
    c.src_ip,
    c.total_events,
    c.auth_failure_count,
    c.block_count,
    c.distinct_dst_ports,
    c.risk_tier,
    CASE WHEN a.src_ip IS NOT NULL THEN 'ALLOWLISTED' ELSE 'NON_ALLOWLISTED' END AS allowlist_status
FROM classified_ips c
LEFT JOIN allowlisted_flagged_ips a
    ON c.src_ip = a.src_ip
ORDER BY
    CASE c.risk_tier
        WHEN 'INVESTIGATE' THEN 1
        WHEN 'WATCH' THEN 2
        ELSE 3
    END,
    c.total_events DESC;

-- 2. Reusable view (does not touch or overwrite suspicious_sources)
CREATE VIEW IF NOT EXISTS source_activity_report AS
WITH filtered_events AS (
    -- Grain: One row per network_event within the chosen time range
    SELECT
        event_id,
        timestamp,
        src_ip,
        dst_port,
        event_type,
        action
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <= '2026-09-18T11:00:59'
),
ip_summary AS (
    -- Grain: One row per src_ip in the filtered time range
    SELECT
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS auth_failure_count,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS block_count,
        COUNT(DISTINCT dst_port) AS distinct_dst_ports
    FROM filtered_events
    GROUP BY src_ip
),
classified_ips AS (
    -- Grain: One row per src_ip with classification
    SELECT
        src_ip,
        total_events,
        auth_failure_count,
        block_count,
        distinct_dst_ports,
        CASE
            WHEN auth_failure_count >= 3
              OR block_count >= 10
              OR distinct_dst_ports >= 15
              OR total_events >= 100 THEN 'INVESTIGATE'
            WHEN auth_failure_count >= 1
              OR block_count >= 4
              OR distinct_dst_ports >= 8 THEN 'WATCH'
            ELSE 'NORMAL'
        END AS risk_tier
    FROM ip_summary
),
allowlist AS (
    SELECT '10.0.0.14' AS src_ip
    UNION ALL SELECT '10.0.0.15'
    UNION ALL SELECT '10.0.0.20'
    UNION ALL SELECT '10.0.0.25'
    UNION ALL SELECT '10.0.1.10'
),
allowlisted_matches AS (
    SELECT src_ip FROM classified_ips
    INTERSECT
    SELECT src_ip FROM allowlist
)
SELECT
    c.src_ip,
    c.total_events,
    c.auth_failure_count,
    c.block_count,
    c.distinct_dst_ports,
    c.risk_tier,
    CASE WHEN m.src_ip IS NOT NULL THEN 1 ELSE 0 END AS is_allowlisted
FROM classified_ips c
LEFT JOIN allowlisted_matches m
    ON c.src_ip = m.src_ip;

-- 3. Example set-comparison queries using INTERSECT and EXCEPT
-- Non-allowlisted IPs flagged for INVESTIGATION:
SELECT src_ip FROM source_activity_report WHERE risk_tier = 'INVESTIGATE'
EXCEPT
SELECT src_ip FROM source_activity_report WHERE is_allowlisted = 1;

-- Allowlisted IPs that also appear in the report:
SELECT src_ip FROM source_activity_report WHERE is_allowlisted = 1
INTERSECT
SELECT src_ip FROM (
    SELECT '10.0.0.14' AS src_ip UNION ALL SELECT '10.0.0.15' UNION ALL
    SELECT '10.0.0.20' UNION ALL SELECT '10.0.0.25' UNION ALL SELECT '10.0.1.10'
);