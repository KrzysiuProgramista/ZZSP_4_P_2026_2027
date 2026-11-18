-- Challenge A: build an analytical report
-- Source: network_security.db (network_events table)
-- Dataset window: 2026-09-18 10:00:00 UTC inclusive to 11:00:00 UTC exclusive.
-- The README states that the sample timestamps should be interpreted as UTC.

-- Recreate only this report view. The existing suspicious_sources view is untouched.
DROP VIEW IF EXISTS source_activity_report;

CREATE VIEW source_activity_report AS
WITH filtered_events AS (
    -- Grain at this stage: one row per network event in the selected time window.
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
    -- Grain: one row per source IP.
    SELECT
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END)
            AS auth_failure_count,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END)
            AS block_count,
        COUNT(DISTINCT dst_port) AS distinct_destination_ports
    FROM filtered_events
    GROUP BY src_ip
)
SELECT
    src_ip,
    total_events,
    auth_failure_count,
    block_count,
    distinct_destination_ports,
    CASE
        WHEN auth_failure_count >= 5
          OR distinct_destination_ports >= 20
            THEN 'INVESTIGATE'
        WHEN auth_failure_count >= 3
          OR block_count >= 10
          OR total_events >= 50
          OR distinct_destination_ports >= 10
            THEN 'WATCH'
        ELSE 'NORMAL'
    END AS classification
FROM source_summary;

-- Main report: one row per source IP.
SELECT
    src_ip,
    total_events,
    auth_failure_count,
    block_count,
    distinct_destination_ports,
    classification
FROM source_activity_report
ORDER BY
    CASE classification
        WHEN 'INVESTIGATE' THEN 1
        WHEN 'WATCH' THEN 2
        ELSE 3
    END,
    total_events DESC,
    src_ip;

-- Compare investigated sources with a small illustrative allowlist.
-- The 10.0.0.x / 10.0.1.x entries are examples, NOT a verified business allowlist.
-- EXCEPT returns investigated source IPs that are not in this allowlist.
WITH allowlist(src_ip) AS (
    VALUES
        ('10.0.0.14'),
        ('10.0.0.15'),
        ('10.0.0.20'),
        ('10.0.0.25'),
        ('10.0.1.10')
),
investigated_sources AS (
    SELECT src_ip
    FROM source_activity_report
    WHERE classification = 'INVESTIGATE'
)
SELECT src_ip
FROM investigated_sources
EXCEPT
SELECT src_ip
FROM allowlist
ORDER BY src_ip;

-- Grain explanation:
-- * filtered_events: one row per event_id (individual network event).
-- * source_summary: one row per src_ip (aggregated source activity).
-- * source_activity_report: one row per src_ip, with metrics and classification.

-- Sample output (13 rows) from the main report query:
--
-- src_ip          | events | auth_fail | blocked | dst_ports | classification
-- --------------- | ------ | --------- | ------- | --------- | --------------
-- 198.51.100.66   | 26     | 0         | 26      | 26        | INVESTIGATE
-- 203.0.113.23    | 10     | 10        | 10      | 1         | INVESTIGATE
-- 198.51.100.77   | 160    | 0         | 0       | 1         | WATCH
-- 10.0.0.20       | 92     | 0         | 11      | 7         | WATCH
-- 203.0.113.18    | 76     | 0         | 8       | 7         | WATCH
-- 10.0.0.15       | 74     | 0         | 13      | 7         | WATCH
-- 203.0.113.60    | 74     | 0         | 15      | 7         | WATCH
-- 192.0.2.44      | 70     | 0         | 7       | 7         | WATCH
-- 10.0.1.10       | 67     | 0         | 8       | 7         | WATCH
-- 10.0.0.14       | 65     | 0         | 7       | 7         | WATCH
-- 198.51.100.8    | 64     | 0         | 12      | 7         | WATCH
-- 198.51.100.90   | 63     | 0         | 9       | 7         | WATCH
-- 10.0.0.25       | 55     | 0         | 7       | 7         | WATCH
--
-- Sample output of the EXCEPT comparison:
-- 198.51.100.66
-- 203.0.113.23
--
-- Classification rationale (teaching thresholds, not production rules):
-- INVESTIGATE: at least 5 AUTH_FAILURE events OR at least 20 distinct
-- destination ports. These indicate a concentrated authentication-failure
-- burst or broad port scanning behavior in this sample.
-- WATCH: at least 3 AUTH_FAILURE events, 10 BLOCK actions, 50 total events,
-- or 10 distinct destination ports. This flags elevated activity for review.
-- NORMAL: none of the above thresholds is met.
-- INVESTIGATE is tested first so it takes precedence over WATCH.
-- In this sample there are no NORMAL rows because every source meets a WATCH
-- threshold or an INVESTIGATE threshold.
