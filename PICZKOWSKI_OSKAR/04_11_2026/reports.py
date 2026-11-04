"""Analytical reports. Every report is a SQL query, not hard-coded output."""
import csv
from pathlib import Path

REPORTS = {
    "event-volume": ("Event volume by type", """
        SELECT t.code AS event_type, COUNT(*) AS events
        FROM network_events e
        JOIN event_types t ON t.event_type_id = e.event_type_id
        GROUP BY t.code
        ORDER BY events DESC, t.code"""),
    "top-sources": ("Top 10 source IPs", """
        SELECT ip.address AS source_ip, COUNT(*) AS events
        FROM network_events e
        JOIN ip_addresses ip ON ip.ip_id = e.src_ip_id
        GROUP BY ip.address
        ORDER BY events DESC, ip.address
        LIMIT 10"""),
    "top-services": ("Top 10 targeted destination ports", """
        SELECT dst_port, COUNT(*) AS events, COUNT(DISTINCT src_ip_id) AS distinct_sources
        FROM network_events
        WHERE dst_port IS NOT NULL
        GROUP BY dst_port
        ORDER BY events DESC, dst_port
        LIMIT 10"""),
    "alerts-overview": ("Alerts by severity and status", """
        SELECT severity, status, COUNT(*) AS alerts
        FROM alerts
        GROUP BY severity, status
        ORDER BY CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                               WHEN 'MEDIUM' THEN 3 ELSE 4 END, status"""),
    "timeline-5min": ("Event timeline (5-minute buckets, UTC)", """
        SELECT strftime('%Y-%m-%dT%H:%M:%S',
                        CAST(strftime('%s', event_time) AS INTEGER) / 300 * 300,
                        'unixepoch') AS bucket_start,
               COUNT(*) AS events
        FROM network_events
        GROUP BY bucket_start
        ORDER BY bucket_start"""),
    "top-targets": ("Top 10 target IPs", """
        SELECT ip.address AS target_ip, COUNT(*) AS events,
               COUNT(DISTINCT e.src_ip_id) AS distinct_sources
        FROM network_events e
        JOIN ip_addresses ip ON ip.ip_id = e.dst_ip_id
        GROUP BY ip.address
        ORDER BY events DESC, ip.address
        LIMIT 10"""),
    "alerts": ("All alerts", """
        SELECT a.alert_id, a.rule_code, a.severity, a.status,
               src.address AS source_ip, dst.address AS target_ip,
               a.service_port, a.window_start, a.event_count, a.description
        FROM alerts a
        JOIN ip_addresses src ON src.ip_id = a.source_ip_id
        JOIN ip_addresses dst ON dst.ip_id = a.target_ip_id
        ORDER BY CASE a.severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2
                                 WHEN 'MEDIUM' THEN 3 ELSE 4 END,
                 a.window_start, a.alert_id"""),
}


def run_report(conn, name):
    title, sql = REPORTS[name]
    cur = conn.execute(sql)
    headers = [col[0] for col in cur.description]
    rows = [tuple(r) for r in cur.fetchall()]
    return title, headers, rows


def format_text(headers, rows):
    cells = [[str(v) for v in row] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in cells)) if cells else len(h)
              for i, h in enumerate(headers)]
    line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    out = [line, "  ".join("-" * w for w in widths)]
    out += ["  ".join(c.ljust(w) for c, w in zip(r, widths)) for r in cells]
    return "\n".join(out) if rows else line + "\n(no rows)"


def write_csv(path, headers, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)
