import argparse
import sqlite3
from pathlib import Path

folder = Path(__file__).resolve().parent / 'database'
parser = argparse.ArgumentParser()
parser.add_argument('--path', type=Path, default=folder / 'workshop.db')
args = parser.parse_args()
if args.path.exists():
    parser.error('Database already exists; choose another --path to prevent duplicate seed rows')
args.path.parent.mkdir(parents=True, exist_ok=True)
try:
    with sqlite3.connect(args.path) as conn:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.executescript((folder / 'schema.sql').read_text(encoding='utf-8'))
        conn.executescript((folder / 'seed.sql').read_text(encoding='utf-8'))
        print('Database initialized:', args.path)
except Exception:
    args.path.unlink(missing_ok=True)
    raise
