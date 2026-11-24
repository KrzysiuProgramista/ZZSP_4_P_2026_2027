"""
detection.py - Transparent, explainable SQL + Python heuristic detection rules.
Supports PORT_SCAN, BRUTE_FORCE, and TRAFFIC_FLOOD with idempotent alert persistence.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List

import db

# Configurable detection constants
PORT_SCAN_THRESHOLD = 20       # distinct destination ports in 5-minute fixed bucket
BRUTE_FORCE_THRESHOLD = 8      # AUTH_FAILURE events to same target+port in 5-minute bucket
TRAFFIC_FLOOD_THRESHOLD = 150  # total events to same target+port in 1-minute bucket


@dataclass
class DetectionRunResult:
    evaluated_rules: int
    new_alerts: int
    existing_alerts: int


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _bucket_end(bucket_start: str, minutes: int) -> str:
    dt = datetime.strptime(bucket_start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return (dt + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _persist_alert(
    conn,
    *,
    rule_code: str,
    source_ip_id: int,
    target_ip_id: int,
    dst_port: int,
    window_start: str,
    window_end: str,
    severity: str,
    event_count: int,
    description: str,
    evidence_event_ids: List[int],
) -> bool:
    """
    Insert alert idempotently using UNIQUE(rule_code, source_ip_id, target_ip_id, dst_port, window_start).
    Returns True if a new alert was inserted, False if it already existed.
    """
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO alerts (
            rule_code, source_ip_id, target_ip_id, dst_port,
            window_start, window_end, severity, event_count, description, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?)
        """,
        (
            rule_code,
            source_ip_id,
            target_ip_id,
            dst_port,
            window_start,
            window_end,
            severity,
            event_count,
            description,
            _utc_now_iso(),
        ),
    )
    if cursor.rowcount == 1:
        alert_id = cursor.lastrowid
        conn.executemany(
            "INSERT OR IGNORE INTO alert_events (alert_id, event_id) VALUES (?, ?)",
            [(alert_id, eid) for eid in evidence_event_ids],
        )
        return True
    return False


