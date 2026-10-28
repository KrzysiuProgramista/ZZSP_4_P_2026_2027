"""Smoke tests for schema.sql. Run: python validate_schema.py."""
import sqlite3
from pathlib import Path

schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.executescript(schema)

def must_fail(label, sql, params=()):
    try:
        db.execute(sql, params)
    except sqlite3.IntegrityError:
        print(f"PASS: rejected {label}")
    else:
        raise AssertionError(f"Expected IntegrityError for: {label}")

# Valid customer, category, product, order and item.
db.execute("INSERT INTO customers(email, full_name) VALUES (?, ?)",
           ("alex@example.com", "Alex Example"))
db.execute("INSERT INTO categories(name) VALUES (?)", ("Books",))
db.execute("""INSERT INTO products(category_id, product_code, name, price)
              VALUES (1, 'BK-001', 'Example Book', 12.50)""")
db.execute("INSERT INTO orders(customer_id, status) VALUES (1, 'pending')")
db.execute("""INSERT INTO order_items(order_id, product_id, quantity, unit_price)
              VALUES (1, 1, 2, 12.50)""")
print("PASS: valid customer, product, order and order item inserted")

must_fail("duplicate email",
          "INSERT INTO customers(email, full_name) VALUES (?, ?)",
          ("ALEX@example.com", "Duplicate Email"))
must_fail("non-positive product price",
          """INSERT INTO products(product_code, name, price)
             VALUES ('BAD-PRICE', 'Invalid Product', 0)""")
must_fail("non-positive item quantity",
          """INSERT INTO order_items(order_id, product_id, quantity, unit_price)
             VALUES (1, 1, 0, 12.50)""")
must_fail("unknown customer_id",
          "INSERT INTO orders(customer_id) VALUES (99999)")
must_fail("invalid order status",
          "INSERT INTO orders(customer_id, status) VALUES (1, 'in-transit')")
must_fail("duplicate product code",
          """INSERT INTO products(product_code, name, price)
             VALUES ('BK-001', 'Duplicate Code', 8.00)""")
must_fail("deleting customer with an order",
          "DELETE FROM customers WHERE customer_id = 1")

indexes = {row[0] for row in db.execute(
    "SELECT name FROM sqlite_master WHERE type = 'index'")}
expected = {"idx_orders_customer_id", "idx_order_items_product_id",
            "idx_orders_status_ordered_at"}
assert expected <= indexes, f"Missing indexes: {expected - indexes}"
print("PASS: all three documented indexes exist")
print("All schema validation tests passed.")
