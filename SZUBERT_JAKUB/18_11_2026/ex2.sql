SELECT type, name, tbl_name, sql 
FROM sqlite_schema 
WHERE type IN ('table', 'trigger', 'index') 
    AND name NOT LIKE 'sqlite_%';

DROP INDEX IF EXISTS idx_events_src_time;

EXPLAIN QUERY PLAN
SELECT timestamp, event_type
FROM network_events
WHERE src_ip = '198.51.100.77'
    AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;

CREATE INDEX idx_events_src_time ON network_events(src_ip, timestamp);

EXPLAIN QUERY PLAN
SELECT timestamp, event_type
FROM network_events
WHERE src_ip = '198.51.100.77'
    AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;