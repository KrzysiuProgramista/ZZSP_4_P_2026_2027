import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "network_analyzer.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def connect(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path=DB_PATH, schema_path=SCHEMA_PATH):
    conn = connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_script = f.read()
    with conn:
        conn.executescript(schema_script)
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
