import sqlite3
import unittest
from pathlib import Path

from service import Workshop, add_service_to_order, complete_order, create_order, get_order

DATA = Path(__file__).resolve().parent / 'database'


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(':memory:')
        self.connection.execute('PRAGMA foreign_keys = ON')
        self.connection.executescript((DATA/'schema.sql').read_text(encoding='utf-8'))
        self.connection.executescript((DATA/'seed.sql').read_text(encoding='utf-8'))
        self.workshop = Workshop(self.connection)

    def tearDown(self):
        self.connection.close()

    def test_new_order_id_and_status(self):
        number = create_order(self.connection, 12, 4, 'Customer reports a rattle')
        self.assertGreater(number, 20)
        self.assertEqual(get_order(self.connection, number)['status'], 'received')

    def test_absent_vehicle_leaves_database_unchanged(self):
        old_count = self.connection.execute('SELECT COUNT(*) FROM service_orders').fetchone()[0]
        with self.assertRaises(LookupError):
            self.workshop.create(99, 4, 'Bad vehicle')
        self.assertEqual(self.connection.execute('SELECT COUNT(*) FROM service_orders').fetchone()[0],old_count)

    def test_inactive_mechanic_is_rejected(self):
        with self.assertRaises(ValueError):
            self.workshop.create(12, 5, 'Bad mechanic')

    def test_cannot_add_to_completed_order(self):
        original = get_order(self.connection,1)
        with self.assertRaises(ValueError):
            add_service_to_order(self.connection,1,5,2,120)
        self.assertEqual(get_order(self.connection,1),original)

    def test_empty_order_cannot_be_completed(self):
        number=self.workshop.create(12,4,'Wait for parts')
        with self.assertRaises(ValueError):
            complete_order(self.connection,number)
        self.assertIsNone(self.workshop.details(number)['completed_at'])

    def test_order_lifecycle(self):
        number=self.workshop.create(12,4,'Inspect brakes')
        self.workshop.add_line(number,2,2,620)
        self.assertEqual(self.workshop.details(number)['status'],'in_progress')
        self.workshop.finish(number)
        self.assertEqual(self.workshop.details(number)['total_price'],620)
        self.assertEqual(self.workshop.details(number)['status'],'completed')

    def test_repeated_line_keeps_original_price(self):
        with self.assertRaises(ValueError):
            self.workshop.add_line(5,3,2,999)
        self.assertEqual(self.workshop.details(5)['services'][0]['final_price'],180)

    def test_missing_service(self):
        with self.assertRaises(LookupError):
            self.workshop.add_line(5,999,1,30)

    def test_cancelled_order_is_locked(self):
        with self.assertRaises(ValueError):
            self.workshop.finish(12)


if __name__ == '__main__':
    unittest.main()
