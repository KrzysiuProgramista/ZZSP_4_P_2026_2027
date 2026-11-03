-- WSZYSTKIE ZAPYTANIA Z EXERCISE 2 - 8 (SLAJDY 27-39)

-- Exercise 2: Zapytania filtrujące
SELECT product_id, name, price, category_id FROM products WHERE category_id = 1 ORDER BY price ASC;
SELECT product_id, name, price FROM products WHERE price BETWEEN 20.00 AND 100.00 ORDER BY price ASC;
SELECT customer_id, name, email FROM customers WHERE email LIKE '%@example.com';
SELECT product_id, name, price FROM products ORDER BY price DESC LIMIT 5;
SELECT DISTINCT status FROM orders;

-- Exercise 3: Agregacja
SELECT category_id, COUNT(*) AS product_count FROM products GROUP BY category_id;
SELECT c.name AS category_name, COUNT(p.product_id) AS product_count, ROUND(AVG(p.price), 2) AS avg_price, MIN(p.price) AS min_price, MAX(p.price) AS max_price FROM categories c LEFT JOIN products p ON c.category_id = p.category_id GROUP BY c.category_id, c.name;
SELECT c.name AS category_name, COUNT(p.product_id) AS product_count, ROUND(AVG(p.price), 2) AS avg_price FROM categories c JOIN products p ON c.category_id = p.category_id GROUP BY c.category_id, c.name HAVING COUNT(p.product_id) > 3;
SELECT order_id, ROUND(SUM(quantity * unit_price), 2) AS order_total_value FROM order_items GROUP BY order_id;

-- Exercise 4: JOIN
SELECT o.order_id, o.order_date, o.status, c.name AS customer_name FROM orders o JOIN customers c ON o.customer_id = c.customer_id;
SELECT oi.order_id, p.name AS product_name, oi.quantity, oi.unit_price, ROUND(oi.quantity * oi.unit_price, 2) AS line_total FROM order_items oi JOIN products p ON oi.product_id = p.product_id;
SELECT p.product_id, p.name AS product_name, c.name AS category_name, p.price FROM products p JOIN categories c ON p.category_id = c.category_id;
SELECT c.customer_id, c.name AS customer_name, ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 2) AS total_revenue FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id LEFT JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_id, c.name ORDER BY total_revenue DESC;
SELECT c.category_id, c.name AS category_name, ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 2) AS category_revenue FROM categories c LEFT JOIN products p ON c.category_id = p.category_id LEFT JOIN order_items oi ON p.product_id = oi.product_id GROUP BY c.category_id, c.name ORDER BY category_revenue DESC;
SELECT c.customer_id, c.name, c.email FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id WHERE o.order_id IS NULL;
SELECT p.product_id, p.product_code, p.name FROM products p LEFT JOIN order_items oi ON p.product_id = oi.product_id WHERE oi.order_id IS NULL;

-- Exercise 5: Subqueries & CASE
SELECT name, price FROM products WHERE price > (SELECT AVG(price) FROM products) ORDER BY price DESC;
WITH customer_spends AS (
    SELECT c.customer_id, c.name, COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_spend
    FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.name
)
SELECT customer_id, name, ROUND(total_spend, 2) AS total_spend FROM customer_spends WHERE total_spend > (SELECT AVG(total_spend) FROM customer_spends);

SELECT o.order_id, o.customer_id, o.order_date FROM orders o
WHERE EXISTS (
    SELECT 1 FROM order_items oi JOIN products p ON oi.product_id = p.product_id WHERE oi.order_id = o.order_id AND p.category_id = 1
);

WITH customer_lifetime_spend AS (
    SELECT c.customer_id, c.name, COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS lifetime_spend
    FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.name
),
customer_bands AS (
    SELECT customer_id, name, lifetime_spend,
           CASE 
               WHEN lifetime_spend >= 1000 THEN 'Gold'
               WHEN lifetime_spend >= 400  THEN 'Silver'
               ELSE 'Bronze'
           END AS customer_band
    FROM customer_lifetime_spend
)
SELECT customer_band, COUNT(*) AS customer_count, ROUND(AVG(lifetime_spend), 2) AS avg_band_spend FROM customer_bands GROUP BY customer_band ORDER BY avg_band_spend DESC;

-- Exercise 6: Window Functions
SELECT product_id, name, category_id, price, ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY price DESC, product_id ASC) AS price_rank FROM products;

WITH ranked_products AS (
    SELECT product_id, name, category_id, price, ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY price DESC, product_id ASC) AS rn FROM products
)
SELECT category_id, product_id, name, price FROM ranked_products WHERE rn <= 2;

WITH order_totals AS (
    SELECT o.order_id, o.customer_id, o.order_date, SUM(oi.quantity * oi.unit_price) AS order_value
    FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_id, o.customer_id, o.order_date
)
SELECT order_id, customer_id, order_date, ROUND(order_value, 2) AS order_value, ROUND(AVG(order_value) OVER (PARTITION BY customer_id), 2) AS avg_customer_order_value FROM order_totals;

WITH order_totals AS (
    SELECT o.order_id, o.customer_id, o.order_date, SUM(oi.quantity * oi.unit_price) AS order_value
    FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_id, o.customer_id, o.order_date
)
SELECT order_id, customer_id, order_date, ROUND(order_value, 2) AS current_order_value, ROUND(LAG(order_value) OVER (PARTITION BY customer_id ORDER BY order_date, order_id), 2) AS previous_order_value FROM order_totals;

WITH daily_revenue AS (
    SELECT o.order_date, SUM(oi.quantity * oi.unit_price) AS day_revenue
    FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY o.order_date
)
SELECT order_date, ROUND(day_revenue, 2) AS daily_revenue, ROUND(SUM(day_revenue) OVER (ORDER BY order_date), 2) AS running_total_revenue FROM daily_revenue;
