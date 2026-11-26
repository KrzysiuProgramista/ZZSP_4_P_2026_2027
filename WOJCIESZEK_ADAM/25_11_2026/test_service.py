from pathlib import Path
import sqlite3
import unittest

from service import (
    ConflictError,
    NotFoundError,
    add_service_to_order,
    complete_order,
    create_order,
    get_order_details,
)

SCHEMA_PATH = Path(__file__).resolve().parent / "database" / "schema.sql"


def build_test_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)

    conn.execute(
        """
        INSERT INTO customers (id, first_name, last_name, phone, email)
        VALUES (1, 'Jan', 'Kowalski', '+48 600 000 001', 'jan@example.com');
        """
    )
    conn.execute(
        """
        INSERT INTO vehicles (id, customer_id, brand, model, year, registration_no, vin)
        VALUES (1, 1, 'Toyota', 'Corolla', 2020, 'EL 12345', 'VIN12345678900001');
        """
    )
    conn.execute(
        """
        INSERT INTO mechanics (id, first_name, last_name, specialization, active)
        VALUES
            (1, 'Adam', 'Nowak', 'General', 1),
            (2, 'Piotr', 'Zieliński', 'Brakes', 0);
        """
    )
    conn.execute(
        """
        INSERT INTO services (id, name, base_price)
        VALUES
            (1, 'Oil change', 250.0),
            (2, 'Brake inspection', 150.0);
        """
    )
    conn.commit()
    return conn


class TestServiceLayer(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = build_test_db()

    def tearDown(self) -> None:
        self.conn.close()

    def test_create_order_succeeds_and_returns_new_id(self) -> None:
        order_id = create_order(self.conn, vehicle_id=1, mechanic_id=1, description="Oil leak check")
        self.assertIsInstance(order_id, int)
        self.assertGreater(order_id, 0)

        order = get_order_details(self.conn, order_id)
        self.assertEqual(order["status"], "received")
        self.assertIsNone(order["completed_at"])
        self.assertEqual(order["description"], "Oil leak check")

    def test_create_order_non_existent_vehicle_fails_and_leaves_db_unchanged(self) -> None:
        before_count = self.conn.execute("SELECT COUNT(*) FROM service_orders;").fetchone()[0]

        with self.assertRaises(NotFoundError):
            create_order(self.conn, vehicle_id=999, mechanic_id=1, description="Missing car")

        after_count = self.conn.execute("SELECT COUNT(*) FROM service_orders;").fetchone()[0]
        self.assertEqual(before_count, after_count)

    def test_create_order_inactive_mechanic_fails(self) -> None:
        with self.assertRaises(ConflictError):
            create_order(self.conn, vehicle_id=1, mechanic_id=2, description="Inactive mechanic order")

    def test_add_service_to_completed_order_fails_and_leaves_db_unchanged(self) -> None:
        order_id = create_order(self.conn, vehicle_id=1, mechanic_id=1, description="Brake service")
        add_service_to_order(self.conn, order_id=order_id, service_id=1, hours_worked=1.5, final_price=300.0)
        complete_order(self.conn, order_id=order_id)

        before_order = get_order_details(self.conn, order_id)
        before_lines_count = self.conn.execute(
            "SELECT COUNT(*) FROM order_services WHERE order_id = ?;", (order_id,)
        ).fetchone()[0]

        with self.assertRaises(ConflictError):
            add_service_to_order(
                self.conn, order_id=order_id, service_id=2, hours_worked=1.0, final_price=150.0
            )

        after_order = get_order_details(self.conn, order_id)
        after_lines_count = self.conn.execute(
            "SELECT COUNT(*) FROM order_services WHERE order_id = ?;", (order_id,)
        ).fetchone()[0]

        self.assertEqual(before_order["status"], "completed")
        self.assertEqual(after_order["status"], "completed")
        self.assertEqual(before_lines_count, after_lines_count)

    def test_complete_order_with_no_service_lines_fails(self) -> None:
        order_id = create_order(self.conn, vehicle_id=1, mechanic_id=1, description="Empty order")

        with self.assertRaises(ConflictError):
            complete_order(self.conn, order_id=order_id)

        order = get_order_details(self.conn, order_id)
        self.assertEqual(order["status"], "received")
        self.assertIsNone(order["completed_at"])


if __name__ == "__main__":
    unittest.main()