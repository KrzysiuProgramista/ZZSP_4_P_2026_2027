# SQL relational model lab — Hubert Zarychta
28 October 2026. Solutions for slides 24–39 (exercises 1–8).

## Run
From this folder run `python run.py` (Python 3.8+ with SQLite 3.25+; no external packages).
The runner rebuilds the generated shop.db, checks the exercises and refreshes the result files.
You can open shop.db directly in a SQLite client and execute queries.sql.
Enable `PRAGMA foreign_keys = ON` on each new connection before modifying data.

## Files and slide coverage
- schema.sql: slides 24–25, five tables, relationship sketch, keys, constraints, deletion policy and justified indexes.
- seed.sql: slide 26, exactly 6 categories, 20 products, 10 customers, 25 orders and 60 lines.
- queries.sql: slides 27–35, 24 executable queries covering filtering, aggregation, joins, missing relationships, subqueries, segmentation and windows.
- transactions.sql and run.py: slides 36–37, parameterized safe order placement, guarded stock updates and asserted rollback after CHECK failure.
- run.py, benchmark_results.json and verification.md: slides 38–39, repeated 100,000-row index experiment, query plans and measured findings.
- query_results.json: column names and complete results for every query on the original seed.
- shop.db: ready-to-open database containing the original seed.

## Decisions
Amounts are in PLN. Order line prices preserve the purchase-time price. Revenue and customer spend count paid and shipped orders only. Order-value analytics include all statuses. Spend averages include all customers, with zero for those without qualifying orders. Gold starts at 1000 PLN, silver at 300 PLN, bronze below 300 PLN. Dates use ISO format. Product IDs break price ties, and order IDs break date ties.

The seed represents a historical snapshot with current stock recorded independently. Only the safe order-placement operation decrements current stock. NUMERIC prices follow the lecture's simple teaching model; production financial systems commonly use integer minor units to avoid binary floating-point rounding.

No changes were made to the source presentation.
