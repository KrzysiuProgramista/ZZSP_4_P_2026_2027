import sqlite3
from datetime import datetime
from db import get_connection


def run_detections():
  conn = get_connection()
  cursor = conn.cursor()
  now_str = datetime.utcnow().isoformat()

  alerts_created = 0

  cursor.execute("""
        SELECT 
            ne.src_ip_id, 
            ne.dst_ip_id,
            strftime('%Y-%m-%d %H:', ne.event_time) || 
            printf('%02d', (CAST(strftime('%M', ne.event_time) AS INTEGER) / 5) * 5) AS bucket_5m,
            COUNT(DISTINCT ne.dst_port) AS unique_ports,
            MIN(ne.event_time) as win_start,
            MAX(ne.event_time) as win_end
        FROM network_events ne
        GROUP BY ne.src_ip_id, ne.dst_ip_id, bucket_5m
        HAVING unique_ports >= 20
    """)

  for row in cursor.fetchall():
    try:
      cursor.execute(
          """
                INSERT INTO alerts 
                (rule_code, source_ip_id, target_ip_id, severity, event_count, window_start, window_end, description, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?)
            """,
          (
              "PORT_SCAN",
              row["src_ip_id"],
              row["dst_ip_id"],
              "HIGH",
              row["unique_ports"],
              row["win_start"],
              row["win_end"],
              (
                  f"Wykryto skanowanie portów: {row['unique_ports']} unikalnych"
                  " portów."
              ),
              now_str,
          ),
      )
      alerts_created += 1
    except sqlite3.IntegrityError:
      pass

  cursor.execute("""
        SELECT 
            ne.src_ip_id, 
            ne.dst_ip_id,
            ne.dst_port,
            strftime('%Y-%m-%d %H:', ne.event_time) || 
            printf('%02d', (CAST(strftime('%M', ne.event_time) AS INTEGER) / 5) * 5) AS bucket_5m,
            COUNT(*) as fail_count,
            MIN(ne.event_time) as win_start,
            MAX(ne.event_time) as win_end
        FROM network_events ne
        JOIN event_types et ON ne.event_type_id = et.event_type_id
        WHERE et.code = 'AUTH_FAILURE'
        GROUP BY ne.src_ip_id, ne.dst_ip_id, ne.dst_port, bucket_5m
        HAVING fail_count >= 8
    """)

  for row in cursor.fetchall():
    try:
      cursor.execute(
          """
                INSERT INTO alerts 
                (rule_code, source_ip_id, target_ip_id, severity, event_count, window_start, window_end, description, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?)
            """,
          (
              "BRUTE_FORCE",
              row["src_ip_id"],
              row["dst_ip_id"],
              "HIGH",
              row["fail_count"],
              row["win_start"],
              row["win_end"],
              (
                  f"Podejrzenie ataku Brute-Force: {row['fail_count']} nieudanych"
                  f" autoryzacji na porcie {row['dst_port']}."
              ),
              now_str,
          ),
      )
      alerts_created += 1
    except sqlite3.IntegrityError:
      pass

  cursor.execute("""
        SELECT 
            ne.src_ip_id, 
            ne.dst_ip_id,
            ne.dst_port,
            strftime('%Y-%m-%d %H:%M', ne.event_time) AS bucket_1m,
            COUNT(*) as event_count,
            MIN(ne.event_time) as win_start,
            MAX(ne.event_time) as win_end
        FROM network_events ne
        GROUP BY ne.src_ip_id, ne.dst_ip_id, ne.dst_port, bucket_1m
        HAVING event_count >= 150
    """)

  for row in cursor.fetchall():
    try:
      cursor.execute(
          """
                INSERT INTO alerts 
                (rule_code, source_ip_id, target_ip_id, severity, event_count, window_start, window_end, description, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'NEW', ?)
            """,
          (
              "TRAFFIC_FLOOD",
              row["src_ip_id"],
              row["dst_ip_id"],
              "CRITICAL",
              row["event_count"],
              row["win_start"],
              row["win_end"],
              (
                  f"Wykryto powódź ruchu (Flood): {row['event_count']} zdarzeń"
                  f" w 1 minutę na porcie {row['dst_port']}."
              ),
              now_str,
          ),
      )
      alerts_created += 1
    except sqlite3.IntegrityError:
      pass

  conn.commit()
  conn.close()
  print(f"[+] Zakończono detekcję. Nowo utworzone alerty: {alerts_created}")