def run_detections(
    db_path: str,
    port_scan_threshold: int = PORT_SCAN_THRESHOLD,
    brute_force_threshold: int = BRUTE_FORCE_THRESHOLD,
    traffic_flood_threshold: int = TRAFFIC_FLOOD_THRESHOLD,
) -> DetectionRunResult:
    """Evaluate all three detection rules in a single atomic SQLite transaction."""
    conn = db.connect(db_path)
    new_count = 0
    existing_count = 0

    try:
        with conn:
            # ------------------------------------------------------------------
            # RULE 1: PORT_SCAN (>= 20 distinct dst_port per src->dst in 5m)
            # ------------------------------------------------------------------
            port_scan_rows = conn.execute(
                """
                SELECT
                    e.src_ip_id,
                    e.dst_ip_id,
                    s_ip.address AS src_ip,
                    d_ip.address AS dst_ip,
                    strftime('%Y-%m-%dT%H:', e.event_time) ||
                        printf('%02d:00Z', (CAST(strftime('%M', e.event_time) AS INTEGER) / 5) * 5)
                        AS bucket_5m,
                    COUNT(DISTINCT e.dst_port) AS distinct_ports
                FROM network_events e
                JOIN ip_addresses s_ip ON e.src_ip_id = s_ip.ip_id
                JOIN ip_addresses d_ip ON e.dst_ip_id = d_ip.ip_id
                WHERE e.dst_port IS NOT NULL
                GROUP BY e.src_ip_id, e.dst_ip_id, bucket_5m
                HAVING COUNT(DISTINCT e.dst_port) >= ?
                """,
                (port_scan_threshold,),
            ).fetchall()

            for row in port_scan_rows:
                win_start = row["bucket_5m"]
                win_end = _bucket_end(win_start, 5)
                ev_rows = conn.execute(
                    """
                    SELECT event_id FROM network_events
                    WHERE src_ip_id = ? AND dst_ip_id = ?
                      AND event_time >= ? AND event_time < ?
                    """,
                    (row["src_ip_id"], row["dst_ip_id"], win_start, win_end),
                ).fetchall()
                desc = (
                    f"Source {row['src_ip']} probed {row['distinct_ports']} distinct destination "
                    f"ports on {row['dst_ip']} within 5-minute window {win_start}..{win_end}."
                )
                inserted = _persist_alert(
                    conn,
                    rule_code="PORT_SCAN",
                    source_ip_id=row["src_ip_id"],
                    target_ip_id=row["dst_ip_id"],
                    dst_port=-1,
                    window_start=win_start,
                    window_end=win_end,
                    severity="HIGH",
                    event_count=row["distinct_ports"],
                    description=desc,
                    evidence_event_ids=[r["event_id"] for r in ev_rows],
                )
                if inserted:
                    new_count += 1
                else:
                    existing_count += 1

            # ------------------------------------------------------------------
            # RULE 2: BRUTE_FORCE (>= 8 AUTH_FAILURE per src->dst:port in 5m)
            # ------------------------------------------------------------------
            brute_rows = conn.execute(
                """
                SELECT
                    e.src_ip_id,
                    e.dst_ip_id,
                    COALESCE(e.dst_port, -1) AS target_port,
                    s_ip.address AS src_ip,
                    d_ip.address AS dst_ip,
                    strftime('%Y-%m-%dT%H:', e.event_time) ||
                        printf('%02d:00Z', (CAST(strftime('%M', e.event_time) AS INTEGER) / 5) * 5)
                        AS bucket_5m,
                    COUNT(*) AS failure_count
                FROM network_events e
                JOIN event_types et  ON e.event_type_id = et.event_type_id
                JOIN ip_addresses s_ip ON e.src_ip_id = s_ip.ip_id
                JOIN ip_addresses d_ip ON e.dst_ip_id = d_ip.ip_id
                WHERE et.code = 'AUTH_FAILURE'
                GROUP BY e.src_ip_id, e.dst_ip_id, target_port, bucket_5m
                HAVING COUNT(*) >= ?
                """,
                (brute_force_threshold,),
            ).fetchall()

            for row in brute_rows:
                win_start = row["bucket_5m"]
                win_end = _bucket_end(win_start, 5)
                ev_rows = conn.execute(
                    """
                    SELECT e.event_id FROM network_events e
                    JOIN event_types et ON e.event_type_id = et.event_type_id
                    WHERE e.src_ip_id = ? AND e.dst_ip_id = ?
                      AND COALESCE(e.dst_port, -1) = ?
                      AND et.code = 'AUTH_FAILURE'
                      AND e.event_time >= ? AND e.event_time < ?
                    """,
                    (row["src_ip_id"], row["dst_ip_id"], row["target_port"], win_start, win_end),
                ).fetchall()
                desc = (
                    f"Source {row['src_ip']} generated {row['failure_count']} AUTH_FAILURE events "
                    f"against {row['dst_ip']}:{row['target_port']} in 5m window {win_start}..{win_end}."
                )
                inserted = _persist_alert(
                    conn,
                    rule_code="BRUTE_FORCE",
                    source_ip_id=row["src_ip_id"],
                    target_ip_id=row["dst_ip_id"],
                    dst_port=row["target_port"],
                    window_start=win_start,
                    window_end=win_end,
                    severity="HIGH",
                    event_count=row["failure_count"],
                    description=desc,
                    evidence_event_ids=[r["event_id"] for r in ev_rows],
                )
                if inserted:
                    new_count += 1
                else:
                    existing_count += 1

            # ------------------------------------------------------------------
            # RULE 3: TRAFFIC_FLOOD (>= 150 events per src->dst:port in 1m)
            # ------------------------------------------------------------------
            flood_rows = conn.execute(
                """
                SELECT
                    e.src_ip_id,
                    e.dst_ip_id,
                    COALESCE(e.dst_port, -1) AS target_port,
                    s_ip.address AS src_ip,
                    d_ip.address AS dst_ip,
                    strftime('%Y-%m-%dT%H:%M:00Z', e.event_time) AS bucket_1m,
                    COUNT(*) AS total_events
                FROM network_events e
                JOIN ip_addresses s_ip ON e.src_ip_id = s_ip.ip_id
                JOIN ip_addresses d_ip ON e.dst_ip_id = d_ip.ip_id
                GROUP BY e.src_ip_id, e.dst_ip_id, target_port, bucket_1m
                HAVING COUNT(*) >= ?
                """,
                (traffic_flood_threshold,),
            ).fetchall()

            for row in flood_rows:
                win_start = row["bucket_1m"]
                win_end = _bucket_end(win_start, 1)
                ev_rows = conn.execute(
                    """
                    SELECT event_id FROM network_events
                    WHERE src_ip_id = ? AND dst_ip_id = ?
                      AND COALESCE(dst_port, -1) = ?
                      AND event_time >= ? AND event_time < ?
                    """,
                    (row["src_ip_id"], row["dst_ip_id"], row["target_port"], win_start, win_end),
                ).fetchall()
                desc = (
                    f"Source {row['src_ip']} sent {row['total_events']} events to "
                    f"{row['dst_ip']}:{row['target_port']} within 1-minute window {win_start}..{win_end}."
                )
                inserted = _persist_alert(
                    conn,
                    rule_code="TRAFFIC_FLOOD",
                    source_ip_id=row["src_ip_id"],
                    target_ip_id=row["dst_ip_id"],
                    dst_port=row["target_port"],
                    window_start=win_start,
                    window_end=win_end,
                    severity="CRITICAL",
                    event_count=row["total_events"],
                    description=desc,
                    evidence_event_ids=[r["event_id"] for r in ev_rows],
                )
                if inserted:
                    new_count += 1
                else:
                    existing_count += 1
    finally:
        conn.close()

    return DetectionRunResult(
        evaluated_rules=3,
        new_alerts=new_count,
        existing_alerts=existing_count,
    )


def update_alert_status(db_path: str, alert_id: int, new_status: str) -> bool:
    """Update lifecycle status (NEW, INVESTIGATING, CLOSED) for an alert."""
    status = new_status.strip().upper()
    if status not in {"NEW", "INVESTIGATING", "CLOSED"}:
        raise ValueError(f"Invalid alert status: {new_status}")
    conn = db.connect(db_path)
    try:
        with conn:
            cur = conn.execute(
                "UPDATE alerts SET status = ? WHERE alert_id = ?",
                (status, alert_id),
            )
            return cur.rowcount == 1
    finally:
        conn.close()