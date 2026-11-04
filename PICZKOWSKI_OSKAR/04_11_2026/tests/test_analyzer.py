"""Tests for import validation, idempotency and detection rules.

Run from the project root:  python -m unittest discover -s tests -v
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from db import connect, init_db  # noqa: E402
from detection import run_detection  # noqa: E402
from importer import import_csv  # noqa: E402

HEADER = "timestamp,sensor_name,src_ip,dst_ip,src_port,dst_port,protocol,event_type,action,bytes,duration_ms\n"


def event(ts="2026-09-18T10:00:00", src="203.0.113.5", dst="10.0.0.20", dport="22",
          etype="CONNECTION", action="ALLOW", sport="50000", proto="TCP",
          nbytes="100", dur="10", sensor="edge-fw-01"):
    return f"{ts},{sensor},{src},{dst},{sport},{dport},{proto},{etype},{action},{nbytes},{dur}\n"


class AnalyzerTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.db_path = os.path.join(self.dir, "test.db")
        init_db(self.db_path)
        self.conn = connect(self.db_path)

    def tearDown(self):
        self.conn.close()
        self._tmp.cleanup()

    def write_csv(self, rows, name="events.csv"):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(HEADER + "".join(rows))
        return path

    def count(self, table):
        return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def alerts(self, rule=None):
        if rule:
            return self.conn.execute("SELECT * FROM alerts WHERE rule_code = ?", (rule,)).fetchall()
        return self.conn.execute("SELECT * FROM alerts").fetchall()


class ImportTests(AnalyzerTestCase):
    def test_valid_import_counts_match_source(self):
        path = self.write_csv([event(ts=f"2026-09-18T10:00:0{i}") for i in range(3)])
        r = import_csv(self.conn, path)
        self.assertEqual((r.read, r.imported, r.rejected, r.duplicates), (3, 3, 0, 0))
        self.assertEqual(self.count("network_events"), 3)

    def test_malformed_rows_are_rejected_with_line_numbers(self):
        path = self.write_csv([
            event(),                       # line 2: valid
            event(dport="70000"),          # line 3: port out of range
            event(src="not-an-ip"),        # line 4: bad IP
            event(proto="SCTP"),           # line 5: unknown protocol
        ])
        r = import_csv(self.conn, path)
        self.assertEqual((r.imported, r.rejected), (1, 3))
        self.assertEqual([line for line, _ in r.rejects], [3, 4, 5])
        self.assertEqual(self.count("network_events"), 1)

    def test_unknown_event_type_is_rejected_and_leaves_no_orphan(self):
        path = self.write_csv([event(etype="MALWARE_BEACON")])
        r = import_csv(self.conn, path)
        self.assertEqual(r.rejected, 1)
        self.assertEqual(self.count("network_events"), 0)

    def test_repeat_import_is_idempotent(self):
        path = self.write_csv([event(), event(ts="2026-09-18T10:00:01")])
        import_csv(self.conn, path)
        r = import_csv(self.conn, path)
        self.assertEqual((r.imported, r.duplicates), (0, 2))
        self.assertEqual(self.count("network_events"), 2)


class DetectionTests(AnalyzerTestCase):
    def _load(self, rows):
        import_csv(self.conn, self.write_csv(rows))

    def test_port_scan_creates_one_alert(self):
        # 25 distinct ports within one 5-minute bucket (10:00-10:04:59).
        self._load([event(ts=f"2026-09-18T10:00:{i:02d}", dport=str(1000 + i)) for i in range(25)])
        run_detection(self.conn)
        scans = self.alerts("PORT_SCAN")
        self.assertEqual(len(scans), 1)
        self.assertEqual(scans[0]["event_count"], 25)
        self.assertEqual(scans[0]["window_start"], "2026-09-18T10:00:00")
        self.assertEqual(scans[0]["window_end"], "2026-09-18T10:05:00")
        self.assertEqual(scans[0]["severity"], "HIGH")

    def test_below_threshold_port_scan_creates_no_alert(self):
        self._load([event(ts=f"2026-09-18T10:00:{i:02d}", dport=str(1000 + i)) for i in range(19)])
        run_detection(self.conn)
        self.assertEqual(self.alerts("PORT_SCAN"), [])

    def test_brute_force_threshold(self):
        self._load([event(ts=f"2026-09-18T10:01:{i:02d}", etype="AUTH_FAILURE", action="BLOCK")
                    for i in range(8)])
        run_detection(self.conn)
        self.assertEqual(len(self.alerts("BRUTE_FORCE")), 1)

    def test_brute_force_below_threshold(self):
        self._load([event(ts=f"2026-09-18T10:01:{i:02d}", etype="AUTH_FAILURE", action="BLOCK")
                    for i in range(7)])
        run_detection(self.conn)
        self.assertEqual(self.alerts("BRUTE_FORCE"), [])

    def test_traffic_flood_threshold(self):
        rows = [event(ts="2026-09-18T10:00:00", dport="443", nbytes=str(i)) for i in range(150)]
        self._load(rows)
        run_detection(self.conn)
        floods = self.alerts("TRAFFIC_FLOOD")
        self.assertEqual(len(floods), 1)
        self.assertEqual(floods[0]["severity"], "CRITICAL")

    def test_running_detection_twice_creates_no_duplicates(self):
        self._load([event(ts=f"2026-09-18T10:00:{i:02d}", dport=str(1000 + i)) for i in range(25)])
        first = run_detection(self.conn)
        second = run_detection(self.conn)
        self.assertEqual(first["PORT_SCAN"][1], 1)
        self.assertEqual(second["PORT_SCAN"][1], 0)
        self.assertEqual(len(self.alerts()), 1)


if __name__ == "__main__":
    unittest.main()
