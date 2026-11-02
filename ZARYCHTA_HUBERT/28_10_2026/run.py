"""Python standard library only. Run: python run.py"""
import sqlite3, time, statistics, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def connect(path=":memory:"):
    db=sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    return db

def snapshot(db):
    return tuple(tuple(db.execute(sql)) for sql in (
        "SELECT * FROM orders ORDER BY order_id",
        "SELECT * FROM order_items ORDER BY order_id,product_id",
        "SELECT product_id,stock FROM products ORDER BY product_id"))

def place_order(db, customer_id, items, force_failure=False):
    # Merge duplicate product IDs so the composite key cannot collide.
    quantities={}
    for product_id, quantity in items:
        if type(quantity) is not int or quantity<=0:
            raise ValueError("Quantity must be a positive integer")
        quantities[product_id]=quantities.get(product_id,0)+quantity
    if not quantities:
        raise ValueError("Empty order")
    try:
        db.execute("BEGIN IMMEDIATE")
        order_id=db.execute("INSERT INTO orders(customer_id,order_date,status) VALUES(?,'2026-10-28','paid')",(customer_id,)).lastrowid
        for product_id,quantity in sorted(quantities.items()):
            row=db.execute("SELECT price FROM products WHERE product_id=?",(product_id,)).fetchone()
            if row is None:
                raise ValueError("Unknown product")
            db.execute("INSERT INTO order_items VALUES(?,?,?,?)",(order_id,product_id,quantity,row[0]))
            changed=db.execute("UPDATE products SET stock=stock-? WHERE product_id=? AND stock>=?",(quantity,product_id,quantity)).rowcount
            if changed!=1:
                raise ValueError("Insufficient stock")
        if force_failure:
            # Force CHECK failure AFTER a real stock change and item insertion.
            db.execute("UPDATE order_items SET quantity=0 WHERE order_id=?",(order_id,))
        db.commit()
        return order_id
    except Exception:
        db.rollback()
        raise

def benchmark():
    # A separate table is essential: UNIQUE product_code already creates an index
    # in the shop schema. Removing that constraint would weaken Exercise 1.
    rows=[(i,f"P-{i:05d}",f"Product {i}") for i in range(1,100001)]
    times={"unindexed_insert":[],"indexed_insert":[],"unindexed_lookup":[],"indexed_lookup":[]}
    plans={}
    for repeat in range(5):
        # Alternate order to reduce systematic warm-up bias.
        for indexed in ([False,True] if repeat%2==0 else [True,False]):
            db=connect()
            db.execute("CREATE TABLE bench(product_id INTEGER PRIMARY KEY, product_code TEXT NOT NULL, name TEXT NOT NULL)")
            label="indexed" if indexed else "unindexed"
            if indexed:
                db.execute("CREATE INDEX idx_bench_code ON bench(product_code)")
            start=time.perf_counter()
            with db:
                db.executemany("INSERT INTO bench VALUES(?,?,?)",rows)
            times[label+"_insert"].append(time.perf_counter()-start)
            query="SELECT * FROM bench WHERE product_code=?"
            plans[label]=[r[3] for r in db.execute("EXPLAIN QUERY PLAN "+query,('P-00123',))]
            assert db.execute(query,('P-00123',)).fetchall()==[(123,'P-00123','Product 123')]
            start=time.perf_counter()
            for _ in range(100):
                db.execute(query,('P-00123',)).fetchall()
            times[label+"_lookup"].append((time.perf_counter()-start)/100)
            db.close()
    return {"method":"5 fresh in-memory databases per condition, 100000 identical rows, one transaction per insert batch, 100 fully fetched lookups per run. Index exists before timed indexed inserts; creation time excluded. Units: seconds.","plans":plans,"runs":times,"median_seconds":{k:statistics.median(v) for k,v in times.items()}}

