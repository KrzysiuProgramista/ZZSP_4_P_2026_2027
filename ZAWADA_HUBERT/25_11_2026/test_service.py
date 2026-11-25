from pathlib import Path
import sqlite3
import unittest

import service

SCHEMA_PATH = Path(__file__).resolve().parent / "database" / "schema.sql"


class TestWorkshopService(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        # Seed baseline data for an isolated test state
        self.conn.execute(
            """
            INSERT INTO customers (id, first_name, last_name, phone, email)
            VALUES (1, 'Anna', 'Kowalska', '+48123456789', 'anna@example.com')
            """
        )
        self.conn.execute(
            """
            INSERT INTO vehicles (id, customer_id, brand, model, year, registration_no, vin)
            VALUES (1, 1, 'Toyota', 'Corolla', 2020, 'KR12345', 'JTDBR32E123456789')
            """
        )
        self.conn.execute(
            """
            INSERT INTO mechanics (id, first_name, last_name, specialization, active)
            VALUES
                (1, 'Jan', 'Nowak', 'Engine & Brakes', 1),
                (2, 'Piotr', 'Wisniewski', 'Diagnostics', 0)
            """
        )
        self.conn.execute(
            """
            INSERT INTO services (id, name, base_price)
            VALUES
                (1, 'Oil Change', 150.0),
                (2, 'Brake Inspection', 100.0)
            """
        )
        self.conn.commit()

    def tearDown(self) -> None:
        self.conn.close()

    def test_1_create_valid_order_receives_new_id(self) -> None:
        order_id_1 = service.create_order(
            self.conn,
            vehicle_id=1,
            mechanic_id=1,
            description="Regular oil and filter replacement",
        )
        order_id_2 = service.create_order(
            self.conn,
            vehicle_id=1,
            mechanic_id=1,
            description="Follow-up brake inspection",
        )

        self.assertIsInstance(order_id_1, int)
        self.assertGreater(order_id_1, 0)
        self.assertGreater(order_id_2, order_id_1)

        row = self.conn.execute(
            "SELECT * FROM service_orders WHERE id = ?",
            (order_id_1,),
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["vehicle_id"], 1)
        self.assertEqual(row["mechanic_id"], 1)
        self.assertEqual(row["status"], "received")
        self.assertIsNotNone(row["received_at"])
        self.assertIsNone(row["completed_at"])
        self.assertEqual(row["description"], "Regular oil and filter replacement")

    def test_2_create_order_nonexistent_vehicle_fails(self) -> None:
        orders_before = self.conn.execute("SELECT * FROM service_orders").fetchall()

        with self.assertRaises(LookupError):
            service.create_order(
                self.conn,
                vehicle_id=999,
                mechanic_id=1,
                description="Diagnostic check",
            )

        orders_after = self.conn.execute("SELECT * FROM service_orders").fetchall()
        self.assertEqual([dict(r) for r in orders_after], [dict(r) for r in orders_before])

    def test_3_create_order_inactive_mechanic_fails(self) -> None:
        orders_before = self.conn.execute("SELECT * FROM service_orders").fetchall()

        with self.assertRaises(ValueError):
            service.create_order(
                self.conn,
                vehicle_id=1,
                mechanic_id=2,  # active = 0
                description="Wheel alignment",
            )

        orders_after = self.conn.execute("SELECT * FROM service_orders").fetchall()
        self.assertEqual([dict(r) for r in orders_after], [dict(r) for r in orders_before])

    def test_4_add_service_to_completed_order_fails_and_leaves_db_unchanged(self) -> None:
        order_id = service.create_order(
            self.conn,
            vehicle_id=1,
            mechanic_id=1,
            description="Oil change",
        )
        service.add_service_to_order(
            self.conn,
            order_id=order_id,
            service_id=1,
            hours_worked=1.0,
            final_price=150.0,
        )
        service.complete_order(self.conn, order_id=order_id)

        order_before = dict(
            self.conn.execute(
                "SELECT * FROM service_orders WHERE id = ?", (order_id,)
            ).fetchone()
        )
        lines_before = [
            dict(r)
            for r in self.conn.execute(
                "SELECT * FROM order_services WHERE order_id = ? ORDER BY service_id",
                (order_id,),
            ).fetchall()
        ]

        with self.assertRaises(ValueError):
            service.add_service_to_order(
                self.conn,
                order_id=order_id,
                service_id=2,
                hours_worked=0.5,
                final_price=100.0,
            )

        order_after = dict(
            self.conn.execute(
                "SELECT * FROM service_orders WHERE id = ?", (order_id,)
            ).fetchone()
        )
        lines_after = [
            dict(r)
            for r in self.conn.execute(
                "SELECT * FROM order_services WHERE order_id = ? ORDER BY service_id",
                (order_id,),
            ).fetchall()
        ]

        self.assertEqual(order_after, order_before)
        self.assertEqual(order_after["status"], "completed")
        self.assertEqual(lines_after, lines_before)

    def test_5_complete_order_with_no_service_lines_fails_and_leaves_db_unchanged(self) -> None:
        order_id = service.create_order(
            self.conn,
            vehicle_id=1,
            mechanic_id=1,
            description="Inspection requested",
        )

        order_before = dict(
            self.conn.execute(
                "SELECT * FROM service_orders WHERE id = ?", (order_id,)
            ).fetchone()
        )
        line_count_before = self.conn.execute(
            "SELECT COUNT(*) FROM order_services WHERE order_id = ?", (order_id,)
        ).fetchone()[0]

        with self.assertRaises(ValueError):
            service.complete_order(self.conn, order_id=order_id)

        order_after = dict(
            self.conn.execute(
                "SELECT * FROM service_orders WHERE id = ?", (order_id,)
            ).fetchone()
        )
        line_count_after = self.conn.execute(
            "SELECT COUNT(*) FROM order_services WHERE order_id = ?", (order_id,)
        ).fetchone()[0]

        self.assertEqual(order_after, order_before)
        self.assertEqual(order_after["status"], "received")
        self.assertIsNone(order_after["completed_at"])
        self.assertEqual(line_count_after, line_count_before)
        self.assertEqual(line_count_after, 0)

    def test_6_add_duplicate_service_to_order_fails_and_leaves_db_unchanged(self) -> None:
        order_id = service.create_order(
            self.conn,
            vehicle_id=1,
            mechanic_id=1,
            description="Oil change",
        )
        service.add_service_to_order(
            self.conn,
            order_id=order_id,
            service_id=1,
            hours_worked=1.0,
            final_price=150.0,
        )

        order_before = dict(
            self.conn.execute(
                "SELECT * FROM service_orders WHERE id = ?", (order_id,)
            ).fetchone()
        )
        lines_before = [
            dict(r)
            for r in self.conn.execute(
                "SELECT * FROM order_services WHERE order_id = ?", (order_id,)
            ).fetchall()
        ]

        with self.assertRaises(ValueError):
            service.add_service_to_order(
                self.conn,
                order_id=order_id,
                service_id=1,
                hours_worked=2.0,
                final_price=300.0,
            )

        order_after = dict(
            self.conn.execute(
                "SELECT * FROM service_orders WHERE id = ?", (order_id,)
            ).fetchone()
        )
        lines_after = [
            dict(r)
            for r in self.conn.execute(
                "SELECT * FROM order_services WHERE order_id = ?", (order_id,)
            ).fetchall()
        ]

        self.assertEqual(order_after, order_before)
        self.assertEqual(order_after["status"], "in_progress")
        self.assertEqual(lines_after, lines_before)


if __name__ == "__main__":
    unittest.main()