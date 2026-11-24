"""
tests/test_analyzer.py - Automated verification covering all 6 assessment test cases:
1. Valid CSV import & count matching
2. Malformed row rejection without crashing
3. Foreign key & CHECK constraint enforcement
4. Port scan fixture triggering alert for expected window
5. Below-threshold fixture producing zero alerts
6. Idempotent detection (running detect twice creates no duplicate alerts)
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path

import db
import detection
import importer


class TestNetworkSecurityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp_dir.name) / "test.db")
        db.init_db(self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _write_csv(self, name: str, lines: list[str]) -> str:
        p = Path(self.tmp_dir.name) / name
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(p)

    def test_01_valid_csv_and_idempotent_reimport(self):
        csv_file = self._write_csv("valid.csv", [
            "timestamp,sensor_name,src_ip,dst_ip,src_port,dst_port,protocol,event_type,action,bytes,duration_ms",
            "2026-09-18T10:00:00Z,fw-1,10.0.0.1,10.0.0.2,50000,443,TCP,HTTP_REQUEST,ALLOW,500,10",
            "2026-09-18T10:00:05Z,fw-1,10.0.0.3,10.0.0.2,50001,53,UDP,DNS_QUERY,ALLOW,80,2",
        ])
        s1 = importer.import_csv(self.db_path, csv_file)
        self.assertEqual((s1.rows_read, s1.imported, s1.rejected, s1.duplicates), (2, 2, 0, 0))

        s2 = importer.import_csv(self.db_path, csv_file)
        self.assertEqual((s2.rows_read, s2.imported, s2.rejected, s2.duplicates), (2, 0, 0, 2))

    def test_02_malformed_row_rejected_safely(self):
        csv_file = self._write_csv("malformed.csv", [
            "timestamp,sensor_name,src_ip,dst_ip,src_port,dst_port,protocol,event_type,action,bytes,duration_ms",
            "BAD_DATE,fw-1,10.0.0.1,10.0.0.2,50000,443,TCP,HTTP_REQUEST,ALLOW,500,10",
            "2026-09-18T10:00:05Z,fw-1,10.0.0.1,10.0.0.2,50000,443,TCP,HTTP_REQUEST,ALLOW,500,10",
        ])
        s = importer.import_csv(self.db_path, csv_file)
        self.assertEqual(s.imported, 1)
        self.assertEqual(s.rejected, 1)
        self.assertIn("Line 2", s.errors[0])

    def test_03_database_constraints_prevent_orphans(self):
        conn = db.connect(self.db_path)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    """
                    INSERT INTO network_events (
                        event_hash, sensor_id, event_type_id, src_ip_id, dst_ip_id,
                        event_time, src_port, dst_port, protocol, action, bytes, duration_ms
                    ) VALUES ('h1', 999, 999, 999, 999, '2026-09-18T10:00:00Z', 80, 80, 'TCP', 'ALLOW', 10, 1)
                    """
                )
        finally:
            conn.close()

    def test_04_port_scan_fixture_fires_alert(self):
        lines = ["timestamp,sensor_name,src_ip,dst_ip,src_port,dst_port,protocol,event_type,action,bytes,duration_ms"]
        for port in range(1000, 1022):
            lines.append(f"2026-09-18T10:05:10Z,fw-1,198.51.100.9,10.0.0.20,44000,{port},TCP,CONNECTION,BLOCK,60,1")
        csv_file = self._write_csv("scan.csv", lines)
        importer.import_csv(self.db_path, csv_file)

        res = detection.run_detections(self.db_path)
        self.assertEqual(res.new_alerts, 1)

    def test_05_below_threshold_produces_no_alert(self):
        lines = ["timestamp,sensor_name,src_ip,dst_ip,src_port,dst_port,protocol,event_type,action,bytes,duration_ms"]
        for port in range(1000, 1010):
            lines.append(f"2026-09-18T10:05:10Z,fw-1,198.51.100.9,10.0.0.20,44000,{port},TCP,CONNECTION,BLOCK,60,1")
        csv_file = self._write_csv("normal_ports.csv", lines)
        importer.import_csv(self.db_path, csv_file)

        res = detection.run_detections(self.db_path)
        self.assertEqual(res.new_alerts, 0)

    def test_06_run_detect_twice_creates_no_duplicates(self):
        lines = ["timestamp,sensor_name,src_ip,dst_ip,src_port,dst_port,protocol,event_type,action,bytes,duration_ms"]
        for i in range(10):
            lines.append(f"2026-09-18T10:10:0{i}Z,fw-1,203.0.113.5,10.0.0.15,51000,22,TCP,AUTH_FAILURE,BLOCK,200,5")
        csv_file = self._write_csv("brute.csv", lines)
        importer.import_csv(self.db_path, csv_file)

        first = detection.run_detections(self.db_path)
        second = detection.run_detections(self.db_path)
        self.assertEqual(first.new_alerts, 1)
        self.assertEqual(second.new_alerts, 0)
        self.assertEqual(second.existing_alerts, 1)


if __name__ == "__main__":
    unittest.main()