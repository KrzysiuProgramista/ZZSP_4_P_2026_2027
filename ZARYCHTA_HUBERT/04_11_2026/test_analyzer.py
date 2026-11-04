import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path
from db import connect,init_db
from importer import FIELDS,import_csv
from detection import detect
from reports import QUERIES,report

class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.cm=connect(':memory:'); self.c=self.cm.__enter__(); init_db(self.c)
    def tearDown(self):
        self.cm.__exit__(None,None,None); self.temp.cleanup()
    def row(self, **changes):
        r=dict(zip(FIELDS,['2026-09-18T10:00:01','sensor','198.51.100.1','10.0.0.1','50000','22','TCP','CONNECTION','ALLOW','20','1']))
        r.update(changes); return r
    def load(self,rows):
        p=Path(self.temp.name)/'events.csv'
        with p.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader();w.writerows(rows)
        return import_csv(self.c,p)
    def test_valid_and_repeat(self):
        self.assertEqual(self.load([self.row()])['imported'],1)
        self.assertEqual(self.load([self.row()])['duplicates'],1)
    def test_bad_rows_continue(self):
        bad=[self.row(src_ip='bad'),self.row(dst_port='65536'),self.row(bytes='-1'),self.row(protocol='BAD'),self.row(timestamp='bad'),self.row(event_type='BAD'),self.row(sensor_name='')]
        s=self.load(bad+[self.row()]);self.assertEqual(s['rejected'],7);self.assertEqual(s['imported'],1);self.assertEqual(s['errors'][0]['line'],2)
    def test_invalid_header(self):
        p=Path(self.temp.name)/'bad.csv';p.write_text('foo,bar\n1,2\n')
        with self.assertRaises(ValueError):import_csv(self.c,p)
    def test_fk(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.execute("INSERT INTO network_events(event_hash,sensor_id,event_type_id,src_ip_id,dst_ip_id,event_time,protocol,action,bytes,duration_ms) VALUES ('x',999,999,999,999,'x','TCP','ALLOW',0,0)")
        self.c.rollback()
    def test_scan_and_repeat_preserves_status(self):
        self.load([self.row(dst_port=str(i)) for i in range(1,21)])
        self.assertEqual(detect(self.c)['PORT_SCAN'],1)
        with self.c:self.c.execute("UPDATE alerts SET status='CLOSED'")
        detect(self.c)
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM alerts').fetchone()[0],1)
        self.assertEqual(self.c.execute('SELECT status FROM alerts').fetchone()[0],'CLOSED')
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM alert_events').fetchone()[0],20)
    def test_below_scan(self):
        self.load([self.row(dst_port=str(i)) for i in range(1,20)])
        self.assertEqual(detect(self.c)['PORT_SCAN'],0)
    def test_brute_force_threshold(self):
        self.load([self.row(event_type='AUTH_FAILURE',src_port=str(1000+i)) for i in range(7)])
        self.assertEqual(detect(self.c)['BRUTE_FORCE'],0)
        self.load([self.row(event_type='AUTH_FAILURE',src_port='1007')])
        self.assertEqual(detect(self.c)['BRUTE_FORCE'],1)
    def test_flood_threshold(self):
        self.load([self.row(src_port=str(1000+i)) for i in range(149)])
        self.assertEqual(detect(self.c)['TRAFFIC_FLOOD'],0)
        self.load([self.row(src_port='1149')])
        self.assertEqual(detect(self.c)['TRAFFIC_FLOOD'],1)
    def test_fixed_boundary(self):
        self.load([self.row(dst_port=str(i),timestamp='2026-09-18T10:04:59' if i<=10 else '2026-09-18T10:05:00') for i in range(1,21)])
        self.assertEqual(detect(self.c)['PORT_SCAN'],0)
    def test_services_separate(self):
        self.load([self.row(event_type='AUTH_FAILURE',src_port=str(1000+i),dst_port='22' if i<4 else '23') for i in range(8)])
        self.assertEqual(detect(self.c)['BRUTE_FORCE'],0)
    def test_ipv6_blank_ports_timezone(self):
        s=self.load([self.row(src_ip='2001:db8::1',dst_port='',src_port='',protocol='ICMP',timestamp='2026-09-18T12:00:01+02:00')])
        self.assertEqual(s['imported'],1)
        self.assertEqual(self.c.execute('SELECT event_time FROM network_events').fetchone()[0],'2026-09-18T10:00:01.000000Z')
    def test_reports(self):
        self.load([self.row()])
        for name in QUERIES:
            for fmt in ('text','csv','json'):self.assertIsInstance(report(self.c,name,fmt),str)
    def test_supplied_dataset(self):
        s=import_csv(self.c,Path(__file__).parent/'data/network_events_sample.csv')
        self.assertEqual((s['read'],s['imported'],s['rejected']),(896,896,0))
        self.assertEqual(detect(self.c),{'PORT_SCAN':1,'BRUTE_FORCE':1,'TRAFFIC_FLOOD':1})
        self.assertEqual(self.c.execute('PRAGMA foreign_key_check').fetchall(),[])

if __name__=='__main__':unittest.main()
