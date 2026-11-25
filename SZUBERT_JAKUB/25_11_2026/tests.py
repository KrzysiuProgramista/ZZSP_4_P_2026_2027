import sqlite3
import unittest

import service


class TestService(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        service.init_db(self.conn, "database/schema.sql")
        with open("seed.sql", "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())

    def tearDown(self) -> None:
        self.conn.close()

    def test_1_valid_order_created_and_receives_new_id(self) -> None:
        new_id = service.create_order(
            self.conn,
            vehicle_id=1,
            mechanic_id=1,
            description="Diagnostics and oil check",
        )
        self.assertEqual(new_id, 21)

        row = self.conn.execute(
            "SELECT vehicle_id, mechanic_id, status, completed_at, description FROM service_orders WHERE id = ?;",
            (new_id,),
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["vehicle_id"], 1)
        self.assertEqual(row["mechanic_id"], 1)
        self.assertEqual(row["status"], "received")
        self.assertIsNone(row["completed_at"])
        self.assertEqual(row["description"], "Diagnostics and oil check")

    def test_2_create_order_nonexistent_vehicle_fails_and_db_unchanged(self) -> None:
        before_count = self.conn.execute("SELECT COUNT() AS cnt FROM service_orders;").fetchone()["cnt"]

        with self.assertRaises(LookupError):
            service.create_order(
                self.conn,
                vehicle_id=999,
                mechanic_id=1,
                description="Unknown vehicle",
            )

        after_count = self.conn.execute("SELECT COUNT() AS cnt FROM service_orders;").fetchone()["cnt"]
        self.assertEqual(before_count, after_count)

    def test_3_create_order_inactive_mechanic_fails(self) -> None:
        with self.assertRaises(service.ConflictError):
            service.create_order(
                self.conn,
                vehicle_id=1,
                mechanic_id=5,
                description="Inactive mechanic test",
            )

    def test_4_add_service_to_completed_order_fails_and_state_unchanged(self) -> None:
        before_order = self.conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = 1;"
        ).fetchone()
        before_lines = self.conn.execute(
            "SELECT COUNT() AS cnt FROM order_services WHERE order_id = 1;"
        ).fetchone()["cnt"]

        with self.assertRaises(service.ConflictError):
            service.add_service_to_order(
                self.conn,
                order_id=1,
                service_id=4,
                hours_worked=1.0,
                final_price=180.0,
            )

        after_order = self.conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = 1;"
        ).fetchone()
        after_lines = self.conn.execute(
            "SELECT COUNT() AS cnt FROM order_services WHERE order_id = 1;"
        ).fetchone()["cnt"]

        self.assertEqual(before_order["status"], "completed")
        self.assertEqual(after_order["status"], "completed")
        self.assertEqual(before_order["completed_at"], after_order["completed_at"])
        self.assertEqual(before_lines, after_lines)

    def test_5_complete_order_with_no_service_lines_fails(self) -> None:
        order_id = service.create_order(
            self.conn,
            vehicle_id=12,
            mechanic_id=4,
            description="Empty order test",
        )

        with self.assertRaises(service.ConflictError):
            service.complete_order(self.conn, order_id=order_id)

        row = self.conn.execute(
            "SELECT status, completed_at FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()