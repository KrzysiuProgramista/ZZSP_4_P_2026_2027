import csv
import os
from db import connect

def get_event_volume_by_type(conn):
    query = """
        SELECT et.code AS event_type, COUNT(ne.event_id) AS total_events
        FROM network_events ne
        JOIN event_types et ON ne.event_type_id = et.event_type_id
        GROUP BY et.code
        ORDER BY total_events DESC;
    """
    return conn.execute(query).fetchall()

def get_top_source_ips(conn, limit=10):
    query = """
        SELECT ip.address AS source_ip, COUNT(ne.event_id) AS event_count
        FROM network_events ne
        JOIN ip_addresses ip ON ne.src_ip_id = ip.ip_id
        GROUP BY ip.address
        ORDER BY event_count DESC
        LIMIT ?;
    """
    return conn.execute(query, (limit,)).fetchall()

def get_top_targeted_services(conn, limit=10):
    query = """
        SELECT dst_port, protocol, COUNT(event_id) AS request_count
        FROM network_events
        WHERE dst_port IS NOT NULL
        GROUP BY dst_port, protocol
        ORDER BY request_count DESC
        LIMIT ?;
    """
    return conn.execute(query, (limit,)).fetchall()

def get_alerts_overview(conn):
    query = """
        SELECT severity, status, COUNT(alert_id) AS alert_count
        FROM alerts
        GROUP BY severity, status
        ORDER BY severity, status;
    """
    return conn.execute(query).fetchall()

def get_timeline(conn):
    query = """
        SELECT strftime('%Y-%m-%dT%H:%M:00', event_time) AS time_bucket, COUNT(event_id) AS event_count
        FROM network_events
        GROUP BY time_bucket
        ORDER BY time_bucket;
    """
    return conn.execute(query).fetchall()

def get_top_targets(conn, limit=10):
    query = """
        SELECT ip.address AS target_ip, COUNT(ne.event_id) AS event_count
        FROM network_events ne
        JOIN ip_addresses ip ON ne.dst_ip_id = ip.ip_id
        GROUP BY ip.address
        ORDER BY event_count DESC
        LIMIT ?;
    """
    return conn.execute(query, (limit,)).fetchall()

def run_reports(fmt="text", output_dir="reports", db_path=None):
    conn = connect(db_path) if db_path else connect()
    
    reports = {
        "event_volume": (get_event_volume_by_type(conn), ["event_type", "total_events"]),
        "top_source_ips": (get_top_source_ips(conn), ["source_ip", "event_count"]),
        "top_targeted_services": (get_top_targeted_services(conn), ["dst_port", "protocol", "request_count"]),
        "alerts_overview": (get_alerts_overview(conn), ["severity", "status", "alert_count"]),
        "timeline": (get_timeline(conn), ["time_bucket", "event_count"]),
        "top_targets": (get_top_targets(conn), ["target_ip", "event_count"])
    }

    if fmt == "csv":
        os.makedirs(output_dir, exist_ok=True)
        for name, (data, headers) in reports.items():
            filepath = os.path.join(output_dir, f"{name}.csv")
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for row in data:
                    writer.writerow(list(row))
            print(f"Report written to {filepath}")
    else:
        print("========================================")
        print("      NETWORK SECURITY ANALYTICS REPORT  ")
        print("========================================\n")
        
        for name, (data, headers) in reports.items():
            print(f"--- Report: {name.replace('_', ' ').title()} ---")
            header_str = " | ".join([h.upper() for h in headers])
            print(header_str)
            print("-" * len(header_str))
            for row in data:
                print(" | ".join([str(val) for val in row]))
            print("\n")
            
    conn.close()
