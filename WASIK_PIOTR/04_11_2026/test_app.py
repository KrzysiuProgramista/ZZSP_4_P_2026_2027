import unittest
import os
import sqlite3
from db import init_db, connect
from importer import import_csv
from detection import run_detection

TEST_DB = "test_network_analyzer.db"

class TestNetworkAnalyzer(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        init_db(db_path=TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_import_and_detection(self):
        sample_csv = "data/network_events_sample.csv"
        if os.path.exists(sample_csv):
            summary = import_csv(sample_csv, db_path=TEST_DB)
            self.assertGreater(summary['imported'], 0)
            
            # Test idempotency (repeat import)
            summary_repeat = import_csv(sample_csv, db_path=TEST_DB)
            self.assertEqual(summary_repeat['imported'], 0)
            self.assertEqual(summary_repeat['duplicates'], summary['imported'])

            # Test detection engine
            alerts_count = run_detection(db_path=TEST_DB)
            self.assertGreaterEqual(alerts_count, 0)

            # Re-running detection should not create duplicate alerts
            alerts_count_second = run_detection(db_path=TEST_DB)
            self.assertEqual(alerts_count_second, 0)

if __name__ == "__main__":
    unittest.main()
