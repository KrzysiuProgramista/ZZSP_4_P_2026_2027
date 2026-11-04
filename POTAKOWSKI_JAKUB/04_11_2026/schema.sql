PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sensor(id INTEGER PRIMARY KEY,label TEXT NOT NULL UNIQUE CHECK(length(trim(label))>0),location TEXT);
CREATE TABLE IF NOT EXISTS host(id INTEGER PRIMARY KEY,ip TEXT NOT NULL UNIQUE,family INTEGER NOT NULL CHECK(family IN (4,6)),private INTEGER NOT NULL CHECK(private IN (0,1)));
CREATE TABLE IF NOT EXISTS category(id INTEGER PRIMARY KEY,name TEXT NOT NULL UNIQUE,severity TEXT NOT NULL CHECK(severity IN ('LOW','MEDIUM','HIGH','CRITICAL')));
CREATE TABLE IF NOT EXISTS observation(
 id INTEGER PRIMARY KEY,fingerprint TEXT NOT NULL UNIQUE,
 sensor INTEGER NOT NULL REFERENCES sensor(id),category INTEGER NOT NULL REFERENCES category(id),
 origin INTEGER NOT NULL REFERENCES host(id),destination INTEGER NOT NULL REFERENCES host(id),
 instant INTEGER NOT NULL CHECK(instant>=0),
 sport INTEGER CHECK(sport BETWEEN 1 AND 65535),dport INTEGER CHECK(dport BETWEEN 1 AND 65535),
 transport TEXT NOT NULL CHECK(transport IN ('TCP','UDP','ICMP')),
 decision TEXT NOT NULL CHECK(decision IN ('ALLOW','BLOCK')),
 octets INTEGER NOT NULL CHECK(octets>=0),elapsed INTEGER NOT NULL CHECK(elapsed>=0));
CREATE INDEX IF NOT EXISTS observation_pair ON observation(origin,destination,instant,dport);
CREATE INDEX IF NOT EXISTS observation_kind ON observation(category,instant);
CREATE TABLE IF NOT EXISTS incident(
 id INTEGER PRIMARY KEY,signature TEXT NOT NULL UNIQUE,
 rule TEXT NOT NULL CHECK(rule IN ('PORT_SCAN','BRUTE_FORCE','TRAFFIC_FLOOD')),
 origin INTEGER NOT NULL REFERENCES host(id),destination INTEGER NOT NULL REFERENCES host(id),
 port INTEGER CHECK(port BETWEEN 1 AND 65535),start_us INTEGER NOT NULL,stop_us INTEGER NOT NULL CHECK(stop_us>start_us),
 severity TEXT NOT NULL CHECK(severity IN ('HIGH','CRITICAL')),
 state TEXT NOT NULL DEFAULT 'NEW' CHECK(state IN ('NEW','INVESTIGATING','CLOSED')),
 quantity INTEGER NOT NULL CHECK(quantity>0),score INTEGER NOT NULL CHECK(score>0),explanation TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT(strftime('%Y-%m-%dT%H:%M:%SZ','now')));
CREATE TABLE IF NOT EXISTS incident_observation(
 incident INTEGER NOT NULL REFERENCES incident(id) ON DELETE CASCADE,
 observation INTEGER NOT NULL REFERENCES observation(id),PRIMARY KEY(incident,observation));
