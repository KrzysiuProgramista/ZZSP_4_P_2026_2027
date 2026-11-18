-- ============================================================================
-- CHALLENGE A: ANALYTICAL REPORT (network_events)
-- ============================================================================
-- Wymagania:
-- 1. Filter: Wybór zdarzeń w zadanym przedziale czasowym (CTE).
-- 2. Summarise: Agregacja per źródłowy adres IP (src_ip).
-- 3. Classify: Klasyfikacja NORMAL / WATCH / INVESTIGATE z uzasadnieniem.
-- 4. Create a view: Utworzenie widoku source_activity_report (bez nadpisywania suspicious_sources).
-- 5. Compare sets: Porównanie zbiorów (EXCEPT oraz INTERSECT) z CTE allowlist.
-- 6. Explain grain: Opis ziarna (granulacji danych) na każdym etapie przetwarzania.
-- ============================================================================

-- Usunięcie widoku, jeśli istniał wcześniej (zapewnia powtarzalność uruchomienia skryptu)
DROP VIEW IF EXISTS source_activity_report;

-- ============================================================================
-- KROK 1: UTWORZENIE WIDOKU ANALITYCZNEGO
-- ============================================================================
CREATE VIEW source_activity_report AS
WITH 
-- ETAP 1: FILTER (Filtrowanie przedziału czasowego)
-- Ziarno (Grain): 1 wiersz = 1 pojedyncze zdarzenie sieciowe (event_id)
-- w wybranym oknie czasowym (2026-09-18 10:00:00 – 10:59:59).
filtered_events AS (
    SELECT 
        event_id,
        timestamp,
        src_ip,
        dst_port,
        event_type,
        action
    FROM network_events
    WHERE timestamp >= '2026-09-18T10:00:00'
      AND timestamp <= '2026-09-18T10:59:59'
),

-- ETAP 2: SUMMARISE (Agregacja per źródłowy adres IP)
-- Ziarno (Grain): 1 wiersz = 1 unikalny źródłowy adres IP (src_ip) aktywny w badanym oknie.
-- Uwaga: W tabeli network_events 'AUTH_FAILURE' znajduje się w kolumnie event_type,
-- natomiast 'BLOCK' znajduje się w kolumnie action.
summarised_sources AS (
    SELECT 
        src_ip,
        COUNT(*) AS total_events,
        SUM(CASE WHEN event_type = 'AUTH_FAILURE' THEN 1 ELSE 0 END) AS auth_failure_count,
        SUM(CASE WHEN action = 'BLOCK' THEN 1 ELSE 0 END) AS block_count,
        COUNT(DISTINCT dst_port) AS distinct_dst_ports
    FROM filtered_events
    GROUP BY src_ip
)

-- ETAP 3: CLASSIFY (Klasyfikacja poziomu ryzyka)
-- Ziarno (Grain): 1 wiersz = 1 unikalny źródłowy adres IP (src_ip) wraz z przypisaną kategorią ryzyka.
--
-- Uzasadnienie progów klasyfikacji:
-- * INVESTIGATE: auth_failure_count >= 5 (zgodne z progiem w widoku suspicious_sources)
--   LUB block_count >= 15 OR distinct_dst_ports >= 15 (wskazuje na agresywne skanowanie portów
--   lub masowe odrzucanie ruchu przez zaporę, np. 198.51.100.66 skanujący 26 portów).
-- * WATCH: auth_failure_count BETWEEN 1 AND 4 OR block_count BETWEEN 8 AND 14
--   (podwyższona liczba odrzuconych pakietów lub pojedyncze błędy logowania wymagające obserwacji).
-- * NORMAL: pozostały ruch mieszczący się w standardowej normie operacyjnej.
SELECT 
    src_ip,
    total_events,
    auth_failure_count,
    block_count,
    distinct_dst_ports,
    CASE 
        WHEN auth_failure_count >= 5 OR block_count >= 15 OR distinct_dst_ports >= 15 THEN 'INVESTIGATE'
        WHEN auth_failure_count >= 1 OR block_count >= 8 THEN 'WATCH'
        ELSE 'NORMAL'
    END AS risk_classification
FROM summarised_sources;


-- ============================================================================
-- KROK 2: ZAPYTANIE DO UTWORZONEGO WIDOKU (WERYFIKACJA WYNIKÓW)
-- ============================================================================
-- Ziarno (Grain): 1 wiersz = 1 źródłowy adres IP z widoku source_activity_report.
SELECT * 
FROM source_activity_report
ORDER BY 
    CASE risk_classification 
        WHEN 'INVESTIGATE' THEN 1 
        WHEN 'WATCH' THEN 2 
        ELSE 3 
    END,
    total_events DESC;


-- ============================================================================
-- KROK 3: COMPARE SETS (Porównanie zbiorów z użyciem EXCEPT oraz INTERSECT)
-- ============================================================================
-- Definiujemy małą listę zaufanych adresów wewnętrznych (allowlist CTE).

