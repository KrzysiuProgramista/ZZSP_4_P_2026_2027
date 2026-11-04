"""Regression tests; every test uses a fresh temporary in-memory SQLite DB."""
import csv
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db import init_db
from detection import detect
from importer import HEADERS, import_csv
from reports import fetch_reports


BASE = {
    "timestamp": "2026-09-18T10:10:00", "sensor_name": "fixture-sensor",
    "src_ip": "198.51.100.66", "dst_ip": "10.0.0.20",
    "src_port": "55555", "dst_port": "443", "protocol": "TCP",
    "event_type": "CONNECTION", "action": "ALLOW",
    "bytes": "100", "duration_ms": "10",
}


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        init_db(self.conn)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.addCleanup(self.conn.close)

    def make_csv(self, records, name="fixtures.csv"):
        path = Path(self.temp_dir.name) / name
        with path.open("w",encoding="utf-8",newline="") as f:
            writer = csv.DictWriter(f,fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(records)
        return path

    def make_scan(self, count=20):
        start = datetime.fromisoformat(BASE["timestamp"])
        return [dict(BASE, timestamp=(start+timedelta(seconds=i)).isoformat(), dst_port=str(8000+i))
                for i in range(count)]

    def test_valid_csv_and_duplicate_import(self):
        path = self.make_csv(self.make_scan(20))
        result,_ = import_csv(self.conn,path)
        self.assertEqual(result,{"read":20,"imported":20,"rejected":0,"duplicates":0})
        result2,_ = import_csv(self.conn,path)
        self.assertEqual(result2,{"read":20,"imported":0,"rejected":0,"duplicates":20})
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0],20)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0],1)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM ip_addresses").fetchone()[0],2)
        self.assertFalse(self.conn.execute("PRAGMA foreign_key_check").fetchall())

    def test_rejected_row_has_csv_line_number(self):
        good = BASE.copy()
        invalid = dict(BASE,timestamp="bad-date",src_port="12345")
        path = self.make_csv([good,invalid])
        result,errors = import_csv(self.conn,path)
        self.assertEqual(result["imported"],1)
        self.assertEqual(result["rejected"],1)
        self.assertEqual(errors[0][0],3)
        audit = self.conn.execute("SELECT line_number,reason FROM import_rejections").fetchone()
        self.assertEqual(audit["line_number"],3)
        self.assertIn("ISO 8601",audit["reason"])

    def test_unknown_type_is_rejected_with_no_orphan(self):
        path = self.make_csv([dict(BASE,event_type="NOT_A_TYPE")])
        result, _ = import_csv(self.conn,path)
        self.assertEqual(result["rejected"],1)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0],0)
        self.assertFalse(self.conn.execute("PRAGMA foreign_key_check").fetchall())

    def test_invalid_protocol_port_and_bytes(self):
        rows = [dict(BASE, protocol="SCTP"),dict(BASE,dst_port="70000"),
                dict(BASE,bytes="-4"),dict(BASE,src_ip="invalid")]
        result,_ = import_csv(self.conn,self.make_csv(rows))
        self.assertEqual(result["rejected"],4)
        self.assertEqual(result["imported"],0)

    def test_detect_scan_once_and_keep_status(self):
        import_csv(self.conn, self.make_csv(self.make_scan(23)))
        run = detect(self.conn)
        self.assertEqual(run["new"],1)
        alert = self.conn.execute("SELECT * FROM alerts").fetchone()
        self.assertEqual(alert["rule_code"],"PORT_SCAN")
        self.assertEqual(alert["metric_count"],23)
        self.assertEqual(alert["event_count"],23)
        self.assertEqual(alert["severity"],"HIGH")
        self.assertEqual(alert["window_start"],"2026-09-18T10:10:00")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM alert_events").fetchone()[0],23)
        with self.conn:
            self.conn.execute("UPDATE alerts SET status='INVESTIGATING' WHERE alert_id=?",(alert["alert_id"],))
        rerun=detect(self.conn)
        self.assertEqual(rerun["new"],0)
        self.assertEqual(rerun["existing"],1)
        self.assertEqual(self.conn.execute("SELECT status FROM alerts").fetchone()[0],"INVESTIGATING")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0],1)

    def test_below_threshold_does_not_alert(self):
        import_csv(self.conn,self.make_csv(self.make_scan(19)))
        self.assertEqual(detect(self.conn)["new"],0)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0],0)

    def test_brute_force_rule(self):
        rows=[]
        for i in range(8):
            rows.append(dict(BASE, timestamp=f"2026-09-18T10:20:{i:02d}",src_port=str(40000+i),
                             src_ip="203.0.113.23", dst_ip="10.0.0.15", dst_port="22",
                             event_type="AUTH_FAILURE"))
        import_csv(self.conn,self.make_csv(rows))
        self.assertEqual(detect(self.conn)["by_rule"]["BRUTE_FORCE"],1)
        alert=self.conn.execute("SELECT rule_code,event_count FROM alerts").fetchone()
        self.assertEqual(tuple(alert),("BRUTE_FORCE",8))

    def test_traffic_flood_rule(self):
        rows=[]
        for i in range(150):
            rows.append(dict(BASE,timestamp=f"2026-09-18T10:40:{i%60:02d}",src_port=str(20000+i),
                             src_ip="198.51.100.77",dst_port="443"))
        import_csv(self.conn,self.make_csv(rows))
        self.assertEqual(detect(self.conn)["by_rule"]["TRAFFIC_FLOOD"],1)
        alert=self.conn.execute("SELECT rule_code,severity,event_count FROM alerts").fetchone()
        self.assertEqual(tuple(alert),("TRAFFIC_FLOOD","CRITICAL",150))

    def test_all_six_sql_reports(self):
        import_csv(self.conn,self.make_csv(self.make_scan(2)))
        result=fetch_reports(self.conn)
        self.assertEqual(set(result),{"types","sources","services","alerts","timeline","targets"})
        self.assertEqual(result["timeline"][2][0][1],2)

    def test_foreign_key_constraint(self):
        with self.assertRaises(sqlite3.IntegrityError):
            with self.conn:
                self.conn.execute("""INSERT INTO network_events (
                    event_hash,sensor_id,event_type_id,src_ip_id,dst_ip_id,
                    event_time,raw_timestamp,protocol,action,bytes,duration_ms
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                ("fake",999,999,999,999,"2026-09-18T10:00:00","2026-09-18T10:00:00","TCP","ALLOW",0,0))


if __name__ == "__main__":
    unittest.main()
