-- transactions.sql
-- Przykład bezpiecznego złożenia zamówienia dla jednego produktu.
-- W aplikacji wartości oznaczone :parametr przekazuje się jako parametry zapytania.
-- Użyj BEGIN IMMEDIATE, aby rozpocząć transakcję zapisu.

PRAGMA foreign_keys = ON;

-- Wariant demonstracyjny: tworzymy zamówienie i jedną pozycję.
BEGIN IMMEDIATE;

INSERT INTO orders(customer_id, status, order_date)
VALUES (1, 'pending', date('now'));

-- Ostatnio utworzone ID zamówienia w tym połączeniu:
-- w aplikacji pobierz cursor.lastrowid; w prostym skrypcie SQLite można użyć last_insert_rowid().
INSERT INTO order_items(order_id, product_id, quantity, unit_price)
SELECT last_insert_rowid(), product_id, 2, price
FROM products
WHERE product_id = 1;

-- Zmniejsz stan tylko wtedy, gdy jest wystarczający.
UPDATE products
SET stock = stock - 2
WHERE product_id = 1 AND stock >= 2;

-- WAŻNE: aplikacja musi sprawdzić, że UPDATE zmienił dokładnie 1 wiersz.
-- Jeśli zmieniono 0 wierszy, należy wykonać ROLLBACK, a nie COMMIT.
-- Jeśli wszystkie operacje się powiodły:
COMMIT;

-- EXERCISE 7: test ROLLBACK — wykonuj osobno po przywróceniu danych testowych.
-- Zapisz stan początkowy:
SELECT COUNT(*) AS orders_before FROM orders;
SELECT stock AS stock_before FROM products WHERE product_id = 1;

BEGIN;
INSERT INTO orders(customer_id, status, order_date)
VALUES (1, 'pending', date('now'));

-- Celowo błędna pozycja: quantity = 0 narusza CHECK(quantity > 0).
-- Oczekiwany błąd CHECK. Po błędzie wykonaj poniższe ROLLBACK ręcznie.
INSERT INTO order_items(order_id, product_id, quantity, unit_price)
VALUES (last_insert_rowid(), 1, 0, 19.99);

ROLLBACK;

-- Po ROLLBACK liczba zamówień i stock powinny wrócić do wartości sprzed BEGIN.
SELECT COUNT(*) AS orders_after FROM orders;
SELECT stock AS stock_after FROM products WHERE product_id = 1;

-- Uwaga: jeśli klient SQL zatrzyma wykonywanie skryptu po błędzie,
-- uruchom ROLLBACK jako osobne polecenie w tej samej sesji.
