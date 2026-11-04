"""Command-line interface."""
import argparse
import logging
import sys
from pathlib import Path

from config import ALERT_STATUSES
from db import connect, has_schema, init_db, transaction
from detection import run_detection
from importer import import_csv
from reports import REPORTS, format_text, run_report, write_csv


def _open(db_path):
    if not Path(db_path).exists():
        raise SystemExit(f"Database {db_path} not found. Run: python main.py init-db")
    conn = connect(db_path)
    if not has_schema(conn):
        conn.close()
        raise SystemExit("Database has no schema. Run: python main.py init-db")
    return conn


def cmd_init_db(args):
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    init_db(args.db)
    print(f"Database ready: {args.db}")


def cmd_import(args):
    conn = _open(args.db)
    try:
        r = import_csv(conn, args.path)
    finally:
        conn.close()
    print(f"Import summary for {args.path}")
    print(f"  read:       {r.read}")
    print(f"  imported:   {r.imported}")
    print(f"  rejected:   {r.rejected}")
    print(f"  duplicates: {r.duplicates}")
    for line_no, reason in r.rejects[:50]:
        print(f"  line {line_no}: {reason}")
    if r.rejected > 50:
        print(f"  ... and {r.rejected - 50} more (see logs)")


def cmd_summary(args):
    conn = _open(args.db)
    try:
        q = lambda sql: conn.execute(sql).fetchone()[0]
        span = conn.execute("SELECT MIN(event_time), MAX(event_time) FROM network_events").fetchone()
        print("Database summary")
        print(f"  events:        {q('SELECT COUNT(*) FROM network_events')}")
        print(f"  time range:    {span[0]} .. {span[1]} (UTC)")
        print(f"  sensors:       {q('SELECT COUNT(*) FROM sensors')}")
        print(f"  IP addresses:  {q('SELECT COUNT(*) FROM ip_addresses')}")
        print(f"  alerts:        {q('SELECT COUNT(*) FROM alerts')}")
        open_alerts = q("SELECT COUNT(*) FROM alerts WHERE status <> 'CLOSED'")
        print(f"  open alerts:   {open_alerts}")
    finally:
        conn.close()


def cmd_detect(args):
    conn = _open(args.db)
    try:
        summary = run_detection(conn)
    finally:
        conn.close()
    print("Detection run")
    for rule, (matches, new) in summary.items():
        print(f"  {rule:<14} matches: {matches:<4} new alerts: {new}")


def cmd_report(args):
    conn = _open(args.db)
    names = list(REPORTS) if args.name == "all" else [args.name]
    try:
        for name in names:
            title, headers, rows = run_report(conn, name)
            if args.format == "csv":
                path = Path(args.out_dir) / f"{name}.csv"
                write_csv(path, headers, rows)
                print(f"Wrote {path} ({len(rows)} rows)")
            else:
                print(f"\n== {title} ==")
                print(format_text(headers, rows))
    finally:
        conn.close()


def cmd_alerts(args):
    conn = _open(args.db)
    try:
        title, headers, rows = run_report(conn, "alerts")
        if args.status:
            idx = headers.index("status")
            rows = [r for r in rows if r[idx] == args.status]
        print(format_text(headers, rows))
    finally:
        conn.close()


def cmd_alert_status(args):
    conn = _open(args.db)
    try:
        with transaction(conn):
            cur = conn.execute("UPDATE alerts SET status = ? WHERE alert_id = ?",
                               (args.status, args.alert_id))
        if cur.rowcount == 0:
            raise SystemExit(f"No alert with id {args.alert_id}")
        print(f"Alert {args.alert_id} status set to {args.status}")
    finally:
        conn.close()


def build_parser():
    p = argparse.ArgumentParser(prog="network-analyzer",
                                description="Rule-based analysis of network event CSV files.")
    p.add_argument("--db", default="data/analyzer.db", help="SQLite database path")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="create tables and indexes").set_defaults(func=cmd_init_db)

    s = sub.add_parser("import-csv", help="validate and import a CSV file")
    s.add_argument("path")
    s.set_defaults(func=cmd_import)

    sub.add_parser("summary", help="database overview").set_defaults(func=cmd_summary)
    sub.add_parser("detect", help="run detection rules and store alerts").set_defaults(func=cmd_detect)

    s = sub.add_parser("report", help="run SQL reports")
    s.add_argument("--name", default="all", choices=["all", *REPORTS])
    s.add_argument("--format", default="text", choices=["text", "csv"])
    s.add_argument("--out-dir", default="reports")
    s.set_defaults(func=cmd_report)

    s = sub.add_parser("alerts", help="list alerts")
    s.add_argument("--status", choices=ALERT_STATUSES)
    s.set_defaults(func=cmd_alerts)

    s = sub.add_parser("alert-status", help="update an alert's status")
    s.add_argument("alert_id", type=int)
    s.add_argument("status", choices=ALERT_STATUSES)
    s.set_defaults(func=cmd_alert_status)
    return p


def main(argv=None):
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0
