import sqlite3
from contextlib import contextmanager
from pathlib import Path
from config import EVENT_TYPES

@contextmanager
def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
    finally:
        conn.close()

def init_db(conn):
    conn.executescript(Path(__file__).with_name('schema.sql').read_text(encoding='utf-8'))
    with conn:
        conn.executemany('INSERT OR IGNORE INTO event_types(code,default_severity) VALUES (?,?)', EVENT_TYPES.items())
