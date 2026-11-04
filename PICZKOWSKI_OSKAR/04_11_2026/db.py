"""Database connection, schema initialisation and transaction helper."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config import KNOWN_EVENT_TYPES

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.isolation_level = None  # autocommit; transactions are explicit below
    return conn


def has_schema(conn):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'network_events'"
    ).fetchone()
    return row is not None


def init_db(db_path):
    """Create tables and indexes if missing and seed the event type vocabulary."""
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        with transaction(conn):
            conn.executemany(
                "INSERT OR IGNORE INTO event_types (code, default_severity) VALUES (?, ?)",
                KNOWN_EVENT_TYPES.items(),
            )
    finally:
        conn.close()


@contextmanager
def transaction(conn):
    """Run a block atomically: COMMIT on success, ROLLBACK on any exception."""
    conn.execute("BEGIN")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")
