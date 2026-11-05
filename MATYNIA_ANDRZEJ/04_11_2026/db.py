import sqlite3

DB_PATH = "network_analyzer.db"


def get_connection():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  conn.execute("PRAGMA foreign_keys = ON")
  return conn


def init_db():
  conn = get_connection()
  with open("schema.sql", "r", encoding="utf-8") as f:
    conn.executescript(f.read())
  conn.commit()
  conn.close()
  print("[+] Baza danych została zainicjalizowana pomyślnie.")
