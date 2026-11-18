-- Challenge A: source activity analytical report
-- SQLite SQL. Run from the folder containing network_security.db:
--   sqlite3 network_security.db < source_activity_report.sql
--
-- Reporting window: [2026-09-18 10:00:00, 2026-09-18 11:00:00)
-- The starter data spans 10:00:00 through 10:59:56 UTC. A half-open
-- interval avoids double-counting the boundary if adjacent windows are used.
--
-- Grain:
--   filtered_events: one row per network event in the reporting window.
--   source_summary:  one row per source IP.
--   source_activity_report view: one row per source IP.
--
-- Classification rationale (teaching thresholds, not production detection):
--   INVESTIGATE: >=5 AUTH_FAILURE events OR >=20 BLOCK actions OR
--                >=20 distinct destination ports.
--   WATCH:       >=60 total events OR >=8 BLOCK actions OR
--                >=7 distinct destination ports.
--   NORMAL:      everything else.
-- INVESTIGATE thresholds flag concentrated authentication failures,
-- broad blocking, or unusually broad destination-port activity. WATCH
-- catches high-volume or moderately broad activity for human review.

DROP VIEW IF EXISTS source_activity_report;

CREATE VIEW source_activity_report AS
WITH filtered_events AS (
    SELECT event_id, timestamp, src_ip, dst_port, event_type, action
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <  '2026-09-18T11:00:00'
),
source_summary AS (
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
          OR block_count >= 20
          OR distinct_destination_ports >= 20
            THEN 'INVESTIGATE'
        WHEN total_events >= 60
          OR block_count >= 8
          OR distinct_destination_ports >= 7
            THEN 'WATCH'
        ELSE 'NORMAL'
    END AS classification
FROM source_summary;

-- Main report: one row per source IP.
SELECT *
FROM source_activity_report
ORDER BY
    CASE classification
        WHEN 'INVESTIGATE' THEN 1
        WHEN 'WATCH' THEN 2
        ELSE 3
    END,
    total_events DESC,
    src_ip;

-- Set comparison: WATCH/INVESTIGATE sources excluding a small allowlist.
-- Replace these illustrative entries with an approved inventory in practice.
WITH allowlist(src_ip) AS (
    VALUES ('10.0.0.14'), ('10.0.0.15'), ('10.0.0.20')
),
attention_sources AS (
    SELECT src_ip
    FROM source_activity_report
    WHERE classification IN ('WATCH', 'INVESTIGATE')
)
SELECT src_ip
FROM attention_sources
EXCEPT
SELECT src_ip
FROM allowlist
ORDER BY src_ip;

-- Example detail row for the source with repeated authentication failures.
SELECT *
FROM source_activity_report
WHERE src_ip = '203.0.113.23';
