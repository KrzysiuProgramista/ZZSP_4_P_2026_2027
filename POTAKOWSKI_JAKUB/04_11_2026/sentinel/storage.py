import sqlite3
from pathlib import Path
from ipaddress import ip_address
from .model import CATEGORIES

ROOT=Path(__file__).resolve().parent.parent

class Store:
    def __init__(self,path):self.path=path
    def __enter__(self):
        self.connection=sqlite3.connect(self.path)
        self.connection.row_factory=sqlite3.Row
        self.connection.execute('PRAGMA foreign_keys=ON')
        return self
    def __exit__(self,*args):self.connection.close()
    def initialize(self):
        self.connection.executescript((ROOT/'schema.sql').read_text(encoding='utf-8'))
        with self.connection:
            self.connection.executemany('INSERT OR IGNORE INTO category(name,severity) VALUES (?,?)',[(x,'MEDIUM' if x=='AUTH_FAILURE' else 'LOW') for x in CATEGORIES])
    def sensor_id(self,name):
        c=self.connection
        c.execute('INSERT OR IGNORE INTO sensor(label) VALUES (?)',(name,))
        return c.execute('SELECT id FROM sensor WHERE label=?',(name,)).fetchone()[0]
    def host_id(self,address):
        c=self.connection;ip=ip_address(address)
        c.execute('INSERT OR IGNORE INTO host(ip,family,private) VALUES (?,?,?)',(address,ip.version,int(ip.is_private)))
        return c.execute('SELECT id FROM host WHERE ip=?',(address,)).fetchone()[0]
    def append(self,event):
        c=self.connection;key=event.fingerprint()
        if c.execute('SELECT 1 FROM observation WHERE fingerprint=?',(key,)).fetchone():return False
        sensor=self.sensor_id(event.sensor)
        src=self.host_id(event.source);dst=self.host_id(event.target)
        kind=c.execute('SELECT id FROM category WHERE name=?',(event.category,)).fetchone()[0]
        c.execute('''INSERT INTO observation(fingerprint,sensor,category,origin,destination,instant,sport,dport,transport,decision,octets,elapsed)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',(key,sensor,kind,src,dst,event.instant,event.sport,event.dport,event.protocol,event.action,event.octets,event.elapsed))
        return True
