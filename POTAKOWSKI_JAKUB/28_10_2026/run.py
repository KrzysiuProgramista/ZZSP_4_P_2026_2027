"""Uruchom: python run.py. Wymaga Python 3.8+ i SQLite 3.30+."""
from pathlib import Path
import sqlite3
import json
from benchmark import measure
HERE=Path(__file__).resolve().parent

def open_db(path=":memory:"):
    con=sqlite3.connect(path,isolation_level=None)
    con.execute("PRAGMA foreign_keys=ON")
    return con

def state(con):
    return {t:con.execute(f"SELECT * FROM {t} ORDER BY 1,2").fetchall() for t in ('customers','products','categories','orders','order_items')}

def buy(con, customer, basket, break_check=False):
    # Nie laczymy duplikatow: koszyk musi zawierac unikatowe produkty.
    if not basket or len({p for p,q in basket})!=len(basket):
        raise ValueError('Pusty koszyk albo powtorzony produkt')
    if any(type(q) is not int or q<1 for p,q in basket):
        raise ValueError('Niepoprawna ilosc')
    con.execute('BEGIN IMMEDIATE')
    try:
        oid=con.execute("INSERT INTO orders(customer_id,order_date,status) VALUES(?,'2026-10-28','paid')",(customer,)).lastrowid
        for product,qty in basket:
            # Cena pobierana z bazy, nie od klienta. Blokada zapisu juz aktywna.
            price=con.execute('SELECT price_cents FROM products WHERE product_id=?',(product,)).fetchone()
            if price is None:
                raise ValueError('Brak produktu')
            con.execute('INSERT INTO order_items VALUES(?,?,?,?)',(oid,product,qty,price[0]))
            count=con.execute('UPDATE products SET stock=stock-? WHERE product_id=? AND stock>=?',(qty,product,qty)).rowcount
            if count!=1:
                raise ValueError('Brak zapasu')
        if break_check:
            con.execute('UPDATE order_items SET quantity=-1 WHERE order_id=?',(oid,))
        con.execute('COMMIT')
        return oid
    except Exception:
        con.execute('ROLLBACK')
        raise

def main():
    con=open_db()
    for file in ['schema.sql','seed.sql']:
        con.executescript((HERE/file).read_text(encoding='utf-8'))
    counts={t:con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in state(con)}
    assert counts==dict(customers=10,products=20,categories=6,orders=25,order_items=60)
    assert not con.execute('PRAGMA foreign_key_check').fetchall()
    tests=["INSERT INTO customers VALUES(90,'Test','KLIENT1@SPORT.TEST')",
           "UPDATE products SET price_cents=0 WHERE product_id=1",
           "UPDATE products SET price_cents=1.5 WHERE product_id=1",
           "INSERT INTO orders VALUES(90,99,'2026-10-28','paid')",
           "UPDATE orders SET status='bad' WHERE order_id=1",
           "UPDATE order_items SET quantity=0 WHERE order_id=1",
           "UPDATE products SET product_code='SP-0001' WHERE product_id=2",
           "DELETE FROM customers WHERE customer_id=1"]
    for statement in tests:
        before=state(con)
        try:
            con.execute(statement)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError('Przyjeto bledne dane: '+statement)
        assert state(con)==before
    results=[]
    statement=''
    for line in (HERE/'queries.sql').read_text(encoding='utf-8').splitlines():
        statement+=line+'\n'
        if sqlite3.complete_statement(statement):
            cur=con.execute(statement)
            results.append({'sql':statement.strip(),'columns':[c[0] for c in cur.description],'rows':cur.fetchall()})
            statement=''
    assert len(results)==25
    assert sum(row[1] for row in results[20]['rows'])==10
    # Bilans przychodu klientow, kategorii i ostatniej sumy narastajacej.
    customer_total=sum(row[2] for row in results[13]['rows'])
    category_total=sum(row[1] for row in results[14]['rows'])
    assert abs(customer_total-category_total)<0.000001
    assert abs(customer_total-results[-1]['rows'][-1][2])<0.000001
    baseline=state(con)
    for basket,forced,exception in [([(1,1),(2,2)],True,sqlite3.IntegrityError), ([(1,1),(2,9999)],False,ValueError)]:
        try:
            buy(con,1,basket,forced)
        except exception:
            pass
        else:
            raise AssertionError('Brak oczekiwanego bledu')
        assert state(con)==baseline
    stock=con.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]
    oid=buy(con,2,[(1,3),(3,1)])
    assert con.execute('SELECT stock FROM products WHERE product_id=1').fetchone()[0]==stock-3
    assert con.execute('SELECT COUNT(*) FROM orders').fetchone()[0]==26
    assert con.execute('SELECT COUNT(*) FROM order_items WHERE order_id=?',(oid,)).fetchone()[0]==2
    # Zapisujemy pierwotne dane, bez probnego zakupu. Plik odtwarzany przy uruchomieniu.
    target=HERE/'sport.db'
    if target.exists(): target.unlink()
    disk=open_db(target)
    for file in ['schema.sql','seed.sql']:
        disk.executescript((HERE/file).read_text(encoding='utf-8'))
    disk.close()
    (HERE/'wyniki_zapytan.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
    report=measure(HERE)
    (HERE/'raport.md').write_text('# Wyniki sprawdzenia\n\n'+f'Liczebnosci: {counts}.\n\n'+
        'Wykonano 25 zapytan. Osiem prob naruszenia ograniczen odrzucono. Segmenty obejmuja wszystkich 10 klientow. Sumy przychodu klientow, kategorii i raportu dziennego sa zgodne.\n\n'+
        'ROLLBACK: pelna zawartosc wszystkich pieciu tabel jest identyczna z punktem wyjscia po wymuszonym bledzie CHECK oraz po braku zapasu w drugim produkcie. W obu probach pierwszy produkt zdazyl juz zmienic stan. Poprawny zakup zatwierdzil dwie pozycje i zmniejszyl zapas. sport.db zawiera dane poczatkowe.\n\n'+report,encoding='utf-8')
    print('OK: dane, 25 zapytan, ograniczenia, bilans raportow, COMMIT, ROLLBACK i pomiary indeksu.')

if __name__=='__main__': main()
