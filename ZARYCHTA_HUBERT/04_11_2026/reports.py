import csv
import io
import json

QUERIES = {
 'event-types': '''SELECT t.code AS event_type,COUNT(e.event_id) AS events FROM event_types t LEFT JOIN network_events e USING(event_type_id) GROUP BY t.event_type_id ORDER BY events DESC,t.code''',
 'top-sources': '''SELECT i.address,COUNT(*) AS events FROM network_events e JOIN ip_addresses i ON i.ip_id=e.src_ip_id GROUP BY i.ip_id ORDER BY events DESC,i.address LIMIT 10''',
 'services': '''SELECT protocol,dst_port,COUNT(*) AS events FROM network_events GROUP BY protocol,dst_port ORDER BY events DESC,protocol,dst_port''',
 'alerts-overview': '''SELECT severity,status,COUNT(*) AS alerts FROM alerts GROUP BY severity,status ORDER BY severity,status''',
 'timeline': '''SELECT strftime('%Y-%m-%dT%H:%M:00Z',(CAST(strftime('%s',event_time) AS INTEGER)/300)*300,'unixepoch') AS bucket_utc,COUNT(*) AS events FROM network_events GROUP BY bucket_utc ORDER BY bucket_utc''',
 'top-targets': '''SELECT i.address,COUNT(*) AS events FROM network_events e JOIN ip_addresses i ON i.ip_id=e.dst_ip_id GROUP BY i.ip_id ORDER BY events DESC,i.address LIMIT 10''',
 'alerts': '''SELECT a.alert_id,a.rule_code,s.address AS source,d.address AS target,a.service_port,a.window_start,a.window_end,a.severity,a.status,a.event_count,a.metric_value,a.description FROM alerts a JOIN ip_addresses s ON s.ip_id=a.source_ip_id JOIN ip_addresses d ON d.ip_id=a.target_ip_id ORDER BY a.alert_id''',
 'above-average-sources': '''SELECT i.address,COUNT(*) AS events FROM network_events e JOIN ip_addresses i ON i.ip_id=e.src_ip_id GROUP BY i.ip_id HAVING COUNT(*) > (SELECT AVG(n) FROM (SELECT COUNT(*) AS n FROM network_events GROUP BY src_ip_id)) ORDER BY events DESC,i.address''',
}

def report(conn, name, fmt='text'):
    cur = conn.execute(QUERIES[name])
    headers = [x[0] for x in cur.description]
    rows = [dict(r) for r in cur]
    if fmt == 'json':
        return json.dumps(rows, indent=2, ensure_ascii=False)
    if fmt == 'csv':
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        return stream.getvalue()
    return '\t'.join(headers) + '\n' + '\n'.join('\t'.join(str(r[h]) for h in headers) for r in rows)
