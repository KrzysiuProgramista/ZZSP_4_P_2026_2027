"""
cli.py - Command-line interface parsing and command orchestration.
"""
import argparse
import sys
from typing import List, Optional

import db
import detection
import importer
import reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="network-analyzer",
        description="Defensive Network Security Event Analyzer (Python 3 + SQLite)",
    )
    parser.add_argument(
        "--db",
        default="security_events.db",
        help="Path to SQLite database file (default: security_events.db)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Create database tables, constraints, and indexes")

    p_import = sub.add_parser("import-csv", help="Validate and import network events CSV")
    p_import.add_argument("csv_file", help="Path to CSV file")

    sub.add_parser("summary", help="Display SQL-generated analytical reports")

    sub.add_parser("detect", help="Run heuristic detection rules and persist alerts")

    p_rep = sub.add_parser("report", help="Export alerts report in text or CSV format")
    p_rep.add_argument("--format", choices=["text", "csv"], default="text")

    p_stat = sub.add_parser("set-status", help="Update analyst triage status of an alert")
    p_stat.add_argument("alert_id", type=int)
    p_stat.add_argument("status", choices=["NEW", "INVESTIGATING", "CLOSED"])

    return parser


def run_cli(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-db":
        db.init_db(args.db)
        print(f"[OK] Database initialised at '{args.db}' with foreign keys & constraints enabled.")
        return 0

    if args.command == "import-csv":
        summary = importer.import_csv(args.db, args.csv_file)
        print(
            f"[IMPORT SUMMARY] read={summary.rows_read} | imported={summary.imported} | "
            f"rejected={summary.rejected} | duplicates={summary.duplicates}"
        )
        for err in summary.errors:
            print(f"  [REJECTED] {err}")
        return 0

    if args.command == "summary":
        print(reports.format_summary_text(args.db))
        return 0

    if args.command == "detect":
        res = detection.run_detections(args.db)
        print(
            f"[DETECTION COMPLETE] rules_evaluated={res.evaluated_rules} | "
            f"new_alerts={res.new_alerts} | existing_duplicates_skipped={res.existing_alerts}"
        )
        print(reports.format_alerts_report(args.db, fmt="text"))
        return 0

    if args.command == "report":
        print(reports.format_alerts_report(args.db, fmt=args.format))
        return 0

    if args.command == "set-status":
        updated = detection.update_alert_status(args.db, args.alert_id, args.status)
        if updated:
            print(f"[OK] Alert #{args.alert_id} updated to {args.status}.")
            return 0
        print(f"[WARN] Alert #{args.alert_id} not found.", file=sys.stderr)
        return 1

    return 1