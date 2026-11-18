-- ZADANIE B | Schemat, audyt i porównanie planów zapytania
-- Uruchom ten plik na kopii network_security.db. Import i asercje wykonuje
-- zadanie_B.py, korzystając z poleceń SQL poniżej.
--
-- Klucze i ograniczenia widoczne w sqlite_schema:
--   sensors: PK sensor_id, UNIQUE(sensor_name).
--   network_events: PK event_id, UNIQUE(event_key), FK sensor_id -> sensors
--     z ON DELETE RESTRICT. CHECK dla zakresu portów, protokołu, akcji oraz
--     nieujemnych bytes i duration_ms. src_port może mieć wartość NULL.
--   alerts: PK alert_id, UNIQUE(source_ip, rule_name, first_seen).
--     CHECK ogranicza status do czterech wartości, a event_count musi być > 0.
--   alert_status_history: PK history_id, FK alert_id -> alerts
--     z ON DELETE RESTRICT i domyślny changed_at = CURRENT_TIMESTAMP.
--   event_statistics: PK source_ip, CHECK(event_count >= 0).
--   Trigger log_alert_status_change dopisuje historię po faktycznej zmianie statusu.
--   Indeksy jawne: idx_events_src_time, idx_events_type_time,
--     idx_alert_history_alert_time. Indeksy sqlite_autoindex obsługują
--     ograniczenia UNIQUE i tekstowy klucz główny.
--
-- Kluczem konfliktu przy imporcie jest stabilny i unikatowy event_key.
-- INSERT podaje dwanaście pól zdarzenia. SQLite sam nadaje event_id.
-- Jeden BEGIN/COMMIT obejmuje całe executemany(). Błąd wycofuje całą partię.
-- ON CONFLICT ignoruje tylko konflikt wskazanego klucza.
--
-- Audyt: UPDATE i wpis triggera są częścią tej samej transakcji. ROLLBACK
-- przywraca status alertu i usuwa wpis dodany podczas demonstracji.
--
-- Indeks: (src_ip, timestamp) pozwala najpierw zawęzić do jednego źródła,
-- następnie przeszukać zakres czasu i odczytać go w kolejności malejącej.
-- EXPLAIN QUERY PLAN pokazuje sposób wykonania zapytania.

PRAGMA foreign_keys = ON;

-- query: schema
SELECT type, name, tbl_name, sql
FROM sqlite_schema
WHERE type IN ('table', 'index', 'trigger', 'view')
ORDER BY type, name;

-- query: begin_audit
BEGIN;

-- query: alert_status
SELECT status
FROM alerts
WHERE alert_id = 1;

-- query: update_alert
UPDATE alerts
SET status = 'INVESTIGATING'
WHERE alert_id = 1;

-- query: alert_history
SELECT history_id, alert_id, old_status, new_status, changed_at
FROM alert_status_history
WHERE alert_id = 1
ORDER BY history_id;

-- query: rollback_audit
ROLLBACK;

-- query: begin_index
BEGIN;

-- query: drop_index
DROP INDEX IF EXISTS idx_events_src_time;

-- query: plan_before
EXPLAIN QUERY PLAN
SELECT timestamp, event_type
FROM network_events
WHERE src_ip = '198.51.100.77'
  AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;

-- query: create_index
CREATE INDEX idx_events_src_time ON network_events(src_ip, timestamp);

-- query: plan_after
EXPLAIN QUERY PLAN
SELECT timestamp, event_type
FROM network_events
WHERE src_ip = '198.51.100.77'
  AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;

-- query: rollback_index
ROLLBACK;

-- query: import_event
/*
INSERT INTO network_events (
    event_key, timestamp, sensor_id, src_ip, dst_ip,
    src_port, dst_port, protocol, event_type, action, bytes, duration_ms
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_key) DO NOTHING;
*/
