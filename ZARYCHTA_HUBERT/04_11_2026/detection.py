from datetime import datetime, timezone
from config import PORT_SCAN_THRESHOLD, BRUTE_FORCE_THRESHOLD, TRAFFIC_FLOOD_THRESHOLD

RULES = (
    ('PORT_SCAN', 300, PORT_SCAN_THRESHOLD, 'HIGH', False, False),
    ('BRUTE_FORCE', 300, BRUTE_FORCE_THRESHOLD, 'HIGH', True, True),
    ('TRAFFIC_FLOOD', 60, TRAFFIC_FLOOD_THRESHOLD, 'CRITICAL', True, False),
)

def iso(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000000Z')

def detect(conn):
    counts = {}
    with conn:
        for code, seconds, threshold, severity, by_port, auth_only in RULES:
            # SQL fragments below come only from internal rule definitions.
            service = 'COALESCE(e.dst_port,0)' if by_port else '0'
            metric = 'COUNT(DISTINCT e.dst_port)' if code == 'PORT_SCAN' else 'COUNT(*)'
            condition = 't.code = ?' if auth_only else '1=1'
            sql = f'''SELECT e.src_ip_id, e.dst_ip_id, {service} AS service,
                (CAST(strftime('%s',e.event_time) AS INTEGER) / ?) * ? AS bucket,
                COUNT(*) AS n, {metric} AS metric
                FROM network_events e JOIN event_types t USING(event_type_id)
                WHERE {condition}
                GROUP BY e.src_ip_id,e.dst_ip_id,service,bucket HAVING {metric} >= ?
                ORDER BY bucket,e.src_ip_id,e.dst_ip_id,service'''
            params = [seconds, seconds] + (['AUTH_FAILURE'] if auth_only else []) + [threshold]
            created = 0
            for row in conn.execute(sql, params).fetchall():
                src, dst, port, bucket, n, value = tuple(row)
                start, end = iso(bucket), iso(bucket + seconds)
                endpoints = [conn.execute('SELECT address FROM ip_addresses WHERE ip_id=?', (ip,)).fetchone()[0] for ip in (src,dst)]
                desc = f'{code}: {endpoints[0]} -> {endpoints[1]}, service={port or "all/unspecified"}, UTC [{start}, {end}), events={n}, metric={value}, threshold={threshold}'
                cur = conn.execute('''INSERT INTO alerts(rule_code,source_ip_id,target_ip_id,service_port,window_start,window_end,severity,event_count,metric_value,description)
                    VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(rule_code,source_ip_id,target_ip_id,service_port,window_start,window_end)
                    DO UPDATE SET event_count=excluded.event_count,metric_value=excluded.metric_value,description=excluded.description
                    RETURNING alert_id''', (code,src,dst,port,start,end,severity,n,value,desc))
                alert_id = cur.fetchone()[0]
                # Refresh evidence as late arriving events can extend an existing alert.
                conn.execute('DELETE FROM alert_events WHERE alert_id=?', (alert_id,))
                evidence = '''INSERT INTO alert_events(alert_id,event_id)
                    SELECT ?,e.event_id FROM network_events e JOIN event_types t USING(event_type_id)
                    WHERE e.src_ip_id=? AND e.dst_ip_id=? AND e.event_time>=? AND e.event_time<?'''
                args = [alert_id,src,dst,start,end]
                if by_port:
                    evidence += ' AND COALESCE(e.dst_port,0)=?'
                    args.append(port)
                if auth_only:
                    evidence += ' AND t.code=?'
                    args.append('AUTH_FAILURE')
                conn.execute(evidence, args)
                created += 1
            counts[code] = created
    return counts
