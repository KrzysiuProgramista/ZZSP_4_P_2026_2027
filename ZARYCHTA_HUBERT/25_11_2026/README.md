# Automotive Service 

W tym wariancie operacje obsługuje klasa `Workshop` oparta na otrzymanym połączeniu `sqlite3`. Wymagane funkcje `create_order`, `add_service_to_order` i `complete_order` są udostępnione jako interfejs modułu; API wywołuje wymagane funkcje, które korzystają z metod klasy. `database/seed.sql` pochodzi z zadania.

Uruchom z katalogu tego wariantu:

```bash
python -m pip install -r requirements.txt
python -m unittest -v test_service.py
uvicorn main:app --reload
```

Dokumentacja: `http://127.0.0.1:8000/docs`. Baza `database/workshop.db` zawiera dane z `seed.sql`. Dla innej lokalizacji bazy: `python init_db.py --path nowa.db`, a przed startem serwera ustaw zmienną `WORKSHOP_DB` na `nowa.db`. Odpowiedzi API: 404 dla brakujących rekordów, 409 dla konfliktów biznesowych, 422 dla niepoprawnych wartości pól. `queries.sql` można otworzyć w narzędziu do SQLite; ostatnie zapytanie odnosi się do ostatnich 12 miesięcy od daty wykonania.
