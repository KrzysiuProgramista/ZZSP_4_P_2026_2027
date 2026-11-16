# Network Security Event Analyzer

Offline, defensive security analytics assignment (Python 3.10+ / SQLite). No external packages, packet capture, network scanning, automatic blocking, or attacks on real systems.

## Quick start

Open a terminal in this project directory:

```bash
python main.py init-db
python main.py import-csv data/network_events_sample.csv
python main.py summary
python main.py report
python main.py detect
python main.py alerts
python main.py explain-alert 1
python main.py report --format csv
python -m unittest discover -s tests -v
```

On Windows, `py main.py ...` works in place of `python main.py ...`. To rebuild from zero, delete `network_events.db`, then repeat these commands. To avoid deleting files, choose an alternate database path using `python main.py --db other.db init-db` and use `--db other.db` before each subsequent subcommand.

## Files

- `main.py`, `cli.py`: command dispatch and user-friendly errors
- `db.py`, `schema.sql`: SQLite connections, normalized schema, constraints, indexes
- `importer.py`: strict CSV validation, atomic imports, fingerprint-based duplicate protection, rejected row logging
- `detection.py`: three SQL-aggregated rules, alert storage and event-level evidence
- `reports.py`: six live SQL reports plus console or CSV export
- `tests/test_analyzer.py`: unit tests for normal, malformed and suspicious input
- `ERD.png`, `ERD.svg`, `ERD.md`: graphical ERD plus source diagram (Mermaid syntax)
- `data/network_events_sample.csv`: provided synthetic data
- `demo_output.txt`: reproducible sample terminal results (generated from attached sample)
- `examples/network_events_demo.db`: example populated SQLite DB (also fully rebuildable)

## CSV format and validation

The **exact 11-column header** must contain:

`timestamp,sensor_name,src_ip,dst_ip,src_port,dst_port,protocol,event_type,action,bytes,duration_ms`

Column order may vary; column names must match, with no unexpected or duplicate columns.

- `timestamp`: parseable ISO 8601 date and time. Naive timestamps from the supplied sample are **assumed to be UTC**; offset-aware times are converted into UTC. Original timestamp text is also preserved in `raw_timestamp`.
- `sensor_name`: nonempty text; new sensors are inserted into the `sensors` dimension table automatically (no orphan FK).
- `src_ip`, `dst_ip`: valid IPv4 or IPv6 (Python `ipaddress`).
- `src_port`, `dst_port`: blank, or integer 1–65535. TCP/UDP records require both ports; ICMP can omit them.
- `protocol`: exactly `TCP`, `UDP` or `ICMP`.
- `event_type`: one of `AUTH_FAILURE`, `AUTH_SUCCESS`, `CONNECTION`, `DNS_QUERY`, `HTTP_REQUEST`. Unknown event types are **rejected** rather than inventing new types.
- `action`: exactly `ALLOW` or `BLOCK`.
- `bytes`, `duration_ms`: non-negative decimal integers.

An invalid row is logged with CSV line number and reason in `import_rejections`. The remaining rows continue. At the end: `read / imported / rejected / duplicates`. CSV format must be valid at the file level; an invalid file header aborts the import before insertion. A database integrity error rolls back the entire batch.

### Duplicate policy

The SHA-256 hash of the original 11 field values in fixed order is unique. Exact repeated rows (across files or repeated imports) are treated as duplicates. A separate event that happens to have identical field values is indistinguishable from a duplicated log line; this is a known limitation of the input without a unique source event ID. Importing identical data twice never doubles the counts. Repeated runs may log repeated invalid rows in the audit table; this does not affect event data.

## Database model

See [`ERD.md`](ERD.md) and [`schema.sql`](schema.sql). Tables: `sensors`, `ip_addresses`, `event_types`, `network_events`, `alerts`, `alert_events`, `import_rejections` (7 total). The model uses PK, FK, `NOT NULL`, `UNIQUE`, `CHECK`, indexes and `PRAGMA foreign_keys = ON`. The `network_events` table references all dimensions by ID; `alert_events` links detections to original events. Import and detection each run in their own transaction, with runtime values passed using `?` SQL parameters.

## Detection rules

**Windows are FIXED UTC-aligned buckets, not sliding windows.** This is explicitly allowed by slide 15 of the assignment. A 5-minute bucket such as `[10:10:00,10:15:00)` includes the start and excludes the end, so a sequence crossing the boundary may be missed. `event_count` is the number of events matching the grouping; `metric_count` is the number of distinct ports for `PORT_SCAN` and equal to `event_count` for the other rules.

