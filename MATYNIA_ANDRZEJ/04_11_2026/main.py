import argparse
from db import init_db
from importer import import_csv
from detection import run_detections
from reports import print_reports


def main():
  parser = argparse.ArgumentParser(
      description="Network Security Event Analyzer"
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  subparsers.add_parser("init-db", help="Inicjalizacja struktury bazy danych")

  parser_import = subparsers.add_parser(
      "import-csv", help="Importuj plik CSV ze zdarzeniami"
  )
  parser_import.add_argument("file", help="Ścieżka do pliku CSV")

  subparsers.add_parser("detect", help="Uruchom reguły wykrywania zagrożeń")

  subparsers.add_parser("report", help="Wyświetl raporty analityczne")

  args = parser.parse_args()

  if args.command == "init-db":
    init_db()
  elif args.command == "import-csv":
    import_csv(args.file)
  elif args.command == "detect":
    run_detections()
  elif args.command == "report":
    print_reports()


if __name__ == "__main__":
  main()
