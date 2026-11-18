# Zadania A i B — Advanced SQL i SQLite

## A — Raport aktywności

Otwórz `network_security.db` w DB Browser for SQLite. W zakładce **Wykonaj SQL** wczytaj i wykonaj `zadanie_A.sql`. Skrypt tworzy widok `source_activity_report` dla godziny 10:00–11:00 UTC z 18 września 2026 r. Komentarze do zapytań zawierają objaśnienie progów, poziom szczegółowości każdego etapu i wyniki na dostarczonej bazie.

Aby zobaczyć obydwa zestawy wyników w DB Browser, zaznacz i uruchom osobno zapytanie raportu oraz zapytanie `WITH allowlist … EXCEPT`. Do zapisania widoku w bazie użyj przycisku **Zapisz zmiany**.

## B — Import, audyt i indeks

Rozpakuj ZIP i uruchom poniższe polecenie w rozpakowanym katalogu.

```bash
python zadanie_B.py
```

Wystarczy Python 3 z wbudowanym modułem `sqlite3`. Skrypt sam tworzy tymczasową kopię załączonej bazy. Wczytuje polecenia z `zadanie_B.sql`, wypisuje schemat, dwukrotnie importuje dwie nowe próbki, testuje trigger z `ROLLBACK` i porównuje plany wykonania tego samego zapytania. Oryginalny CSV ze startera jest już zaimportowany w bazie, więc do testu użyto dwóch zdarzeń z nowymi kluczami.

`wyniki_B.txt` zawiera zapis rzeczywistego uruchomienia. Pozycja `changed_at` w zapisie audytu zależy od chwili wykonania. Plik `zadanie_B.sql` można też uruchomić osobno na kopii bazy, żeby sprawdzić schemat, historię alertu i plany zapytania bezpośrednio w SQLite.
