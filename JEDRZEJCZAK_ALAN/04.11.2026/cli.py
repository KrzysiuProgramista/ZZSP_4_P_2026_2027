"""Command-line interface for import, detect, inspect and report."""
import argparse
import csv
from pathlib import Path
import sqlite3
import sys

from db import DEFAULT_DB_PATH, connect, init_db
from importer import import_csv
from detection import detect
from reports import (REPORTS, show_summary, write_report, show_alerts,
                     update_alert_status, explain_alert)


def build_parser():
    parser = argparse.ArgumentParser(description="Network Security Event Analyzer (offline, synthetic CSV)")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="SQLite database path")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("init-db", help="Create schema and seed known event types")
    csvcmd = subs.add_parser("import-csv", help="Validate and import event CSV")
    csvcmd.add_argument("file",type=Path)
    subs.add_parser("summary", help="Print database summary")
    subs.add_parser("detect", help="Run three detection rules and persist evidence")
    report = subs.add_parser("report",help="Show or export SQL analytical reports")
    report.add_argument("--name",choices=["all", *REPORTS.keys()],default="all")
    report.add_argument("--format",choices=["text","csv"],default="text")
    report.add_argument("--output",type=Path)
    alerts = subs.add_parser("alerts",help="Inspect stored alerts")
    alerts.add_argument("--status",choices=["NEW","INVESTIGATING","CLOSED"])
    status = subs.add_parser("set-status",help="Change stored alert lifecycle status")
    status.add_argument("alert_id",type=int)
    status.add_argument("status",choices=["NEW","INVESTIGATING","CLOSED"])
    explain = subs.add_parser("explain-alert",help="Explain alert and show linked evidence")
    explain.add_argument("alert_id",type=int)
    return parser


def run(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.db.parent.mkdir(parents=True,exist_ok=True)
        with connect(args.db) as conn:
            if args.command == "init-db":
                init_db(conn)
                print(f"Initialized SQLite database: {args.db}")
                return 0
            # An explicit init-db is part of the reproducible workflow.
            has_schema = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='network_events'"
            ).fetchone()
            if not has_schema:
                raise RuntimeError("Database not initialized. Run: python main.py init-db")
            if args.command == "import-csv":
                counts, errors = import_csv(conn,args.file)
                for num, reason in errors:
                    print(f"Rejected CSV line {num}: {reason}")
                print("Import summary: " + " / ".join(f"{name}={value}" for name,value in counts.items()))
            elif args.command == "summary":
                show_summary(conn)
            elif args.command == "detect":
                result = detect(conn)
                print(f"Detection complete: new={result['new']} / existing={result['existing']}")
                for code, count in result["by_rule"].items():
                    print(f"  {code}: {count} matched window(s)")
            elif args.command == "report":
                write_report(conn,args.name,args.format,args.output)
            elif args.command == "alerts":
                show_alerts(conn,args.status)
            elif args.command == "set-status":
                update_alert_status(conn,args.alert_id,args.status)
            elif args.command == "explain-alert":
                explain_alert(conn,args.alert_id)
        return 0
    except (OSError, ValueError, RuntimeError, sqlite3.DatabaseError, UnicodeError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

