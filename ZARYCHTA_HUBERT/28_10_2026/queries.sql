-- Exercises 2-6, slides 27-35. Prices/spend are in PLN.
-- Historical order value includes all statuses. Revenue/spend includes only paid
-- and shipped orders. Customers without qualifying orders have zero spend.
-- BETWEEN includes both endpoints. product_id resolves price ties.
-- 2.1
SELECT product_id,name,price FROM products WHERE category_id=1 ORDER BY price,product_id;
-- 2.2
SELECT product_id,name,price FROM products WHERE price BETWEEN 10 AND 100 ORDER BY price,product_id;
-- 2.3
SELECT customer_id,name,email FROM customers WHERE email LIKE '%@example.com' ORDER BY customer_id;
-- 2.4
SELECT product_id,name,price FROM products ORDER BY price DESC,product_id LIMIT 5;
-- 2.5
SELECT DISTINCT status FROM orders ORDER BY status;
-- 3.1-2: LEFT JOIN also retains empty categories.
SELECT c.category_id,c.name,COUNT(p.product_id) AS product_count,
 AVG(p.price) AS average_price,MIN(p.price) AS minimum_price,MAX(p.price) AS maximum_price
FROM categories c LEFT JOIN products p USING(category_id) GROUP BY c.category_id,c.name;
-- 3.3
SELECT category_id,COUNT(*) AS product_count FROM products GROUP BY category_id HAVING COUNT(*)>3;
-- 3.4
SELECT o.order_id,COALESCE(SUM(i.quantity*i.unit_price),0) AS order_value
FROM orders o LEFT JOIN order_items i USING(order_id) GROUP BY o.order_id ORDER BY o.order_id;
-- WHERE selects individual rows before grouping; HAVING selects completed groups.
SELECT category_id,AVG(price) AS average_price FROM products
WHERE price>10 GROUP BY category_id HAVING COUNT(*)>3;
-- 4.1: one row per order.
SELECT o.order_id,o.order_date,o.status,c.name AS customer_name FROM orders o JOIN customers c USING(customer_id);
-- 4.2: one row per order line.
SELECT i.order_id,i.product_id,p.name,i.quantity,i.unit_price,i.quantity*i.unit_price AS line_total
FROM order_items i JOIN products p USING(product_id);
-- 4.3: one row per product.
SELECT p.product_id,p.name,c.name AS category_name FROM products p JOIN categories c USING(category_id);
-- 4.4: one row per customer, including zero revenue.
SELECT c.customer_id,c.name,COALESCE(SUM(CASE WHEN o.status IN ('paid','shipped')
 THEN i.quantity*i.unit_price ELSE 0 END),0) AS revenue
FROM customers c LEFT JOIN orders o USING(customer_id) LEFT JOIN order_items i USING(order_id)
GROUP BY c.customer_id,c.name;
-- 4.5: one row per category.
SELECT c.category_id,c.name,COALESCE(SUM(CASE WHEN o.status IN ('paid','shipped')
 THEN i.quantity*i.unit_price ELSE 0 END),0) AS revenue
FROM categories c LEFT JOIN products p USING(category_id) LEFT JOIN order_items i USING(product_id)
LEFT JOIN orders o USING(order_id) GROUP BY c.category_id,c.name;
-- 4.6-7: INNER JOIN would discard unmatched rows before the NULL test.
SELECT c.customer_id,c.name FROM customers c LEFT JOIN orders o USING(customer_id) WHERE o.order_id IS NULL;
SELECT p.product_id,p.name FROM products p LEFT JOIN order_items i USING(product_id) WHERE i.order_id IS NULL;
-- 5.1
SELECT product_id,name,price FROM products WHERE price>(SELECT AVG(price) FROM products);
-- 5.2: average across ALL customers, including zero spend.
WITH spend AS (
 SELECT c.customer_id,c.name,COALESCE(SUM(CASE WHEN o.status IN ('paid','shipped')
 THEN i.quantity*i.unit_price ELSE 0 END),0) AS lifetime_spend
 FROM customers c LEFT JOIN orders o USING(customer_id) LEFT JOIN order_items i USING(order_id)
 GROUP BY c.customer_id,c.name)
SELECT * FROM spend WHERE lifetime_spend>(SELECT AVG(lifetime_spend) FROM spend);
-- 5.3: EXISTS returns each order once, even with several matching products.
SELECT o.order_id,o.order_date FROM orders o WHERE EXISTS (
 SELECT 1 FROM order_items i JOIN products p USING(product_id)
 WHERE i.order_id=o.order_id AND p.category_id=1);
-- 5.4: chosen thresholds: gold >=1000 PLN, silver >=300 PLN, bronze <300 PLN.
WITH spend AS (
 SELECT c.customer_id,COALESCE(SUM(CASE WHEN o.status IN ('paid','shipped')
 THEN i.quantity*i.unit_price ELSE 0 END),0) AS lifetime_spend
 FROM customers c LEFT JOIN orders o USING(customer_id) LEFT JOIN order_items i USING(order_id)
 GROUP BY c.customer_id), bands AS (
 SELECT customer_id,CASE WHEN lifetime_spend>=1000 THEN 'gold'
 WHEN lifetime_spend>=300 THEN 'silver' ELSE 'bronze' END AS customer_band FROM spend)
SELECT customer_band,COUNT(*) AS customer_count FROM bands GROUP BY customer_band;
-- 6.1: tied prices share a rank.
SELECT product_id,name,category_id,price,RANK() OVER(PARTITION BY category_id ORDER BY price DESC) AS price_rank FROM products;
-- 6.5: at most two products per category, deterministic on ties.
WITH ranked AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY category_id ORDER BY price DESC,product_id) AS rn FROM products)
SELECT product_id,name,category_id,price,rn FROM ranked WHERE rn<=2 ORDER BY category_id,rn;
-- 6.2-3: order values include every status; ties in dates use order_id.
WITH totals AS (SELECT o.order_id,o.customer_id,o.order_date,COALESCE(SUM(i.quantity*i.unit_price),0) AS order_value
 FROM orders o LEFT JOIN order_items i USING(order_id) GROUP BY o.order_id,o.customer_id,o.order_date)
SELECT *,AVG(order_value) OVER(PARTITION BY customer_id) AS customer_average_order_value,
 LAG(order_value) OVER(PARTITION BY customer_id ORDER BY order_date,order_id) AS previous_order_value
FROM totals ORDER BY customer_id,order_date,order_id;
-- 6.4: aggregate qualifying revenue to daily grain before the running sum.
WITH daily AS (SELECT o.order_date,SUM(i.quantity*i.unit_price) AS daily_revenue
 FROM orders o JOIN order_items i USING(order_id) WHERE o.status IN ('paid','shipped') GROUP BY o.order_date)
SELECT order_date,daily_revenue,SUM(daily_revenue) OVER(ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_revenue
FROM daily ORDER BY order_date;
