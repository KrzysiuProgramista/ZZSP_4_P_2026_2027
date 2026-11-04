import argparse
import csv
import ipaddress
import sqlite3
from datetime import datetime

DB = "network_events.db"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS sensors (
    sensor_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    location TEXT
);
CREATE TABLE IF NOT EXISTS ip_addresses (
    ip_id INTEGER PRIMARY KEY,
    address TEXT NOT NULL UNIQUE,
    is_private INTEGER NOT NULL CHECK(is_private IN (0,1))
);
CREATE TABLE IF NOT EXISTS event_types (
    event_type_id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    default_severity TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS network_events (
    event_id INTEGER PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensors(sensor_id),
    src_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    dst_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    event_type_id INTEGER NOT NULL REFERENCES event_types(event_type_id),
    event_time TEXT NOT NULL,
    src_port INTEGER CHECK(src_port BETWEEN 1 AND 65535),
    dst_port INTEGER CHECK(dst_port BETWEEN 1 AND 65535),
    protocol TEXT NOT NULL CHECK(protocol IN ('TCP','UDP','ICMP')),
    action TEXT NOT NULL CHECK(action IN ('ALLOW','BLOCK')),
    bytes INTEGER NOT NULL CHECK(bytes >= 0),
    duration_ms INTEGER NOT NULL CHECK(duration_ms >= 0),
    event_key TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY,
    rule_code TEXT NOT NULL,
    source_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    target_ip_id INTEGER NOT NULL REFERENCES ip_addresses(ip_id),
    service_port INTEGER,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('HIGH','CRITICAL')),
    event_count INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW'
        CHECK(status IN ('NEW','INVESTIGATING','CLOSED')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(rule_code, source_ip_id, target_ip_id, service_port, window_start)
);
CREATE INDEX IF NOT EXISTS idx_events_time ON network_events(event_time);
CREATE INDEX IF NOT EXISTS idx_events_source ON network_events(src_ip_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON network_events(event_type_id);
"""

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)
    print("Database ready:", DB)

def validate(row):
    required = ["timestamp","sensor_name","src_ip","dst_ip","src_port","dst_port",
                "protocol","event_type","action","bytes","duration_ms"]
    if any(row.get(k) is None for k in required):
        raise ValueError("missing required field")
    timestamp = datetime.fromisoformat(row["timestamp"])
    if not row["sensor_name"].strip():
        raise ValueError("empty sensor_name")
    ipaddress.ip_address(row["src_ip"])
    ipaddress.ip_address(row["dst_ip"])
    for field in ("src_port", "dst_port"):
        value = row[field].strip()
        if value:
            number = int(value)
            if not 1 <= number <= 65535:
                raise ValueError(field + " must be 1..65535")
    if row["protocol"] not in ("TCP","UDP","ICMP"):
        raise ValueError("invalid protocol")
    if row["action"] not in ("ALLOW","BLOCK"):
        raise ValueError("invalid action")
    if not row["event_type"].strip():
        raise ValueError("empty event_type")
    for field in ("bytes","duration_ms"):
        if int(row[field]) < 0:
            raise ValueError(field + " cannot be negative")
    # Store a consistent ISO timestamp string. The sample has no timezone suffix.
    return timestamp.isoformat(timespec="seconds")

def get_id(conn, table, column, value, extra=None):
    if table == "sensors":
        conn.execute("INSERT OR IGNORE INTO sensors(name) VALUES (?)", (value,))
        return conn.execute("SELECT sensor_id FROM sensors WHERE name=?", (value,)).fetchone()[0]
    if table == "ip_addresses":
        ip = ipaddress.ip_address(value)
        conn.execute("INSERT OR IGNORE INTO ip_addresses(address,is_private) VALUES (?,?)",
                     (value, int(ip.is_private)))
        return conn.execute("SELECT ip_id FROM ip_addresses WHERE address=?", (value,)).fetchone()[0]
    if table == "event_types":
        conn.execute("INSERT OR IGNORE INTO event_types(code,default_severity) VALUES (?,?)",
                     (value, "MEDIUM"))
        return conn.execute("SELECT event_type_id FROM event_types WHERE code=?", (value,)).fetchone()[0]

def import_csv(path):
    read = imported = rejected = duplicates = 0
    with open(path, newline="", encoding="utf-8-sig") as f, connect() as conn:
        reader = csv.DictReader(f)
        expected = {"timestamp","sensor_name","src_ip","dst_ip","src_port","dst_port",
                    "protocol","event_type","action","bytes","duration_ms"}
        if not reader.fieldnames or not expected.issubset(set(reader.fieldnames)):
            raise ValueError("CSV is missing required columns: " + ", ".join(sorted(expected)))
        for line, row in enumerate(reader, start=2):
            read += 1
            try:
                event_time = validate(row)
                src = get_id(conn,"ip_addresses","address",row["src_ip"])
                dst = get_id(conn,"ip_addresses","address",row["dst_ip"])
                sensor = get_id(conn,"sensors","name",row["sensor_name"])
                etype = get_id(conn,"event_types","code",row["event_type"])
                key = "|".join([event_time,row["sensor_name"],row["src_ip"],row["dst_ip"],
                    row["src_port"],row["dst_port"],row["protocol"],row["event_type"],
                    row["action"],row["bytes"],row["duration_ms"]])
                cur = conn.execute("""INSERT OR IGNORE INTO network_events
                    (sensor_id,src_ip_id,dst_ip_id,event_type_id,event_time,src_port,dst_port,
                     protocol,action,bytes,duration_ms,event_key)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (sensor,src,dst,etype,event_time,int(row["src_port"]) if row["src_port"].strip() else None,
                     int(row["dst_port"]) if row["dst_port"].strip() else None,row["protocol"],
                     row["action"],int(row["bytes"]),int(row["duration_ms"]),key))
                if cur.rowcount:
                    imported += 1
                else:
                    duplicates += 1
            except (ValueError, TypeError, sqlite3.Error) as e:
                rejected += 1
                print(f"Rejected CSV line {line}: {e}")
    print(f"Read: {read} | Imported: {imported} | Rejected: {rejected} | Duplicates: {duplicates}")

def bucket_expr(minutes):
    return (f"strftime('%Y-%m-%d %H:', event_time) || "
            f"printf('%02d', (CAST(strftime('%M', event_time) AS INTEGER) / {minutes}) * {minutes})")

def detect():
    created = 0
    with connect() as conn:
        rules = [
            ("PORT_SCAN", 5, "HIGH", "COUNT(DISTINCT e.dst_port) >= 20",
             "COUNT(DISTINCT e.dst_port)", "NULL"),
            ("BRUTE_FORCE", 5, "HIGH",
             "SUM(CASE WHEN t.code='AUTH_FAILURE' THEN 1 ELSE 0 END) >= 8",
             "SUM(CASE WHEN t.code='AUTH_FAILURE' THEN 1 ELSE 0 END)", "e.dst_port"),
            ("TRAFFIC_FLOOD", 1, "CRITICAL", "COUNT(*) >= 150", "COUNT(*)", "e.dst_port")
        ]
        for rule, mins, severity, having, count_sql, service_sql in rules:
            bucket = bucket_expr(mins)
            sql = f"""
            SELECT e.src_ip_id, e.dst_ip_id, {service_sql} AS service_port,
                   {bucket} AS win, {count_sql} AS total
            FROM network_events e
            JOIN event_types t ON t.event_type_id=e.event_type_id
            WHERE (? != 'BRUTE_FORCE' OR t.code='AUTH_FAILURE')
            GROUP BY e.src_ip_id,e.dst_ip_id,{service_sql},win
            HAVING {having}
            """
            for r in conn.execute(sql, (rule,)).fetchall():
                start = r["win"] + ":00"
                end = f"window of {mins} minute(s)"
                src = conn.execute("SELECT address FROM ip_addresses WHERE ip_id=?", (r["src_ip_id"],)).fetchone()[0]
                dst = conn.execute("SELECT address FROM ip_addresses WHERE ip_id=?", (r["dst_ip_id"],)).fetchone()[0]
                desc = f"{rule}: {src} -> {dst}; {r['total']} matching events; {end}"
                cur = conn.execute("""INSERT OR IGNORE INTO alerts
                    (rule_code,source_ip_id,target_ip_id,service_port,window_start,window_end,
                     severity,event_count,description)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                    (rule,r["src_ip_id"],r["dst_ip_id"],r["service_port"] if r["service_port"] is not None else -1,start,end,severity,r["total"],desc))
                created += cur.rowcount
    print("New alerts created:", created)

def show_query(conn, title, sql):
    print("\\n" + title)
    rows = conn.execute(sql).fetchall()
    if not rows:
        print("(no rows)")
    for row in rows:
        print(" | ".join(str(v) for v in row))

def summary():
    with connect() as conn:
        print("Events:", conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0])
        print("Alerts:", conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0])

def report():
    with connect() as conn:
        show_query(conn,"1. Event volume by type", """
            SELECT t.code,COUNT(*) AS events FROM network_events e
            JOIN event_types t USING(event_type_id) GROUP BY t.code ORDER BY events DESC""")
        show_query(conn,"2. Top 10 source IPs", """
            SELECT ip.address,COUNT(*) AS events FROM network_events e
            JOIN ip_addresses ip ON ip.ip_id=e.src_ip_id
            GROUP BY ip.address ORDER BY events DESC LIMIT 10""")
        show_query(conn,"3. Top targeted destination ports", """
            SELECT dst_port,COUNT(*) AS events FROM network_events
            WHERE dst_port IS NOT NULL GROUP BY dst_port ORDER BY events DESC LIMIT 10""")
        show_query(conn,"4. Alerts by severity and status", """
            SELECT severity,status,COUNT(*) FROM alerts
            GROUP BY severity,status ORDER BY severity,status""")
        show_query(conn,"5. Top destination IPs", """
            SELECT ip.address,COUNT(*) AS events FROM network_events e
            JOIN ip_addresses ip ON ip.ip_id=e.dst_ip_id
            GROUP BY ip.address ORDER BY events DESC LIMIT 10""")

def main():
    parser = argparse.ArgumentParser(description="Offline network event analyzer")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-db")
    imp = sub.add_parser("import-csv")
    imp.add_argument("csv_file")
    sub.add_parser("summary")
    sub.add_parser("detect")
    sub.add_parser("report")
    args = parser.parse_args()
    if args.command == "init-db": init_db()
    elif args.command == "import-csv": import_csv(args.csv_file)
    elif args.command == "summary": summary()
    elif args.command == "detect": detect()
    elif args.command == "report": report()

if __name__ == "__main__":
    main()
