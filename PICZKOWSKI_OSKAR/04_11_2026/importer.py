"""CSV reading, validation, normalisation and idempotent import."""
import csv
import hashlib
import ipaddress
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from config import KNOWN_EVENT_TYPES, VALID_ACTIONS, VALID_PROTOCOLS
from db import transaction

log = logging.getLogger(__name__)

REQUIRED_COLUMNS = (
    "timestamp", "sensor_name", "src_ip", "dst_ip", "src_port", "dst_port",
    "protocol", "event_type", "action", "bytes", "duration_ms",
)


class RowError(ValueError):
    """A row failed validation; the message is the reason stored with the rejection."""


@dataclass
class ImportResult:
    read: int = 0
    imported: int = 0
    rejected: int = 0
    duplicates: int = 0
    rejects: list = field(default_factory=list)  # (line_number, reason)


def _parse_timestamp(value):
    try:
        ts = datetime.fromisoformat(value)
    except ValueError:
        raise RowError(f"timestamp is not ISO 8601: {value!r}")
    if ts.tzinfo is not None:
        ts = ts.astimezone(timezone.utc).replace(tzinfo=None)
    # Timestamps without an offset are interpreted as UTC (documented in README).
    return ts.strftime("%Y-%m-%dT%H:%M:%S")


def _parse_ip(value, name):
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        raise RowError(f"{name} is not a valid IP address: {value!r}")
    return str(ip), ip.is_private


def _parse_port(value, name):
    if value == "":
        return None  # blank is allowed when a port is not applicable
    if not (value.isascii() and value.isdigit()) or not 1 <= int(value) <= 65535:
        raise RowError(f"{name} must be an integer 1-65535 or blank: {value!r}")
    return int(value)


def _parse_non_negative(value, name):
    if not (value.isascii() and value.isdigit()):
        raise RowError(f"{name} must be a non-negative integer: {value!r}")
    return int(value)


def parse_row(raw):
    """Validate one CSV record and return a normalised dict. Raises RowError."""
    missing = [c for c in REQUIRED_COLUMNS if raw.get(c) is None]
    if missing:
        raise RowError(f"missing fields: {', '.join(missing)}")

    if not raw["sensor_name"].strip():
        raise RowError("sensor_name is empty")

    src_ip, src_private = _parse_ip(raw["src_ip"], "src_ip")
    dst_ip, dst_private = _parse_ip(raw["dst_ip"], "dst_ip")

    if raw["protocol"] not in VALID_PROTOCOLS:
        raise RowError(f"unknown protocol: {raw['protocol']!r}")
    if raw["event_type"] not in KNOWN_EVENT_TYPES:
        raise RowError(f"unknown event_type: {raw['event_type']!r}")
    if raw["action"] not in VALID_ACTIONS:
        raise RowError(f"unknown action: {raw['action']!r}")

    return {
        "timestamp": _parse_timestamp(raw["timestamp"]),
        "sensor_name": raw["sensor_name"],
        "src_ip": src_ip,
        "src_is_private": src_private,
        "dst_ip": dst_ip,
        "dst_is_private": dst_private,
        "src_port": _parse_port(raw["src_port"], "src_port"),
        "dst_port": _parse_port(raw["dst_port"], "dst_port"),
        "protocol": raw["protocol"],
        "event_type": raw["event_type"],
        "action": raw["action"],
        "bytes": _parse_non_negative(raw["bytes"], "bytes"),
        "duration_ms": _parse_non_negative(raw["duration_ms"], "duration_ms"),
    }


def _event_key(rec):
    """Stable identity of an event: SHA-256 over all normalised fields."""
    payload = "|".join("" if v is None else str(v) for v in rec.values())
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _get_or_create_ip(conn, address, is_private):
    conn.execute(
        "INSERT OR IGNORE INTO ip_addresses (address, is_private) VALUES (?, ?)",
        (address, int(is_private)),
    )
    return conn.execute("SELECT ip_id FROM ip_addresses WHERE address = ?", (address,)).fetchone()[0]


def _get_or_create_sensor(conn, name):
    conn.execute("INSERT OR IGNORE INTO sensors (name) VALUES (?)", (name,))
    return conn.execute("SELECT sensor_id FROM sensors WHERE name = ?", (name,)).fetchone()[0]


def _insert_event(conn, key, rec):
    sensor_id = _get_or_create_sensor(conn, rec["sensor_name"])
    src_id = _get_or_create_ip(conn, rec["src_ip"], rec["src_is_private"])
    dst_id = _get_or_create_ip(conn, rec["dst_ip"], rec["dst_is_private"])
    type_id = conn.execute(
        "SELECT event_type_id FROM event_types WHERE code = ?", (rec["event_type"],)
    ).fetchone()[0]
    conn.execute(
        """INSERT INTO network_events
           (event_key, sensor_id, event_type_id, src_ip_id, dst_ip_id, event_time,
            src_port, dst_port, protocol, action, bytes, duration_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (key, sensor_id, type_id, src_id, dst_id, rec["timestamp"],
         rec["src_port"], rec["dst_port"], rec["protocol"], rec["action"],
         rec["bytes"], rec["duration_ms"]),
    )


def import_csv(conn, path):
    """Import a CSV file in one transaction. Bad rows are skipped and reported."""
    result = ImportResult()
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing_cols = set(REQUIRED_COLUMNS) - set(reader.fieldnames or [])
        if missing_cols:
            raise ValueError(f"CSV header is missing columns: {sorted(missing_cols)}")

        with transaction(conn):
            for raw in reader:
                result.read += 1
                line_no = reader.line_num
                try:
                    rec = parse_row(raw)
                except RowError as exc:
                    result.rejected += 1
                    result.rejects.append((line_no, str(exc)))
                    log.warning("line %d rejected: %s", line_no, exc)
                    continue

                key = _event_key(rec)
                exists = conn.execute(
                    "SELECT 1 FROM network_events WHERE event_key = ?", (key,)
                ).fetchone()
                if exists:
                    result.duplicates += 1
                    continue

                _insert_event(conn, key, rec)
                result.imported += 1
    return result
