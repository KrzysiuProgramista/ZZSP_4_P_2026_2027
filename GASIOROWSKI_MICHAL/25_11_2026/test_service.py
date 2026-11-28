from pathlib import Path
import sqlite3
import unittest

from service import (
    ConflictError,
    NotFoundError,
    add_service_to_order,
    complete_order,
    create_order,
)


class ServiceOrderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db_conn = sqlite3.connect(":memory:")
        self.db_conn.row_factory = sqlite3.Row
        self.db_conn.execute("PRAGMA foreign_keys = ON;")

        schema_sql = Path("database/schema.sql").read_text(encoding="utf-8")
        self.db_conn.executescript(schema_sql)

        with self.db_conn:
            self.db_conn.execute(
                """
                INSERT INTO customers (id, first_name, last_name, phone, email)
                VALUES (1, 'Jan', 'Kowalski', '500600700', 'jan@example.com');
                """
            )
            self.db_conn.execute(
                """
                INSERT INTO vehicles (id, customer_id, brand, model, year, registration_no, vin)
                VALUES (1, 1, 'Toyota', 'Corolla', 2020, 'EL12345', 'VIN12345678901234');
                """
            )
            self.db_conn.execute(
                """
                INSERT INTO mechanics (id, first_name, last_name, specialization, active)
                VALUES
                    (1, 'Adam', 'Nowak', 'Engines', 1),
                    (2, 'Piotr', 'Zieliński', 'Brakes', 0);
                """
            )
            self.db_conn.execute(
                """
                INSERT INTO services (id, name, base_price)
                VALUES (1, 'Oil Change', 200.0);
                """
            )

    def tearDown(self) -> None:
        self.db_conn.close()

    def test_create_valid_order_returns_new_id(self) -> None:
        order_id = create_order(
            self.db_conn, vehicle_id=1, mechanic_id=1, description="Routine check"
        )

        self.assertIsInstance(order_id, int)
        self.assertGreater(order_id, 0)

        row = self.db_conn.execute(
            "SELECT id, status, completed_at, description FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["status"], "received")
        self.assertIsNone(row["completed_at"])
        self.assertEqual(row["description"], "Routine check")

    def test_create_order_non_existent_vehicle_fails_and_leaves_db_unchanged(self) -> None:
        before_count = self.db_conn.execute(
            "SELECT COUNT(*) AS cnt FROM service_orders;"
        ).fetchone()["cnt"]

        with self.assertRaises(NotFoundError):
            create_order(
                self.db_conn, vehicle_id=999, mechanic_id=1, description="Missing vehicle"
            )

        after_count = self.db_conn.execute(
            "SELECT COUNT(*) AS cnt FROM service_orders;"
        ).fetchone()["cnt"]
        self.assertEqual(after_count, before_count)

    def test_create_order_inactive_mechanic_fails_and_leaves_db_unchanged(self) -> None:
        before_count = self.db_conn.execute(
            "SELECT COUNT(*) AS cnt FROM service_orders;"
        ).fetchone()["cnt"]

        with self.assertRaises(ConflictError):
            create_order(
                self.db_conn, vehicle_id=1, mechanic_id=2, description="Inactive mechanic"
            )

        after_count = self.db_conn.execute(
            "SELECT COUNT(*) AS cnt FROM service_orders;"
        ).fetchone()["cnt"]
        self.assertEqual(after_count, before_count)

    def test_add_service_to_completed_order_fails_and_leaves_db_unchanged(self) -> None:
        order_id = create_order(
            self.db_conn, vehicle_id=1, mechanic_id=1, description="Oil replacement"
        )
        add_service_to_order(
            self.db_conn,
            order_id=order_id,
            service_id=1,
            hours_worked=1.0,
            final_price=200.0,
        )
        complete_order(self.db_conn, order_id=order_id)

        before_lines = self.db_conn.execute(
            "SELECT COUNT(*) AS cnt FROM order_services WHERE order_id = ?;",
            (order_id,),
        ).fetchone()["cnt"]
        before_order = self.db_conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()

        with self.assertRaises(ConflictError):
            add_service_to_order(
                self.db_conn,
                order_id=order_id,
                service_id=1,
                hours_worked=0.5,
                final_price=100.0,
            )

        after_lines = self.db_conn.execute(
            "SELECT COUNT(*) AS cnt FROM order_services WHERE order_id = ?;",
            (order_id,),
        ).fetchone()["cnt"]
        after_order = self.db_conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()

        self.assertEqual(after_lines, before_lines)
        self.assertEqual(after_order["status"], before_order["status"])
        self.assertEqual(after_order["completed_at"], before_order["completed_at"])

    def test_complete_order_with_no_service_lines_fails_and_leaves_db_unchanged(self) -> None:
        order_id = create_order(
            self.db_conn, vehicle_id=1, mechanic_id=1, description="Empty order"
        )

        before_order = self.db_conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()

        with self.assertRaises(ConflictError):
            complete_order(self.db_conn, order_id=order_id)

        after_order = self.db_conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()

        self.assertEqual(after_order["status"], before_order["status"])
        self.assertEqual(after_order["completed_at"], before_order["completed_at"])


if __name__ == "__main__":
    unittest.main()
