# Network Security Event Analyzer

A small defensive analytics tool written in Python 3 with SQLite. It imports a CSV
file of network events, validates and normalises it into a relational database, runs
three transparent detection rules, stores the resulting alerts, and produces SQL-powered
reports.

This is an analysis tool, not an intrusion detection system. Alerts are heuristics that
flag patterns for human review; they are not proof of malicious activity.

## Requirements

- Python 3.10 or newer
- No third-party packages (standard library only)

## Quick start (reproducible command sequence)

```bash
python main.py init-db                               # create schema and seed event types
python main.py import-csv data/network_events_sample.csv
python main.py summary
python main.py detect                                # run rules and store alerts
python main.py detect                                # safe to repeat: no duplicate alerts
python main.py alerts
python main.py report                                # all text reports
python main.py report --format csv --out-dir reports # all reports as CSV files
python -m unittest discover -s tests -v              # run the test suite
```

To rebuild from scratch, delete `data/analyzer.db` and repeat the sequence. The same
input file always produces the same imported events and the same alerts.

## Commands

| Command | Purpose |
|---|---|
| `init-db` | Create tables and indexes if they do not exist, and seed event types. |
| `import-csv PATH` | Validate, normalise and store events in one transaction. Prints read / imported / rejected / duplicates and the reason for each rejected line. |
| `summary` | Event count, time range, sensors, IP addresses, alert counts. |
| `detect` | Run all three rules and persist alerts. |
| `alerts [--status NEW\|INVESTIGATING\|CLOSED]` | List alerts with rule, severity, endpoints, window, count and description. |
| `alert-status ID STATUS` | Update an alert's lifecycle status. |
| `report [--name NAME] [--format text\|csv] [--out-dir DIR]` | Run SQL reports. Names: `event-volume`, `top-sources`, `top-services`, `alerts-overview`, `timeline-5min`, `top-targets`, `alerts`. |

The global option `--db PATH` selects the database (default `data/analyzer.db`).

## CSV input format

The header must contain these columns (extra columns are ignored):

| Column | Rule |
|---|---|
| `timestamp` | ISO 8601. Without an offset it is interpreted as **UTC**; with an offset it is converted to UTC. |
| `sensor_name` | Non-empty text. |
| `src_ip`, `dst_ip` | Valid IPv4 or IPv6 address. |
| `src_port`, `dst_port` | Integer 1–65535, or blank when not applicable. |
| `protocol` | `TCP`, `UDP` or `ICMP`. |
| `event_type` | One of `HTTP_REQUEST`, `CONNECTION`, `DNS_QUERY`, `AUTH_SUCCESS`, `AUTH_FAILURE`. |
| `action` | `ALLOW` or `BLOCK`. |
| `bytes`, `duration_ms` | Non-negative integers. |

Values are never silently changed: a row either passes validation as written, or it is
rejected with its line number and reason. The application continues after a rejected row.

## Database design

Six tables (see `schema.sql`):

- `sensors(sensor_id, name UNIQUE, location)`
- `ip_addresses(ip_id, address UNIQUE, is_private)`
- `event_types(event_type_id, code UNIQUE, default_severity)`
- `network_events(event_id, event_key UNIQUE, sensor_id FK, event_type_id FK, src_ip_id FK, dst_ip_id FK, event_time, src_port, dst_port, protocol, action, bytes, duration_ms)`
- `alerts(alert_id, rule_code, source_ip_id FK, target_ip_id FK, service_port, window_start, window_end, severity, status, event_count, description, created_at)`

Constraints: primary and foreign keys (enforced with `PRAGMA foreign_keys = ON`), `NOT NULL`,
`UNIQUE`, and `CHECK` on ports (1–65535), byte and duration counts (≥ 0), protocol, action,
status and severity values. Sensor names, IP addresses and event types are stored once and
referenced by ID.

Duplicates: each event has an `event_key`, the SHA-256 of all its normalised fields. Importing
the same file again inserts nothing and counts every row as a duplicate. Two rows that are
byte-for-byte identical in every field are also treated as duplicates. Within the sample file
there are no such rows.

Alert uniqueness: `UNIQUE(rule_code, source_ip_id, target_ip_id, service_port, window_start)`.
Re-running detection on the same data therefore does not create new alerts, and an analyst's
status change survives re-runs.

## Detection rules

Thresholds are constants in `config.py`. Windows are **fixed, aligned buckets** in UTC: a 5-minute
window starts at :00, :05, :10 … and a 1-minute window at every full minute.

| Rule | Trigger | Grouping | Severity |
|---|---|---|---|
| `PORT_SCAN` | ≥ 20 distinct destination ports | same source and target, 5-minute bucket | HIGH |
| `BRUTE_FORCE` | ≥ 8 `AUTH_FAILURE` events | same source, target and destination port, 5-minute bucket | HIGH |
| `TRAFFIC_FLOOD` | ≥ 150 events | same source, target and destination port, 1-minute bucket | CRITICAL |

