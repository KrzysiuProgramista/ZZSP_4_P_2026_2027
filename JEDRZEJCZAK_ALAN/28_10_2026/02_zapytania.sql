-- Zadanie 2, slajdy 26-27. Dane: ../dane.sql.
-- Parametry przykladow: kategoria 1 (Elektronika), ceny 49 i 249 PLN,
-- domena example.com. Zmieniaj literalne wartosci, zachowujac strukture SQL.

-- Q2.1 Produkty jednej kategorii, od najtanszego.
SELECT product_id, code, name, price
FROM products
WHERE category_id = 1
ORDER BY price ASC, product_id ASC;

-- Q2.2 BETWEEN obejmuje oba konce przedzialu: 49 i 249.
SELECT product_id, name, price
FROM products
WHERE price BETWEEN 49 AND 249
ORDER BY price, product_id;

-- Q2.3 Znak @ zapobiega dopasowaniu np. notexample.com.
SELECT customer_id, full_name, email
FROM customers
WHERE email LIKE '%@example.com'
ORDER BY customer_id;

-- Q2.4 Dokladnie piec produktow. Remisy rozstrzyga product_id.
-- LIMIT 5 moze pominac czesc produktow z cena rowna cenie piatego.
SELECT product_id, name, price
FROM products
ORDER BY price DESC, product_id ASC
LIMIT 5;

-- Q2.5 Tylko statusy faktycznie wystepujace w danych.
SELECT DISTINCT status FROM orders ORDER BY status;
