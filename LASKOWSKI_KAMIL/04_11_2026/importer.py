"""
importer.py - CSV contract validation, field normalisation, deduplication, and atomic import.
"""
import csv
import hashlib
import ipaddress
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import db

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "timestamp",
    "sensor_name",
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "protocol",
    "event_type",
    "action",
    "bytes",
    "duration_ms",
}

ALLOWED_PROTOCOLS = {"TCP", "UDP", "ICMP"}
ALLOWED_ACTIONS = {"ALLOW", "BLOCK"}
KNOWN_EVENT_TYPES = {
    "AUTH_FAILURE",
    "AUTH_SUCCESS",
    "CONNECTION",
    "HTTP_REQUEST",
    "DNS_QUERY",
    "PING",
    "PORT_PROBE",
    "MALWARE_ALERT",
}


@dataclass
class ImportSummary:
    rows_read: int = 0
    imported: int = 0
    rejected: int = 0
    duplicates: int = 0
    errors: List[str] = field(default_factory=list)


def parse_utc_timestamp(raw: str) -> str:
    """Parse ISO-8601 timestamp and normalise to canonical UTC format YYYY-MM-DDTHH:MM:SSZ."""
    cleaned = raw.strip()
    if not cleaned:
        raise ValueError("Empty timestamp")
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_optional_port(raw: str, field_name: str) -> Optional[int]:
    """Parse integer port in range 1..65535 or None if blank."""
    val = raw.strip()
    if val == "":
        return None
    if not val.isdigit():
        raise ValueError(f"Invalid {field_name}: '{raw}' is not an integer")
    port = int(val)
    if not (1 <= port <= 65535):
        raise ValueError(f"Out-of-range {field_name}: {port} (must be 1..65535)")
    return port


def parse_non_negative_int(raw: str, field_name: str) -> int:
    """Parse non-negative integer field."""
    val = raw.strip()
    if not val.isdigit():
        raise ValueError(f"Invalid {field_name}: '{raw}' must be a non-negative integer")
    return int(val)


def validate_row(row: Dict[str, str]) -> Tuple[dict, str]:
    """
    Validate and normalise a raw CSV row without mutating source values silently.
    Returns (normalised_record, deterministic_sha256_hash).
    """
    if any(v is None for v in row.values()):
        raise ValueError("Row has fewer columns than CSV header")

    event_time = parse_utc_timestamp(row["timestamp"])

    sensor_name = row["sensor_name"].strip()
    if not sensor_name:
        raise ValueError("sensor_name must be non-empty")

    try:
        src_ip = ipaddress.ip_address(row["src_ip"].strip()).compressed
        dst_ip = ipaddress.ip_address(row["dst_ip"].strip()).compressed
    except ValueError as exc:
        raise ValueError(f"Invalid IP address: {exc}") from exc

    src_port = parse_optional_port(row["src_port"], "src_port")
    dst_port = parse_optional_port(row["dst_port"], "dst_port")

    protocol = row["protocol"].strip().upper()
    if protocol not in ALLOWED_PROTOCOLS:
        raise ValueError(f"Unsupported protocol '{row['protocol']}'")

    event_type = row["event_type"].strip().upper()
    if event_type not in KNOWN_EVENT_TYPES:
        raise ValueError(f"Unknown event_type '{row['event_type']}'")

    action = row["action"].strip().upper()
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Invalid action '{row['action']}'")

    byte_count = parse_non_negative_int(row["bytes"], "bytes")
    duration_ms = parse_non_negative_int(row["duration_ms"], "duration_ms")

    # Deterministic SHA-256 key ensures repeat imports of the same CSV are idempotent
    canonical_key = "|".join([
        event_time,
        sensor_name,
        src_ip,
        dst_ip,
        str(src_port or ""),
        str(dst_port or ""),
        protocol,
        event_type,
        action,
        str(byte_count),
        str(duration_ms),
    ])
    event_hash = hashlib.sha256(canonical_key.encode("utf-8")).hexdigest()

    return {
        "event_hash": event_hash,
        "event_time": event_time,
        "sensor_name": sensor_name,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": protocol,
        "event_type": event_type,
        "action": action,
        "bytes": byte_count,
        "duration_ms": duration_ms,
    }, event_hash


def import_csv(db_path: str, csv_path: str) -> ImportSummary:
    """Read CSV file, validate every row, normalise entities, and store in a transaction."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    summary = ImportSummary()
    conn = db.connect(db_path)

    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError("CSV file is empty or missing header row")

            header_set = {col.strip() for col in reader.fieldnames if col}
            missing = REQUIRED_COLUMNS - header_set
            if missing:
                raise ValueError(f"CSV missing required columns: {sorted(missing)}")

            with conn:
                for line_num, raw_row in enumerate(reader, start=2):
                    summary.rows_read += 1
                    try:
                        rec, event_hash = validate_row(raw_row)
                    except ValueError as err:
                        summary.rejected += 1
                        msg = f"Line {line_num}: {err}"
                        summary.errors.append(msg)
                        logger.warning(msg)
                        continue

                    sensor_id = db.get_or_create_sensor(conn, rec["sensor_name"])
                    src_ip_id = db.get_or_create_ip(conn, rec["src_ip"])
                    dst_ip_id = db.get_or_create_ip(conn, rec["dst_ip"])
                    event_type_id = db.get_or_create_event_type(conn, rec["event_type"])

                    cursor = conn.execute(
                        """
                        INSERT OR IGNORE INTO network_events (
                            event_hash, sensor_id, event_type_id, src_ip_id, dst_ip_id,
                            event_time, src_port, dst_port, protocol, action, bytes, duration_ms
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            event_hash,
                            sensor_id,
                            event_type_id,
                            src_ip_id,
                            dst_ip_id,
                            rec["event_time"],
                            rec["src_port"],
                            rec["dst_port"],
                            rec["protocol"],
                            rec["action"],
                            rec["bytes"],
                            rec["duration_ms"],
                        ),
                    )
                    if cursor.rowcount == 1:
                        summary.imported += 1
                    else:
                        summary.duplicates += 1
    finally:
        conn.close()

    return summary