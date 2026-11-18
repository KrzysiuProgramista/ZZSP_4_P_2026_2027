"""Import i weryfikacja na tymczasowych kopiach dołączonej bazy SQLite."""

import csv
import hashlib
import sqlite3
from contextlib import closing
from datetime import datetime
from ipaddress import ip_address
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_COLUMNS = (
    "timestamp", "sensor_name", "src_ip", "dst_ip", "src_port", "dst_port",
    "protocol", "event_type", "action", "bytes", "duration_ms",
)
INSERT_EVENT = """
INSERT INTO network_events (
    event_key, timestamp, sensor_id, src_ip, dst_ip, src_port, dst_port,
    protocol, event_type, action, bytes, duration_ms
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING
"""


def load_batch(csv_path, sensors):
    batch = []
    with csv_path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        if tuple(next(reader, ())) != CSV_COLUMNS:
            raise ValueError("Nieprawidłowy nagłówek CSV")
        for line_number, fields in enumerate(reader, start=2):
            try:
                if len(fields) != len(CSV_COLUMNS) or any("|" in value for value in fields):
                    raise ValueError("Nieprawidłowy zestaw pól")
                timestamp, sensor, src, dst, sport, dport, protocol, event, action, size, duration = fields
                parsed_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
                if parsed_timestamp.isoformat() != timestamp:
                    raise ValueError("Nieprawidłowy format czasu")
                ip_address(src)
                ip_address(dst)
                if not event.strip() or protocol not in {"TCP", "UDP", "ICMP"}:
                    raise ValueError("Nieprawidłowy typ zdarzenia lub protokół")
                if action not in {"ALLOW", "BLOCK"}:
                    raise ValueError("Nieprawidłowa akcja")
                # Zachowanie tekstu z CSV daje klucze zgodne z bazą startową.
                key = hashlib.sha256("|".join(fields).encode("utf-8")).hexdigest()
                batch.append((
                    key, timestamp, sensors[sensor], src, dst,
                    int(sport) if sport else None, int(dport),
                    protocol, event, action, int(size), int(duration),
                ))
            except (ValueError, KeyError) as error:
                raise ValueError(f"CSV, wiersz {line_number}: {error}") from error
    return batch


def import_twice(db, batch, expected_counts):
    before = db.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
    inserted_counts = []
    for attempt in (1, 2):
        # Cały executemany jest objęty jedną transakcją. Kontekst połączenia
        # zatwierdza kompletną partię albo wycofuje ją po wyjątku.
        with db:
            db.execute("BEGIN")
            inserted = db.executemany(INSERT_EVENT, batch).rowcount
        count = db.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
        assert count == before + inserted
        print(f"Import {attempt}: przed={before}, dodano={inserted}, po={count}")
        inserted_counts.append(inserted)
        before = count
    assert tuple(inserted_counts) == expected_counts


def check_database(db):
    sql = (ROOT / "B_weryfikacja.sql").read_text(encoding="utf-8")
    statement = ""
    results = []
    for line in sql.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            cursor = db.execute(statement)
            statement = ""
            if cursor.description:
                rows = cursor.fetchall()
                results.append(rows)
                print(" | ".join(column[0] for column in cursor.description))
                for row in rows:
                    print(" | ".join(str(value) for value in row))
                print()
    schema, before, history_before, during, audit, after, history_after, no_index, indexed = results
    assert any(row[:2] == ("trigger", "log_alert_status_change") for row in schema)
    assert before == after == [(1, "OPEN")]
    assert during == [(1, "INVESTIGATING")]
    assert audit[0][:3] == (1, "OPEN", "INVESTIGATING")
    assert history_before == history_after == [(0,)]
    assert any("SCAN network_events" in row[3] for row in no_index)
    assert any("TEMP B-TREE" in row[3] for row in no_index)
    assert any("SEARCH network_events USING INDEX idx_events_src_time" in row[3] for row in indexed)
    assert not any("TEMP B-TREE" in row[3] for row in indexed)


def main():
    print(f"SQLite {sqlite3.sqlite_version}")
    starter_uri = (ROOT / "network_security.db").as_uri() + "?mode=ro"
    with (
        closing(sqlite3.connect(starter_uri, uri=True)) as starter,
        closing(sqlite3.connect(":memory:")) as full_copy,
        closing(sqlite3.connect(":memory:")) as empty_copy,
    ):
        starter.backup(full_copy)
        starter.backup(empty_copy)
        full_copy.execute("PRAGMA foreign_keys = ON")
        empty_copy.execute("PRAGMA foreign_keys = ON")
        sensors = dict(full_copy.execute("SELECT sensor_name, sensor_id FROM sensors"))
        batch = load_batch(ROOT / "network_events_sample.csv", sensors)
        assert len(batch) == 896
        print("\nKopia bazy startowej (CSV już zaimportowany)")
        import_twice(full_copy, batch, (0, 0))
        print("\nDruga kopia (wyczyszczono wyłącznie network_events)")
        with empty_copy:
            empty_copy.execute("DELETE FROM network_events")
        import_twice(empty_copy, batch, (896, 0))
        for db in (empty_copy, full_copy):
            assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
            assert not db.execute("PRAGMA foreign_key_check").fetchall()
        stored_keys = {row[0] for row in full_copy.execute("SELECT event_key FROM network_events")}
        assert stored_keys == {row[0] for row in batch}
        print("\nSchemat, audyt i plany zapytań na kopii bazy startowej")
        check_database(full_copy)
        print("OK: import, zgodność kluczy, audyt, rollback, indeks i integralność.")


if __name__ == "__main__":
    main()
