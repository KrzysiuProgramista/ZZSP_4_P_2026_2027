NETWORK SECURITY SQLITE DATABASE

Files
- network_security.db: pre-populated SQLite database
- network_security_schema.sql: schema, indexes and audit trigger
- network_events_sample.csv: original synthetic import file (896 events)

Tables
- sensors: source sensor metadata
- network_events: 896 imported synthetic network events
- alerts: three illustrative pre-seeded alerts (PORT_SCAN, AUTH_FAILURE_BURST, TRAFFIC_FLOOD)
- alert_status_history: audit trail populated automatically by log_alert_status_change
- event_statistics: per-source aggregates for UPSERT exercises

How to open
    sqlite3 network_security.db
    .tables
    .schema network_events
    .headers on
    .mode column

Python
    import sqlite3
    conn = sqlite3.connect("network_security.db")
    conn.execute("PRAGMA foreign_keys = ON")

Important notes
- CSV timestamps are stored as ISO-like text without an explicit timezone suffix. For the classroom dataset, interpret them consistently as UTC.
- Event keys are deterministic SHA-256 hashes of the source CSV fields, so the same CSV rows can be recognised on re-import.
- The sample is synthetic and intended for teaching, not operational threat detection.
- Trigger test is included in the build process; the database starts with an empty alert_status_history table.
