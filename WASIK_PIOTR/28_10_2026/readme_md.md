# Dokumentacja i Instrukcja – SQL & Relational Model (Lab 5, Slajdy 24–39)

Niniejsze sprawozdanie zawiera kompletne rozwiązanie zadań laboratoryjnych ze slajdów 24–39 z wykładu *SQL & The Relational Model*.

---

## 📁 Zawartość Zestawu

W skład oddawanego rozwiązania wchodzą następujące pliki:

1. **`README.md`** – Niniejsza instrukcja dla prowadzącego z opisem zawartości i mapowaniem zadań.
2. **`schema.sql`** – Skrypt DDL tworzący bazę danych, relacje, klucze główne/obce, więzy integralności oraz indeksy.
3. **`seed.sql`** – Skrypt DML populujący bazę danymi testowymi o odpowiednim wolumenie i z uwzględnieniem przypadków brzegowych.
4. **`queries.sql`** – Skrypt zawierający zapytania SQL odpowiadające wszystkim ćwiczeniom ze slajdów 27–39 wraz z wymaganymi komentarzami teoretycznymi.
5. **`erd_diagram.jpg`** – Diagram relacji encji (ERD) wizualizujący strukturę 5 tabel bazy danych i zachodzące między nimi relacje.

---

## 🚀 Instrukcja Uruchomienia (SQLite)

Aby zweryfikować i uruchomić rozwiązanie w konsoli SQLite, należy wykonać poniższe komendy:

```bash
# 1. Uruchomienie/utworzenie bazy danych w SQLite
sqlite3 lab5.db

# 2. Włączenie wsparcia dla kluczy obcych (w SQLite wymagane dla każdego połączenia)
PRAGMA foreign_keys = ON;

# 3. Wczytanie schematu tabel i indeksów
.read schema.sql

# 4. Wypełnienie bazy danymi testowymi
.read seed.sql

# 5. Wykonanie zapytań z ćwiczeń 2–8
.read queries.sql
```

---

## 🗺️ Mapowanie Slajdów na Pliki i Kod

| Slajd | Ćwiczenie | Lokalizacja / Plik | Opis Rozwiązania |
| :--- | :--- | :--- | :--- |
| **Slajd 24–25** | **Exercise 1 – Schema & Validation** | `schema.sql` oraz `erd_diagram.jpg` | Definicja 5 tabel (`categories`, `customers`, `products`, `orders`, `order_items`), klucze główne, klucze obce z regułami, więzy `CHECK`, `UNIQUE`, `NOT NULL` oraz 2 zidentyfikowane i uzasadnione indeksy (`idx_products_category`, `idx_orders_customer`). |
| **Slajd 26** | **Exercise 2 – Seed Data** | `seed.sql` | Wstawienie 6 kategorii, 20 produktów, 10 klientów, 25 zamówień i 60 pozycji zamówień. Zapewniono obecność klientów bez zamówień i produktów niezamówionych. |
| **Slajd 27** | **Exercise 2 – Filtering & Sorting** | `queries.sql` *(Sekcja 2)* | Zapytania z klauzulami `WHERE`, `BETWEEN`, `LIKE`, `LIMIT` oraz `DISTINCT`. |
| **Slajd 28–29** | **Exercise 3 – Aggregation & HAVING** | `queries.sql` *(Sekcja 3)* | Obliczenia podsumowujące (`COUNT`, `AVG`, `MIN`, `MAX`), filtrowanie grup przy użyciu `HAVING` oraz **komentarz teoretyczny opisujący różnicę między `WHERE` a `HAVING`**. |
| **Slajd 30–31** | **Exercise 4 – JOINs & Missing Rel.** | `queries.sql` *(Sekcja 4)* | Złączenia `JOIN`, wyliczenie przychodów per klient/kategoria oraz wykrycie rekordów bez relacji (`LEFT JOIN ... WHERE IS NULL`) z **komentarzem wyjaśniającym działanie `INNER JOIN` vs `LEFT JOIN`**. |
| **Slajd 32–33** | **Exercise 5 – Subqueries & CASE** | `queries.sql` *(Sekcja 5)* | Podzapytania skalarne (produkty i klienci powyżej średniej), test predykatu `EXISTS` oraz segmentacja klientów (Gold, Silver, Bronze) za pomocą `CASE`. |
| **Slajd 34–35** | **Exercise 6 – Window Functions** | `queries.sql` *(Sekcja 6)* | Funkcje okna: `ROW_NUMBER()` (ranking produktów i Top 2 per kategoria), `AVG() OVER()`, `LAG()` (poprzednia wartość zamówienia) oraz `SUM() OVER()` (narastający przychód). |
| **Slajd 36–37** | **Exercise 7 – Transactions & Safety** | `queries.sql` *(Sekcja 7)* | Zapis operacji kupna jako transakcji (`BEGIN`, `INSERT`, `UPDATE` ze sprawdzaniem stanu magazynowego, `COMMIT`/`ROLLBACK`) oraz **komentarz wyjaśniający wymóg atomiczności**. |
| **Slajd 38–39** | **Exercise 8 – Query Plan & Trade-offs** | `queries.sql` *(Sekcja 8)* | Wykorzystanie `EXPLAIN QUERY PLAN`, porównanie operacji `SCAN` vs `SEARCH` oraz **raport analizujący wpływ indeksów na operacje odczytu i zapisu**. |

---

## 📝 Komentarze Teoretyczne (Fragmenty z kodu)

1. **WHERE vs HAVING (Slajd 29):**
   * `WHERE` filtruje poszczególne wiersze *przed* pogrupowaniem danych (`GROUP BY`).
   * `HAVING` filtruje zagregowane grupy *po* wykonaniu grupowania i wyliczeniu funkcji agregujących.

2. **Brakujące relacje i LEFT JOIN (Slajd 31):**
   * Zastosowanie `INNER JOIN` usunęłoby klientów bez zamówień i niezamówione produkty, ponieważ wymaga obecności klucza po obu stronach relacji. `LEFT JOIN` zachowuje wiersze z lewej tabeli, wstawiając `NULL` w brakujące pola.

3. **Atomiczność transakcji (Slajd 37):**
   * Wstawienie zamówienia, pozycji oraz zmiana stanu magazynowego muszą stanowić niepodzielną całość (Atomic) – awaria w trakcie execution bez transakcji doprowadziłaby do niespójności bazy danych.

4. **Wydajność indeksów (Slajd 39):**
   * Indeksy zastępują skanowanie całej tabeli (`SCAN`, $O(N)$) szybkimi wyszukiwaniami w drzewie ($O(\log N)$), przyspieszając zapytania `SELECT`, ale nieznacznie spowalniają operacje modyfikujące dane (`INSERT`, `UPDATE`, `DELETE`).