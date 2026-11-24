1. Initialise SQLite database from schema.sql
python main.py init-db

2. Validate, normalise and import CSV events
python main.py import-csv data/network_events_sample.csv

3. Inspect SQL reports
python main.py summary

4. Run heuristic detection rules and persist alerts
python main.py detect

5. Export alerts to CSV
python main.py report --format csv

6. Execute automated unit tests
python -m unittest discover -s tests -v