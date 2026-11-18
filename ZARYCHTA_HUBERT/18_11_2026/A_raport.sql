-- Zadanie A. Okno UTC: [2026-09-18 10:00, 11:00).
-- filtered_events: jeden wiersz = jedno zdarzenie w oknie.
-- source_totals i widok: jeden wiersz = jeden źródłowy adres IP w tym oknie.
-- Progi dobrano do danych ćwiczeniowych. Co najmniej 8 błędów logowania,
-- 20 blokad, 15 portów docelowych lub 120 zdarzeń to INVESTIGATE.
-- Kryteria wskazują na serie nieudanych logowań, blokad, szeroki zakres
-- portów lub wyjątkowo duży ruch. W tej próbce tło obejmuje do 92 zdarzeń,
-- 15 blokad i 7 portów na IP. Co najmniej 3 błędy logowania, 10 blokad,
-- 10 portów lub 80 zdarzeń daje WATCH. Reszta to NORMAL.
-- INVESTIGATE ma pierwszeństwo przed WATCH dzięki kolejności w CASE.
CREATE VIEW IF NOT EXISTS source_activity_report AS
WITH filtered_events AS (
    SELECT src_ip, event_type, action, dst_port
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <  '2026-09-18T11:00:00'
),
source_totals AS (
    SELECT src_ip,
           COUNT(*) AS total_events,
           SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS auth_failures,
           SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS blocked_events,
           COUNT(DISTINCT dst_port) AS distinct_dst_ports
    FROM filtered_events
    GROUP BY src_ip
)
SELECT *,
       CASE
           WHEN auth_failures >= 8 OR blocked_events >= 20
                OR distinct_dst_ports >= 15 OR total_events >= 120 THEN 'INVESTIGATE'
           WHEN auth_failures >= 3 OR blocked_events >= 10
                OR distinct_dst_ports >= 10 OR total_events >= 80 THEN 'WATCH'
           ELSE 'NORMAL'
       END AS classification
FROM source_totals;

SELECT * FROM source_activity_report ORDER BY total_events DESC, src_ip;

-- allowlist i wynik EXCEPT: jeden wiersz = jeden unikalny adres IP.
-- Przykładowa lista dopuszczonych źródeł jest fikcyjna.
WITH allowlist(src_ip) AS (
    VALUES ('10.0.0.20'), ('10.0.0.15')
)
SELECT src_ip FROM source_activity_report WHERE classification IN ('WATCH', 'INVESTIGATE')
EXCEPT
SELECT src_ip FROM allowlist
ORDER BY src_ip;

-- Przykładowy wynik wykonania na dołączonej bazie:
-- src_ip | total_events | auth_failures | blocked_events | distinct_dst_ports | classification
-- 198.51.100.77 | 160 | 0 | 0 | 1 | INVESTIGATE
-- 10.0.0.20 | 92 | 0 | 11 | 7 | WATCH
-- 203.0.113.18 | 76 | 0 | 8 | 7 | NORMAL
-- 10.0.0.15 | 74 | 0 | 13 | 7 | WATCH
-- 203.0.113.60 | 74 | 0 | 15 | 7 | WATCH
-- 192.0.2.44 | 70 | 0 | 7 | 7 | NORMAL
-- 10.0.1.10 | 67 | 0 | 8 | 7 | NORMAL
-- 10.0.0.14 | 65 | 0 | 7 | 7 | NORMAL
-- 198.51.100.8 | 64 | 0 | 12 | 7 | WATCH
-- 198.51.100.90 | 63 | 0 | 9 | 7 | NORMAL
-- 10.0.0.25 | 55 | 0 | 7 | 7 | NORMAL
-- 198.51.100.66 | 26 | 0 | 26 | 26 | INVESTIGATE
-- 203.0.113.23 | 10 | 10 | 10 | 1 | INVESTIGATE
--
-- src_ip
-- 198.51.100.66
-- 198.51.100.77
-- 198.51.100.8
-- 203.0.113.23
-- 203.0.113.60
--
