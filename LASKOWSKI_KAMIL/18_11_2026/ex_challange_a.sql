WITH recent_events AS (
    SELECT 
        src_ip, 
        event_type, 
        action, 
        dst_port,
        timestamp
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
    FROM recent_events
    GROUP BY src_ip
)
SELECT 
    src_ip,
    total_events,
    failed_logins,
    blocked_events,
    unique_ports,
    CASE 
        WHEN failed_logins >= 5 OR unique_ports >= 10 THEN 'INVESTIGATE'
        WHEN blocked_events >= 5 OR total_events >= 20 THEN 'WATCH'
        ELSE 'NORMAL'
    END AS threat_classification
FROM source_summary
ORDER BY total_events DESC;
DROP VIEW IF EXISTS source_activity_report;

CREATE VIEW source_activity_report AS
WITH recent_events AS (
    SELECT 
        src_ip, 
        event_type, 
        action, 
        dst_port,
        timestamp
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
    FROM recent_events
    GROUP BY src_ip
)
SELECT 
    src_ip,
    total_events,
    failed_logins,
    blocked_events,
    unique_ports,
    CASE 
        WHEN failed_logins >= 5 OR unique_ports >= 10 THEN 'INVESTIGATE'
        WHEN blocked_events >= 5 OR total_events >= 20 THEN 'WATCH'
        ELSE 'NORMAL'
    END AS threat_classification
FROM source_summary;

SELECT * 
FROM source_activity_report 
ORDER BY total_events DESC;

WITH allowlist(src_ip) AS (
    VALUES ('10.0.0.14'), ('10.0.0.15'), ('10.0.0.20')
)
SELECT src_ip, threat_classification 
FROM source_activity_report
EXCEPT
SELECT r.src_ip, r.threat_classification 
FROM source_activity_report r
JOIN allowlist a ON r.src_ip = a.src_ip
ORDER BY threat_classification, src_ip;