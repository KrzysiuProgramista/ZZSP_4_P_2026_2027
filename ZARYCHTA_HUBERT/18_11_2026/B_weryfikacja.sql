-- Zadanie B. Uruchom na roboczej kopii bazy, np. wczytaj przez .read w sqlite3.
PRAGMA foreign_keys = ON;

-- Definicje tabel ujawniają PK, UNIQUE, CHECK i FK. Indeksy automatyczne
-- SQLite mogą mieć sql = NULL. Audyt zapewnia istniejący trigger.
SELECT type, name, tbl_name, sql
FROM sqlite_schema
WHERE type IN ('table', 'index', 'trigger')
ORDER BY type, name;

-- Stan początkowy, zmiana i wpis audytowy w tej samej transakcji.
SELECT alert_id, status FROM alerts WHERE alert_id = 1;
SELECT COUNT(*) AS history_before FROM alert_status_history WHERE alert_id = 1;
BEGIN;
UPDATE alerts SET status = 'INVESTIGATING' WHERE alert_id = 1 AND status = 'OPEN';
SELECT alert_id, status FROM alerts WHERE alert_id = 1;
SELECT alert_id, old_status, new_status, changed_at
FROM alert_status_history WHERE alert_id = 1 ORDER BY history_id DESC LIMIT 1;
ROLLBACK;
SELECT alert_id, status FROM alerts WHERE alert_id = 1;
SELECT COUNT(*) AS history_after FROM alert_status_history WHERE alert_id = 1;

-- Ten sam filtr i sortowanie przed i po odtworzeniu indeksu.
-- src_ip jest warunkiem równości, timestamp ogranicza zakres i umożliwia
-- odczyt w kolejności malejącej. ROLLBACK przywraca pierwotny stan indeksów.
BEGIN;
DROP INDEX IF EXISTS idx_events_src_time;
EXPLAIN QUERY PLAN
SELECT timestamp, event_type FROM network_events
WHERE src_ip = '198.51.100.77' AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;
CREATE INDEX idx_events_src_time ON network_events(src_ip, timestamp);
EXPLAIN QUERY PLAN
SELECT timestamp, event_type FROM network_events
WHERE src_ip = '198.51.100.77' AND timestamp >= '2026-09-18T10:00:00'
ORDER BY timestamp DESC;
ROLLBACK;
