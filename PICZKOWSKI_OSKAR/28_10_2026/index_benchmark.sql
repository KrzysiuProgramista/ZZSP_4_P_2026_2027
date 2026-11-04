-- index_benchmark.sql
-- EXERCISE 8: porównanie planu i kosztu indeksu.
-- Włącz pomiar czasu w sqlite3 CLI poleceniem: .timer on

DROP TABLE IF EXISTS benchmark_no_index;
DROP TABLE IF EXISTS benchmark_with_index;

CREATE TABLE benchmark_no_index (
    id INTEGER PRIMARY KEY,
    product_code TEXT NOT NULL,
    payload TEXT
);
CREATE TABLE benchmark_with_index (
    id INTEGER PRIMARY KEY,
    product_code TEXT NOT NULL,
    payload TEXT
);

-- 100 000 deterministycznych rekordów bez indeksu na product_code.
BEGIN;
WITH RECURSIVE seq(n) AS (
    SELECT 1
    UNION ALL SELECT n + 1 FROM seq WHERE n < 100000
)
INSERT INTO benchmark_no_index(product_code, payload)
SELECT printf('P-%05d', n), 'sample-data'
FROM seq;
COMMIT;

-- Te same rekordy w tabeli, na której utworzymy indeks.
CREATE INDEX idx_benchmark_code ON benchmark_with_index(product_code);
BEGIN;
WITH RECURSIVE seq(n) AS (
    SELECT 1
    UNION ALL SELECT n + 1 FROM seq WHERE n < 100000
)
INSERT INTO benchmark_with_index(product_code, payload)
SELECT printf('P-%05d', n), 'sample-data'
FROM seq;
COMMIT;

-- Porównaj plany: bez indeksu powinien być SCAN, z indeksem SEARCH.
EXPLAIN QUERY PLAN
SELECT * FROM benchmark_no_index WHERE product_code = 'P-00123';

EXPLAIN QUERY PLAN
SELECT * FROM benchmark_with_index WHERE product_code = 'P-00123';

-- Wykonaj poniższe SELECT-y wielokrotnie przy .timer on i porównaj czas.
SELECT * FROM benchmark_no_index WHERE product_code = 'P-00123';
SELECT * FROM benchmark_with_index WHERE product_code = 'P-00123';

-- INSERT do tabeli z indeksem wymaga dodatkowej aktualizacji indeksu.
-- Porównanie czasu INSERT: uruchom osobno ten sam INSERT/CTE dla obu tabel
-- po usunięciu/odtworzeniu danych, zachowując tę samą liczbę wierszy i warunki.
-- Raport: indeks przyspiesza selektywne odczyty, ale zwiększa koszt zapisu
-- oraz zajmuje dodatkowe miejsce. Wynik zależy od rozmiaru i selektywności danych.
