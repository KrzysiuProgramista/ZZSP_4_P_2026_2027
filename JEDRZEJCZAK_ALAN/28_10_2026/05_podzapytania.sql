-- Zadanie 5, slajdy 32-33. Wydatki = paid/shipped, brak zakupow = 0.
-- Srednia wydatkow obejmuje WSZYSTKICH 10 klientow, rowniez z zerem.
-- Progi w PLN: gold >= 3000, silver >= 1000 i < 3000, bronze < 1000.

-- Q5.1 Cena produktu wieksza od sredniej ceny wszystkich produktow.
SELECT product_id, name, price,
       ROUND((SELECT AVG(price) FROM products), 2) AS overall_avg_price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC, product_id;

-- Q5.2 Klienci powyzej srednich wydatkow (przed porownaniem nie zaokraglam).
WITH spend AS (
  SELECT c.customer_id, c.full_name,
         COALESCE(SUM(i.quantity * i.unit_price), 0) AS lifetime_spend
  FROM customers AS c
  LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id AND o.status IN ('paid', 'shipped')
  LEFT JOIN order_items AS i ON i.order_id = o.order_id
  GROUP BY c.customer_id, c.full_name
)
SELECT customer_id, full_name, ROUND(lifetime_spend, 2) AS lifetime_spend,
       ROUND((SELECT AVG(lifetime_spend) FROM spend), 2) AS avg_customer_spend
FROM spend
WHERE lifetime_spend > (SELECT AVG(lifetime_spend) FROM spend)
ORDER BY lifetime_spend DESC, customer_id;

-- Q5.3 Zamowienia zawierajace co najmniej jeden produkt z kategorii 1.
-- EXISTS zwraca kazde zamowienie tylko raz, nawet przy kilku dopasowaniach.
SELECT o.order_id, o.customer_id, o.ordered_at, o.status
FROM orders AS o
WHERE EXISTS (
  SELECT 1 FROM order_items AS i
  JOIN products AS p ON p.product_id = i.product_id
  WHERE i.order_id = o.order_id AND p.category_id = 1
)
ORDER BY o.order_id;

-- Q5.4 Dokladnie jeden segment dla kazdego klienta, takze z zerem.
WITH spend AS (
  SELECT c.customer_id, c.full_name,
         COALESCE(SUM(i.quantity * i.unit_price), 0) AS lifetime_spend
  FROM customers AS c
  LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id AND o.status IN ('paid', 'shipped')
  LEFT JOIN order_items AS i ON i.order_id = o.order_id
  GROUP BY c.customer_id, c.full_name
)
SELECT customer_id, full_name, ROUND(lifetime_spend, 2) AS lifetime_spend,
       CASE WHEN lifetime_spend >= 3000 THEN 'gold'
            WHEN lifetime_spend >= 1000 THEN 'silver'
            ELSE 'bronze' END AS customer_band
FROM spend
ORDER BY customer_id;

-- Q5.5 Liczba klientow w kazdym segmencie (rowniez gdy liczba wynosi 0).
WITH spend AS (
  SELECT c.customer_id, COALESCE(SUM(i.quantity * i.unit_price), 0) AS total
  FROM customers AS c
  LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id AND o.status IN ('paid', 'shipped')
  LEFT JOIN order_items AS i ON i.order_id = o.order_id
  GROUP BY c.customer_id
), segmented AS (
  SELECT customer_id, CASE WHEN total >= 3000 THEN 'gold'
                          WHEN total >= 1000 THEN 'silver'
                          ELSE 'bronze' END AS band
  FROM spend
), bands AS (
  SELECT 'gold' AS band, 1 AS sort_order
  UNION ALL SELECT 'silver', 2
  UNION ALL SELECT 'bronze', 3
)
SELECT b.band AS customer_band, COUNT(s.customer_id) AS customer_count
FROM bands AS b
LEFT JOIN segmented AS s ON s.band = b.band
GROUP BY b.band, b.sort_order
ORDER BY b.sort_order;
