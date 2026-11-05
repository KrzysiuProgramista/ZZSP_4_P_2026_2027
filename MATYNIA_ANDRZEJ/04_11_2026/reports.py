from db import get_connection


def print_reports():
  conn = get_connection()
  cursor = conn.cursor()

  print("\n=== RAPORT 1: Wolumen zdarzeń według typu ===")
  cursor.execute("""
        SELECT et.code, COUNT(ne.event_id) as total 
        FROM event_types et
        LEFT JOIN network_events ne ON et.event_type_id = ne.event_type_id
        GROUP BY et.code
        ORDER BY total DESC;
    """)
  for row in cursor.fetchall():
    print(f" - {row['code']}: {row['total']} zdarzeń")

  print("\n=== RAPORT 2: Top 10 adresów źródłowych ===")
  cursor.execute("""
        SELECT ip.address, COUNT(ne.event_id) as total 
        FROM network_events ne
        JOIN ip_addresses ip ON ne.src_ip_id = ip.ip_id
        GROUP BY ip.address
        ORDER BY total DESC
        LIMIT 10;
    """)
  for row in cursor.fetchall():
    print(f" - IP {row['address']}: {row['total']} zdarzeń")

  print("\n=== RAPORT 3: Najczęściej atakowane / celowane porty ===")
  cursor.execute("""
        SELECT dst_port, COUNT(event_id) as total 
        FROM network_events 
        WHERE dst_port IS NOT NULL
        GROUP BY dst_port
        ORDER BY total DESC
        LIMIT 5;
    """)
  for row in cursor.fetchall():
    print(f" - Port {row['dst_port']}: {row['total']} zdarzeń")

  print("\n=== RAPORT 4: Przegląd alertów (wg ważności i statusu) ===")
  cursor.execute("""
        SELECT rule_code, severity, status, COUNT(*) as count 
        FROM alerts
        GROUP BY rule_code, severity, status;
    """)
  rows = cursor.fetchall()
  if not rows:
    print(" Brak aktywnych alertów.")
  for row in rows:
    print(
        f" - [{row['severity']}] {row['rule_code']} ({row['status']}):"
        f" {row['count']}"
    )

  conn.close()
