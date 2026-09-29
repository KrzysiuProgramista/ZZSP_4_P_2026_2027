# Ćwiczenia 2–6: dekoratory w Pythonie

Gotowe przykłady wymagają **Pythona 3.10+** i korzystają wyłącznie z biblioteki
standardowej. Otwórz terminal w folderze `16_09_2026` i uruchom:

```powershell
python run_exercises.py
python -m unittest test_ex2 -v
```

Każde ćwiczenie można też uruchomić osobno, np. `python ex3.py`.
Importowanie modułów nie uruchamia demonstracji. Demonstracja `retry` oraz
wszystkie jej testy zastępują `sleep` atrapą, więc nie czekają na opóźnienia.

| Plik | Zawartość |
| --- | --- |
| `ex2.py` | Ponawianie wywołań, narastające opóźnienia i logowanie |
| `ex3.py` | Własne `memoize`, Fibonacci i `lru_cache` |
| `ex4.py` | Walidacja typów i wartości oraz ostrzeżenia |
| `ex5.py` | Dekorowanie metod i klas, porównanie z metaklasą |
| `ex6.py` | Kolejność działania kilku dekoratorów |
| `test_ex2.py` | Dokładnie sześć testów `retry` |
| `run_exercises.py` | Uruchomienie wszystkich demonstracji |

## Ćwiczenie 2 — dekorator z argumentami

```python
@retry(times=5, delay=0.5, exceptions=(ValueError,), backoff=2)
def unstable():
    ...
```

- `times` oznacza łączną liczbę prób, razem z pierwszym wywołaniem.
- Opóźnienie rośnie według `delay * backoff ** retry_index`: 0.5, 1, 2, 4 s.
  `backoff=1` daje stałe opóźnienie.
- Domyślnie ponawiany jest tylko `ValueError` i jego podklasy. Parametr
  `exceptions` pozwala wskazać inną krotkę klas wyjątków.
- Każde faktyczne ponowienie zapisuje w logu numer próby, błąd i opóźnienie.
  Po ostatniej porażce wyjątek jest zgłaszany dalej bez dodatkowego czekania.
- `functools.wraps` zachowuje nazwę i dokumentację oryginalnej funkcji.

Demonstracja kończy się wynikiem `"success"` po dwóch porażkach. Atrapa `sleep`
rejestruje opóźnienia `[0.5, 1.0]`. Sześć testów sprawdza natychmiastowy sukces,
sukces po błędach wraz z backoffem i logowaniem, wyczerpanie prób, wskazane
wyjątki i ich podklasy, inne wyjątki oraz przekazywanie argumentów i stały backoff.

## Ćwiczenie 3 — zapamiętywanie wyników

`ex3.py` porównuje `fib_naive(35)`, `fib_memoized(35)` i `fib(35)` z dekoratorem
`@lru_cache(maxsize=128)`. Wszystkie zwracają **9 227 465**. Mierzone są pierwsze
wywołanie z pustym cache i kolejne wywołanie; czasy zależą od komputera.

Własny `@memoize` przechowuje wyniki w słowniku. Klucz zawiera argumenty pozycyjne
i posortowane argumenty nazwane. Listy i słowniki nie mogą być kluczami:
wywołania z takimi argumentami działają, lecz pomijają cache. Przykład pokazuje
dwa wykonania dla dwóch list oraz jedno wykonanie dla dwóch takich samych krotek.

Rekurencja przechodzi przez udekorowane funkcje, więc wyniki pośrednie również
są zapamiętywane. Własny cache jest nieograniczony; `lru_cache` ogranicza liczbę
wpisów, udostępnia statystyki i także wymaga argumentów hashowalnych.

```text
fib.cache_info(): CacheInfo(hits=34, misses=36, maxsize=128, currsize=36)
```

Statystyka uwzględnia drugie wywołanie `fib(35)`. Cache stosuj do funkcji, których
wynik pozostaje poprawny przy ponownym użyciu tych samych argumentów.

## Ćwiczenie 4 — walidacja

- `@validate_types` korzysta z `inspect.signature` i `typing.get_type_hints`.
  Sprawdza argumenty pozycyjne, nazwane, domyślne i zmienną liczbę argumentów.
  Obsługuje zwykłe typy, unie i popularne kontenery, także zagnieżdżone.
  Niezgodność powoduje `TypeError`; typ wyniku nie jest sprawdzany.
- `@require_positive("amount")` odnajduje argument po nazwie, również przy
  przekazaniu pozycyjnym lub użyciu wartości domyślnej. Zero i wartości ujemne
  powodują `ValueError`, a nieodpowiednie typy — `TypeError`.
- `@deprecated("use new_function instead")` emituje `DeprecationWarning`.
  `stacklevel=2` wskazuje miejsce wywołania. Demonstracja przechwytuje ostrzeżenie,
  ponieważ ta kategoria bywa domyślnie ukryta.

## Ćwiczenie 5 — metody i klasy

`@timer` przekazuje `*args, **kwargs`, w tym `self` jako pierwszy argument metody.
`@time_all_methods` dekoruje metody zdefiniowane bezpośrednio w klasie:
zwykłe, statyczne, klasowe oraz `__init__`. Zachowuje ich sposób wiązania.
Przykład dotyczy metod synchronicznych; nie zmienia metod odziedziczonych ani
akcesorów `property`.

`TimedMeta` robi to samo podczas tworzenia klasy. Komentarz w kodzie wyjaśnia,
dlaczego dekorator klasy jest tu czytelniejszy. Metaklasa automatycznie obejmuje
nowe metody podklas; dekorator trzeba nałożyć na podklasę ponownie.

## Ćwiczenie 6 — nakładanie dekoratorów

`ex6.py` importuje `timer` z `ex5.py`. Dekoratory nakłada się od dołu:
`@logged` nad `@timer` odpowiada `logged(timer(funkcja))`.

```text
@logged nad @timer: logged enter -> timer enter -> body -> timer exit -> logged exit
@timer nad @logged: timer enter -> logged enter -> body -> logged exit -> timer exit
```

Zewnętrzny dekorator rozpoczyna działanie pierwszy i kończy ostatni.
Demonstracja wypisuje przewidywaną i rzeczywistą kolejność. Gdy `timer` jest
zewnętrzny, czas obejmuje również oba komunikaty `logged`. Dwa przykładowe
wywołania korzystają z krótkich, rzeczywistych opóźnień po 0.01 s.
