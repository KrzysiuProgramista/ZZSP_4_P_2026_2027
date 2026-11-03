PRAGMA foreign_keys=ON;
-- Model: categories -> products -> order_items <- orders <- customers.
-- Kwoty przechowujemy w groszach, co pozwala uniknac bledow float.
CREATE TABLE categories(category_id INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE);
CREATE TABLE customers(customer_id INTEGER PRIMARY KEY,name TEXT NOT NULL,
 email TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK(instr(email,'@')>1));
CREATE TABLE products(product_id INTEGER PRIMARY KEY,product_code TEXT NOT NULL UNIQUE,
 name TEXT NOT NULL,category_id INTEGER NOT NULL REFERENCES categories ON DELETE RESTRICT,
 price_cents INTEGER NOT NULL CHECK(typeof(price_cents)='integer' AND price_cents>0),
 stock INTEGER NOT NULL CHECK(typeof(stock)='integer' AND stock>=0));
CREATE TABLE orders(order_id INTEGER PRIMARY KEY,customer_id INTEGER NOT NULL REFERENCES customers ON DELETE RESTRICT,
 order_date TEXT NOT NULL CHECK(date(order_date) IS NOT NULL AND date(order_date)=order_date),
 status TEXT NOT NULL CHECK(status IN ('new','paid','sent','cancelled')));
CREATE TABLE order_items(order_id INTEGER NOT NULL REFERENCES orders ON DELETE CASCADE,
 product_id INTEGER NOT NULL REFERENCES products ON DELETE RESTRICT,
 quantity INTEGER NOT NULL CHECK(typeof(quantity)='integer' AND quantity>0),
 unit_price_cents INTEGER NOT NULL CHECK(typeof(unit_price_cents)='integer' AND unit_price_cents>0),
 PRIMARY KEY(order_id,product_id));
-- Indeks przyspiesza filtrowanie asortymentu kategorii i sortowanie ceny.
CREATE INDEX ix_catalog ON products(category_id,price_cents,product_id);
-- Indeks ulatwia historie klienta i kolejnosc jego zamowien.
CREATE INDEX ix_history ON orders(customer_id,order_date,order_id);
-- PK pozycji zaczyna sie od order_id, potrzebny jest osobny dostep od produktu.
CREATE INDEX ix_product_sales ON order_items(product_id,order_id);
-- RESTRICT chroni historie klientow i produktow. CASCADE usuwa pozycje
-- tylko razem z naglowkiem zamowienia. Cena w pozycji jest historyczna.
