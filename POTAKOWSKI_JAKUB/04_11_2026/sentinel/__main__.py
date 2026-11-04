import argparse
import json
import sqlite3
import sys
from pathlib import Path
from .storage import Store,ROOT
from .ingest import ingest
from .engine import analyze,load_rules
from .analytics import REPORTS,render

def main(argv=None):
    parser=argparse.ArgumentParser(description='Sentinel v2: offline SQLite analyzer')
    parser.add_argument('--database',type=Path,default=ROOT/'security.sqlite3')
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('setup')
    imp=commands.add_parser('load');imp.add_argument('csv',type=Path)
    scan=commands.add_parser('analyze');scan.add_argument('--config',type=Path)
    rep=commands.add_parser('show');rep.add_argument('report',choices=REPORTS);rep.add_argument('--format',choices=['text','csv','json'],default='text');rep.add_argument('--save',type=Path)
    state=commands.add_parser('status');state.add_argument('id',type=int);state.add_argument('value',choices=['NEW','INVESTIGATING','CLOSED'])
    proof=commands.add_parser('proof');proof.add_argument('id',type=int)
    demo=commands.add_parser('demo');demo.add_argument('--csv',type=Path,default=ROOT/'data/events.csv')
    args=parser.parse_args(argv)
    try:
        with Store(args.database) as store:
            c=store.connection
            if args.command=='setup':store.initialize();print('Schema ready.')
            elif args.command=='load':print(json.dumps(ingest(store,args.csv),indent=2))
            elif args.command=='analyze':print(json.dumps(analyze(store,load_rules(args.config)),indent=2))
            elif args.command=='show':
                content=render(store,args.report,args.format)
                if args.save:args.save.write_text(content,encoding='utf-8')
                else:print(content)
            elif args.command=='status':
                with c:
                    changed=c.execute('UPDATE incident SET state=? WHERE id=?',(args.value,args.id)).rowcount
                    if not changed:raise ValueError('Incident does not exist')
                print('Status saved.')
            elif args.command=='proof':
                if not c.execute('SELECT 1 FROM incident WHERE id=?',(args.id,)).fetchone():raise ValueError('Incident does not exist')
                rows=c.execute('SELECT o.* FROM observation o JOIN incident_observation p ON p.observation=o.id WHERE p.incident=? ORDER BY o.instant,o.id',(args.id,))
                print(json.dumps([dict(r) for r in rows],indent=2))
            elif args.command=='demo':
                store.initialize();print(json.dumps(ingest(store,args.csv),indent=2))
                print(json.dumps(analyze(store,load_rules()),indent=2))
                for name in REPORTS:print('\n'+name.upper()+'\n'+render(store,name,'text'))
        return 0
    except (OSError,ValueError,sqlite3.Error,KeyError,TypeError) as exc:
        print('Error: '+str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
