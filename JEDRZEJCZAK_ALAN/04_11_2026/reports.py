"""Six SQL-based analytical reports, plus text and CSV export."""
import csv
from pathlib import Path
import sys

# Every report is computed from live SQLite rows, never hard-coded sample numbers.
REPORTS = {
    "types": ("Event volume by type", """
        SELECT t.code AS event_type, COUNT(e.event_id) AS event_count
        FROM event_types t LEFT JOIN network_events e ON e.event_type_id = t.event_type_id
        GROUP BY t.event_type_id, t.code ORDER BY event_count DESC, t.code
    """),
    "sources": ("Top 10 source IPs", """
        SELECT ip.address AS source_ip, COUNT(*) AS event_count,
               (SELECT MAX(e2.event_time) FROM network_events e2
                WHERE e2.src_ip_id = e.src_ip_id) AS last_seen_utc
        FROM network_events e JOIN ip_addresses ip ON ip.ip_id = e.src_ip_id
        GROUP BY e.src_ip_id, ip.address
        ORDER BY event_count DESC, ip.address LIMIT 10
    """),
    "services": ("Top targeted destination ports", """
        SELECT e.dst_port AS destination_port, e.protocol, COUNT(*) AS event_count
        FROM network_events e WHERE e.dst_port IS NOT NULL
        GROUP BY e.dst_port, e.protocol
        ORDER BY event_count DESC, e.dst_port, e.protocol LIMIT 15
    """),
    "alerts": ("Alerts overview by severity and status", """
        SELECT severity, status, COUNT(*) AS alert_count
        FROM alerts GROUP BY severity, status
        ORDER BY CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END,
                 status
    """),
    "timeline": ("5-minute UTC timeline", """
        SELECT strftime('%Y-%m-%dT%H:', event_time) ||
               printf('%02d:00', (CAST(strftime('%M', event_time) AS INTEGER) / 5) * 5)
               AS bucket_start_utc, COUNT(*) AS event_count
        FROM network_events GROUP BY bucket_start_utc
        ORDER BY bucket_start_utc
    """),
    "targets": ("Top destination IPs", """
        SELECT ip.address AS target_ip, COUNT(*) AS event_count
        FROM network_events e JOIN ip_addresses ip ON ip.ip_id = e.dst_ip_id
        GROUP BY e.dst_ip_id, ip.address
        ORDER BY event_count DESC, ip.address LIMIT 10
    """),
}


def fetch_reports(conn, selected="all"):
    if selected != "all" and selected not in REPORTS:
        raise ValueError(f"Unknown report: {selected}")
    names = list(REPORTS) if selected == "all" else [selected]
    result = {}
    for name in names:
        title, sql = REPORTS[name]
        cursor = conn.execute(sql)
        result[name] = (title, [col[0] for col in cursor.description], cursor.fetchall())
    return result


def text_table(headers, rows):
    values = [["" if cell is None else str(cell) for cell in row] for row in rows]
    widths = [max(len(str(header)), *(len(row[i]) for row in values)) for i,header in enumerate(headers)]
    fmt = "  ".join(f"{{:<{width}}}" for width in widths)
    return "\n".join([
        fmt.format(*headers),
        fmt.format(*("-" * width for width in widths)),
        *(fmt.format(*row) for row in values),
        *( ["(no matching records)"] if not values else [] ),
    ])


