import sqlite3
import unittest
from pathlib import Path

from service import create_order, add_service_to_order, complete_order, get_order

SCHEMA = (Path(__file__).resolve().parent / 'database' / 'schema.sql').read_text(encoding='utf-8')
SEED = (Path(__file__).resolve().parent / 'database' / 'seed.sql').read_text(encoding='utf-8')


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.conn.executescript(SCHEMA)
        self.conn.executescript(SEED)

    def tearDown(self):
        self.conn.close()

    def test_create_valid_order(self):
        order_id = create_order(self.conn, 12, 4, 'Check suspension')
        self.assertGreater(order_id, 20)
        self.assertEqual(get_order(self.conn, order_id)['status'], 'received')
        self.assertIsNone(get_order(self.conn, order_id)['completed_at'])

    def test_unknown_vehicle(self):
        before = self.conn.execute('SELECT COUNT(*) FROM service_orders').fetchone()[0]
        with self.assertRaises(LookupError):
            create_order(self.conn, 999, 1, 'Test')
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM service_orders').fetchone()[0], before)

    def test_inactive_mechanic(self):
        with self.assertRaises(ValueError):
            create_order(self.conn, 1, 5, 'Test')

    def test_add_to_completed_order_preserves_state(self):
        before = get_order(self.conn, 1)
        with self.assertRaises(ValueError):
            add_service_to_order(self.conn, 1, 5, 2, 250)
        self.assertEqual(get_order(self.conn, 1), before)

    def test_cannot_complete_empty_order(self):
        order_id = create_order(self.conn, 12, 4, 'Check suspension')
        with self.assertRaises(ValueError):
            complete_order(self.conn, order_id)
        self.assertEqual(get_order(self.conn, order_id)['status'], 'received')

    def test_full_order_lifecycle(self):
        order_id = create_order(self.conn, 12, 4, 'Check suspension')
        add_service_to_order(self.conn, order_id, 9, 1.5, 250)
        self.assertEqual(get_order(self.conn, order_id)['status'], 'in_progress')
        complete_order(self.conn, order_id)
        result = get_order(self.conn, order_id)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['total_price'], 250)
        self.assertIsNotNone(result['completed_at'])

    def test_duplicate_service_rejected(self):
        original = get_order(self.conn, 1)
        with self.assertRaises(ValueError):
            add_service_to_order(self.conn, 1, 1, 2, 500)
        self.assertEqual(get_order(self.conn, 1), original)

    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            add_service_to_order(self.conn, 5, 1, 2, -1)
        self.assertEqual(get_order(self.conn, 5)['status'], 'in_progress')

    def test_foreign_keys_enabled(self):
        self.assertEqual(self.conn.execute('PRAGMA foreign_keys').fetchone()[0], 1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute('INSERT INTO vehicles(customer_id,brand,model,year,registration_no,vin) '
                              'VALUES (?,?,?,?,?,?)', (999, 'A', 'B', 2000, 'NEW', 'NEWVIN'))


if __name__ == '__main__':
    unittest.main()
