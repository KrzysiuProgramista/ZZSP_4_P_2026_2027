-- Zadanie 8, slajdy 38-39. Uruchom w OSOBNEJ, pustej bazie pomiarowej.
-- W glownej bazie products.code ma UNIQUE i juz posiada indeks SQLite.
-- Dlatego tutaj stosujemy osobna tabele bez UNIQUE na kolumnie testowej.
-- product_code odpowiada kolumnie code w schema.sql.
-- W konsoli sqlite3 mozna przed wykonaniem wlaczyc: .timer on
-- Zmierz INSERT/COMMIT i selektywny SELECT; powtorz na swiezej bazie.

-- Wspolny deterministyczny zestaw: 100000 wierszy, przygotowany poza pomiarem.
CREATE TEMP TABLE benchmark_seed AS
WITH RECURSIVE seq(n) AS (
    SELECT 0 UNION ALL SELECT n+1 FROM seq WHERE n<99999
)
SELECT n+1 AS product_id, printf('P-%05d', n) AS product_code,
       CAST(10+n%1000 AS REAL) AS price
FROM seq;

CREATE TABLE benchmark_products (
    product_id INTEGER PRIMARY KEY,
    product_code TEXT NOT NULL,
    price REAL NOT NULL
);
CREATE TABLE benchmark_products_indexed (
    product_id INTEGER PRIMARY KEY,
    product_code TEXT NOT NULL,
    price REAL NOT NULL
);
-- Indeks istnieje PRZED wstawianiem do drugiej tabeli.
CREATE INDEX idx_insert_product_code
ON benchmark_products_indexed(product_code);

-- Wariant bez indeksu na product_code: identyczne dane, jedna transakcja.
BEGIN;
INSERT INTO benchmark_products SELECT * FROM benchmark_seed;
COMMIT;
-- Wariant z indeksem: identyczne dane i taki sam sposob wstawiania.
BEGIN;
INSERT INTO benchmark_products_indexed SELECT * FROM benchmark_seed;
COMMIT;

-- Ten sam selektywny odczyt przed i po dodaniu indeksu.
EXPLAIN QUERY PLAN
SELECT * FROM benchmark_products WHERE product_code='P-00123';
SELECT * FROM benchmark_products WHERE product_code='P-00123';
CREATE INDEX idx_benchmark_product_code ON benchmark_products(product_code);
EXPLAIN QUERY PLAN
SELECT * FROM benchmark_products WHERE product_code='P-00123';
SELECT * FROM benchmark_products WHERE product_code='P-00123';

-- PLAN PRZED: SCAN benchmark_products
-- PLAN PO: SEARCH benchmark_products USING INDEX
--          idx_benchmark_product_code (product_code=?)
-- W obu przypadkach wynik: (124, 'P-00123', 133.0).

-- WYKONANY POMIAR I WNIOSKI
-- Rzeczywisty pomiar: 5 par swiezych baz plikowych, po 100000 identycznych
-- wierszy. W pierwotnym pomiarze INSERT wykonywano przez executemany
-- w jednej transakcji; dane przygotowano poza pomiarem, kolejnosc par
-- zmieniano. Powyzszy samodzielny SQL odtwarza dane przez INSERT SELECT.
-- Odczyt: ta sama baza przed/po indeksem, 10 rozgrzewek + 100 odczytow.
-- journal_mode=DELETE, synchronous=FULL, cache_size=8192 KiB; cieply cache.
-- Srodowisko pomiaru: Python 3.12.14, SQLite 3.53.1, Windows 11.
-- Proba | INSERT bez [ms] | INSERT z [ms] | SELECT bez [us] | SELECT z [us]
--     1 |           89.89 |        140.17 |         4176.36 |        111.26
--     2 |           87.56 |        136.49 |         4192.17 |        108.39
--     3 |           87.39 |        135.53 |         4164.08 |        108.55
--     4 |           92.46 |        136.20 |         4220.59 |        107.04
--     5 |           87.92 |        132.70 |         4291.50 |        112.35
-- Mediana INSERT bez indeksu: 87.919 ms.
-- Mediana INSERT z indeksem: 136.201 ms.
-- Mediana SELECT bez indeksu: 4192.172 us.
-- Mediana SELECT z indeksem: 108.554 us.
-- SELECT przyspieszyl 38.6 razy; INSERT trwal o 54.9% dluzej.
-- Budowa indeksu na istniejacych danych: mediana 33.023 ms.
-- Korzysc przy selektywnych odczytach jest duza w tej probie, ale zapis
-- wymaga utrzymywania dodatkowej struktury i indeks zajmuje miejsce.
-- Wyniki zaleza od sprzetu, cache i metody wstawiania; nie sa gwarancja
-- wydajnosci innego komputera. SCAN malej tabeli nie musi byc bledem.
-- Nie nalezy dublowac indeksu juz zapewnianego przez UNIQUE(code).