def write_report(conn, name="all", fmt="text", output=None):
    reports = fetch_reports(conn,name)
    if fmt == "text":
        blocks = [f"=== {title} ===\n{text_table(columns, rows)}" for title,columns,rows in reports.values()]
        message = "\n\n".join(blocks) + "\n"
        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(message, encoding="utf-8")
            print(f"Text report saved to {path}")
        else:
            print(message,end="")
        return

    if fmt != "csv":
        raise ValueError(f"Unsupported output format: {fmt}")
    if name == "all":
        folder = Path(output) if output else Path(__file__).resolve().parent / "reports"
        folder.mkdir(parents=True,exist_ok=True)
        for report_name, (_,cols,rows) in reports.items():
            destination = folder / f"{report_name}.csv"
            with destination.open("w",encoding="utf-8",newline="") as file:
                writer = csv.writer(file)
                writer.writerow(cols)
                writer.writerows(rows)
        print(f"Exported {len(reports)} CSV reports to {folder}")
    else:
        _,cols,rows = reports[name]
        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w",encoding="utf-8",newline="") as file:
                writer = csv.writer(file)
                writer.writerow(cols)
                writer.writerows(rows)
            print(f"CSV report saved to {path}")
        else:
            writer = csv.writer(sys.stdout,lineterminator="\n")
            writer.writerow(cols)
            writer.writerows(rows)


def show_summary(conn):
    counts = {
        "events": "SELECT COUNT(*) FROM network_events",
        "sensors": "SELECT COUNT(*) FROM sensors",
        "IP addresses": "SELECT COUNT(*) FROM ip_addresses",
        "alerts": "SELECT COUNT(*) FROM alerts",
        "logged rejected rows": "SELECT COUNT(*) FROM import_rejections",
    }
    print("DATABASE SUMMARY")
    for label, sql in counts.items():
        print(f"  {label}: {conn.execute(sql).fetchone()[0]}")
    print("\nMost common event types:")
    title,cols,rows = fetch_reports(conn,"types")["types"]
    print(text_table(cols,rows))


ALERTS_SQL = """
    SELECT a.alert_id, a.rule_code, src.address AS source_ip,
           dst.address AS target_ip, a.dst_port, a.window_start, a.window_end,
           a.event_count, a.metric_count, a.severity, a.status
    FROM alerts a
    JOIN ip_addresses src ON src.ip_id = a.source_ip_id
    JOIN ip_addresses dst ON dst.ip_id = a.target_ip_id
"""


def show_alerts(conn, status=None):
    if status:
        cursor = conn.execute(ALERTS_SQL + " WHERE a.status = ? ORDER BY a.alert_id", (status,))
    else:
        cursor = conn.execute(ALERTS_SQL + " ORDER BY a.alert_id")
    rows = cursor.fetchall()
    print(text_table([v[0] for v in cursor.description],rows))


def update_alert_status(conn, alert_id, status):
    with conn:
        cursor = conn.execute("UPDATE alerts SET status = ? WHERE alert_id = ?", (status, alert_id))
    if not cursor.rowcount:
        raise ValueError(f"Alert #{alert_id} does not exist")
    print(f"Updated alert #{alert_id} to {status}")


def explain_alert(conn, alert_id):
    cursor = conn.execute(ALERTS_SQL + " WHERE a.alert_id = ?", (alert_id,))
    alert = cursor.fetchone()
    if alert is None:
        raise ValueError(f"Alert #{alert_id} does not exist")
    print(f"ALERT #{alert_id} - {alert['rule_code']} ({alert['severity']})")
    for col in alert.keys():
        if col != "alert_id":
            print(f"  {col}: {alert[col]}")
    description = conn.execute("SELECT description FROM alerts WHERE alert_id = ?", (alert_id,)).fetchone()[0]
    print(f"  description: {description}")
    total = conn.execute("SELECT COUNT(*) FROM alert_events WHERE alert_id = ?", (alert_id,)).fetchone()[0]
    cursor = conn.execute("""
        SELECT e.event_id, e.event_time, t.code AS event_type, e.dst_port, e.action
        FROM alert_events ae JOIN network_events e ON e.event_id = ae.event_id
        JOIN event_types t ON t.event_type_id = e.event_type_id
        WHERE ae.alert_id = ? ORDER BY e.event_time,e.event_id LIMIT 10
    """, (alert_id,))
    rows = cursor.fetchall()
    print(f"  stored evidence: {total} events (first {len(rows)} shown)")
    print(text_table([v[0] for v in cursor.description],rows))
