"""Defensive, idempotent CSV importer with row validation and rejection logging."""
import csv
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import sqlite3

HEADERS = (
    "timestamp", "sensor_name", "src_ip", "dst_ip", "src_port", "dst_port",
    "protocol", "event_type", "action", "bytes", "duration_ms",
)
PROTOCOLS = {"TCP", "UDP", "ICMP"}
ACTIONS = {"ALLOW", "BLOCK"}


class ValidationError(ValueError):
    pass


def required_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name}: non-empty text required")
    return value.strip()


def parse_nonnegative(value, name):
    text = required_text(value, name)
    if not text.isdecimal():
        raise ValidationError(f"{name}: expected non-negative integer")
    return int(text)


def parse_port(value, name):
    if value is None or value == "":
        return None
    text = required_text(value, name)
    if not text.isdecimal():
        raise ValidationError(f"{name}: expected integer 1..65535 or blank")
    port = int(text)
    if not 1 <= port <= 65535:
        raise ValidationError(f"{name}: out of range 1..65535")
    return port


def parse_time(value):
    text = required_text(value, "timestamp")
    if "T" not in text and " " not in text:
        raise ValidationError("timestamp: ISO 8601 date and time required")
    try:
        moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"timestamp: invalid ISO 8601: {text!r}") from exc
    # Input sample timestamps are timezone-naive; documented choice: UTC.
    # Convert offset-aware values to the same canonical UTC representation.
    if moment.tzinfo is not None:
        moment = moment.astimezone(timezone.utc).replace(tzinfo=None)
    return moment.isoformat(timespec="microseconds" if moment.microsecond else "seconds")


def parse_ip(value, name):
    text = required_text(value, name)
    try:
        result = ipaddress.ip_address(text)
    except ValueError as exc:
        raise ValidationError(f"{name}: invalid IPv4/IPv6 address: {text!r}") from exc
    return str(result), int(result.is_private)


def validate(row, event_type_codes):
    if None in row:
        raise ValidationError("unexpected extra CSV columns")
    if any(c not in row for c in HEADERS):
        raise ValidationError("missing required CSV column")
    sensor = required_text(row["sensor_name"], "sensor_name")
    timestamp = parse_time(row["timestamp"])
    src_ip, src_private = parse_ip(row["src_ip"], "src_ip")
    dst_ip, dst_private = parse_ip(row["dst_ip"], "dst_ip")
    protocol = required_text(row["protocol"], "protocol")
    event_type = required_text(row["event_type"], "event_type")
    action = required_text(row["action"], "action")
    if protocol not in PROTOCOLS:
        raise ValidationError(f"protocol: unsupported value {protocol!r}")
    if event_type not in event_type_codes:
        raise ValidationError(f"event_type: unknown value {event_type!r}")
    if action not in ACTIONS:
        raise ValidationError(f"action: unsupported value {action!r}")

    src_port = parse_port(row["src_port"], "src_port")
    dst_port = parse_port(row["dst_port"], "dst_port")
    if protocol in {"TCP", "UDP"} and (src_port is None or dst_port is None):
        raise ValidationError(f"{protocol} requires both src_port and dst_port")
    b = parse_nonnegative(row["bytes"], "bytes")
    duration = parse_nonnegative(row["duration_ms"], "duration_ms")
    # The fingerprint covers exactly the original 11 CSV values, in fixed order.
    # Reimporting identical records, including through another file path, is safe.
    fingerprint = hashlib.sha256(
        json.dumps([row[c] for c in HEADERS], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "event_hash": fingerprint, "sensor": sensor, "timestamp": timestamp,
        "raw_timestamp": row["timestamp"], "src_ip": src_ip, "dst_ip": dst_ip,
        "src_private": src_private, "dst_private": dst_private,
        "src_port": src_port, "dst_port": dst_port,
        "protocol": protocol, "event_type": event_type, "action": action,
        "bytes": b, "duration_ms": duration,
    }


def get_or_create(conn, table, unique_field, unique_value, extra=()):
    # table and column names come from these fixed internal call sites, never CSV.
    fields = {"sensors": ("sensor_id", "name"), "ip_addresses": ("ip_id", "address")}
    id_col, expected_field = fields[table]
    assert unique_field == expected_field
    if table == "sensors":
        conn.execute("INSERT OR IGNORE INTO sensors(name) VALUES (?)", (unique_value,))
    else:
        conn.execute("INSERT OR IGNORE INTO ip_addresses(address,is_private) VALUES (?,?)", (unique_value, extra[0]))
    return conn.execute(f"SELECT {id_col} FROM {table} WHERE {unique_field} = ?", (unique_value,)).fetchone()[0]


def import_csv(conn, file_path):
    file_path = Path(file_path)
    codes = {r[0] for r in conn.execute("SELECT code FROM event_types")}
    if not codes:
        raise RuntimeError("Database is not initialized. Run init-db first.")
    counters = {"read": 0, "imported": 0, "rejected": 0, "duplicates": 0}
    errors = []
    with file_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV is empty; expected a header")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("CSV has duplicate header columns")
        missing = sorted(set(HEADERS) - set(reader.fieldnames))
        unexpected = sorted(set(reader.fieldnames) - set(HEADERS))
        if missing or unexpected:
            raise ValueError(f"Invalid CSV header; missing={missing}, unexpected={unexpected}")

        # One transaction per import. Individual malformed rows are logged and skipped.
        with conn:
            for line_number, row in enumerate(reader, start=2):
                counters["read"] += 1
                try:
                    event = validate(row, codes)
                except ValidationError as exc:
                    counters["rejected"] += 1
                    reason = str(exc)
                    errors.append((line_number, reason))
                    conn.execute(
                        "INSERT INTO import_rejections(filename,line_number,reason,raw_row) VALUES (?,?,?,?)",
                        (str(file_path), line_number, reason, json.dumps(row, ensure_ascii=False)),
                    )
                    continue

                # Skip duplicates BEFORE inserting dimension rows.
                if conn.execute("SELECT 1 FROM network_events WHERE event_hash = ?", (event["event_hash"],)).fetchone():
                    counters["duplicates"] += 1
                    continue
                try:
                    sensor_id = get_or_create(conn, "sensors", "name", event["sensor"])
                    src_id = get_or_create(conn, "ip_addresses", "address", event["src_ip"], (event["src_private"],))
                    dst_id = get_or_create(conn, "ip_addresses", "address", event["dst_ip"], (event["dst_private"],))
                    type_id = conn.execute("SELECT event_type_id FROM event_types WHERE code = ?", (event["event_type"],)).fetchone()[0]
                    conn.execute("""
                        INSERT INTO network_events(
                          event_hash,sensor_id,event_type_id,src_ip_id,dst_ip_id,
                          event_time,raw_timestamp,src_port,dst_port,protocol,action,bytes,duration_ms
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        event["event_hash"],sensor_id,type_id,src_id,dst_id,
                        event["timestamp"],event["raw_timestamp"],event["src_port"],
                        event["dst_port"],event["protocol"],event["action"],
                        event["bytes"],event["duration_ms"],
                    ))
                except sqlite3.IntegrityError as exc:
                    # Unexpected integrity errors should not silently discard a row.
                    raise RuntimeError(f"Database integrity error at CSV line {line_number}: {exc}") from exc
                counters["imported"] += 1
    return counters, errors
