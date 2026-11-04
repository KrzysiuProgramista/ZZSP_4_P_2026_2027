import sqlite3
from contextlib import closing

DB_NAME = "shop.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price REAL NOT NULL CHECK (price > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    ordered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price > 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
"""


def connect():
    """Open the database and enable foreign-key enforcement."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialise_database():
    with closing(connect()) as conn:
        conn.executescript(SCHEMA)
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO customers(customer_id, name) VALUES (?, ?)",
                (1, "Alex Smith"),
            )
            conn.execute(
                "INSERT OR IGNORE INTO categories(category_id, name) VALUES (?, ?)",
                (1, "Electronics"),
            )
            conn.executemany(
                """INSERT OR IGNORE INTO products
                   (product_id, category_id, code, name, price, stock)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (1, 1, "KB-101", "Keyboard", 129.99, 10),
                    (2, 1, "MS-101", "Mouse", 59.50, 20),
                    (3, 1, "HD-200", "Headphones", 249.00, 5),
                ],
            )


def place_order(conn, customer_id, items):
    """Create an order atomically. items is [(product_id, quantity), ...]."""
    if not items:
        raise ValueError("The order must contain at least one product")

    # Reject invalid quantities and duplicate product IDs before writing.
    seen_product_ids = set()
    for product_id, quantity in items:
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        if product_id in seen_product_ids:
            raise ValueError("A product may appear only once in the order")
        seen_product_ids.add(product_id)

    with conn:
        customer = conn.execute(
            "SELECT customer_id FROM customers WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()
        if customer is None:
            raise ValueError("Customer not found")

        # The order header, order lines and stock changes share this transaction.
        cursor = conn.execute(
            "INSERT INTO orders(customer_id, status) VALUES (?, 'pending')",
            (customer_id,),
        )
        order_id = cursor.lastrowid

        for product_id, quantity in items:
            product = conn.execute(
                "SELECT price, stock FROM products WHERE product_id = ?",
                (product_id,),
            ).fetchone()
            if product is None:
                raise ValueError(f"Product {product_id} not found")

            if product["stock"] < quantity:
                raise ValueError(
                    f"Not enough stock for product {product_id}. "
                    f"Available: {product['stock']}, requested: {quantity}"
                )

            # The stock condition is checked again in the UPDATE itself.
            update = conn.execute(
                """UPDATE products
                   SET stock = stock - ?
                   WHERE product_id = ? AND stock >= ?""",
                (quantity, product_id, quantity),
            )
            if update.rowcount != 1:
                raise ValueError(f"Could not reserve stock for product {product_id}")

            conn.execute(
                """INSERT INTO order_items
                   (order_id, product_id, quantity, unit_price)
                   VALUES (?, ?, ?, ?)""",
                (order_id, product_id, quantity, product["price"]),
            )

    # Reached only after the transaction commits successfully.
    return order_id


def show_products(conn):
    print("\nPRODUCTS")
    for row in conn.execute(
        "SELECT product_id, name, price, stock FROM products ORDER BY product_id"
    ):
        print(
            f"ID: {row['product_id']} | {row['name']} | "
            f"Price: {row['price']:.2f} | Stock: {row['stock']}"
        )


def test_rollback(conn):
    """Force a failure after one valid item and prove all changes roll back."""
    print("\nROLLBACK TEST")
    before_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    before_stock = conn.execute(
        "SELECT stock FROM products WHERE product_id = 1"
    ).fetchone()[0]

    try:
        # Product 1 is valid; product 999 does not exist, so the transaction fails.
        place_order(conn, 1, [(1, 1), (999, 1)])
    except (ValueError, sqlite3.IntegrityError) as exc:
        print(f"Expected failure: {exc}")

    after_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    after_stock = conn.execute(
        "SELECT stock FROM products WHERE product_id = 1"
    ).fetchone()[0]

    print(f"Orders before: {before_orders}; after: {after_orders}")
    print(f"Product 1 stock before: {before_stock}; after: {after_stock}")
    assert before_orders == after_orders, "Rollback failed: order header remains"
    assert before_stock == after_stock, "Rollback failed: stock was changed"
    print("PASS: failed order left no order header and did not change stock.")


def main():
    initialise_database()

    with closing(connect()) as conn:
        fk_enabled = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        print(f"Foreign keys enabled: {fk_enabled}")
        show_products(conn)

        print("\nSUCCESSFUL ORDER TEST")
        try:
            order_id = place_order(conn, 1, [(1, 2), (2, 1)])
            print(f"Order placed successfully. Order ID: {order_id}")
        except (ValueError, sqlite3.IntegrityError) as exc:
            print(f"Order not placed: {exc}")

        show_products(conn)
        test_rollback(conn)

        print("\nORDERS IN DATABASE")
        for row in conn.execute(
            """SELECT o.order_id, c.name AS customer, o.status, o.ordered_at
               FROM orders AS o
               JOIN customers AS c ON c.customer_id = o.customer_id
               ORDER BY o.order_id"""
        ):
            print(dict(row))


if __name__ == "__main__":
    main()
