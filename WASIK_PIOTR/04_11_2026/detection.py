from datetime import datetime
from db import connect

def run_detection(db_path=None):
    conn = connect(db_path) if db_path else connect()
    cursor = conn.cursor()
    new_alerts_count = 0

    now_str = datetime.utcnow().isoformat()

    # Rule 1: PORT_SCAN
    # Threshold: >= 20 distinct dst_ports, same src_ip + dst_ip, within 5 minutes
    port_scan_query = """
        SELECT 
            src_ip_id, 
            dst_ip_id, 
            strftime('%Y-%m-%dT%H:', event_time) || 
            printf('%02d', (CAST(strftime('%M', event_time) AS INTEGER) / 5) * 5) || ':00' AS bucket_start,
            strftime('%Y-%m-%dT%H:', event_time) || 
            printf('%02d', ((CAST(strftime('%M', event_time) AS INTEGER) / 5) * 5) + 4) || ':59' AS bucket_end,
            COUNT(DISTINCT dst_port) AS distinct_ports
        FROM network_events
        WHERE dst_port IS NOT NULL
        GROUP BY src_ip_id, dst_ip_id, bucket_start
        HAVING COUNT(DISTINCT dst_port) >= 20
    """
    cursor.execute(port_scan_query)
    port_scans = cursor.fetchall()

    for row in port_scans:
        src_ip_id = row['src_ip_id']
        dst_ip_id = row['dst_ip_id']
        w_start = row['bucket_start']
        w_end = row['bucket_end']
        port_count = row['distinct_ports']

        # Get IP string for description
        cursor.execute("SELECT address FROM ip_addresses WHERE ip_id = ?", (src_ip_id,))
        src_ip = cursor.fetchone()['address']
        cursor.execute("SELECT address FROM ip_addresses WHERE ip_id = ?", (dst_ip_id,))
        dst_ip = cursor.fetchone()['address']

        desc = f"Port scan detected: {src_ip} targeted {port_count} distinct ports on {dst_ip} within a 5-minute window."

        try:
            cursor.execute("""
                INSERT INTO alerts (
                    rule_code, source_ip_id, target_ip_id, dst_port, window_start, window_end,
                    severity, event_count, description, status, created_at
                ) VALUES (?, ?, ?, NULL, ?, ?, 'HIGH', ?, ?, 'NEW', ?)
            """, ('PORT_SCAN', src_ip_id, dst_ip_id, w_start, w_end, port_count, desc, now_str))
            new_alerts_count += 1
        except Exception:
            # Duplicate alert ignored due to UNIQUE constraint
            pass

    # Rule 2: BRUTE_FORCE
    # Threshold: >= 8 AUTH_FAILURE events, same src_ip + dst_ip + dst_port, within 5 minutes
    brute_force_query = """
        SELECT 
            ne.src_ip_id, 
            ne.dst_ip_id, 
            ne.dst_port,
            strftime('%Y-%m-%dT%H:', ne.event_time) || 
            printf('%02d', (CAST(strftime('%M', ne.event_time) AS INTEGER) / 5) * 5) || ':00' AS bucket_start,
            strftime('%Y-%m-%dT%H:', ne.event_time) || 
            printf('%02d', ((CAST(strftime('%M', ne.event_time) AS INTEGER) / 5) * 5) + 4) || ':59' AS bucket_end,
            COUNT(*) AS fail_count
        FROM network_events ne
        JOIN event_types et ON ne.event_type_id = et.event_type_id
        WHERE et.code = 'AUTH_FAILURE' AND ne.dst_port IS NOT NULL
        GROUP BY ne.src_ip_id, ne.dst_ip_id, ne.dst_port, bucket_start
        HAVING COUNT(*) >= 8
    """
    cursor.execute(brute_force_query)
    brute_forces = cursor.fetchall()

    for row in brute_forces:
        src_ip_id = row['src_ip_id']
        dst_ip_id = row['dst_ip_id']
        dst_port = row['dst_port']
        w_start = row['bucket_start']
        w_end = row['bucket_end']
        fail_count = row['fail_count']

        cursor.execute("SELECT address FROM ip_addresses WHERE ip_id = ?", (src_ip_id,))
        src_ip = cursor.fetchone()['address']
        cursor.execute("SELECT address FROM ip_addresses WHERE ip_id = ?", (dst_ip_id,))
        dst_ip = cursor.fetchone()['address']

        desc = f"Brute force attempt detected: {src_ip} generated {fail_count} AUTH_FAILURE events on {dst_ip}:{dst_port} within 5 minutes."

        try:
            cursor.execute("""
                INSERT INTO alerts (
                    rule_code, source_ip_id, target_ip_id, dst_port, window_start, window_end,
                    severity, event_count, description, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'HIGH', ?, ?, 'NEW', ?)
            """, ('BRUTE_FORCE', src_ip_id, dst_ip_id, dst_port, w_start, w_end, fail_count, desc, now_str))
            new_alerts_count += 1
        except Exception:
            pass

    # Rule 3: TRAFFIC_FLOOD
    # Threshold: >= 150 events, same src_ip + dst_ip + dst_port, within 1 minute
    flood_query = """
        SELECT 
            src_ip_id, 
            dst_ip_id, 
            dst_port,
            strftime('%Y-%m-%dT%H:%M:00', event_time) AS bucket_start,
            strftime('%Y-%m-%dT%H:%M:59', event_time) AS bucket_end,
            COUNT(*) AS event_count
        FROM network_events
        WHERE dst_port IS NOT NULL
        GROUP BY src_ip_id, dst_ip_id, dst_port, bucket_start
        HAVING COUNT(*) >= 150
    """
    cursor.execute(flood_query)
    floods = cursor.fetchall()

    for row in floods:
        src_ip_id = row['src_ip_id']
        dst_ip_id = row['dst_ip_id']
        dst_port = row['dst_port']
        w_start = row['bucket_start']
        w_end = row['bucket_end']
        ev_count = row['event_count']

        cursor.execute("SELECT address FROM ip_addresses WHERE ip_id = ?", (src_ip_id,))
        src_ip = cursor.fetchone()['address']
        cursor.execute("SELECT address FROM ip_addresses WHERE ip_id = ?", (dst_ip_id,))
        dst_ip = cursor.fetchone()['address']

        desc = f"Traffic flood detected: {src_ip} flooded {dst_ip}:{dst_port} with {ev_count} events in 1 minute."

        try:
            cursor.execute("""
                INSERT INTO alerts (
                    rule_code, source_ip_id, target_ip_id, dst_port, window_start, window_end,
                    severity, event_count, description, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'CRITICAL', ?, ?, 'NEW', ?)
            """, ('TRAFFIC_FLOOD', src_ip_id, dst_ip_id, dst_port, w_start, w_end, ev_count, desc, now_str))
            new_alerts_count += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    print(f"Detection run completed. New alerts generated: {new_alerts_count}")
    return new_alerts_count
