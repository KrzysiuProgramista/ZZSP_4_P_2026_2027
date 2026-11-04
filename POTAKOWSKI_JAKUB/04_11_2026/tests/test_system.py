import csv
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from sentinel.storage import Store,ROOT
from sentinel.model import COLUMNS,Event
from sentinel.ingest import ingest
from sentinel.engine import analyze,load_rules
from sentinel.analytics import REPORTS,render

class SystemTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store(':memory:');self.store.__enter__();self.store.initialize();self.c=self.store.connection
    def tearDown(self):self.store.__exit__();self.tmp.cleanup()
    def row(self,**kw):
        r=dict(zip(COLUMNS,['2026-09-18T10:04:50','sensor','198.51.100.1','10.0.0.1','50000','22','TCP','CONNECTION','ALLOW','5','1']))
        r.update(kw);return r
    def load(self,rows):
        file=Path(self.tmp.name)/'test.csv'
        with file.open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=COLUMNS);writer.writeheader();writer.writerows(rows)
        return ingest(self.store,file)
    def test_import_and_duplicate(self):
        self.assertEqual(self.load([self.row()])['imported'],1)
        self.assertEqual(self.load([self.row()])['duplicates'],1)
    def test_rejected_rows(self):
        bad=[self.row(src_ip='bad'),self.row(dst_port='0'),self.row(bytes='-5'),self.row(protocol='X'),self.row(event_type='BAD'),self.row(timestamp='bad'),self.row(sensor_name=' ')]
        stats=self.load(bad+[self.row()]);self.assertEqual(stats['rejected'],7);self.assertEqual(stats['imported'],1);self.assertEqual(stats['errors'][0]['line'],2)
    def test_sqlite_integer_overflow_rejected(self):
        self.assertEqual(self.load([self.row(bytes=str(2**64)),self.row()])['rejected'],1)
    def test_rolling_across_fixed_boundary(self):
        self.load([self.row(dst_port=str(i),timestamp='2026-09-18T10:04:50' if i<11 else '2026-09-18T10:05:10') for i in range(1,21)])
        self.assertEqual(analyze(self.store,load_rules())['PORT_SCAN'],1)
        self.assertEqual(self.c.execute('SELECT score FROM incident').fetchone()[0],20)
    def test_exact_window_end_excluded(self):
        self.load([self.row(dst_port=str(i)) for i in range(1,20)]+[self.row(dst_port='20',timestamp='2026-09-18T10:09:50')])
        self.assertEqual(analyze(self.store,load_rules())['PORT_SCAN'],0)
    def test_duplicate_anchor_not_multiplied(self):
        self.load([self.row(src_port=str(i),event_type='AUTH_FAILURE') for i in range(1,8)])
        self.assertEqual(analyze(self.store,load_rules())['BRUTE_FORCE'],0)
        self.load([self.row(src_port='8',event_type='AUTH_FAILURE')])
        self.assertEqual(analyze(self.store,load_rules())['BRUTE_FORCE'],1)
        self.assertEqual(self.c.execute('SELECT quantity FROM incident').fetchone()[0],8)
    def test_flood_threshold(self):
        self.load([self.row(src_port=str(i)) for i in range(1,150)])
        self.assertEqual(analyze(self.store,load_rules())['TRAFFIC_FLOOD'],0)
        self.load([self.row(src_port='150')]);self.assertEqual(analyze(self.store,load_rules())['TRAFFIC_FLOOD'],1)
    def test_service_separation(self):
        self.load([self.row(event_type='AUTH_FAILURE',src_port=str(i),dst_port='22' if i<5 else '23') for i in range(1,9)])
        self.assertEqual(analyze(self.store,load_rules())['BRUTE_FORCE'],0)
    def test_ipv6_null_and_timezone(self):
        event=Event.parse(self.row(src_ip='2001:db8::1',protocol='ICMP',src_port='',dst_port='',timestamp='2026-09-18T12:04:50+02:00'))
        self.assertEqual(event.instant,Event.parse(self.row()).instant);self.assertIsNone(event.dport)
    def test_orphans_prevented(self):
        with self.assertRaises(sqlite3.IntegrityError):self.c.execute('INSERT INTO incident_observation VALUES (?,?)',(999,999))
        self.c.rollback()
    def test_all_reports(self):
        self.load([self.row()])
        for name in REPORTS:
            self.assertIsInstance(render(self.store,name,'text'),str)
            self.assertIsInstance(render(self.store,name,'csv'),str)
            self.assertIsInstance(json.loads(render(self.store,name,'json')),list)
    def test_bad_header(self):
        path=Path(self.tmp.name)/'bad.csv';path.write_text('x,y\n1,2\n')
        with self.assertRaises(ValueError):ingest(self.store,path)
    def test_original_and_idempotent_detection(self):
        stats=ingest(self.store,ROOT/'data/events.csv');self.assertEqual(stats['imported'],896)
        self.assertEqual(analyze(self.store,load_rules()),{'PORT_SCAN':1,'BRUTE_FORCE':1,'TRAFFIC_FLOOD':1})
        with self.c:self.c.execute("UPDATE incident SET state='CLOSED'")
        analyze(self.store,load_rules());self.assertEqual(self.c.execute('SELECT COUNT(*) FROM incident').fetchone()[0],3)
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM incident WHERE state='CLOSED'").fetchone()[0],3)
        for r in self.c.execute('SELECT id,quantity FROM incident'):
            self.assertEqual(r['quantity'],self.c.execute('SELECT COUNT(*) FROM incident_observation WHERE incident=?',(r['id'],)).fetchone()[0])
        self.assertEqual(self.c.execute('PRAGMA foreign_key_check').fetchall(),[])
    def test_import_transaction_rollback(self):
        original=self.store.append;calls=0
        def fail(event):
            nonlocal calls
            calls+=1
            if calls==2:raise sqlite3.OperationalError('simulated write failure')
            return original(event)
        self.store.append=fail
        with self.assertRaises(sqlite3.OperationalError):self.load([self.row(),self.row(src_port='2')])
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM observation').fetchone()[0],0)
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM sensor').fetchone()[0],0)
    def test_invalid_settings(self):
        path=Path(self.tmp.name)/'config.json';rules=load_rules();rules['PORT_SCAN']['threshold']=0;path.write_text(json.dumps(rules))
        with self.assertRaises(ValueError):load_rules(path)

if __name__=='__main__':unittest.main()
