import csv
import ipaddress
from datetime import datetime
from db import get_connection


def is_valid_ip(ip_str):
  try:
    ipaddress.ip_address(ip_str)
    return True
  except ValueError:
    return False


def import_csv(file_path):
  conn = get_connection()
  cursor = conn.cursor()

  read_count = 0
  imported_count = 0
  rejected_count = 0
  duplicate_count = 0

  sensors_cache = {}
  ip_cache = {}
  types_cache = {}

  def get_or_create_sensor(name):
    if name in sensors_cache:
      return sensors_cache[name]
    cursor.execute(
        "INSERT OR IGNORE INTO sensors (name) VALUES (?)", (name,)
    )
    cursor.execute("SELECT sensor_id FROM sensors WHERE name = ?", (name,))
    row = cursor.fetchone()
    sensors_cache[name] = row["sensor_id"]
    return row["sensor_id"]

  def get_or_create_ip(ip_str):
    if ip_str in ip_cache:
      return ip_cache[ip_str]
    try:
      obj = ipaddress.ip_address(ip_str)
      is_priv = 1 if obj.is_private else 0
    except ValueError:
      is_priv = 0
    cursor.execute(
        "INSERT OR IGNORE INTO ip_addresses (address, is_private) VALUES (?, ?)",
        (ip_str, is_priv),
    )
    cursor.execute("SELECT ip_id FROM ip_addresses WHERE address = ?", (ip_str,))
    row = cursor.fetchone()
    ip_cache[ip_str] = row["ip_id"]
    return row["ip_id"]

  def get_or_create_event_type(code):
    if code in types_cache:
      return types_cache[code]
    cursor.execute(
        "INSERT OR IGNORE INTO event_types (code, default_severity) VALUES (?,"
        " ?)",
        (code, "MEDIUM"),
    )
    cursor.execute(
        "SELECT event_type_id FROM event_types WHERE code = ?", (code,)
    )
    row = cursor.fetchone()
    types_cache[code] = row["event_type_id"]
    return row["event_type_id"]

  try:
    with open(file_path, mode="r", encoding="utf-8") as f:
      reader = csv.DictReader(f)
      for row_idx, row in enumerate(reader, start=2):
        read_count += 1
        try:
          timestamp = row["timestamp"].strip()
          datetime.fromisoformat(timestamp)

          sensor_name = row["sensor_name"].strip()
          if not sensor_name:
            raise ValueError("Pusta nazwa sensora")

          src_ip = row["src_ip"].strip()
          dst_ip = row["dst_ip"].strip()
          if not is_valid_ip(src_ip) or not is_valid_ip(dst_ip):
            raise ValueError(f"Niepoprawny adres IP: {src_ip} lub {dst_ip}")

          src_port = (
              int(row["src_port"])
              if row["src_port"].strip()
              else None
          )
          dst_port = (
              int(row["dst_port"])
              if row["dst_port"].strip()
              else None
          )
          if src_port and not (1 <= src_port <= 65535):
            raise ValueError("Port źródłowy poza zakresem")
          if dst_port and not (1 <= dst_port <= 65535):
            raise ValueError("Port docelowy poza zakresem")

          protocol = row["protocol"].strip().upper()
          if protocol not in ("TCP", "UDP", "ICMP"):
            raise ValueError(f"Nieznany protokół: {protocol}")

          event_type = row["event_type"].strip()
          bytes_val = int(row["bytes"])
          if bytes_val < 0:
            raise ValueError("Ujemna liczba bajtów")

          s_id = get_or_create_sensor(sensor_name)
          src_ip_id = get_or_create_ip(src_ip)
          dst_ip_id = get_or_create_ip(dst_ip)
          et_id = get_or_create_event_type(event_type)

          cursor.execute(
              """
                        SELECT event_id FROM network_events 
                        WHERE sensor_id = ? AND event_type_id = ? AND src_ip_id = ? 
                          AND dst_ip_id = ? AND event_time = ? AND dst_port = ?
                    """,
              (s_id, et_id, src_ip_id, dst_ip_id, timestamp, dst_port),
          )
          if cursor.fetchone():
            duplicate_count += 1
            continue

          cursor.execute(
              """
                        INSERT INTO network_events 
                        (sensor_id, event_type_id, src_ip_id, dst_ip_id, event_time, src_port, dst_port, protocol, bytes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
              (
                  s_id,
                  et_id,
                  src_ip_id,
                  dst_ip_id,
                  timestamp,
                  src_port,
                  dst_port,
                  protocol,
                  bytes_val,
              ),
          )
          imported_count += 1

        except Exception as e:
          rejected_count += 1
          print(f"[-] Odrzucono wiersz {row_idx}: {e}")

    conn.commit()
  except Exception as e:
    conn.rollback()
    print(f"[-] Błąd krytyczny podczas importu: {e}")
  finally:
    conn.close()

  print("\n--- PODSUMOWANIE ---")
  print(f"Przeczytano wierszy: {read_count}")
  print(f"Zaimportowano pomyślnie: {imported_count}")
  print(f"Odrzucono (błędy walidacji): {rejected_count}")
  print(f"Pominięto duplikatów: {duplicate_count}")
