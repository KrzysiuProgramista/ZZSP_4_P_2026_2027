import csv
import io
import json

REPORTS={
 'types': 'SELECT k.name,COUNT(o.id) AS events FROM category k LEFT JOIN observation o ON k.id=o.category GROUP BY k.id ORDER BY events DESC,k.name',
 'sources': 'SELECT h.ip,COUNT(*) AS events FROM host h JOIN observation o ON o.origin=h.id GROUP BY h.id ORDER BY events DESC,h.ip LIMIT 10',
 'services': 'SELECT transport,dport,COUNT(*) AS events FROM observation GROUP BY transport,dport ORDER BY events DESC,transport,dport',
 'states': 'SELECT severity,state,COUNT(*) AS alerts FROM incident GROUP BY severity,state ORDER BY severity,state',
 'timeline': "SELECT strftime('%Y-%m-%dT%H:%M:00Z',instant/1000000,'unixepoch') AS minute_utc,COUNT(*) AS events FROM observation GROUP BY minute_utc ORDER BY minute_utc",
 'targets': 'SELECT h.ip,COUNT(*) AS events FROM host h JOIN observation o ON o.destination=h.id GROUP BY h.id ORDER BY events DESC,h.ip LIMIT 10',
 'unusual-sources': 'SELECT h.ip,COUNT(*) AS events FROM observation o JOIN host h ON h.id=o.origin GROUP BY h.id HAVING COUNT(*)>(SELECT AVG(n) FROM (SELECT COUNT(*) AS n FROM observation GROUP BY origin)) ORDER BY events DESC,h.ip',
 'alerts': 'SELECT i.id,i.rule,s.ip AS source,t.ip AS target,i.port,i.severity,i.state,i.quantity,i.score,i.explanation FROM incident i JOIN host s ON s.id=i.origin JOIN host t ON t.id=i.destination ORDER BY i.id',
}

def render(store,name,fmt):
    cursor=store.connection.execute(REPORTS[name]);headers=[x[0] for x in cursor.description]
    rows=[dict(r) for r in cursor]
    if fmt=='json':return json.dumps(rows,indent=2,ensure_ascii=False)
    if fmt=='csv':
        output=io.StringIO(newline='');writer=csv.DictWriter(output,fieldnames=headers);writer.writeheader();writer.writerows(rows)
        return output.getvalue()
    widths=[max([len(h)]+[len(str(r[h])) for r in rows]) for h in headers]
    def line(values):return ' | '.join(str(v).ljust(w) for v,w in zip(values,widths))
    return '\n'.join([line(headers),'-+-'.join('-'*w for w in widths)]+[line([r[h] for h in headers]) for r in rows])
