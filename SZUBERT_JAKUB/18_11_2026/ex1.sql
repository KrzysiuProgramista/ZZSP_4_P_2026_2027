DROP VIEW IF EXISTS source_activity_report;

CREATE VIEW source_activity_report AS
WITH filtered_events AS (
    SELECT src_ip, event_type, action, dst_port
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00' 
      AND timestamp <  '2026-09-18T11:00:00'
),
source_summary AS (
    SELECT 
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS failed_logins,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS blocked_events,
        COUNT(DISTINCT dst_port) AS unique_ports
    FROM filtered_events
    GROUP BY src_ip
)

SELECT 
    s.src_ip,
    s.total_events,
    s.failed_logins,
    s.blocked_events,
    s.unique_ports,
    CASE 
        WHEN s.failed_logins >= 5 OR s.unique_ports >= 20 THEN 'INVESTIGATE'
        WHEN s.blocked_events > 0 THEN 'WATCH'
        ELSE 'NORMAL'
    END AS classification
FROM source_summary s
WHERE s.src_ip NOT IN (
    SELECT src_ip FROM (VALUES ('10.0.0.14'), ('10.0.0.15')) AS allowlist(src_ip)
);