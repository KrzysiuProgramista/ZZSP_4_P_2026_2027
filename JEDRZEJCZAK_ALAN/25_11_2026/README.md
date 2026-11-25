# Automotive Service

Python `sqlite3`, FastAPI i `unittest`. Plik `database/seed.sql` to dołączone dane zadania.

## Uruchomienie

```bash
python -m pip install -r requirements.txt
python -m unittest -v test_service.py
uvicorn main:app --reload
```

Uruchamiaj polecenia z katalogu tego wariantu. API: `http://127.0.0.1:8000/docs`. Gotowa baza `database/workshop.db` zawiera zaimportowany `seed.sql`. Jeśli chcesz utworzyć dodatkową bazę, użyj `python init_db.py --path nowa.db`, a dla API ustaw `WORKSHOP_DB` na tę ścieżkę. Połączenia aplikacji i testów włączają sprawdzanie kluczy obcych. Nie używamy ORM. Brakujące rekordy: `LookupError`/404, stan lub błędny argument w serwisie: `ValueError`/409, błędy treści żądania: 422.

Zapytania z `queries.sql` można wykonywać kolejno w DB Browser for SQLite. Zapytanie 7 liczy okres względem chwili wykonania (`now`), zgodnie z poleceniem; próbka z datami 2025–2026 może dać inne wyniki po upływie czasu.
