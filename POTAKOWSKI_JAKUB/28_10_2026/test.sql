PRAGMA foreign_keys = ON;

INSERT INTO customers (customer_id, name, email)
VALUES (1, 'Jan Kowalski', 'jan@example.com');

INSERT INTO categories (category_id, name)
VALUES (1, 'Electronics');

INSERT INTO products (
    product_id, category_id, name, product_code, price
)
VALUES (1, 1, 'Keyboard', 'KB-001', 149.99);

INSERT INTO orders (order_id, customer_id, status)
VALUES (1, 1, 'pending');

INSERT INTO order_items (
    order_id, product_id, quantity, unit_price
)
VALUES (1, 1, 2, 149.99);

INSERT INTO customers (customer_id, name, email)
VALUES (2, 'Anna Nowak', 'jan@example.com');

INSERT INTO products (
    product_id, category_id, name, product_code, price
)
VALUES (2, 1, 'Invalid Product', 'BAD-001', 0);

INSERT INTO orders (order_id, customer_id, status)
VALUES (2, 999, 'pending');

INSERT INTO orders (order_id, customer_id, status)
VALUES (3, 1, 'processing');

INSERT INTO order_items (
    order_id, product_id, quantity, unit_price
)
VALUES (1, 1, 0, 149.99);

SELECT * FROM customers;
SELECT * FROM products;
SELECT * FROM orders;
SELECT * FROM order_items;
