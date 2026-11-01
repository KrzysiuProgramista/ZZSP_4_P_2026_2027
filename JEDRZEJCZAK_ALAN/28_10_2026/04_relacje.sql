-- Zadanie 4, slajdy 30-31.
-- Przychod = quantity * unit_price dla statusow paid oraz shipped.
-- Pending i cancelled nie daja przychodu. Klienci/kategorie bez niego = 0.

-- Q4.1 Jeden wiersz na zamowienie z nazwa klienta.
SELECT o.order_id, c.full_name, o.ordered_at, o.status
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
ORDER BY o.order_id;

-- Q4.2 Jeden wiersz na pozycje zamowienia.
SELECT i.order_id, i.product_id, p.name AS product_name,
       i.quantity, i.unit_price,
       ROUND(i.quantity * i.unit_price, 2) AS line_total
FROM order_items AS i
JOIN products AS p ON p.product_id = i.product_id
ORDER BY i.order_id, i.product_id;

-- Q4.3 Jeden wiersz na produkt z nazwa kategorii.
SELECT p.product_id, p.name AS product_name, c.name AS category_name, p.price
FROM products AS p
JOIN categories AS c ON c.category_id = p.category_id
ORDER BY p.product_id;

-- Q4.4 Przychod na klienta. Filtr statusu w ON zachowuje klientow z zerem.
SELECT c.customer_id, c.full_name,
       ROUND(COALESCE(SUM(i.quantity * i.unit_price), 0), 2) AS revenue
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id AND o.status IN ('paid', 'shipped')
LEFT JOIN order_items AS i ON i.order_id = o.order_id
GROUP BY c.customer_id, c.full_name
ORDER BY revenue DESC, c.customer_id;

-- Q4.5 Przychod na kategorie; kazda pozycja liczona raz.
SELECT c.category_id, c.name AS category_name,
       ROUND(COALESCE(SUM(CASE WHEN o.status IN ('paid', 'shipped')
                              THEN i.quantity * i.unit_price ELSE 0 END), 0), 2)
           AS revenue
FROM categories AS c
LEFT JOIN products AS p ON p.category_id = c.category_id
LEFT JOIN order_items AS i ON i.product_id = p.product_id
LEFT JOIN orders AS o ON o.order_id = i.order_id
GROUP BY c.category_id, c.name
ORDER BY revenue DESC, c.category_id;

-- Q4.6 Nigdy nie zlozyli zamowienia (niezaleznie od statusu).
SELECT c.customer_id, c.full_name, c.email
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL
ORDER BY c.customer_id;

-- Q4.7 Nigdy nie wystapily w zadnej pozycji zamowienia.
SELECT p.product_id, p.code, p.name
FROM products AS p
LEFT JOIN order_items AS i ON i.product_id = p.product_id
WHERE i.order_id IS NULL
ORDER BY p.product_id;

-- INNER JOIN zachowuje tylko pasujace pary, wiec usunalby wlasnie
-- klientow bez zamowien i produkty bez pozycji, ktorych szukamy.
-- LEFT JOIN zachowuje lewy wiersz i wypelnia prawa strone wartosciami NULL.
