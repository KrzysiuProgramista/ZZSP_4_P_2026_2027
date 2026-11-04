import csv
import hashlib
import ipaddress
from datetime import datetime
from db import connect

def is_private_ip(ip_str):
    try:
        return 1 if ipaddress.ip_address(ip_str).is_private else 0
    except ValueError:
        return 0

def validate_row(row, row_num):
    # Required columns check
    required_cols = ['timestamp', 'sensor_name', 'src_ip', 'dst_ip', 'protocol', 'event_type', 'action', 'bytes', 'duration_ms']
    for col in required_cols:
        if col not in row or not row[col].strip():
            return False, f"Missing required column '{col}'"

    # Validate ISO 8601 timestamp
    try:
        dt = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
    except Exception:
        return False, f"Invalid timestamp format: '{row['timestamp']}'"

    # Validate IP addresses
    for ip_field in ['src_ip', 'dst_ip']:
        try:
            ipaddress.ip_address(row[ip_field])
        except ValueError:
            return False, f"Invalid IP address in {ip_field}: '{row[ip_field]}'"

    # Validate ports if present
    for port_field in ['src_port', 'dst_port']:
        val = row.get(port_field, '').strip()
        if val:
            try:
                port = int(val)
                if not (1 <= port <= 65535):
                    return False, f"Port out of range 1-65535 in {port_field}: {port}"
            except ValueError:
                return False, f"Invalid integer port in {port_field}: '{val}'"

    # Validate protocol
    proto = row['protocol'].upper()
    if proto not in ['TCP', 'UDP', 'ICMP']:
        return False, f"Invalid protocol: '{proto}'"

    # Validate action
    act = row['action'].upper()
    if act not in ['ALLOW', 'BLOCK']:
        return False, f"Invalid action: '{act}'"

    # Validate non-negative integers
    for num_field in ['bytes', 'duration_ms']:
        try:
            val = int(row[num_field])
            if val < 0:
                return False, f"Negative value in {num_field}: {val}"
        except ValueError:
            return False, f"Invalid integer in {num_field}: '{row[num_field]}'"

    return True, None

def compute_event_hash(row):
    raw_key = f"{row['timestamp']}|{row['sensor_name']}|{row['src_ip']}|{row['dst_ip']}|{row.get('src_port','')}|{row.get('dst_port','')}|{row['protocol']}|{row['event_type']}|{row['action']}|{row['bytes']}|{row['duration_ms']}"
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

def import_csv(file_path, db_path=None):
    conn = connect(db_path) if db_path else connect()
    
    total_read = 0
    imported = 0
    rejected = 0
    duplicates = 0

    sensor_cache = {}
    ip_cache = {}
    event_type_cache = {}

    # Helper function to get or insert sensor
    def get_or_create_sensor(cursor, name):
        if name in sensor_cache:
            return sensor_cache[name]
        cursor.execute("SELECT sensor_id FROM sensors WHERE name = ?", (name,))
        res = cursor.fetchone()
        if res:
            sensor_id = res['sensor_id']
        else:
            cursor.execute("INSERT INTO sensors (name) VALUES (?)", (name,))
            sensor_id = cursor.lastrowid
        sensor_cache[name] = sensor_id
        return sensor_id

    # Helper function to get or insert IP
    def get_or_create_ip(cursor, address):
        if address in ip_cache:
            return ip_cache[address]
        cursor.execute("SELECT ip_id FROM ip_addresses WHERE address = ?", (address,))
        res = cursor.fetchone()
        if res:
            ip_id = res['ip_id']
        else:
            priv = is_private_ip(address)
            cursor.execute("INSERT INTO ip_addresses (address, is_private) VALUES (?, ?)", (address, priv))
            ip_id = cursor.lastrowid
        ip_cache[address] = ip_id
        return ip_id

    # Helper function to get or insert event type
    def get_or_create_event_type(cursor, code):
        if code in event_type_cache:
            return event_type_cache[code]
        cursor.execute("SELECT event_type_id FROM event_types WHERE code = ?", (code,))
        res = cursor.fetchone()
        if res:
            et_id = res['event_type_id']
        else:
            cursor.execute("INSERT INTO event_types (code) VALUES (?)", (code,))
            et_id = cursor.lastrowid
        event_type_cache[code] = et_id
        return et_id

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with conn:
            cursor = conn.cursor()
            for row_num, row in enumerate(reader, start=2):
                total_read += 1
                is_valid, error_msg = validate_row(row, row_num)
                if not is_valid:
                    print(f"Row {row_num}: REJECTED - {error_msg}")
                    rejected += 1
                    continue

                event_hash = compute_event_hash(row)
                cursor.execute("SELECT event_id FROM network_events WHERE event_hash = ?", (event_hash,))
                if cursor.fetchone():
                    duplicates += 1
                    continue

                sensor_id = get_or_create_sensor(cursor, row['sensor_name'].strip())
                src_ip_id = get_or_create_ip(cursor, row['src_ip'].strip())
                dst_ip_id = get_or_create_ip(cursor, row['dst_ip'].strip())
                event_type_id = get_or_create_event_type(cursor, row['event_type'].strip())

                src_port = int(row['src_port']) if row.get('src_port', '').strip() else None
                dst_port = int(row['dst_port']) if row.get('dst_port', '').strip() else None

                cursor.execute("""
                    INSERT INTO network_events (
                        sensor_id, event_type_id, src_ip_id, dst_ip_id, event_time,
                        src_port, dst_port, protocol, action, bytes, duration_ms, event_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sensor_id, event_type_id, src_ip_id, dst_ip_id, row['timestamp'].strip(),
                    src_port, dst_port, row['protocol'].strip().upper(), row['action'].strip().upper(),
                    int(row['bytes']), int(row['duration_ms']), event_hash
                ))
                imported += 1

    conn.close()
    summary = {
        'total_read': total_read,
        'imported': imported,
        'rejected': rejected,
        'duplicates': duplicates
    }
    print(f"--- Import Summary ---")
    print(f"Total rows read: {total_read}")
    print(f"Successfully imported: {imported}")
    print(f"Rejected rows: {rejected}")
    print(f"Duplicates skipped: {duplicates}")
    return summary
