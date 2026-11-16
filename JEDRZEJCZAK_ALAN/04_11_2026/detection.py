"""Explainable SQL-driven rules using fixed UTC-aligned time buckets."""
from datetime import datetime, timezone, timedelta

# Thresholds and window duration are deliberately configurable constants.
RULES = {
    "PORT_SCAN": {"threshold": 20, "seconds": 300, "severity": "HIGH"},
    "BRUTE_FORCE": {"threshold": 8, "seconds": 300, "severity": "HIGH"},
    "TRAFFIC_FLOOD": {"threshold": 150, "seconds": 60, "severity": "CRITICAL"},
}

# A bucket is [start, end), e.g. 10:10:00 through 10:14:59.999...
# Fixed windows are allowed by the assignment (see slide 15).
BUCKET_SQL = "(CAST(strftime('%s', e.event_time) AS INTEGER) / {seconds}) * {seconds}"


def find_candidates(conn, rule_code, config):
    bucket = BUCKET_SQL.format(seconds=config["seconds"])
    if rule_code == "PORT_SCAN":
        sql = f"""
            SELECT e.src_ip_id, e.dst_ip_id, NULL AS dst_port,
                   {bucket} AS bucket_epoch,
                   COUNT(*) AS event_count,
                   COUNT(DISTINCT e.dst_port) AS metric_count
            FROM network_events e
            WHERE e.dst_port IS NOT NULL
            GROUP BY e.src_ip_id, e.dst_ip_id, bucket_epoch
            HAVING COUNT(DISTINCT e.dst_port) >= ?
            ORDER BY bucket_epoch, e.src_ip_id, e.dst_ip_id
        """
    elif rule_code == "BRUTE_FORCE":
        sql = f"""
            SELECT e.src_ip_id, e.dst_ip_id, e.dst_port,
                   {bucket} AS bucket_epoch,
                   COUNT(*) AS event_count,
                   COUNT(*) AS metric_count
            FROM network_events e
            JOIN event_types t ON e.event_type_id = t.event_type_id
            WHERE t.code = 'AUTH_FAILURE' AND e.dst_port IS NOT NULL
            GROUP BY e.src_ip_id, e.dst_ip_id, e.dst_port, bucket_epoch
            HAVING COUNT(*) >= ?
            ORDER BY bucket_epoch, e.src_ip_id, e.dst_ip_id, e.dst_port
        """
    elif rule_code == "TRAFFIC_FLOOD":
        sql = f"""
            SELECT e.src_ip_id, e.dst_ip_id, e.dst_port,
                   {bucket} AS bucket_epoch,
                   COUNT(*) AS event_count,
                   COUNT(*) AS metric_count
            FROM network_events e
            GROUP BY e.src_ip_id, e.dst_ip_id, e.dst_port, bucket_epoch
            HAVING COUNT(*) >= ?
            ORDER BY bucket_epoch, e.src_ip_id, e.dst_ip_id, e.dst_port
        """
    else:
        raise ValueError(f"Unknown detection rule: {rule_code}")
    return conn.execute(sql, (config["threshold"],)).fetchall()


def format_epoch(value):
    return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def evidence_ids(conn, rule, candidate, start, end):
    sql = """SELECT e.event_id FROM network_events e
             WHERE e.src_ip_id = ? AND e.dst_ip_id = ?
             AND e.event_time >= ? AND e.event_time < ?"""
    params = [candidate["src_ip_id"],candidate["dst_ip_id"],start,end]
    if rule == "PORT_SCAN":
        sql += " AND e.dst_port IS NOT NULL"
    else:
        sql += " AND e.dst_port IS ?"
        params.append(candidate["dst_port"])
    if rule == "BRUTE_FORCE":
        sql += " AND e.event_type_id = (SELECT event_type_id FROM event_types WHERE code = ?)"
        params.append("AUTH_FAILURE")
    sql += " ORDER BY e.event_id"
    return [row[0] for row in conn.execute(sql, params)]


def detect(conn):
    stats = {"new": 0, "existing": 0, "by_rule": {}}
    with conn:
        for rule, config in RULES.items():
            stats["by_rule"][rule] = 0
            for hit in find_candidates(conn, rule, config):
                start = format_epoch(hit["bucket_epoch"])
                end = format_epoch(hit["bucket_epoch"] + config["seconds"])
                src = conn.execute("SELECT address FROM ip_addresses WHERE ip_id = ?", (hit["src_ip_id"],)).fetchone()[0]
                dst = conn.execute("SELECT address FROM ip_addresses WHERE ip_id = ?", (hit["dst_ip_id"],)).fetchone()[0]
                port = hit["dst_port"]
                if rule == "PORT_SCAN":
                    metric = f"{hit['metric_count']} distinct destination ports"
                else:
                    metric = f"{hit['event_count']} events"
                target = f"{dst}:{port}" if port is not None else dst
                description = f"{rule}: {src} -> {target}; {metric} in UTC window [{start}, {end}); inspect evidence before conclusions."
                result = conn.execute("""
                    INSERT OR IGNORE INTO alerts(
                      rule_code,source_ip_id,target_ip_id,dst_port,window_start,window_end,
                      severity,event_count,metric_count,description
                    ) VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (
                    rule,hit["src_ip_id"],hit["dst_ip_id"],port,start,end,
                    config["severity"],hit["event_count"],hit["metric_count"],description,
                ))
                if result.rowcount:
                    stats["new"] += 1
                else:
                    stats["existing"] += 1
                stats["by_rule"][rule] += 1
                alert_id = conn.execute("""
                    SELECT alert_id FROM alerts WHERE rule_code = ? AND source_ip_id = ?
                     AND target_ip_id = ? AND dst_port IS ? AND window_start = ? AND window_end = ?
                """, (rule,hit["src_ip_id"],hit["dst_ip_id"],port,start,end)).fetchone()[0]
                # Update counts in case new events entered this fixed bucket since last detection;
                # the analyst-controlled status stays untouched.
                conn.execute("""
                    UPDATE alerts SET event_count = ?, metric_count = ?, description = ?
                    WHERE alert_id = ?
                """, (hit["event_count"],hit["metric_count"],description,alert_id))
                ids = evidence_ids(conn,rule,hit,start,end)
                if len(ids) != hit["event_count"]:
                    raise RuntimeError(f"Detection evidence count mismatch: {rule} bucket={start}")
                conn.executemany(
                    "INSERT OR IGNORE INTO alert_events(alert_id,event_id) VALUES (?,?)",
                    ((alert_id, event_id) for event_id in ids),
                )
    return stats
