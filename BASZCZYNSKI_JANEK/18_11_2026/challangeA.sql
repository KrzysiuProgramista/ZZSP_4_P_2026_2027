-- =============================================================================
-- Challenge A: Build an Analytical Report
-- Target database: network_security.db (SQLite)
-- Source table:    network_events
--
-- Chosen time range: 2026-09-18T10:00:00Z to 2026-09-18T11:00:00Z (exclusive)
-- Covers the full 1-hour capture window in network_events_sample.csv.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- PART 1: Standalone Analytical Query (Write SQL first)
-- -----------------------------------------------------------------------------
-- GRAIN BY STEP:
--   0. network_events (base table):
--      1 row = 1 raw network event captured by a sensor.
--   1. filtered_events (CTE):
--      1 row = 1 network event within the chosen 1-hour UTC window.
--   2. source_summary (CTE):
--      1 row = 1 distinct source IP (src_ip) active in the chosen window,
--      aggregated to total events, AUTH_FAILURE count, BLOCK count, and
--      distinct destination port count.
--   3. Final SELECT:
--      1 row = 1 distinct source IP (src_ip) with its derived risk
--      classification ('NORMAL', 'WATCH', or 'INVESTIGATE').
-- -----------------------------------------------------------------------------

WITH filtered_events AS (
    -- Step 1 (Filter): Restrict events to the chosen UTC time window.
    -- Grain: 1 row per network event inside [2026-09-18T10:00:00, 11:00:00).
    SELECT
        event_id,
        timestamp,
        src_ip,
        dst_port,
        event_type,
        action
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <  '2026-09-18T11:00:00'
),
source_summary AS (
    -- Step 2 (Summarise): Aggregate to source-IP grain.
    -- Grain: 1 row per distinct src_ip.
    SELECT
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS auth_failure_count,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS block_count,
        COUNT(DISTINCT dst_port) AS distinct_dst_ports
    FROM filtered_events
    GROUP BY src_ip
)
-- Step 3 (Classify): Assign NORMAL, WATCH, or INVESTIGATE using CASE.
-- Grain: 1 row per distinct src_ip.
SELECT
    src_ip,
    total_events,
    auth_failure_count,
    block_count,
    distinct_dst_ports,
    CASE
        WHEN auth_failure_count >= 5
          OR distinct_dst_ports >= 15
          OR block_count        >= 20
          OR total_events       >= 120
            THEN 'INVESTIGATE'
        WHEN auth_failure_count >= 1
          OR distinct_dst_ports >= 8
          OR block_count        >= 10
          OR total_events       >= 90
            THEN 'WATCH'
        ELSE 'NORMAL'
    END AS classification
FROM source_summary
ORDER BY
    CASE classification
        WHEN 'INVESTIGATE' THEN 1
        WHEN 'WATCH'       THEN 2
        ELSE 3
    END,
    auth_failure_count DESC,
    block_count DESC,
    total_events DESC,
    src_ip ASC;


-- -----------------------------------------------------------------------------
-- PART 2: Expose Reusable Result Through a New View
-- -----------------------------------------------------------------------------
-- Creates `source_activity_report` without touching `suspicious_sources`.
-- Grain of `source_activity_report`: 1 row = 1 distinct source IP (src_ip)
-- observed in the 2026-09-18T10:00:00Z .. 2026-09-18T11:00:00Z window.
-- -----------------------------------------------------------------------------

DROP VIEW IF EXISTS source_activity_report;

CREATE VIEW source_activity_report AS
WITH filtered_events AS (
    SELECT
        event_id,
        timestamp,
        src_ip,
        dst_port,
        event_type,
        action
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <  '2026-09-18T11:00:00'
),
source_summary AS (
    SELECT
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS auth_failure_count,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS block_count,
        COUNT(DISTINCT dst_port) AS distinct_dst_ports
    FROM filtered_events
    GROUP BY src_ip
)
SELECT
    src_ip,
    total_events,
    auth_failure_count,
    block_count,
    distinct_dst_ports,
    CASE
        WHEN auth_failure_count >= 5
          OR distinct_dst_ports >= 15
          OR block_count        >= 20
          OR total_events       >= 120
            THEN 'INVESTIGATE'
        WHEN auth_failure_count >= 1
          OR distinct_dst_ports >= 8
          OR block_count        >= 10
          OR total_events       >= 90
            THEN 'WATCH'
        ELSE 'NORMAL'
    END AS classification
FROM source_summary;

-- Verify the view contents:
SELECT *
FROM source_activity_report
ORDER BY
    CASE classification
        WHEN 'INVESTIGATE' THEN 1
        WHEN 'WATCH'       THEN 2
        ELSE 3
    END,
    total_events DESC,
    src_ip ASC;


-- -----------------------------------------------------------------------------
-- PART 3: Compare Sets Using EXCEPT and INTERSECT with an Allowlist CTE
-- -----------------------------------------------------------------------------
-- allowlist CTE grain: 1 row = 1 trusted/internal source IP (10.0.0.0/8 hosts).
-- -----------------------------------------------------------------------------

