-- queries.sql
PRAGMA foreign_keys = ON;

-- EXERCISE 2: podstawowe zapytania
-- 1. Produkty w kategorii nr 1, posortowane po cenie.
SELECT product_id, name, price
FROM products
WHERE category_id = 1
ORDER BY price ASC;

-- 2. Produkty w przedziale cenowym 20-150 (BETWEEN obejmuje oba końce).
SELECT product_id, name, price
FROM products
WHERE price BETWEEN 20 AND 150
ORDER BY price ASC;

-- 3. Klienci z adresem e-mail w domenie example.com.
SELECT customer_id, name, email
FROM customers
WHERE email LIKE '%@example.com'
ORDER BY name;

-- 4. Pięć najdroższych produktów.
SELECT product_id, name, price
FROM products
ORDER BY price DESC, product_id
LIMIT 5;

-- 5. Różne statusy wykorzystane w zamówieniach.
SELECT DISTINCT status
FROM orders
ORDER BY status;


-- EXERCISE 3: agregacje
-- 1. Liczba produktów w każdej kategorii.
SELECT c.category_id, c.name AS category_name, COUNT(p.product_id) AS product_count
FROM categories AS c
LEFT JOIN products AS p ON p.category_id = c.category_id
GROUP BY c.category_id, c.name
ORDER BY c.category_id;

-- 2. Średnia, minimalna i maksymalna cena w każdej kategorii.
SELECT c.category_id, c.name AS category_name,
       AVG(p.price) AS avg_price, MIN(p.price) AS min_price, MAX(p.price) AS max_price
FROM categories AS c
LEFT JOIN products AS p ON p.category_id = c.category_id
GROUP BY c.category_id, c.name
ORDER BY c.category_id;

-- 3. Kategorie mające więcej niż 3 produkty.
SELECT category_id, COUNT(*) AS product_count
FROM products
GROUP BY category_id
HAVING COUNT(*) > 3;

-- 4. Wartość każdego zamówienia = suma ilość * cena_z_chwili_zakupu.
SELECT o.order_id,
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS order_value
FROM orders AS o
LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
GROUP BY o.order_id
ORDER BY o.order_id;


-- EXERCISE 4: JOIN
-- 1. Każde zamówienie wraz z imieniem/nazwiskiem klienta.
SELECT o.order_id, o.order_date, o.status, c.name AS customer_name
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
ORDER BY o.order_id;

-- 2. Każda pozycja zamówienia wraz z nazwą produktu i wartością pozycji.
SELECT oi.order_id, oi.order_item_id, p.name AS product_name,
       oi.quantity, oi.unit_price,
       oi.quantity * oi.unit_price AS line_total
FROM order_items AS oi
JOIN products AS p ON p.product_id = oi.product_id
ORDER BY oi.order_id, oi.order_item_id;

-- 3. Każdy produkt wraz z nazwą kategorii.
SELECT p.product_id, p.name AS product_name, c.name AS category_name
FROM products AS p
JOIN categories AS c ON c.category_id = p.category_id
ORDER BY p.product_id;

-- 4. Przychód na klienta (tylko zamówienia nieanulowane).
SELECT c.customer_id, c.name AS customer_name,
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
FROM customers AS c
LEFT JOIN orders AS o
       ON o.customer_id = c.customer_id AND o.status <> 'cancelled'
LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
GROUP BY c.customer_id, c.name
ORDER BY revenue DESC, c.customer_id;

-- 5. Przychód na kategorię (tylko zamówienia nieanulowane).
WITH valid_order_items AS (
    SELECT oi.product_id, oi.quantity, oi.unit_price
    FROM order_items AS oi
    JOIN orders AS o ON o.order_id = oi.order_id
    WHERE o.status <> 'cancelled'
)
SELECT cat.category_id, cat.name AS category_name,
       COALESCE(SUM(voi.quantity * voi.unit_price), 0) AS revenue
FROM categories AS cat
LEFT JOIN products AS p ON p.category_id = cat.category_id
LEFT JOIN valid_order_items AS voi ON voi.product_id = p.product_id
GROUP BY cat.category_id, cat.name
ORDER BY revenue DESC, cat.category_id;


-- EXERCISE 4: brakujące relacje
-- 6. Klienci, którzy nigdy nie złożyli zamówienia.
SELECT c.customer_id, c.name
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL;

-- 7. Produkty, których nigdy nie zamówiono.
SELECT p.product_id, p.name
FROM products AS p
LEFT JOIN order_items AS oi ON oi.product_id = p.product_id
WHERE oi.order_item_id IS NULL;


-- EXERCISE 5: podzapytania i EXISTS
-- 1. Produkty droższe niż średnia cena wszystkich produktów.
SELECT product_id, name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;

