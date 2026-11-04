import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.executescript(
    """
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    price REAL NOT NULL CHECK(price > 0),
    category_id INTEGER NOT NULL,
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED')),
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price > 0),
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
"""
)

for i in range(1, 7):
    cursor.execute(
        "INSERT INTO categories (name) VALUES (?)", (f"Category {i}",)
    )

for i in range(1, 11):
    cursor.execute(
        "INSERT INTO customers (email, name) VALUES (?, ?)",
        (f"user{i}@example.com", f"Customer {i}"),
    )

for i in range(1, 21):
    cursor.execute(
        "INSERT INTO products (product_code, name, price, category_id) VALUES (?, ?, ?, ?)",
        (f"P{i:03d}", f"Product {i}", i * 10.0, (i % 6) + 1),
    )

statuses = ["PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"]
for i in range(1, 26):
    cursor.execute(
        "INSERT INTO orders (customer_id, status) VALUES (?, ?)",
        ((i % 10) + 1, statuses[i % 5]),
    )

for i in range(1, 61):
    cursor.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        ((i % 25) + 1, (i % 20) + 1, (i % 3) + 1, 15.0),
    )

queries = [
    "SELECT name, price FROM products WHERE category_id = 1 ORDER BY price;",
    "SELECT name, price FROM products WHERE price BETWEEN 20.0 AND 100.0;",
    "SELECT email FROM customers WHERE email LIKE '%@example.com';",
    "SELECT name, price FROM products ORDER BY price DESC LIMIT 5;",
    "SELECT DISTINCT status FROM orders;",
]

for q in queries:
    cursor.execute(q)
    print(cursor.fetchall())

conn.close()