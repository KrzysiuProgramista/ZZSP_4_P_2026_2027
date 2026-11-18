"""Uruchamia demonstrację zadania B na tymczasowej kopii bazy SQLite."""

import argparse
from contextlib import closing
from pathlib import Path
import re
import sqlite3
from tempfile import TemporaryDirectory


PROJECT_DIR = Path(__file__).resolve().parent
SQL_FILE = PROJECT_DIR / "zadanie_B.sql"

# SQLite automatycznie nadaje event_id każdemu nowemu wierszowi.
EVENT_BATCH = [
    (
        "challenge-b-demo-001", "2026-09-18T11:00:00", 1,
        "192.0.2.10", "10.0.0.5", 51514, 443, "TCP",
        "CONNECTION", "ALLOW", 1200, 85,
    ),
    (
        "challenge-b-demo-002", "2026-09-18T11:01:00", 2,
        "192.0.2.11", "10.0.0.5", 51515, 53, "UDP",
        "DNS_QUERY", "ALLOW", 250, 20,
    ),
]


def load_queries():
    sql_script = SQL_FILE.read_text(encoding="utf-8")
    sections = re.split(r"^-- query: (\w+)\s*\n", sql_script, flags=re.MULTILINE)
    queries = {
        name: sql.strip()
        for name, sql in zip(sections[1::2], sections[2::2])
    }
    # Szablon z parametrami pozostaje w komentarzu, gdy plik SQL jest
    # wykonywany samodzielnie z poziomu klienta SQLite.
    queries["import_event"] = queries["import_event"][2:-2].strip()
    return queries


def inspect_schema(connection, queries):
    print("=== 1. SCHEMAT Z SQLITE_SCHEMA ===")
    for object_type, name, table_name, definition in connection.execute(queries["schema"]):
        print(f"{object_type} {name} (tabela lub widok: {table_name})")
        print(definition or "Indeks automatyczny utworzony przez SQLite.")
    print()


def import_batch(connection, statement, rows):
    try:
        connection.execute("BEGIN")
        cursor = connection.executemany(statement, rows)
        connection.commit()
        return cursor.rowcount
    except Exception:
        connection.rollback()
        raise


def check_idempotency(connection, queries):
    print("=== 2. IMPORT I IDEMPOTENCJA ===")
    count_events = "SELECT COUNT(*) FROM network_events"
    before = connection.execute(count_events).fetchone()[0]
    inserted_first = import_batch(connection, queries["import_event"], EVENT_BATCH)
    after_first = connection.execute(count_events).fetchone()[0]
    inserted_second = import_batch(connection, queries["import_event"], EVENT_BATCH)
    after_second = connection.execute(count_events).fetchone()[0]

    print(f"Zdarzenia przed importem: {before}")
    print(f"Import 1: dodano {inserted_first}, razem {after_first}")
    print(f"Import 2: dodano {inserted_second}, razem {after_second}")
    if (inserted_first, after_first - before) != (len(EVENT_BATCH), len(EVENT_BATCH)):
        raise RuntimeError("Pierwszy import powinien dodać wszystkie zdarzenia z partii.")
    if inserted_second != 0 or after_second != after_first:
        raise RuntimeError("Drugi import dodał powtórzone zdarzenia.")
    print("OK: drugi import tej samej partii nie zwiększył liczby wierszy.\n")


def check_audit(connection, queries):
    print("=== 3. TRIGGER AUDYTU I ROLLBACK ===")
    connection.execute(queries["begin_audit"])
    try:
        status_before = connection.execute(queries["alert_status"]).fetchone()
        if status_before != ("OPEN",):
            raise RuntimeError("Demonstracja wymaga alertu 1 o statusie OPEN.")
        history_before = connection.execute(queries["alert_history"]).fetchall()

        connection.execute(queries["update_alert"])
        status_inside = connection.execute(queries["alert_status"]).fetchone()
        history_inside = connection.execute(queries["alert_history"]).fetchall()
        new_entries = history_inside[len(history_before):]

        print(f"Status przed UPDATE: {status_before[0]}")
        print(f"Status w transakcji: {status_inside[0]}")
        print("Nowe wiersze (history_id, alert_id, old_status, new_status, changed_at):")
        for entry in new_entries:
            print(entry)
        if (
            status_inside != ("INVESTIGATING",)
            or len(new_entries) != 1
            or new_entries[0][1:4] != (1, "OPEN", "INVESTIGATING")
        ):
            raise RuntimeError("Trigger powinien zapisać jedną zmianę OPEN -> INVESTIGATING.")
    finally:
        connection.execute(queries["rollback_audit"])

    status_after = connection.execute(queries["alert_status"]).fetchone()
    history_after = connection.execute(queries["alert_history"]).fetchall()
    print(f"Status po ROLLBACK: {status_after[0]}")
    print(f"Wiersze historii przed i po ROLLBACK: {len(history_before)} -> {len(history_after)}")
    if status_after != status_before or history_after != history_before:
        raise RuntimeError("ROLLBACK nie przywrócił stanu sprzed aktualizacji.")
    print("OK: wycofano zmianę statusu i wpis w historii.\n")


def check_query_plans(connection, queries):
    print("=== 4. EXPLAIN QUERY PLAN NA KOPII BAZY ===")
    connection.execute(queries["begin_index"])
    try:
        connection.execute(queries["drop_index"])
        before = [row[3] for row in connection.execute(queries["plan_before"])]
        connection.execute(queries["create_index"])
        after = [row[3] for row in connection.execute(queries["plan_after"])]
    finally:
        connection.execute(queries["rollback_index"])

    print("Bez idx_events_src_time:")
    print("\n".join(before))
    print("\nZ idx_events_src_time:")
    print("\n".join(after))
    if any("idx_events_src_time" in detail for detail in before):
        raise RuntimeError("Plan bez indeksu nadal wskazuje idx_events_src_time.")
    if not any("SEARCH" in detail and "idx_events_src_time" in detail for detail in after):
        raise RuntimeError("Plan z indeksem nie korzysta z idx_events_src_time.")
    print("OK: z indeksem SQLite wyszukuje według adresu IP i zakresu czasu.\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db", type=Path, default=PROJECT_DIR / "network_security.db",
        help="Ścieżka do bazy źródłowej (domyślnie network_security.db obok skryptu).",
    )
    args = parser.parse_args()
    source_uri = args.db.resolve().as_uri() + "?mode=ro"
    queries = load_queries()

    with TemporaryDirectory(prefix="zadanie_b_") as temporary_dir:
        copy_path = Path(temporary_dir) / "network_security_copy.db"
        # Wyłączamy cache zapytań, aby EXPLAIN było przygotowane po każdej
        # zmianie indeksu.
        with closing(sqlite3.connect(copy_path, cached_statements=0)) as connection:
            with closing(sqlite3.connect(source_uri, uri=True)) as source:
                source.backup(connection)
            connection.execute("PRAGMA foreign_keys = ON")
            print(f"SQLite {sqlite3.sqlite_version} | baza źródłowa: {args.db.name}\n")
            inspect_schema(connection, queries)
            check_idempotency(connection, queries)
            check_audit(connection, queries)
            check_query_plans(connection, queries)

    print("Wszystkie testy zadania B przeszły.")


if __name__ == "__main__":
    main()
