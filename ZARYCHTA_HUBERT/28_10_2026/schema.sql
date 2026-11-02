PRAGMA foreign_keys = ON;
-- categories 1:N products; customers 1:N orders; orders 1:N order_items;
-- products 1:N order_items. Purchase prices belong to order_items.
CREATE TABLE categories(category_id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE customers(customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE);
CREATE TABLE products(product_id INTEGER PRIMARY KEY, product_code TEXT NOT NULL UNIQUE,
 name TEXT NOT NULL, category_id INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
 price NUMERIC NOT NULL CHECK(price>0), stock INTEGER NOT NULL CHECK(stock>=0));
CREATE TABLE orders(order_id INTEGER PRIMARY KEY,
 customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
 order_date TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','paid','shipped','cancelled')));
CREATE TABLE order_items(order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
 product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
 quantity INTEGER NOT NULL CHECK(quantity>0), unit_price NUMERIC NOT NULL CHECK(unit_price>0),
 PRIMARY KEY(order_id,product_id));
-- Customer order histories and date-ordered window queries.
CREATE INDEX idx_orders_customer_date ON orders(customer_id,order_date,order_id);
-- Category filters and price ordering.
CREATE INDEX idx_products_category_price ON products(category_id,price);
-- Reverse product-to-order lookups; the composite PK starts with order_id.
CREATE INDEX idx_items_product ON order_items(product_id);
-- Customer deletion is restricted to preserve order history.
