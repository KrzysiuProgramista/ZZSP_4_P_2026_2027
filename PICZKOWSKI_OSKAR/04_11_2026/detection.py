"""Rule-based detection. SQL performs grouping and counting; Python persists alerts."""
from datetime import datetime, timedelta, timezone

from config import RULES
from db import transaction

# Fixed, aligned time buckets: epoch seconds rounded down to the window size.
_BUCKET = "(CAST(strftime('%s', e.event_time) AS INTEGER) / {w} * {w})"

_RULE_SQL = """
SELECT e.src_ip_id, e.dst_ip_id,
       {service} AS service_port,
       {bucket} AS bucket_start,
       {metric} AS metric,
       COUNT(*) AS event_count,
       s.address AS src_address,
       d.address AS dst_address
FROM network_events e
JOIN ip_addresses s ON s.ip_id = e.src_ip_id
JOIN ip_addresses d ON d.ip_id = e.dst_ip_id
JOIN event_types t  ON t.event_type_id = e.event_type_id
WHERE {where}
GROUP BY e.src_ip_id, e.dst_ip_id, {extra_group} bucket_start
HAVING {metric} >= ?
"""

# Only constant SQL fragments live here; user data is always bound with '?'.
_SPECS = {
    "PORT_SCAN": {
        "service": "0",
        "metric": "COUNT(DISTINCT e.dst_port)",
        "where": "e.dst_port IS NOT NULL",
        "extra_group": "",
    },
    "BRUTE_FORCE": {
        "service": "e.dst_port",
        "metric": "COUNT(*)",
        "where": "t.code = 'AUTH_FAILURE'",
        "extra_group": "e.dst_port,",
    },
    "TRAFFIC_FLOOD": {
        "service": "e.dst_port",
        "metric": "COUNT(*)",
        "where": "e.dst_port IS NOT NULL",
        "extra_group": "e.dst_port,",
    },
}

_INSERT_ALERT = """
INSERT OR IGNORE INTO alerts
  (rule_code, source_ip_id, target_ip_id, service_port, window_start, window_end,
   severity, status, event_count, description, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, 'NEW', ?, ?, ?)
"""


def _describe(rule, row, metric_value, start, end, threshold):
    src, dst, window = row["src_address"], row["dst_address"], f"{start} to {end} UTC"
    if rule == "PORT_SCAN":
        return (f"{src} contacted {metric_value} distinct destination ports on {dst} "
                f"({row['event_count']} events) between {window}. "
                f"Rule threshold: {threshold} distinct ports.")
    if rule == "BRUTE_FORCE":
        return (f"{src} generated {metric_value} AUTH_FAILURE events against "
                f"{dst}:{row['service_port']} between {window}. "
                f"Rule threshold: {threshold} failures.")
    return (f"{src} sent {metric_value} events to {dst}:{row['service_port']} "
            f"between {window}. Rule threshold: {threshold} events.")


def run_detection(conn, now=None):
    """Evaluate all rules and store new alerts. Returns {rule: (matches, new_alerts)}.

    Running detection twice does not create duplicate alerts: the UNIQUE key
    (rule, source, target, service port, window start) makes inserts idempotent.
    """
    created_at = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%S")
    summary = {}
    with transaction(conn):
        for rule, spec in _SPECS.items():
            cfg = RULES[rule]
            width = cfg["window_seconds"]
            sql = _RULE_SQL.format(
                service=spec["service"],
                bucket=_BUCKET.format(w=width),
                metric=spec["metric"],
                where=spec["where"],
                extra_group=spec["extra_group"],
            )
            matches = new = 0
            for row in conn.execute(sql, (cfg["threshold"],)).fetchall():
                matches += 1
                start = datetime.fromtimestamp(row["bucket_start"], tz=timezone.utc).replace(tzinfo=None)
                end = start + timedelta(seconds=width)
                start_s, end_s = start.strftime("%Y-%m-%dT%H:%M:%S"), end.strftime("%Y-%m-%dT%H:%M:%S")
                description = _describe(rule, row, row["metric"], start_s, end_s, cfg["threshold"])
                cur = conn.execute(_INSERT_ALERT, (
                    rule, row["src_ip_id"], row["dst_ip_id"], row["service_port"],
                    start_s, end_s, cfg["severity"], row["event_count"],
                    description, created_at,
                ))
                new += cur.rowcount
            summary[rule] = (matches, new)
    return summary
