-- Zadanie 7, slajdy 36-37. SQLite.
-- Uruchamiaj trzy scenariusze osobno, w podanej kolejnosci, na bazie
-- utworzonej z schema.sql oraz dane.sql. PRAGMA foreign_keys = ON.
-- W scenariuszu 2 celowo wystapi blad CHECK. Po nim wykonaj ROLLBACK
-- oraz ostatni SELECT. W SQLite sam blad CHECK nie cofa calej transakcji.
-- Dodatkowy obiekt TEMP kontroluje liczbe zmienionych wierszy po UPDATE.
-- Przy braku zapasu RAISE(ROLLBACK) automatycznie wycofuje cala operacje.
-- Obiekty TEMP istnieja tylko na tym polaczeniu; model biznesowy ma 5 tabel.

PRAGMA foreign_keys = ON;
CREATE TEMP TABLE IF NOT EXISTS stock_update_check (affected_rows INTEGER);
CREATE TEMP TRIGGER IF NOT EXISTS stock_update_guard
BEFORE INSERT ON stock_update_check
WHEN NEW.affected_rows <> 1
BEGIN
    SELECT RAISE(ROLLBACK, 'Brak zapasu: UPDATE nie zmienil jednego wiersza');
END;

-- SCENARIO: success
-- Przed: orders=25, items=60, stock_1=30, stock_2=80.
SELECT
  (SELECT COUNT(*) FROM orders) AS orders_count,
  (SELECT COUNT(*) FROM order_items) AS items_count,
  (SELECT stock FROM products WHERE product_id = 1) AS stock_1,
  (SELECT stock FROM products WHERE product_id = 2) AS stock_2;
BEGIN IMMEDIATE;
INSERT INTO orders(order_id, customer_id, ordered_at, status)
VALUES (1001, 1, '2026-10-28 16:00:00', 'pending');
INSERT INTO order_items(order_id, product_id, quantity, unit_price)
SELECT 1001, product_id, 2, price FROM products WHERE product_id = 1;
UPDATE products SET stock = stock - 2 WHERE product_id = 1 AND stock >= 2;
INSERT INTO stock_update_check VALUES (changes());
INSERT INTO order_items(order_id, product_id, quantity, unit_price)
SELECT 1001, product_id, 1, price FROM products WHERE product_id = 2;
UPDATE products SET stock = stock - 1 WHERE product_id = 2 AND stock >= 1;
INSERT INTO stock_update_check VALUES (changes());
COMMIT;
SELECT
  (SELECT COUNT(*) FROM orders) AS orders_count,
  (SELECT COUNT(*) FROM order_items) AS items_count,
  (SELECT stock FROM products WHERE product_id = 1) AS stock_1,
  (SELECT stock FROM products WHERE product_id = 2) AS stock_2;
-- Wynik sprawdzony: orders=26, items=62, stock_1=28, stock_2=79.

-- SCENARIO: check_failure
SELECT
  (SELECT COUNT(*) FROM orders) AS orders_count,
  (SELECT COUNT(*) FROM order_items) AS items_count,
  (SELECT stock FROM products WHERE product_id = 1) AS stock_1,
  (SELECT stock FROM products WHERE product_id = 2) AS stock_2;
BEGIN IMMEDIATE;
INSERT INTO orders(order_id, customer_id, ordered_at, status)
VALUES (1002, 2, '2026-10-28 16:10:00', 'pending');
INSERT INTO order_items(order_id, product_id, quantity, unit_price)
SELECT 1002, product_id, 1, price FROM products WHERE product_id = 1;
UPDATE products SET stock = stock - 1 WHERE product_id = 1 AND stock >= 1;
INSERT INTO stock_update_check VALUES (changes());
-- Celowy blad CHECK(quantity > 0), po zapisie pozycji i zmianie magazynu.
INSERT INTO order_items(order_id, product_id, quantity, unit_price)
SELECT 1002, product_id, 0, price FROM products WHERE product_id = 2;
-- Po oczekiwanym bledzie wykonaj nastepne dwa polecenia:
ROLLBACK;
SELECT
  (SELECT COUNT(*) FROM orders) AS orders_count,
  (SELECT COUNT(*) FROM order_items) AS items_count,
  (SELECT stock FROM products WHERE product_id = 1) AS stock_1,
  (SELECT stock FROM products WHERE product_id = 2) AS stock_2;
-- Wynik sprawdzony: orders=26, items=62, stock_1=28, stock_2=79.
-- Brak zamowienia 1002 i jego pozycji; wszystkie wiersze pieciu tabel
-- sa identyczne jak przed BEGIN, nie tylko powyzsze cztery liczniki.

-- SCENARIO: insufficient_stock
SELECT
  (SELECT COUNT(*) FROM orders) AS orders_count,
  (SELECT COUNT(*) FROM order_items) AS items_count,
  (SELECT stock FROM products WHERE product_id = 1) AS stock_1,
  (SELECT stock FROM products WHERE product_id = 2) AS stock_2;
BEGIN IMMEDIATE;
INSERT INTO orders(order_id, customer_id, ordered_at, status)
VALUES (1003, 3, '2026-10-28 16:20:00', 'pending');
INSERT INTO order_items(order_id, product_id, quantity, unit_price)
SELECT 1003, product_id, 1000000, price FROM products WHERE product_id = 1;
UPDATE products SET stock = stock - 1000000
WHERE product_id = 1 AND stock >= 1000000;
-- UPDATE zmienia 0 wierszy. Ponizszy INSERT uruchamia automatyczny ROLLBACK.
INSERT INTO stock_update_check VALUES (changes());
-- Po oczekiwanym bledzie triggera wykonaj SELECT. Nie ma juz transakcji.
SELECT
  (SELECT COUNT(*) FROM orders) AS orders_count,
  (SELECT COUNT(*) FROM order_items) AS items_count,
  (SELECT stock FROM products WHERE product_id = 1) AS stock_1,
  (SELECT stock FROM products WHERE product_id = 2) AS stock_2;
-- Wynik sprawdzony: orders=26, items=62, stock_1=28, stock_2=79.
-- Brak zamowienia 1003 i pozycji; pelny stan zostal przywrocony.

-- Zamowienie, pozycje i zmiany stock musza nalezec do jednej transakcji:
-- czesciowy zapis moglby zostawic zamowienie bez pozycji lub zmniejszyc
-- magazyn mimo nieudanego zakupu. COMMIT wykonujemy dopiero po powodzeniu
-- wszystkich krokow; kazdy blad wymaga ROLLBACK.