-- 3A. EXCEPT: External / non-allowlisted sources flagged as WATCH or INVESTIGATE.
-- Grain: 1 row = 1 flagged source IP not present in the allowlist.
WITH allowlist(src_ip) AS (
    VALUES
        ('10.0.0.14'),
        ('10.0.0.15'),
        ('10.0.0.20'),
        ('10.0.0.25'),
        ('10.0.1.10')
)
SELECT src_ip
FROM source_activity_report
WHERE classification IN ('WATCH', 'INVESTIGATE')
EXCEPT
SELECT src_ip
FROM allowlist
ORDER BY src_ip;

-- 3B. INTERSECT: Allowlisted internal sources that still triggered WATCH or
--     INVESTIGATE (useful for spotting noisy or compromised internal hosts).
-- Grain: 1 row = 1 allowlisted source IP that also appeared in WATCH/INVESTIGATE.
WITH allowlist(src_ip) AS (
    VALUES
        ('10.0.0.14'),
        ('10.0.0.15'),
        ('10.0.0.20'),
        ('10.0.0.25'),
        ('10.0.1.10')
)
SELECT src_ip
FROM source_activity_report
WHERE classification IN ('WATCH', 'INVESTIGATE')
INTERSECT
SELECT src_ip
FROM allowlist
ORDER BY src_ip;


-- -----------------------------------------------------------------------------
-- PART 4: Sample Output & Classification Rules Explanation
-- -----------------------------------------------------------------------------
--
-- SAMPLE OUTPUT (SELECT * FROM source_activity_report ...):
-- (Exact counts verified from CSV for the three incident IPs; background host
--  counts marked with ~ are approximate until run directly against the .db file.)
--
-- src_ip          total_events  auth_failure_count  block_count  distinct_dst_ports  classification
-- --------------  ------------  ------------------  -----------  ------------------  --------------
-- 203.0.113.23              10                  10           10                   1  INVESTIGATE
-- 198.51.100.66             26                   0           26                  26  INVESTIGATE
-- 198.51.100.77            160                   0            0                   1  INVESTIGATE
-- 203.0.113.60             ~70                   0          ~15                   7  WATCH
-- 198.51.100.8             ~70                   0          ~12                   7  WATCH
-- 10.0.0.15                ~70                   0          ~12                   7  WATCH
-- 10.0.0.20                ~70                   0          ~11                   7  WATCH
-- 198.51.100.90            ~70                   0           ~9                   7  NORMAL
-- 10.0.1.10                ~70                   0           ~8                   7  NORMAL
-- 203.0.113.18             ~70                   0           ~8                   7  NORMAL
-- 192.0.2.44               ~70                   0           ~7                   7  NORMAL
-- 10.0.0.14                ~70                   0           ~7                   7  NORMAL
-- 10.0.0.25                ~70                   0           ~7                   7  NORMAL
--
-- SAMPLE OUTPUT (3A. Flagged EXCEPT allowlist):
--   198.51.100.66
--   198.51.100.77
--   198.51.100.8
--   203.0.113.23
--   203.0.113.60
--
-- SAMPLE OUTPUT (3B. Flagged INTERSECT allowlist):
--   10.0.0.15
--   10.0.0.20
--
--
-- JUSTIFICATION OF CLASSIFICATION RULES:
--
-- Baseline context in this 1-hour dataset:
--   Normal hosts average ~70 events across 7 standard service ports
--   (22, 53, 80, 123, 443, 3389, 8080), with 0 AUTH_FAILURE events and ~7-9 blocks.
--
-- 1. INVESTIGATE (Immediate analyst triage):
--    - auth_failure_count >= 5 : Indicates brute-force / credential-stuffing
--      rather than an occasional mistyped password (flags 203.0.113.23: 10 failures).
--    - distinct_dst_ports >= 15: More than 2x the 7-port baseline footprint;
--      strongly signals port scanning/enumeration (flags 198.51.100.66: 26 ports).
--    - block_count >= 20       : Sustained firewall denials in a 1-hour window
--      (flags 198.51.100.66: 26 blocks).
--    - total_events >= 120     : Nearly 2x the normal hourly volume, indicating a
--      traffic flood / DoS burst (flags 198.51.100.77: 160 events in <1 minute).
--
-- 2. WATCH (Elevated / borderline activity to monitor):
--    - auth_failure_count >= 1 : Any failed login deserves visibility.
--    - distinct_dst_ports >= 8 : Activity extending beyond the 7 standard ports.
--    - block_count >= 10       : Double-digit blocks (~14%+ block rate on a
--      70-event baseline), separating noisier hosts from normal ~7-9 block hosts.
--    - total_events >= 90      : Moderately above normal hourly traffic volume.
--
-- 3. NORMAL:
--    - Everything below all WATCH thresholds; consistent with baseline traffic.
-- =============================================================================