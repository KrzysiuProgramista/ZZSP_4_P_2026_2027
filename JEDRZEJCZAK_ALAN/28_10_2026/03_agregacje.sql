-- Zadanie 3, slajdy 28-29. Jeden wiersz na kategorie albo zamowienie.

-- Q3.1 Liczba produktow; COUNT(p.product_id) uwzglednia puste kategorie jako 0.
SELECT c.category_id, c.name AS category_name,
       COUNT(p.product_id) AS product_count
FROM categories AS c
LEFT JOIN products AS p ON p.category_id = c.category_id
GROUP BY c.category_id, c.name
ORDER BY c.category_id;

-- Q3.2 Srednia, minimum i maksimum ceny. Pusta kategoria ma NULL,
-- poniewaz srednia cena w pustym zbiorze nie jest rowna zero.
SELECT c.category_id, c.name AS category_name,
       ROUND(AVG(p.price), 2) AS avg_price,
       MIN(p.price) AS min_price, MAX(p.price) AS max_price
FROM categories AS c
LEFT JOIN products AS p ON p.category_id = c.category_id
GROUP BY c.category_id, c.name
ORDER BY c.category_id;

-- Q3.3 HAVING wybiera kategorie majace wiecej niz trzy produkty.
SELECT c.category_id, c.name AS category_name,
       COUNT(p.product_id) AS product_count
FROM categories AS c
JOIN products AS p ON p.category_id = c.category_id
GROUP BY c.category_id, c.name
HAVING COUNT(p.product_id) > 3
ORDER BY c.category_id;

-- Q3.4 Wartosc kazdego zamowienia (wszystkie statusy), pustego = 0.
-- Uzywam historycznego unit_price, a nie obecnej ceny products.price.
SELECT o.order_id, o.status,
       ROUND(COALESCE(SUM(i.quantity * i.unit_price), 0), 2) AS order_total
FROM orders AS o
LEFT JOIN order_items AS i ON i.order_id = o.order_id
GROUP BY o.order_id, o.status
ORDER BY o.order_id;

-- Q3.5 WHERE odrzuca pojedyncze produkty przed liczeniem sredniej.
SELECT c.category_id, c.name AS category_name,
       COUNT(*) AS product_count, ROUND(AVG(p.price), 2) AS avg_price
FROM categories AS c
JOIN products AS p ON p.category_id = c.category_id
WHERE p.price > 10
GROUP BY c.category_id, c.name
ORDER BY c.category_id;

-- WHERE filtruje wiersze wejsciowe przed GROUP BY, np. cena > 10.
-- HAVING filtruje gotowe grupy po agregacji, np. COUNT(*) > 3.
-- W danych wszystkie ceny sa > 10, dlatego Q3.5 obejmuje wszystkie
-- produkty. Test brzegowy dodatkowo sprawdza odrzucenie ceny rownej 10.
