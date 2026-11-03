# Wyniki sprawdzenia

Liczebnosci: {'customers': 10, 'products': 20, 'categories': 6, 'orders': 25, 'order_items': 60}.

Wykonano 25 zapytan. Osiem prob naruszenia ograniczen odrzucono. Segmenty obejmuja wszystkich 10 klientow. Sumy przychodu klientow, kategorii i raportu dziennego sa zgodne.

ROLLBACK: pelna zawartosc wszystkich pieciu tabel jest identyczna z punktem wyjscia po wymuszonym bledzie CHECK oraz po braku zapasu w drugim produkcie. W obu probach pierwszy produkt zdazyl juz zmienic stan. Poprawny zakup zatwierdzil dwie pozycje i zmniejszyl zapas. sport.db zawiera dane poczatkowe.

## Indeks: slajdy 38-39

Trzy powtorzenia na nowych bazach plikowych. Kazda proba: te same 100 000 rekordow, jeden COMMIT dla calej partii. Indeks istnieje przed mierzonym insertem. Czas jego utworzenia nie wchodzi do pomiaru. Kolejnosc wariantow jest zmieniana. Po jednym odczycie rozgrzewajacym mierzymy 150 odczytow z pobraniem wszystkich wynikow. Tabela sample nie ma UNIQUE na kodzie, aby pomiar bez indeksu byl rzeczywisty.

| Mediana | Bez indeksu | Z indeksem |
| --- | ---: | ---: |
| INSERT 100 000 | 0.067689 s | 0.104296 s |
| SELECT, jeden odczyt | 0.002116322 s | 0.000042435 s |

Plan bez indeksu: ['SCAN sample'].
Plan z indeksem: ['SEARCH sample USING INDEX code_lookup (product_code=?)'].

W tym pomiarze stosunek czasu INSERT z indeksem do czasu bez indeksu wyniosl 1.54, a stosunek czasu SELECT bez indeksu do czasu z indeksem 49.9. Indeks usprawnia selektywny odczyt, ale wymaga aktualizacji przy zapisie. Wyniki dotycza lokalnego dysku i rozgrzanej pamieci podrecznej, nie dowodza identycznej korzysci dla innego obciazenia. Na malej tabeli SCAN moze byc uzasadniony. Pelne pomiary: pomiary.json.

W docelowej tabeli products UNIQUE(product_code) juz tworzy indeks. Nie dodajemy drugiego identycznego indeksu. Oddzielna tabela pomiarowa zachowuje poprawnosc ograniczen sklepu.
