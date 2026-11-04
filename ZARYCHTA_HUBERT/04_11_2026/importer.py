import csv
import hashlib
import ipaddress
import json
import re
from datetime import datetime, timezone
from config import EVENT_TYPES

FIELDS = 'timestamp sensor_name src_ip dst_ip src_port dst_port protocol event_type action bytes duration_ms'.split()

def integer(value, field, optional=False):
    if optional and value == '':
        return None
    if not re.fullmatch(r'[0-9]+', value):
        raise ValueError(f'{field}: expected non-negative integer')
    result = int(value)
    if optional and not 1 <= result <= 65535:
        raise ValueError(f'{field}: port outside 1..65535')
    return result

def validate(row):
    if None in row or any(row.get(k) is None for k in FIELDS):
        raise ValueError('incorrect number of CSV fields')
    out = dict(row)
    stamp = row['timestamp']
    if 'T' not in stamp:
        raise ValueError('timestamp: expected ISO date and time separated by T')
    dt = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    dt = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
    out['timestamp'] = dt.isoformat(timespec='microseconds').replace('+00:00', 'Z')
    if not row['sensor_name'].strip():
        raise ValueError('sensor_name: empty')
    for name in ('src_ip', 'dst_ip'):
        out[name] = str(ipaddress.ip_address(row[name]))
    for name in ('src_port', 'dst_port'):
        out[name] = integer(row[name], name, True)
    for name in ('bytes', 'duration_ms'):
        out[name] = integer(row[name], name)
    if row['protocol'] not in ('TCP', 'UDP', 'ICMP'):
        raise ValueError('unknown protocol')
    if row['event_type'] not in EVENT_TYPES:
        raise ValueError('unknown event_type')
    if row['action'] not in ('ALLOW', 'BLOCK'):
        raise ValueError('unknown action')
    return out

def import_csv(conn, path):
    stats = dict(read=0, imported=0, rejected=0, duplicates=0, errors=[])
    with open(path, newline='', encoding='utf-8-sig') as stream, conn:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames) or set(reader.fieldnames) != set(FIELDS):
            raise ValueError('CSV header must contain exactly: ' + ','.join(FIELDS))
        for raw in reader:
            stats['read'] += 1
            try:
                row = validate(raw)
            except (ValueError, TypeError, OverflowError) as exc:
                stats['rejected'] += 1
                stats['errors'].append({'line': reader.line_num, 'reason': str(exc)})
                continue
            digest = hashlib.sha256(json.dumps([row[k] for k in FIELDS], ensure_ascii=False).encode()).hexdigest()
            if conn.execute('SELECT 1 FROM network_events WHERE event_hash=?', (digest,)).fetchone():
                stats['duplicates'] += 1
                continue
            conn.execute('INSERT OR IGNORE INTO sensors(name) VALUES (?)', (row['sensor_name'],))
            sensor = conn.execute('SELECT sensor_id FROM sensors WHERE name=?', (row['sensor_name'],)).fetchone()[0]
            ids = []
            for key in ('src_ip', 'dst_ip'):
                address = row[key]
                conn.execute('INSERT OR IGNORE INTO ip_addresses(address,is_private) VALUES (?,?)', (address, int(ipaddress.ip_address(address).is_private)))
                ids.append(conn.execute('SELECT ip_id FROM ip_addresses WHERE address=?', (address,)).fetchone()[0])
            kind = conn.execute('SELECT event_type_id FROM event_types WHERE code=?', (row['event_type'],)).fetchone()[0]
            conn.execute('''INSERT INTO network_events(event_hash,sensor_id,event_type_id,src_ip_id,dst_ip_id,event_time,src_port,dst_port,protocol,action,bytes,duration_ms)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', (digest,sensor,kind,*ids,row['timestamp'],row['src_port'],row['dst_port'],row['protocol'],row['action'],row['bytes'],row['duration_ms']))
            stats['imported'] += 1
    return stats