def main():
    db=connect()
    db.executescript((ROOT/'schema.sql').read_text())
    db.executescript((ROOT/'seed.sql').read_text())
    expected=dict(categories=6,products=20,customers=10,orders=25,order_items=60)
    actual={table:db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in expected}
    assert actual==expected
    failures=[
      ("duplicate email","INSERT INTO customers VALUES(100,'Duplicate','customer1@example.com')"),
      ("nonpositive price","INSERT INTO products VALUES(100,'BAD','Bad',1,0,0)"),
      ("unknown customer","INSERT INTO orders VALUES(100,999,'2026-10-28','paid')"),
      ("invalid status","INSERT INTO orders VALUES(100,1,'2026-10-28','unknown')"),
      ("nonpositive quantity","INSERT INTO order_items VALUES(1,20,0,10)"),
      ("duplicate code","INSERT INTO products VALUES(100,'P-00001','Duplicate',1,10,0)"),
      ("customer deletion restricted","DELETE FROM customers WHERE customer_id=1")]
    for label,sql in failures:
        before=snapshot(db)
        try:
            db.execute(sql)
        except sqlite3.IntegrityError:
            db.rollback()
        else:
            raise AssertionError('Constraint accepted: '+label)
        assert before==snapshot(db)
    assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
    # Produce all query results from the original seed before transaction tests.
    results=[]
    statements=[]
    buffer=''
    for line in (ROOT/'queries.sql').read_text().splitlines():
        buffer+=line+'\n'
        if sqlite3.complete_statement(buffer):
            statements.append(buffer)
            buffer=''
    for statement in statements:
        if not statement.strip():
            continue
        cur=db.execute(statement)
        if cur.description:
            results.append({'query':statement.strip(),'columns':[c[0] for c in cur.description],'rows':cur.fetchall()})
    assert len(results)==24, len(results)
    assert db.execute('SELECT customer_id FROM customers WHERE NOT EXISTS (SELECT 1 FROM orders WHERE orders.customer_id=customers.customer_id) ORDER BY customer_id').fetchall()==[(9,),(10,)]
    assert db.execute('SELECT product_id FROM products WHERE NOT EXISTS (SELECT 1 FROM order_items WHERE order_items.product_id=products.product_id) ORDER BY product_id').fetchall()==[(19,),(20,)]
    (ROOT/'query_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    baseline=snapshot(db)
    for items,forced,error in [([(1,2)],True,sqlite3.IntegrityError), ([(1,1000000)],False,ValueError)]:
        try:
            place_order(db,1,items,forced)
        except error:
            pass
        else:
            raise AssertionError('Expected transaction failure')
        assert snapshot(db)==baseline
    stock=db.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]
    new_id=place_order(db,1,[(1,2),(2,1)])
    assert db.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]==stock-2
    assert db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]==26
    assert db.execute('SELECT COUNT(*) FROM order_items WHERE order_id=?',(new_id,)).fetchone()[0]==2
    # Persist pristine seed rather than the successful transaction demonstration.
    disk=connect(ROOT/'shop.db')
    disk.close()
    # Rebuild is deliberate and repeatable; only the generated shop.db is replaced.
    (ROOT/'shop.db').unlink()
    disk=connect(ROOT/'shop.db')
    disk.executescript((ROOT/'schema.sql').read_text())
    disk.executescript((ROOT/'seed.sql').read_text())
    disk.close()
    measurements=benchmark()
    (ROOT/'benchmark_results.json').write_text(json.dumps(measurements,indent=2),encoding='utf-8')
    m=measurements['median_seconds']
    report=f"""# Verification and measurements

Seed counts: {actual}.

All 24 query statements executed. Foreign-key check passed. Seven invalid-data tests were rejected. Customers 9 and 10 have no orders. Products 19 and 20 have never been ordered.

Transaction proof: the forced quantity CHECK failure occurred after inserting an order, inserting a line and decreasing stock. Full order/item snapshots and all product stocks equalled the baseline after rollback. Insufficient stock also rolled back. A valid order committed two lines and decreased stock by the requested amounts. shop.db retains the original seed (25 orders).

## Index experiment (slides 38-39)

{measurements['method']}

| Operation | No code index | With code index |
| --- | ---: | ---: |
| Insert 100,000 rows | {m['unindexed_insert']:.6f} s | {m['indexed_insert']:.6f} s |
| One selective lookup | {m['unindexed_lookup']:.9f} s | {m['indexed_lookup']:.9f} s |

Plan without index: {measurements['plans']['unindexed']}.

Plan with index: {measurements['plans']['indexed']}.

The indexed lookup was {m['unindexed_lookup']/m['indexed_lookup']:.1f} times faster in this run. Indexed inserts took {m['indexed_insert']/m['unindexed_insert']:.2f} times the unindexed duration. These are local in-memory measurements, not predictions for disk-based production workloads. Raw repeated measurements appear in benchmark_results.json.

The shop product_code column is UNIQUE, so SQLite already maintains an automatic unique index. Adding another index there would duplicate its work. The separate bench table deliberately has no UNIQUE constraint on product_code, allowing a genuine SCAN versus SEARCH comparison without weakening the shop schema.
"""
    (ROOT/'verification.md').write_text(report,encoding='utf-8')
    print('PASS: schema, seed, 24 queries, constraints, successful transaction, two rollback paths, and index benchmark.')

if __name__=='__main__':
    main()
