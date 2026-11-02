# Verification and measurements

Seed counts: {'categories': 6, 'products': 20, 'customers': 10, 'orders': 25, 'order_items': 60}.

All 24 query statements executed. Foreign-key check passed. Seven invalid-data tests were rejected. Customers 9 and 10 have no orders. Products 19 and 20 have never been ordered.

Transaction proof: the forced quantity CHECK failure occurred after inserting an order, inserting a line and decreasing stock. Full order/item snapshots and all product stocks equalled the baseline after rollback. Insufficient stock also rolled back. A valid order committed two lines and decreased stock by the requested amounts. shop.db retains the original seed (25 orders).

## Index experiment (slides 38-39)

5 fresh in-memory databases per condition, 100000 identical rows, one transaction per insert batch, 100 fully fetched lookups per run. Index exists before timed indexed inserts; creation time excluded. Units: seconds.

| Operation | No code index | With code index |
| --- | ---: | ---: |
| Insert 100,000 rows | 0.042159 s | 0.069839 s |
| One selective lookup | 0.002180445 s | 0.000001422 s |

Plan without index: ['SCAN bench'].

Plan with index: ['SEARCH bench USING INDEX idx_bench_code (product_code=?)'].

The indexed lookup was 1533.4 times faster in this run. Indexed inserts took 1.66 times the unindexed duration. These are local in-memory measurements, not predictions for disk-based production workloads. Raw repeated measurements appear in benchmark_results.json.

The shop product_code column is UNIQUE, so SQLite already maintains an automatic unique index. Adding another index there would duplicate its work. The separate bench table deliberately has no UNIQUE constraint on product_code, allowing a genuine SCAN versus SEARCH comparison without weakening the shop schema.
