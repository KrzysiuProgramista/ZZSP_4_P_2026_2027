"""
reports.py - SQL-backed analytical reports and alert exporters (text & CSV).
Implements all 6 required analytical reports using JOINs, aggregates, and time buckets.
"""
import csv
import io
from typing import Dict, List

import db


def fetch_all_reports(db_path: str) -> Dict[str, List[dict]]:
    """Execute all 6 analytical SQL queries and return structured dictionaries."""
    conn = db.connect(db_path)
    try:
        by_type = [
            dict(r)
            for r in conn.execute(
                """
                SELECT et.code AS event_type,
                       et.default_severity AS base_severity,
                       COUNT(e.event_id) AS event_count,
                       COALESCE(SUM(e.bytes), 0) AS total_bytes
                FROM event_types et
                LEFT JOIN network_events e ON e.event_type_id = et.event_type_id
                GROUP BY et.event_type_id, et.code, et.default_severity
                ORDER BY event_count DESC
                """
            ).fetchall()
        ]

        top_sources = [
            dict(r)
            for r in conn.execute(
                """
                SELECT ip.address AS source_ip,
                       CASE ip.is_private WHEN 1 THEN 'PRIVATE' ELSE 'PUBLIC' END AS scope,
                       COUNT(*) AS event_count,
                       COUNT(DISTINCT e.dst_ip_id) AS unique_targets
                FROM network_events e
                JOIN ip_addresses ip ON e.src_ip_id = ip.ip_id
                GROUP BY e.src_ip_id, ip.address, ip.is_private
                ORDER BY event_count DESC
                LIMIT 10
                """
            ).fetchall()
        ]

        top_services = [
            dict(r)
            for r in conn.execute(
                """
                SELECT e.dst_port,
                       e.protocol,
                       COUNT(*) AS hit_count,
                       SUM(CASE WHEN e.action = 'BLOCK' THEN 1 ELSE 0 END) AS blocked_count
                FROM network_events e
                WHERE e.dst_port IS NOT NULL
                GROUP BY e.dst_port, e.protocol
                ORDER BY hit_count DESC
                LIMIT 10
                """
            ).fetchall()
        ]

        alerts_overview = [
            dict(r)
            for r in conn.execute(
                """
                SELECT severity, status, COUNT(*) AS alert_count
                FROM alerts
                GROUP BY severity, status
                ORDER BY CASE severity
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    ELSE 4 END, status
                """
            ).fetchall()
        ]

        timeline = [
            dict(r)
            for r in conn.execute(
                """
                SELECT strftime('%Y-%m-%dT%H:', event_time) ||
                       printf('%02d:00Z', (CAST(strftime('%M', event_time) AS INTEGER) / 5) * 5)
                       AS bucket_5m,
                       COUNT(*) AS event_count,
                       SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS blocked_events
                FROM network_events
                GROUP BY bucket_5m
                ORDER BY bucket_5m ASC
                """
            ).fetchall()
        ]

        top_targets = [
            dict(r)
            for r in conn.execute(
                """
                SELECT ip.address AS target_ip,
                       COUNT(*) AS event_count,
                       COUNT(DISTINCT e.src_ip_id) AS distinct_sources
                FROM network_events e
                JOIN ip_addresses ip ON e.dst_ip_id = ip.ip_id
                GROUP BY e.dst_ip_id, ip.address
                ORDER BY event_count DESC
                LIMIT 10
                """
            ).fetchall()
        ]

        return {
            "event_volume_by_type": by_type,
            "top_source_ips": top_sources,
            "top_targeted_services": top_services,
            "alerts_overview": alerts_overview,
            "timeline_5m": timeline,
            "top_targets": top_targets,
        }
    finally:
        conn.close()


def fetch_alerts(db_path: str) -> List[dict]:
    """Retrieve all persisted alerts joined with IP addresses."""
    conn = db.connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT a.alert_id,
                   a.rule_code,
                   a.severity,
                   s_ip.address AS source_ip,
                   t_ip.address AS target_ip,
                   a.dst_port,
                   a.window_start,
                   a.window_end,
                   a.event_count,
                   a.status,
                   a.description
            FROM alerts a
            JOIN ip_addresses s_ip ON a.source_ip_id = s_ip.ip_id
            JOIN ip_addresses t_ip ON a.target_ip_id = t_ip.ip_id
            ORDER BY a.alert_id ASC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def format_summary_text(db_path: str) -> str:
    """Render readable CLI analytical summary across all 6 SQL reports."""
    data = fetch_all_reports(db_path)
    lines = ["=== NETWORK SECURITY ANALYTICAL SUMMARY ==="]

    lines.append("[01] EVENT VOLUME BY TYPE")
    for r in data["event_volume_by_type"]:
        lines.append(f"  - {r['event_type']:<15} count={r['event_count']:<5} bytes={r['total_bytes']}")

    lines.append("[02] TOP SOURCE IPS")
    for r in data["top_source_ips"]:
        lines.append(
            f"  - {r['source_ip']:<16} ({r['scope']}) events={r['event_count']:<5} targets={r['unique_targets']}"
        )

    lines.append("[03] TOP TARGETED SERVICES")
    for r in data["top_targeted_services"]:
        lines.append(
            f"  - port {r['dst_port']}/{r['protocol']:<4} hits={r['hit_count']:<5} blocked={r['blocked_count']}"
        )

    lines.append("[04] ALERTS OVERVIEW")
    if not data["alerts_overview"]:
        lines.append("  - No alerts persisted yet (run 'detect').")
    for r in data["alerts_overview"]:
        lines.append(f"  - {r['severity']:<8} [{r['status']}] : {r['alert_count']}")

    lines.append("[05] 5-MINUTE ACTIVITY TIMELINE (UTC)")
    for r in data["timeline_5m"]:
        lines.append(
            f"  - {r['bucket_5m']}  events={r['event_count']:<5} blocked={r['blocked_events']}"
        )

    lines.append("[06] TOP TARGET DESTINATION IPS")
    for r in data["top_targets"]:
        lines.append(
            f"  - {r['target_ip']:<16} events={r['event_count']:<5} distinct_sources={r['distinct_sources']}"
        )

    return "".join(lines)


def format_alerts_report(db_path: str, fmt: str = "text") -> str:
    """Export persisted alerts in 'text' or 'csv' format."""
    alerts = fetch_alerts(db_path)
    if fmt == "csv":
        buf = io.StringIO()
        fieldnames = [
            "alert_id",
            "rule_code",
            "severity",
            "source_ip",
            "target_ip",
            "dst_port",
            "window_start",
            "window_end",
            "event_count",
            "status",
            "description",
        ]
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(alerts)
        return buf.getvalue().strip()

    if not alerts:
        return "No alerts found in database."

    lines = ["=== SECURITY ALERTS REPORT ==="]
    for a in alerts:
        lines.append(
            f"[#{a['alert_id']}] {a['severity']} | {a['rule_code']} | "
            f"{a['source_ip']} -> {a['target_ip']} | window={a['window_start']}..{a['window_end']} | "
            f"count={a['event_count']} | status={a['status']}"
        )
        lines.append(f"      Evidence: {a['description']}")
    return "".join(lines)