-- 2. Klienci wydający więcej niż średnia wartość wydatków na klienta.
-- Przyjęte założenie: anulowane zamówienia nie liczą się, klienci bez zakupów mają 0.
WITH customer_spend AS (
    SELECT c.customer_id, c.name,
           COALESCE(SUM(CASE WHEN o.status <> 'cancelled'
                             THEN oi.quantity * oi.unit_price ELSE 0 END), 0) AS lifetime_spend
    FROM customers AS c
    LEFT JOIN orders AS o ON o.customer_id = c.customer_id
    LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id, c.name
)
SELECT customer_id, name, lifetime_spend
FROM customer_spend
WHERE lifetime_spend > (SELECT AVG(lifetime_spend) FROM customer_spend)
ORDER BY lifetime_spend DESC;

-- 3. Zamówienia zawierające co najmniej jeden produkt z kategorii nr 1.
SELECT o.order_id, o.order_date
FROM orders AS o
WHERE EXISTS (
    SELECT 1
    FROM order_items AS oi
    JOIN products AS p ON p.product_id = oi.product_id
    WHERE oi.order_id = o.order_id AND p.category_id = 1
)
ORDER BY o.order_id;


-- EXERCISE 5: CASE i segmentacja klientów
-- Progi przykładowe (jawna decyzja biznesowa): gold >= 1000, silver >= 300, reszta bronze.
WITH customer_spend AS (
    SELECT c.customer_id, c.name,
           COALESCE(SUM(CASE WHEN o.status <> 'cancelled'
                             THEN oi.quantity * oi.unit_price ELSE 0 END), 0) AS lifetime_spend
    FROM customers AS c
    LEFT JOIN orders AS o ON o.customer_id = c.customer_id
    LEFT JOIN order_items AS oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id, c.name
),
segmented AS (
    SELECT customer_id, name, lifetime_spend,
           CASE
             WHEN lifetime_spend >= 1000 THEN 'gold'
             WHEN lifetime_spend >= 300 THEN 'silver'
             ELSE 'bronze'
           END AS customer_band
    FROM customer_spend
)
SELECT customer_band, COUNT(*) AS customer_count
FROM segmented
GROUP BY customer_band
ORDER BY CASE customer_band WHEN 'gold' THEN 1 WHEN 'silver' THEN 2 ELSE 3 END;


-- EXERCISE 6: funkcje okna
-- 1. Ranking produktów w kategorii według ceny (RANK pozwala na remisy).
SELECT product_id, name, category_id, price,
       RANK() OVER (PARTITION BY category_id ORDER BY price DESC) AS price_rank
FROM products
ORDER BY category_id, price_rank, product_id;

-- 5. Dwa najlepsze/cenowo najdroższe produkty z każdej kategorii.
WITH ranked_products AS (
    SELECT product_id, name, category_id, price,
           ROW_NUMBER() OVER (
               PARTITION BY category_id
               ORDER BY price DESC, product_id
           ) AS rn
    FROM products
)
SELECT product_id, name, category_id, price, rn
FROM ranked_products
WHERE rn <= 2
ORDER BY category_id, rn;


-- EXERCISE 6: analiza zamówień w czasie
-- 2. Wartość zamówienia obok średniej wartości zamówień danego klienta.
WITH order_values AS (
    SELECT o.order_id, o.customer_id, o.order_date,
           SUM(oi.quantity * oi.unit_price) AS order_value
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status <> 'cancelled'
    GROUP BY o.order_id, o.customer_id, o.order_date
)
SELECT order_id, customer_id, order_date, order_value,
       AVG(order_value) OVER (PARTITION BY customer_id) AS customer_avg_order_value
FROM order_values
ORDER BY customer_id, order_date, order_id;

-- 3. Poprzednia wartość zamówienia tego samego klienta.
WITH order_values AS (
    SELECT o.order_id, o.customer_id, o.order_date,
           SUM(oi.quantity * oi.unit_price) AS order_value
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status <> 'cancelled'
    GROUP BY o.order_id, o.customer_id, o.order_date
)
SELECT order_id, customer_id, order_date, order_value,
       LAG(order_value) OVER (
           PARTITION BY customer_id ORDER BY order_date, order_id
       ) AS previous_order_value
FROM order_values
ORDER BY customer_id, order_date, order_id;

-- 4. Narastający przychód według dni; najpierw agregujemy do jednego wiersza na dzień.
WITH daily_revenue AS (
    SELECT o.order_date,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE o.status <> 'cancelled'
    GROUP BY o.order_date
)
SELECT order_date, revenue,
       SUM(revenue) OVER (ORDER BY order_date) AS running_revenue
FROM daily_revenue
ORDER BY order_date;
