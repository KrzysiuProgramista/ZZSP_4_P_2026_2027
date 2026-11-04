# Network Security Event Analyzer

A Python + SQLite defensive analytics application that transforms raw network logs/events into structured database records, executes transparent SQL detection rules, and outputs actionable security reports and alerts.

## Project Structure
```text
network-analyzer/
├── data/
│   └── network_events_sample.csv   # Sample CSV data
├── reports/                        # Exported CSV reports directory
├── schema.sql                      # Relational schema definition (5+ tables, FKs, CHECKs)
├── db.py                          # Database initialization and connection handling
├── importer.py                    # CSV validation, idempotency hash, and import logic
├── detection.py                   # SQL-based detection rules (PORT_SCAN, BRUTE_FORCE, TRAFFIC_FLOOD)
├── reports.py                     # Analytical SQL reports generator
├── main.py                        # Command Line Interface (CLI)
├── test_app.py                    # Unit tests suite
└── README.md                       # System documentation
```

## Setup & Quickstart

1. **Initialize the Database:**
   ```bash
   python main.py init-db
   ```

2. **Import Events from CSV:**
   ```bash
   python main.py import-csv data/network_events_sample.csv
   ```

3. **Run Detection Engine:**
   ```bash
   python main.py detect
   ```

4. **View Summary & Generate Analytical Reports:**
   ```bash
   python main.py summary
   python main.py report --format text
   python main.py report --format csv
   ```

5. **Run Unit Tests:**
   ```bash
   python test_app.py
   ```

## Detection Rules & Thresholds

1. **PORT_SCAN (HIGH Severity)**
   - **Threshold:** $\ge 20$ distinct destination ports on the same target host from a single source host within a 5-minute window.
   - **Mechanism:** SQL `COUNT(DISTINCT dst_port)` with 5-minute time bucket aggregation.

2. **BRUTE_FORCE (HIGH Severity)**
   - **Threshold:** $\ge 8$ `AUTH_FAILURE` events against the same service port on a target host within a 5-minute window.
   - **Mechanism:** SQL filter on `event_type = 'AUTH_FAILURE'` grouped by 5-minute window.

3. **TRAFFIC_FLOOD (CRITICAL Severity)**
   - **Threshold:** $\ge 150$ total network events directed at a specific host/port within a 1-minute window.
   - **Mechanism:** SQL `COUNT(*)` grouped by 1-minute time bucket.

## Limitations and Assumptions
- **Time Windows:** Rules use fixed time-bucket aggregation (`YYYY-MM-DDTHH:MM`). Rolling window coverage can be implemented in future iterations.
- **Traffic Nature:** High connection volumes may indicate legitimate enterprise operations (e.g., security scanners, proxies, or bulk sync jobs).
- **Security Guidance:** Alerts serve as indicators for human triage and investigation; automatic firewall blocking is not applied.
