import sqlite3
import unittest
from pathlib import Path

import service
from service import ConflictError, NotFoundError

SCHEMA_PATH = Path(__file__).parent / "database" / "schema.sql"


class TestServiceLayer(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        self.conn.executescript(schema_sql)

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO customers (id, first_name, last_name, phone, email)
                VALUES (1, 'Jan', 'Kowalski', '+48 500 100 200', 'jan@example.com');
                """
            )
            self.conn.execute(
                """
                INSERT INTO vehicles (id, customer_id, brand, model, year, registration_no, vin)
                VALUES (1, 1, 'Toyota', 'Corolla', 2020, 'EL 12345', 'JTDEPRAE0LJ100001');
                """
            )
            self.conn.execute(
                """
                INSERT INTO mechanics (id, first_name, last_name, specialization, active)
                VALUES
                    (1, 'Adam', 'Mazur', 'General mechanics', 1),
                    (2, 'Robert', 'Krol', 'Engine repairs', 0);
                """
            )
            self.conn.execute(
                """
                INSERT INTO services (id, name, base_price)
                VALUES
                    (1, 'Oil change', 280.00),
                    (2, 'Brake pads replacement', 620.00);
                """
            )

    def tearDown(self) -> None:
        self.conn.close()

    def test_create_valid_order_receives_new_id(self) -> None:
        order_id = service.create_order(
            self.conn,
            vehicle_id=1,
            mechanic_id=1,
            description="Routine oil service",
        )

        self.assertIsInstance(order_id, int)
        self.assertGreater(order_id, 0)

        row = self.conn.execute(
            "SELECT vehicle_id, mechanic_id, status, completed_at, description FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], 1)
        self.assertEqual(row[2], "received")
        self.assertIsNone(row[3])
        self.assertEqual(row[4], "Routine oil service")

    def test_create_order_for_non_existent_vehicle_fails_and_leaves_db_unchanged(self) -> None:
        count_before = self.conn.execute("SELECT COUNT(*) FROM service_orders;").fetchone()[0]

        with self.assertRaises(NotFoundError):
            service.create_order(
                self.conn,
                vehicle_id=999,
                mechanic_id=1,
                description="Should fail",
            )

        count_after = self.conn.execute("SELECT COUNT(*) FROM service_orders;").fetchone()[0]
        self.assertEqual(count_before, count_after)

    def test_create_order_with_inactive_mechanic_fails_and_leaves_db_unchanged(self) -> None:
        count_before = self.conn.execute("SELECT COUNT(*) FROM service_orders;").fetchone()[0]

        with self.assertRaises(ConflictError):
            service.create_order(
                self.conn,
                vehicle_id=1,
                mechanic_id=2,
                description="Inactive mechanic test",
            )

        count_after = self.conn.execute("SELECT COUNT(*) FROM service_orders;").fetchone()[0]
        self.assertEqual(count_before, count_after)

    def test_add_service_to_completed_order_fails_and_leaves_db_unchanged(self) -> None:
        order_id = service.create_order(self.conn, 1, 1, "Brake inspection")
        service.add_service_to_order(self.conn, order_id, service_id=1, hours_worked=1.0, final_price=300.0)
        service.complete_order(self.conn, order_id)

        order_before = self.conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        lines_before = self.conn.execute(
            "SELECT service_id, hours_worked, final_price FROM order_services WHERE order_id = ?;",
            (order_id,),
        ).fetchall()

        with self.assertRaises(ConflictError):
            service.add_service_to_order(
                self.conn,
                order_id,
                service_id=2,
                hours_worked=2.0,
                final_price=600.0,
            )

        order_after = self.conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        lines_after = self.conn.execute(
            "SELECT service_id, hours_worked, final_price FROM order_services WHERE order_id = ?;",
            (order_id,),
        ).fetchall()

        self.assertEqual(order_before, order_after)
        self.assertEqual(lines_before, lines_after)

    def test_complete_order_with_no_service_lines_fails_and_leaves_db_unchanged(self) -> None:
        order_id = service.create_order(self.conn, 1, 1, "Empty order")
        before = self.conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()

        with self.assertRaises(ConflictError):
            service.complete_order(self.conn, order_id)

        after = self.conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        self.assertEqual(before, after)
        self.assertEqual(after[0], "received")
        self.assertIsNone(after[1])

    def test_add_service_updates_status_and_complete_sets_completed_at(self) -> None:
        order_id = service.create_order(self.conn, 1, 1, "Full service")
        service.add_service_to_order(self.conn, order_id, service_id=1, hours_worked=1.5, final_price=320.0)

        status_after_add = self.conn.execute(
            "SELECT status FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()[0]
        self.assertEqual(status_after_add, "in_progress")

        service.complete_order(self.conn, order_id)
        row_after_complete = self.conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        self.assertEqual(row_after_complete[0], "completed")
        self.assertIsNotNone(row_after_complete[1])

    def test_adding_duplicate_service_to_order_fails(self) -> None:
        order_id = service.create_order(self.conn, 1, 1, "Duplicate check")
        service.add_service_to_order(self.conn, order_id, service_id=1, hours_worked=1.0, final_price=280.0)

        with self.assertRaises(ConflictError):
            service.add_service_to_order(self.conn, order_id, service_id=1, hours_worked=0.5, final_price=100.0)

if __name__ == "__main__":
    unittest.main()