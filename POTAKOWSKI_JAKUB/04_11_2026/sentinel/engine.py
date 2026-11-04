"""SQL candidate discovery over event-anchored rolling windows."""
import hashlib
import json
from .model import utc
from .storage import ROOT

def load_rules(path=None):
    rules=json.loads((ROOT/'settings.json' if path is None else path).read_text(encoding='utf-8'))
    if set(rules)!={'PORT_SCAN','BRUTE_FORCE','TRAFFIC_FLOOD'}:raise ValueError('Three required rule names expected')
    for cfg in rules.values():
        for key in ('seconds','threshold'):
            if type(cfg.get(key)) is not int or cfg[key]<1 or cfg[key]>1000000:raise ValueError('Invalid rule '+key)
        if cfg.get('severity') not in ('HIGH','CRITICAL'):raise ValueError('Invalid severity')
    return rules

def analyze(store,rules):
    c=store.connection;counts={}
    with c:
        for code,cfg in rules.items():
            span=cfg['seconds']*1000000
            by_service=code!='PORT_SCAN'
            # These expressions are chosen only from internal constants.
            service='b.dport IS a.dport' if by_service else '1=1'
            auth="AND b.category=(SELECT id FROM category WHERE name='AUTH_FAILURE')" if code=='BRUTE_FORCE' else ''
            metric='COUNT(DISTINCT b.dport)' if code=='PORT_SCAN' else 'COUNT(*)'
            candidates=c.execute(f'''WITH anchors AS (SELECT DISTINCT origin,destination,{'dport' if by_service else 'NULL AS dport'},instant FROM observation) SELECT a.origin,a.destination,{'a.dport' if by_service else 'NULL'} AS port,
                a.instant AS start,COUNT(*) AS quantity,{metric} AS score
                FROM anchors a JOIN observation b ON b.origin=a.origin AND b.destination=a.destination
                AND b.instant>=a.instant AND b.instant<a.instant+? AND {service} {auth}
                GROUP BY a.origin,a.destination,port,a.instant HAVING {metric}>=?
                ORDER BY score DESC,quantity DESC,start,a.origin,a.destination,port''',(span,cfg['threshold'])).fetchall()
            # Choose strongest non-overlapping windows for each endpoint/service group.
            # This prevents one burst from creating an alert at every event timestamp.
            selected=[]
            for r in candidates:
                key=(r['origin'],r['destination'],r['port'])
                if any(k==key and r['start']<end and start<r['start']+span for k,start,end in selected):continue
                selected.append((key,r['start'],r['start']+span))
                src,dst,port=key;start=r['start'];end=start+span
                signature=hashlib.sha256(json.dumps([code,*key,start,end],separators=(',',':')).encode()).hexdigest()
                ips=[c.execute('SELECT ip FROM host WHERE id=?',(i,)).fetchone()[0] for i in (src,dst)]
                desc=f"{code}: {ips[0]} -> {ips[1]}, port={port}, UTC [{utc(start)}, {utc(end)}), events={r['quantity']}, metric={r['score']} >= {cfg['threshold']}"
                c.execute('''INSERT INTO incident(signature,rule,origin,destination,port,start_us,stop_us,severity,quantity,score,explanation)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(signature) DO UPDATE SET quantity=excluded.quantity,score=excluded.score,explanation=excluded.explanation,severity=excluded.severity''',
                    (signature,code,src,dst,port,start,end,cfg['severity'],r['quantity'],r['score'],desc))
                incident=c.execute('SELECT id FROM incident WHERE signature=?',(signature,)).fetchone()[0]
                c.execute('DELETE FROM incident_observation WHERE incident=?',(incident,))
                statement='''INSERT INTO incident_observation(incident,observation) SELECT ?,b.id FROM observation b
                    WHERE b.origin=? AND b.destination=? AND b.instant>=? AND b.instant<?'''
                params=[incident,src,dst,start,end]
                if by_service:statement+=' AND b.dport IS ?';params.append(port)
                if auth:statement+=auth
                c.execute(statement,params)
            counts[code]=len(selected)
    return counts
