-- Zadanie 6, slajdy 34-35.
-- ordered_at to nazwa pola daty w naszym schemacie (na slajdzie: order_date).

-- Q6.1 RANK: rowne ceny maja wspolna pozycje, nastepna ma luke.
SELECT p.product_id, c.name AS category_name, p.name, p.price,
       RANK() OVER (PARTITION BY p.category_id ORDER BY p.price DESC) AS price_rank
FROM products AS p
JOIN categories AS c ON c.category_id = p.category_id
ORDER BY p.category_id, price_rank, p.product_id;

-- Q6.2 Kazde zamowienie i srednia wartosc zamowienia tego klienta.
-- Najpierw agregacja pozycji do jednego wiersza na zamowienie. Wszystkie statusy.
WITH totals AS (
  SELECT o.order_id, o.customer_id, o.ordered_at,
         COALESCE(SUM(i.quantity * i.unit_price), 0) AS total
  FROM orders AS o
  LEFT JOIN order_items AS i ON i.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.ordered_at
)
SELECT order_id, customer_id, ROUND(total, 2) AS order_total,
       ROUND(AVG(total) OVER (PARTITION BY customer_id), 2) AS customer_avg_order
FROM totals
ORDER BY customer_id, ordered_at, order_id;

-- Q6.3 Poprzednia wartosc u tego samego klienta. Pierwsza = NULL.
-- order_id rozstrzyga identyczne daty i czasy w sposob deterministyczny.
WITH totals AS (
  SELECT o.order_id, o.customer_id, o.ordered_at,
         COALESCE(SUM(i.quantity * i.unit_price), 0) AS total
  FROM orders AS o
  LEFT JOIN order_items AS i ON i.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.ordered_at
)
SELECT order_id, customer_id, ordered_at, ROUND(total, 2) AS order_total,
       ROUND(LAG(total) OVER (
           PARTITION BY customer_id ORDER BY ordered_at, order_id), 2) AS previous_total
FROM totals
ORDER BY customer_id, ordered_at, order_id;

-- Q6.4 Przychod dzienny i narastajacy (paid/shipped).
-- Najpierw jeden wiersz na dzien, potem jawna rama ROWS.
-- Wynik zawiera dni z uznanym przychodem, bez dopisywania kalendarza.
WITH daily AS (
  SELECT date(o.ordered_at) AS revenue_date,
         SUM(i.quantity * i.unit_price) AS daily_revenue
  FROM orders AS o
  JOIN order_items AS i ON i.order_id = o.order_id
  WHERE o.status IN ('paid', 'shipped')
  GROUP BY date(o.ordered_at)
)
SELECT revenue_date, ROUND(daily_revenue, 2) AS daily_revenue,
       ROUND(SUM(daily_revenue) OVER (
           ORDER BY revenue_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ), 2) AS running_revenue
FROM daily
ORDER BY revenue_date;

-- Q6.5 Dokladnie do dwoch produktow na kategorie, takze przy remisach.
WITH ranked AS (
  SELECT p.product_id, p.category_id, c.name AS category_name, p.name, p.price,
         ROW_NUMBER() OVER (
             PARTITION BY p.category_id ORDER BY p.price DESC, p.product_id
         ) AS rn
  FROM products AS p
  JOIN categories AS c ON c.category_id = p.category_id
)
SELECT product_id, category_name, name, price, rn
FROM ranked WHERE rn <= 2
ORDER BY category_id, rn;
