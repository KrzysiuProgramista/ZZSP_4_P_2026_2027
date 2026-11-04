import argparse
import json
import sqlite3
import sys
from pathlib import Path
from db import connect, init_db
from importer import import_csv
from detection import detect
from reports import QUERIES, report

def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline Network Security Event Analyzer')
    parser.add_argument('--db', default='network_events.db', help='SQLite database path (before command)')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init-db')
    imp = sub.add_parser('import-csv'); imp.add_argument('path')
    sub.add_parser('summary'); sub.add_parser('detect')
    rep = sub.add_parser('report')
    rep.add_argument('--name', choices=QUERIES, default='alerts')
    rep.add_argument('--format', choices=['text','csv','json'], default='text')
    rep.add_argument('--output')
    status = sub.add_parser('set-status')
    status.add_argument('alert_id', type=int)
    status.add_argument('status', choices=['NEW','INVESTIGATING','CLOSED'])
    evidence = sub.add_parser('evidence'); evidence.add_argument('alert_id',type=int)
    args = parser.parse_args(argv)
    try:
        with connect(args.db) as conn:
            if args.command == 'init-db':
                init_db(conn); print('Database initialised.')
            elif args.command == 'import-csv':
                print(json.dumps(import_csv(conn,args.path), indent=2))
            elif args.command == 'detect':
                print(json.dumps(detect(conn),indent=2))
            elif args.command == 'summary':
                for table in ('sensors','ip_addresses','event_types','network_events','alerts'):
                    print(f'{table}: {conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]}')
                for name in ('event-types','top-sources','services','alerts-overview','timeline','top-targets','above-average-sources'):
                    print('\n' + name + '\n' + report(conn,name))
            elif args.command == 'report':
                result = report(conn,args.name,args.format)
                if args.output:
                    Path(args.output).write_text(result,encoding='utf-8')
                else:
                    print(result)
            elif args.command == 'set-status':
                with conn:
                    cur=conn.execute('UPDATE alerts SET status=? WHERE alert_id=?',(args.status,args.alert_id))
                    if not cur.rowcount: raise ValueError('Unknown alert ID')
                print('Status updated.')
            elif args.command == 'evidence':
                if not conn.execute('SELECT 1 FROM alerts WHERE alert_id=?',(args.alert_id,)).fetchone():
                    raise ValueError('Unknown alert ID')
                rows=conn.execute('SELECT e.* FROM network_events e JOIN alert_events a USING(event_id) WHERE a.alert_id=? ORDER BY e.event_time,e.event_id',(args.alert_id,))
                print(json.dumps([dict(r) for r in rows],indent=2))
        return 0
    except (OSError,ValueError,sqlite3.Error) as exc:
        print(f'Error: {exc}',file=sys.stderr)
        return 1
