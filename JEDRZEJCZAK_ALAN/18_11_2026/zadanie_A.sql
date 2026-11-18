-- ZADANIE A | Raport aktywności według źródłowego IP
-- Uruchom cały plik w istniejącej bazie network_security.db.
-- Okres raportu: 18.09.2026, od 10:00 (włącznie) do 11:00 (wyłącznie), UTC.
-- To pełna godzina dostępna w zestawie. Daty mają ten sam format ISO 8601
-- co kolumna timestamp, dlatego można je porównać jako tekst.
--
-- Poziom szczegółowości (grain):
--   events_in_range: jeden wiersz = jedno zdarzenie z wybranego okresu.
--   source_summary: jeden wiersz = jeden źródłowy adres IP w tym okresie.
--   widok: jeden wiersz = jeden źródłowy adres IP z metrykami i klasyfikacją.
--   allowlist i EXCEPT: jeden wiersz = jeden źródłowy adres IP.
--
-- Reguły (CASE sprawdza INVESTIGATE przed WATCH):
--   INVESTIGATE: >= 8 błędów logowania lub >= 20 różnych portów docelowych.
--     W tej próbce tyle błędów wskazuje na serię prób logowania, a 20
--     różnych portów warto sprawdzić (typowe źródła w tej godzinie miały do 7).
--   WATCH: >= 3 błędy logowania, >= 10 blokad lub >= 150 zdarzeń.
--     Niższa liczba błędów, liczne blokady lub duży ruch uzasadniają obserwację.
--   NORMAL: pozostałe źródła.
-- Są to progi ćwiczeniowe dobrane do godzinnego raportu. Same metryki
-- wskazują źródła do sprawdzenia. Wykrywanie krótkich serii wymaga krótszych okien.

DROP VIEW IF EXISTS source_activity_report;

CREATE VIEW source_activity_report AS
WITH events_in_range AS (
    SELECT src_ip, event_type, action, dst_port
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <  '2026-09-18T11:00:00'
),
source_summary AS (
    SELECT
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS failed_logins,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS blocked_events,
        COUNT(DISTINCT dst_port) AS unique_ports
    FROM events_in_range
    GROUP BY src_ip
)
SELECT
    src_ip,
    total_events,
    failed_logins,
    blocked_events,
    unique_ports,
    CASE
        WHEN failed_logins >= 8 OR unique_ports >= 20 THEN 'INVESTIGATE'
        WHEN failed_logins >= 3 OR blocked_events >= 10 OR total_events >= 150 THEN 'WATCH'
        ELSE 'NORMAL'
    END AS classification
FROM source_summary;

SELECT src_ip, total_events, failed_logins, blocked_events, unique_ports, classification
FROM source_activity_report
ORDER BY total_events DESC, src_ip;

-- Adresy do sprawdzenia spoza przykładowej listy dozwolonych adresów.
WITH allowlist(src_ip) AS (
    VALUES ('10.0.0.14'), ('10.0.0.15'), ('10.0.0.20')
)
SELECT src_ip
FROM source_activity_report
WHERE classification IN ('WATCH', 'INVESTIGATE')
EXCEPT
SELECT src_ip
FROM allowlist
ORDER BY src_ip;

-- Wynik raportu na dostarczonej bazie (wszystkie 13 wierszy):
-- src_ip         total_events  failed_logins  blocked_events  unique_ports  classification
-- 198.51.100.77  160           0              0               1             WATCH
-- 10.0.0.20       92           0             11               7             WATCH
-- 203.0.113.18    76           0              8               7             NORMAL
-- 10.0.0.15       74           0             13               7             WATCH
-- 203.0.113.60    74           0             15               7             WATCH
-- 192.0.2.44      70           0              7               7             NORMAL
-- 10.0.1.10       67           0              8               7             NORMAL
-- 10.0.0.14       65           0              7               7             NORMAL
-- 198.51.100.8    64           0             12               7             WATCH
-- 198.51.100.90   63           0              9               7             NORMAL
-- 10.0.0.25       55           0              7               7             NORMAL
-- 198.51.100.66   26           0             26              26             INVESTIGATE
-- 203.0.113.23    10          10             10               1             INVESTIGATE
--
-- Wynik EXCEPT (5 adresów):
-- 198.51.100.66
-- 198.51.100.77
-- 198.51.100.8
-- 203.0.113.23
-- 203.0.113.60
