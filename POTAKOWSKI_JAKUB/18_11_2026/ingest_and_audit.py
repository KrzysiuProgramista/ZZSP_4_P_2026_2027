#!/usr/bin/env python3
"""Safe, repeatable import and audit demonstration for network_security.db."""
from __future__ import annotations
import csv
import hashlib
import shutil
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE / "network_security.db"
CSV_FILE = HERE / "network_events_sample.csv"
OPT_DB = HERE / "network_security_optimization_copy.db"
OUTPUT = HERE / "challenge_b_output.txt"

INSERT_SQL = """
INSERT INTO network_events (
    event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port,
    protocol, event_type, action, bytes, duration_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING
"""

QUERY = """SELECT COUNT(*)
FROM network_events
WHERE src_ip = ? AND timestamp >= ? AND timestamp < ?"""


def inspect_schema(conn: sqlite3.Connection, out: list[str]) -> None:
    out.append("1) SCHEMA INSPECTION (existing objects; nothing recreated)")
    objects = conn.execute("""
        SELECT type, name, sql FROM sqlite_master
        WHERE name NOT LIKE 'sqlite_%'
        ORDER BY type, name
    """).fetchall()
    for obj_type, name, sql in objects:
        out.append(f"- {obj_type}: {name}")
        if obj_type == "trigger":
            out.append("  SQL: " + " ".join(sql.split()))
    out.append("network_events columns:")
    for col in conn.execute("PRAGMA table_info(network_events)"):
        out.append(f"  {col[1]} {col[2]} | notnull={col[3]} | pk={col[5]}")
    out.append("network_events indexes:")
    for idx in conn.execute("PRAGMA index_list(network_events)"):
        out.append(f"  {idx[1]} (unique={idx[2]})")
    out.append("Foreign keys:")
    for fk in conn.execute("PRAGMA foreign_key_list(network_events)"):
        out.append(f"  {fk}")


def read_batch(conn: sqlite3.Connection) -> list[tuple]:
    sensors = dict(conn.execute("SELECT sensor_name, sensor_id FROM sensors"))
    rows: list[tuple] = []
    with CSV_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected = ["timestamp", "sensor_name", "src_ip", "dst_ip", "src_port",
                    "dst_port", "protocol", "event_type", "action", "bytes", "duration_ms"]
        if reader.fieldnames != expected:
            raise ValueError(f"Unexpected CSV header: {reader.fieldnames}")
        for row in reader:
            # The starter pack defines event_key as SHA-256 of the 11 CSV values
            # in their original order, joined with the pipe character.
            event_key = hashlib.sha256("|".join(row[k] for k in expected).encode("utf-8")).hexdigest()
            sensor_id = sensors[row["sensor_name"]]
            rows.append((
                event_key, row["timestamp"], sensor_id, row["src_ip"], row["dst_ip"],
                int(row["src_port"]) if row["src_port"] else None,
                int(row["dst_port"]), row["protocol"], row["event_type"], row["action"],
                int(row["bytes"]), int(row["duration_ms"]),
            ))
    return rows


def explain(conn: sqlite3.Connection, label: str, out: list[str]) -> None:
    out.append(label)
    for row in conn.execute("EXPLAIN QUERY PLAN " + QUERY,
                            ("198.51.100.66", "2026-09-18T10:00:00", "2026-09-18T11:00:00")):
        out.append("  " + " | ".join(str(x) for x in row))


def main() -> None:
    if not DB.exists() or not CSV_FILE.exists():
        raise FileNotFoundError("Place this script beside network_security.db and network_events_sample.csv")
    out: list[str] = []
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        inspect_schema(conn, out)
        batch = read_batch(conn)
        out.append("\n2) IDEMPOTENT IMPORT (executemany + ON CONFLICT(event_key) DO NOTHING)")
        out.append(f"CSV rows in batch: {len(batch)}")
        before = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
        out.append(f"Rows before import: {before}")
        conn.executemany(INSERT_SQL, batch)
        conn.commit()
        after_first = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
        out.append(f"Rows after first run: {after_first}")
        conn.executemany(INSERT_SQL, batch)
        conn.commit()
        after_second = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
        out.append(f"Rows after second run: {after_second}")
        out.append(f"Second run added: {after_second - after_first}")

        out.append("\n3) AUDIT TRIGGER TEST (transaction is rolled back)")
        before_alert = conn.execute("SELECT status FROM alerts WHERE alert_id=1").fetchone()[0]
        out.append(f"Alert 1 status before: {before_alert}")
        conn.execute("BEGIN")
        conn.execute("UPDATE alerts SET status='INVESTIGATING' WHERE alert_id=1")
        history = conn.execute("""
            SELECT history_id, alert_id, old_status, new_status, changed_at
            FROM alert_status_history WHERE alert_id=1 ORDER BY history_id DESC LIMIT 1
        """).fetchone()
        out.append(f"Trigger-created history row inside transaction: {history}")
        conn.rollback()
        after_alert = conn.execute("SELECT status FROM alerts WHERE alert_id=1").fetchone()[0]
        history_count = conn.execute("SELECT COUNT(*) FROM alert_status_history").fetchone()[0]
        out.append(f"Alert 1 status after ROLLBACK: {after_alert}")
        out.append(f"History rows after ROLLBACK: {history_count}")

        out.append("\n4) QUERY PLAN COMPARISON ON A DATABASE COPY")
        if OPT_DB.exists():
            OPT_DB.unlink()
        conn.commit()
        conn.close()
        shutil.copy2(DB, OPT_DB)
        opt = sqlite3.connect(OPT_DB)
        opt.execute("PRAGMA foreign_keys = ON")
        # The supplied schema already has this index. Drop it only on the copy
        # to create a genuine before/after comparison; original DB is untouched.
        opt.execute("DROP INDEX IF EXISTS idx_events_src_time")
        opt.commit()
        explain(opt, "Before idx_events_src_time:", out)
        opt.execute("CREATE INDEX idx_events_src_time ON network_events(src_ip, timestamp)")
        opt.commit()
        explain(opt, "After idx_events_src_time:", out)
        opt.close()
        out.append(f"Optimization copy: {OPT_DB.name}")
    finally:
        try:
            conn.close()
        except Exception:
            pass
    OUTPUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print(f"\nSaved captured output to: {OUTPUT}")

if __name__ == "__main__":
    main()
