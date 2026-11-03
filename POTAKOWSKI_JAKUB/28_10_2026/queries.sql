-- Slajdy 27-35. Kwoty raportowane w PLN, baza przechowuje grosze.
-- Obrot = paid lub sent. new i cancelled nie tworza przychodu.
-- 2. Filtrowanie; BETWEEN obejmuje oba konce. LIMIT zwraca dokladnie 5
-- produktow, rowne ceny rozstrzyga kod produktu.
SELECT product_code,name,price_cents/100.0 AS cena_pln FROM products WHERE category_id=2 ORDER BY price_cents,product_code;
SELECT name,price_cents/100.0 AS cena_pln FROM products WHERE price_cents BETWEEN 2500 AND 9900 ORDER BY price_cents,name;
SELECT name,email FROM customers WHERE email LIKE '%@sport.test' ORDER BY name;
SELECT product_code,name,price_cents/100.0 AS cena_pln FROM products ORDER BY price_cents DESC,product_code LIMIT 5;
SELECT DISTINCT status FROM orders ORDER BY status;
-- 3. Oddzielnie liczebnosc oraz statystyki kategorii.
SELECT c.name,COUNT(p.product_id) AS liczba_produktow FROM categories c LEFT JOIN products p ON p.category_id=c.category_id GROUP BY c.category_id ORDER BY c.category_id;
SELECT c.name,AVG(p.price_cents)/100.0 AS srednia_pln,MIN(p.price_cents)/100.0 AS minimum_pln,MAX(p.price_cents)/100.0 AS maksimum_pln FROM categories c LEFT JOIN products p ON p.category_id=c.category_id GROUP BY c.category_id;
SELECT category_id,COUNT(*) AS liczba FROM products GROUP BY category_id HAVING COUNT(*)>3;
SELECT o.order_id,COALESCE(t.suma,0)/100.0 AS wartosc_pln FROM orders o LEFT JOIN (SELECT order_id,SUM(quantity*unit_price_cents) AS suma FROM order_items GROUP BY order_id) t ON t.order_id=o.order_id ORDER BY o.order_id;
-- WHERE odrzuca konkretne produkty przed liczeniem. HAVING ocenia wynik
-- calej grupy. Tutaj liczebnosc dotyczy tylko produktow drozszych niz 10 PLN.
SELECT category_id,COUNT(*) AS liczba,AVG(price_cents)/100.0 AS srednia_pln FROM products WHERE price_cents>1000 GROUP BY category_id HAVING COUNT(*)>3;
-- 4. Ziarno: zamowienie / pozycja / produkt / klient / kategoria.
SELECT o.order_id,c.name AS klient,o.order_date,o.status FROM customers c JOIN orders o ON o.customer_id=c.customer_id ORDER BY o.order_id;
SELECT i.order_id,p.name,i.quantity,i.unit_price_cents/100.0 AS cena_zakupu_pln,(i.quantity*i.unit_price_cents)/100.0 AS wartosc_pozycji_pln FROM products p JOIN order_items i ON i.product_id=p.product_id ORDER BY i.order_id,p.product_id;
SELECT p.product_code,p.name,c.name AS kategoria FROM categories c JOIN products p ON p.category_id=c.category_id ORDER BY p.product_id;
WITH paid_totals AS (SELECT o.customer_id,SUM(i.quantity*i.unit_price_cents) AS cents FROM orders o JOIN order_items i ON i.order_id=o.order_id WHERE o.status IN ('paid','sent') GROUP BY o.customer_id)
SELECT c.customer_id,c.name,COALESCE(t.cents,0)/100.0 AS przychod_pln FROM customers c LEFT JOIN paid_totals t ON t.customer_id=c.customer_id ORDER BY c.customer_id;
WITH sales AS (SELECT p.category_id,SUM(i.quantity*i.unit_price_cents) AS cents FROM products p JOIN order_items i ON i.product_id=p.product_id JOIN orders o ON o.order_id=i.order_id WHERE o.status IN ('paid','sent') GROUP BY p.category_id)
SELECT c.name,COALESCE(s.cents,0)/100.0 AS przychod_pln FROM categories c LEFT JOIN sales s ON s.category_id=c.category_id ORDER BY c.category_id;
-- INNER JOIN usuwa rekordy bez dopasowania. Nie moglby pokazac brakujacych
-- relacji. LEFT JOIN zachowuje lewa strone i daje NULL po prawej.
SELECT c.customer_id,c.name FROM customers c LEFT JOIN orders o ON o.customer_id=c.customer_id WHERE o.order_id IS NULL ORDER BY c.customer_id;
SELECT p.product_id,p.name FROM products p LEFT JOIN order_items i ON i.product_id=p.product_id WHERE i.order_id IS NULL ORDER BY p.product_id;
-- 5. Podzapytania: srednia cen i wydatki wszystkich 10 klientow (brak = 0).
SELECT name,price_cents/100.0 AS cena_pln FROM products WHERE price_cents>(SELECT AVG(price_cents) FROM products);
WITH customer_spend AS (SELECT c.customer_id,c.name,COALESCE((SELECT SUM(i.quantity*i.unit_price_cents) FROM orders o JOIN order_items i ON i.order_id=o.order_id WHERE o.customer_id=c.customer_id AND o.status IN ('paid','sent')),0) AS cents FROM customers c)
SELECT name,cents/100.0 AS wydatki_pln FROM customer_spend WHERE cents>(SELECT AVG(cents) FROM customer_spend);
-- EXISTS sprawdza obecnosc, dlatego nie powiela zamowien.
SELECT o.order_id FROM orders o WHERE EXISTS(SELECT 1 FROM order_items i JOIN products p ON p.product_id=i.product_id WHERE i.order_id=o.order_id AND p.category_id=2) ORDER BY o.order_id;
-- Wlasne progi: gold od 2000 PLN, silver od 750 PLN, pozostali bronze.
-- Jawna lista pasm pozwala pokazac takze segment z zerem klientow.
WITH spending AS (SELECT c.customer_id,COALESCE(SUM(i.quantity*i.unit_price_cents) FILTER(WHERE o.status IN ('paid','sent')),0) AS cents FROM customers c LEFT JOIN orders o ON o.customer_id=c.customer_id LEFT JOIN order_items i ON i.order_id=o.order_id GROUP BY c.customer_id),
segments AS (SELECT customer_id,CASE WHEN cents>=200000 THEN 'gold' WHEN cents>=75000 THEN 'silver' ELSE 'bronze' END AS band FROM spending),
bands(band,position) AS (VALUES('gold',1),('silver',2),('bronze',3))
SELECT b.band,COUNT(s.customer_id) AS klienci FROM bands b LEFT JOIN segments s ON s.band=b.band GROUP BY b.band,b.position ORDER BY b.position;
-- 6. RANK zachowuje wspolna pozycje przy remisie ceny.
SELECT category_id,name,price_cents/100.0 AS cena_pln,RANK() OVER(PARTITION BY category_id ORDER BY price_cents DESC) AS miejsce FROM products ORDER BY category_id,miejsce,name;
WITH positions AS (SELECT product_id,category_id,name,price_cents,ROW_NUMBER() OVER(PARTITION BY category_id ORDER BY price_cents DESC,product_code) AS position FROM products)
SELECT category_id,name,price_cents/100.0 AS cena_pln FROM positions WHERE position<=2 ORDER BY category_id,position;
-- Zamowienia wszystkich statusow. Data + ID daje stabilna kolejnosc.
WITH order_values AS (SELECT o.order_id,o.customer_id,o.order_date,COALESCE(SUM(i.quantity*i.unit_price_cents),0) AS cents FROM orders o LEFT JOIN order_items i ON i.order_id=o.order_id GROUP BY o.order_id)
SELECT order_id,customer_id,order_date,cents/100.0 AS wartosc_pln,AVG(cents) OVER customer_window/100.0 AS srednia_klienta_pln,LAG(cents) OVER history_window/100.0 AS poprzednia_wartosc_pln FROM order_values
WINDOW customer_window AS (PARTITION BY customer_id),history_window AS (PARTITION BY customer_id ORDER BY order_date,order_id)
ORDER BY customer_id,order_date,order_id;
-- Najpierw jedna suma na dzien, potem suma narastajaca.
WITH daily AS (SELECT o.order_date,SUM(i.quantity*i.unit_price_cents) AS cents FROM orders o JOIN order_items i ON i.order_id=o.order_id WHERE o.status IN ('paid','sent') GROUP BY o.order_date)
SELECT order_date,cents/100.0 AS dzien_pln,SUM(cents) OVER(ORDER BY order_date ROWS UNBOUNDED PRECEDING)/100.0 AS narastajaco_pln FROM daily ORDER BY order_date;