Grouping and counting are done in SQL (`detection.py`); Python orchestrates the rules and
writes alerts in one transaction. Each alert stores the rule, both endpoints, the service port
(0 for port-agnostic PORT_SCAN), the window, the event count and a human-readable description
stating the threshold.

The severities are a judgement made for this version. `TRAFFIC_FLOOD` is marked CRITICAL
because high-volume floods can degrade services quickly, but a legitimate burst (a backup job,
a monitoring agent, a busy proxy) can reach the same count.

## Reports

Each report is a SQL query in `reports.py`:

1. **Event volume by type**: events per `event_type`.
2. **Top source IPs**: the top 10 sources by event count.
3. **Top targeted services**: the top 10 destination ports, with the number of distinct sources.
4. **Alerts overview**: alert counts grouped by severity and status.
5. **Timeline**: events per 5-minute UTC bucket.
6. **Top targets**: the top 10 destination IPs, with the number of distinct sources.

Reports are also available as `alerts` (full list).

## Sample output

Import of `data/network_events_sample.csv` (896 rows):

```
Import summary for data/network_events_sample.csv
  read:       896
  imported:   896
  rejected:   0
  duplicates: 0
```

Detection (first run; the second run creates 0 new alerts):

```
Detection run
  PORT_SCAN      matches: 1    new alerts: 1
  BRUTE_FORCE    matches: 1    new alerts: 1
  TRAFFIC_FLOOD  matches: 1    new alerts: 1
```

Alerts produced by the sample:

| ID | Rule | Severity | Source | Target | Port | Window (UTC) | Events |
|---|---|---|---|---|---|---|---|
| 1 | PORT_SCAN | HIGH | 198.51.100.66 | 10.0.0.20 | any | 10:10:00–10:15:00 | 23 |
| 2 | BRUTE_FORCE | HIGH | 203.0.113.23 | 10.0.0.15 | 22 | 10:20:00–10:25:00 | 10 |
| 3 | TRAFFIC_FLOOD | CRITICAL | 198.51.100.77 | 10.0.0.20 | 443 | 10:40:00–10:41:00 | 160 |

Example explanation of alert 1: 198.51.100.66 contacted 23 distinct destination ports on
10.0.0.20 within the 10:10–10:15 window, against a threshold of 20 ports.

The full reports are in `reports/*.csv` and were generated by SQL queries.

## Tests

`tests/test_analyzer.py` covers:

- valid import: counts match the source;
- malformed rows (bad port, bad IP, unknown protocol) are rejected with line numbers and do not stop the import;
- unknown event type is rejected and leaves no orphan rows;
- repeat import is idempotent;
- port scan: exactly one alert at 20 ports, none at 19;
- brute force: alert at 8 failures, none at 7;
- traffic flood: alert at 150 events with CRITICAL severity;
- running detection twice creates no duplicate alerts.

## Project structure

```
network-analyzer/
├── data/network_events_sample.csv   # provided synthetic sample
├── reports/                         # CSV exports of all reports
├── schema.sql                       # schema with constraints and indexes
├── config.py                        # thresholds, windows, vocabularies
├── db.py                            # connection, schema init, transaction helper
├── importer.py                      # CSV validation and import
├── detection.py                     # rule evaluation and alert persistence
├── reports.py                       # SQL reports and formatting
├── cli.py                           # command-line interface
├── main.py                          # entry point
├── tests/test_analyzer.py           # unit tests
└── README.md
```

## Limitations and assumptions

- **Heuristics, not proof.** Alerts flag patterns for human review. Legitimate vulnerability
  scanners, monitoring systems, backups and busy proxies can trigger them (false positives).
- **Low-and-slow activity is missed.** An attacker who stays below the thresholds, spreads
  activity over time, or uses multiple source addresses will not be flagged (false negatives).
- **Fixed buckets split bursts.** A burst that straddles a bucket boundary (for example
  10:04:50–10:05:10) may fall below the threshold in each bucket. Rolling windows would avoid
  this and are an optional extension.
- **Flow records, not packets.** Each row is one observed event or flow. No payloads, no
  packet-level detail, no TCP flags.
- **Synthetic data.** The sample is synthetic and cannot represent every network. Thresholds
  were not tuned against real traffic.
- **Attribution is limited.** NAT, proxies and shared infrastructure mean a source IP does not
  identify one actor.
- **UTC assumed.** Timestamps without an offset are treated as UTC. Mixing timezones in one
  file would distort windows.
- **Recommended action is investigation, not blocking.** The tool does not block traffic or
  change any system.
- **Scope.** No live capture, no PCAP parsing, no scanning of real systems, no machine learning.