-- 3A. EXCEPT: Zwraca podejrzane/obserwowane adresy IP (WATCH lub INVESTIGATE),
-- które NIE znajdują się na liście allowlist (wymagają reakcji zespołu SOC).
-- Ziarno (Grain): 1 wiersz = 1 unikalny adres IP (src_ip) spoza listy zaufanych.
WITH allowlist AS (
    SELECT '10.0.0.14' AS src_ip
    UNION ALL
    SELECT '10.0.0.15' AS src_ip
    UNION ALL
    SELECT '10.0.0.20' AS src_ip
)
SELECT src_ip 
FROM source_activity_report
WHERE risk_classification IN ('WATCH', 'INVESTIGATE')
EXCEPT
SELECT src_ip 
FROM allowlist
ORDER BY src_ip;

-- 3B. INTERSECT: Zwraca adresy IP z listy allowlist, które mimo statusu zaufanego
-- wygenerowały alerty (WATCH lub INVESTIGATE) – np. potencjalnie skompromitowany host wewnętrzny.
-- Ziarno (Grain): 1 wiersz = 1 unikalny zaufany adres IP (src_ip) wykazujący anomalie.
WITH allowlist AS (
    SELECT '10.0.0.14' AS src_ip
    UNION ALL
    SELECT '10.0.0.15' AS src_ip
    UNION ALL
    SELECT '10.0.0.20' AS src_ip
)
SELECT src_ip 
FROM source_activity_report
WHERE risk_classification IN ('WATCH', 'INVESTIGATE')
INTERSECT
SELECT src_ip 
FROM allowlist
ORDER BY src_ip;


/* ============================================================================
   PRZYKŁADOWY WYNIK (SAMPLE OUTPUT) Z BAZY network_security.db
   ============================================================================

   1. Wynik zapytania: SELECT * FROM source_activity_report ...
   +---------------+--------------+--------------------+-------------+--------------------+---------------------+
   | src_ip        | total_events | auth_failure_count | block_count | distinct_dst_ports | risk_classification |
   +---------------+--------------+--------------------+-------------+--------------------+---------------------+
   | 198.51.100.66 |           26 |                  0 |          26 |                 26 | INVESTIGATE         |
   | 203.0.113.23  |           10 |                 10 |          10 |                  1 | INVESTIGATE         |
   | 203.0.113.60  |           74 |                  0 |          15 |                  7 | INVESTIGATE         |
   | 10.0.0.20     |           92 |                  0 |          11 |                  7 | WATCH               |
   | 203.0.113.18  |           76 |                  0 |           8 |                  7 | WATCH               |
   | 10.0.0.15     |           74 |                  0 |          13 |                  7 | WATCH               |
   | 10.0.1.10     |           67 |                  0 |           8 |                  7 | WATCH               |
   | 198.51.100.8  |           64 |                  0 |          12 |                  7 | WATCH               |
   | 198.51.100.90 |           63 |                  0 |           9 |                  7 | WATCH               |
   | 198.51.100.77 |          160 |                  0 |           0 |                  1 | NORMAL              |
   | 192.0.2.44    |           70 |                  0 |           7 |                  7 | NORMAL              |
   | 10.0.0.14     |           65 |                  0 |           7 |                  7 | NORMAL              |
   | 10.0.0.25     |           55 |                  0 |           7 |                  7 | NORMAL              |
   +---------------+--------------+--------------------+-------------+--------------------+---------------------+

   2. Wynik zapytania EXCEPT (niezaufane adresy wymagające uwagi):
   +---------------+
   | src_ip        |
   +---------------+
   | 10.0.1.10     |
   | 198.51.100.66 |
   | 198.51.100.8  |
   | 198.51.100.90 |
   | 203.0.113.18  |
   | 203.0.113.23  |
   | 203.0.113.60  |
   +---------------+

   3. Wynik zapytania INTERSECT (zaufane adresy z allowlist generujące anomalie):
   +-----------+
   | src_ip    |
   +-----------+
   | 10.0.0.15 |
   | 10.0.0.20 |
   +-----------+

   KRÓTKIE WYJAŚNIENIE REGUŁ KLASYFIKACJI I ZIARNA:
   - Ziarno (Grain): W CTE filtered_events pojedynczy wiersz oznacza jedno zdarzenie sieciowe
     (event_id). Po grupowaniu w summarised_sources oraz w widoku source_activity_report
     ziarno zmienia się na jeden unikalny źródłowy adres IP (src_ip).
   - Reguły klasyfikacji:
     * INVESTIGATE: >= 5 nieudanych logowań (spójne z logiką widoku suspicious_sources),
       >= 15 blokad lub >= 15 różnych portów docelowych (wykrywa skanowanie portów, np. 198.51.100.66).
     * WATCH: 1–4 nieudane logowania lub 8–14 blokad (podwyższona aktywność odrzuconego ruchu).
     * NORMAL: pozostały ruch poniżej zdefiniowanych progów ostrzegawczych.
============================================================================ */
