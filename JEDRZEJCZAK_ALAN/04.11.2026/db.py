"""SQLite connection and schema initialization."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "network_events.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

EVENT_TYPES = (
    ("AUTH_FAILURE", "HIGH"),
    ("AUTH_SUCCESS", "INFO"),
    ("CONNECTION", "INFO"),
    ("DNS_QUERY", "INFO"),
    ("HTTP_REQUEST", "INFO"),
)


@contextmanager
def connect(path=DEFAULT_DB_PATH):
    """Close every connection, including when a command raises an exception."""
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        yield conn
    finally:
        conn.close()


def init_db(conn):
    """Idempotently create all tables/indexes and seed known event types."""
    # executescript commits transactions implicitly; call it outside an open batch.
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    with conn:
        conn.executemany(
            "INSERT OR IGNORE INTO event_types(code,default_severity) VALUES (?,?)",
            EVENT_TYPES,
        )
