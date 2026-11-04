import sys
import argparse
from db import init_db, connect
from importer import import_csv
from detection import run_detection
from reports import run_reports

def main():
    parser = argparse.ArgumentParser(description="Network Security Event Analyzer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init-db
    subparsers.add_parser("init-db", help="Initialize the SQLite database schema")

    # import-csv
    import_parser = subparsers.add_parser("import-csv", help="Import network events from CSV file")
    import_parser.add_argument("file", help="Path to the CSV file")

    # detect
    subparsers.add_parser("detect", help="Run detection rules on imported events")

    # report
    report_parser = subparsers.add_parser("report", help="Generate analytical reports")
    report_parser.add_argument("--format", choices=["text", "csv"], default="text", help="Output format (text or csv)")

    # summary
    subparsers.add_parser("summary", help="Show database summary metrics")

    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
    elif args.command == "import-csv":
        import_csv(args.file)
    elif args.command == "detect":
        run_detection()
    elif args.command == "report":
        run_reports(fmt=args.format)
    elif args.command == "summary":
        conn = connect()
        events_cnt = conn.execute("SELECT COUNT(*) FROM network_events").fetchone()[0]
        alerts_cnt = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        ips_cnt = conn.execute("SELECT COUNT(*) FROM ip_addresses").fetchone()[0]
        sensors_cnt = conn.execute("SELECT COUNT(*) FROM sensors").fetchone()[0]
        print(f"--- Database Summary ---")
        print(f"Total Events Imported: {events_cnt}")
        print(f"Total Unique IPs:      {ips_cnt}")
        print(f"Total Active Sensors:  {sensors_cnt}")
        print(f"Total Security Alerts: {alerts_cnt}")
        conn.close()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