| Rule | Grouping | Condition | Window | Severity |
|---|---|---|---|---|
| `PORT_SCAN` | source IP + target IP | >=20 **distinct** destination ports | 5 minutes | HIGH |
| `BRUTE_FORCE` | source IP + target IP + destination port, `AUTH_FAILURE` only | >=8 events | 5 minutes | HIGH |
| `TRAFFIC_FLOOD` | source IP + target IP + destination port | >=150 events | 1 minute | CRITICAL |

Thresholds are configurable constants in `detection.py` (`RULES`). SQL does all grouping, time bucketing and counting. Python saves each result as an alert, including source and target IP, service port (if applicable), UTC window, total number of supporting events, metric, severity, description, and created time. A linked row in `alert_events` exists for each contributing event. `explain-alert` displays a sample of those stored rows. Running detection twice is idempotent: the alert uniqueness index prevents duplicates. If additional events arrive in the same bucket, evidence and counts update while the analyst's status is retained.

Analyst status flow: `NEW`, `INVESTIGATING`, `CLOSED`. Example:

```bash
python main.py set-status 1 INVESTIGATING
python main.py alerts --status INVESTIGATING
python main.py explain-alert 1
```

## Analytical reports

All reports use real SQLite queries (no hard-coded results). Available:

1. `types`: event volume by type (LEFT JOIN and aggregate)
2. `sources`: top 10 source IPs, with last event timestamp (JOIN, aggregate, correlated subquery)
3. `services`: most targeted destination ports, with protocol (aggregate)
4. `alerts`: alert counts by severity and status (aggregate)
5. `timeline`: events in 5-minute UTC buckets (date grouping)
6. `targets`: most targeted destination IPs (JOIN and aggregate)

```bash
python main.py report --name sources
python main.py report --name timeline --format csv --output reports/timeline.csv
python main.py report --format csv
python main.py report --format csv --output reports
python main.py report --format text --output reports/all_reports.txt
```

For `--name all`, CSV output produces six separate CSV files in the target folder (default `reports/`). For a named report, CSV without an output path goes to standard output.

## Sample run and expected observations

The provided file has **896 rows**. A clean import should show `read=896 / imported=896 / rejected=0 / duplicates=0`. With the fixed-window rules above, it yields three alerts, one per rule:

- `PORT_SCAN`: `198.51.100.66 -> 10.0.0.20`, 23 different ports in the 10:10–10:15 UTC window.
- `BRUTE_FORCE`: `203.0.113.23 -> 10.0.0.15:22`, 10 failures in the 10:20–10:25 UTC window.
- `TRAFFIC_FLOOD`: `198.51.100.77 -> 10.0.0.20:443`, 160 events in the 10:40–10:41 UTC window.

These are **suspicious patterns, not proven intrusions**. The sample data is synthetic. A ready-to-inspect database is included at `examples/network_events_demo.db`. The main working database (`network_events.db`) is intentionally **not included** in the zip, so the quick-start import begins from zero. The saved sample database and `demo_output.txt` can be rebuilt with the commands above.

## Testing

`python -m unittest discover -s tests -v` verifies:

- valid CSV and exact counts;
- rejection and line-number auditing for malformed rows;
- rejection of unknown event types without orphan FK records;
- optional creation of new sensor dimension records without orphan events;
- port-scan detection at/above threshold and no alert below threshold;
- brute-force and flood detection thresholds;
- repeat import/detection do not duplicate events/alerts;
- status changes survive repeat detection.

## Limitations and assumptions

- Heuristics can create **false positives** (legitimate scanners, busy proxies, planned monitoring) and **false negatives** (low-and-slow behavior, distributed sources). A fixed window cannot detect activity split across its boundary.
- Events/flows are **not packet contents**; no payload analysis, user identity, or network topology is available.
- Sample data is synthetic; thresholds should not be treated as production standards.
- IP attribution is complicated by NAT, proxies, shared infrastructure and dynamic address reuse. `ipaddress.is_private` is a technical classification, **not proof that an IP belongs to this organization**.
- CSV has no source-provided event ID; genuinely identical rows collapse to one event by fingerprint.
- Unknown event types are rejected until the approved `EVENT_TYPES` mapping is updated; unknown sensor names are accepted into `sensors` as new dimension entries.
- Timezone-naive input is assumed UTC, not guessed from the local PC timezone.
- **Investigate alerts manually; do not automatically block sources** based on these findings.
