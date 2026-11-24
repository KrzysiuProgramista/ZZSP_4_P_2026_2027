"""
db.py - Database connection management, schema initialization, and lookup helpers.
Uses Python's built-in sqlite3 module with foreign keys enabled and parameterised SQL.
"""
import ipaddress
import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

DEFAULT_SEVERITIES = {
    "AUTH_FAILURE": "MEDIUM",
    "AUTH_SUCCESS": "LOW",
    "CONNECTION": "LOW",
    "HTTP_REQUEST": "LOW",
    "DNS_QUERY": "LOW",
    "PING": "LOW",
    "PORT_PROBE": "HIGH",
    "MALWARE_ALERT": "CRITICAL",
}


def connect(db_path: str) -> sqlite3.Connection:
    """Open a SQLite connection with Row factory and foreign key enforcement."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str, schema_path: Optional[Path] = None) -> None:
    """Initialise database tables, constraints, and indexes from schema.sql."""
    path = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
    schema_sql = path.read_text(encoding="utf-8")
    conn = connect(db_path)
    try:
        with conn:
            conn.executescript(schema_sql)
            conn.execute("PRAGMA foreign_keys = ON;")
    finally:
        conn.close()


def get_or_create_sensor(conn: sqlite3.Connection, name: str, location: str = "edge") -> int:
    """Return sensor_id for name, inserting if not yet present."""
    conn.execute(
        "INSERT OR IGNORE INTO sensors (name, location) VALUES (?, ?)",
        (name, location),
    )
    row = conn.execute(
        "SELECT sensor_id FROM sensors WHERE name = ?",
        (name,),
    ).fetchone()
    return int(row["sensor_id"])


def get_or_create_ip(conn: sqlite3.Connection, address: str) -> int:
    """Normalise IP address string, determine privacy flag, and return ip_id."""
    ip_obj = ipaddress.ip_address(address)
    canonical = ip_obj.compressed
    is_private = 1 if ip_obj.is_private else 0
    conn.execute(
        "INSERT OR IGNORE INTO ip_addresses (address, is_private) VALUES (?, ?)",
        (canonical, is_private),
    )
    row = conn.execute(
        "SELECT ip_id FROM ip_addresses WHERE address = ?",
        (canonical,),
    ).fetchone()
    return int(row["ip_id"])


def get_or_create_event_type(conn: sqlite3.Connection, code: str) -> int:
    """Return event_type_id for code, seeding default severity if new."""
    severity = DEFAULT_SEVERITIES.get(code, "LOW")
    conn.execute(
        "INSERT OR IGNORE INTO event_types (code, default_severity) VALUES (?, ?)",
        (code, severity),
    )
    row = conn.execute(
        "SELECT event_type_id FROM event_types WHERE code = ?",
        (code,),
    ).fetchone()
    return int(row["event_type_id"])