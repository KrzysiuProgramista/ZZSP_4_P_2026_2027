"""Pomiar na plikowych bazach w katalogu tymczasowym."""
import sqlite3
import tempfile
import time
import statistics
import json
from pathlib import Path

def measure(output):
    data=[(i,f'P-{i:05d}',i%600) for i in range(1,100001)]
    results=[]
    with tempfile.TemporaryDirectory() as temp:
        for trial in range(3):
            for indexed in ([False,True] if trial%2==0 else [True,False]):
                con=sqlite3.connect(Path(temp)/f'{trial}_{indexed}.db')
                con.execute('CREATE TABLE sample(id INTEGER PRIMARY KEY,product_code TEXT NOT NULL,amount INTEGER NOT NULL)')
                if indexed: con.execute('CREATE INDEX code_lookup ON sample(product_code)')
                con.commit()
                start=time.perf_counter()
                with con: con.executemany('INSERT INTO sample VALUES(?,?,?)',data)
                insert=time.perf_counter()-start
                query="SELECT * FROM sample WHERE product_code='P-00123'"
                plan=[r[3] for r in con.execute('EXPLAIN QUERY PLAN '+query)]
                assert con.execute(query).fetchall()==[(123,'P-00123',123)]
                start=time.perf_counter()
                for _ in range(150): con.execute(query).fetchall()
                lookup=(time.perf_counter()-start)/150
                results.append(dict(trial=trial+1,indexed=indexed,insert_s=insert,lookup_s=lookup,plan=plan))
                con.close()
    (output/'pomiary.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    med={flag:{key:statistics.median(r[key] for r in results if r['indexed']==flag) for key in ['insert_s','lookup_s']} for flag in [False,True]}
    a,b=med[False],med[True]
    return f"""## Indeks: slajdy 38-39

Trzy powtorzenia na nowych bazach plikowych. Kazda proba: te same 100 000 rekordow, jeden COMMIT dla calej partii. Indeks istnieje przed mierzonym insertem. Czas jego utworzenia nie wchodzi do pomiaru. Kolejnosc wariantow jest zmieniana. Po jednym odczycie rozgrzewajacym mierzymy 150 odczytow z pobraniem wszystkich wynikow. Tabela sample nie ma UNIQUE na kodzie, aby pomiar bez indeksu byl rzeczywisty.

| Mediana | Bez indeksu | Z indeksem |
| --- | ---: | ---: |
| INSERT 100 000 | {a['insert_s']:.6f} s | {b['insert_s']:.6f} s |
| SELECT, jeden odczyt | {a['lookup_s']:.9f} s | {b['lookup_s']:.9f} s |

Plan bez indeksu: {next(r['plan'] for r in results if not r['indexed'])}.
Plan z indeksem: {next(r['plan'] for r in results if r['indexed'])}.

W tym pomiarze stosunek czasu INSERT z indeksem do czasu bez indeksu wyniosl {b['insert_s']/a['insert_s']:.2f}, a stosunek czasu SELECT bez indeksu do czasu z indeksem {a['lookup_s']/b['lookup_s']:.1f}. Indeks usprawnia selektywny odczyt, ale wymaga aktualizacji przy zapisie. Wyniki dotycza lokalnego dysku i rozgrzanej pamieci podrecznej, nie dowodza identycznej korzysci dla innego obciazenia. Na malej tabeli SCAN moze byc uzasadniony. Pelne pomiary: pomiary.json.

W docelowej tabeli products UNIQUE(product_code) juz tworzy indeks. Nie dodajemy drugiego identycznego indeksu. Oddzielna tabela pomiarowa zachowuje poprawnosc ograniczen sklepu.
"""
