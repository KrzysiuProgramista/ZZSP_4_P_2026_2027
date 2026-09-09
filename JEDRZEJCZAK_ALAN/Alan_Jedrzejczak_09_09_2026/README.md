# expenses

A tiny FastAPI service to track expenses. In-memory storage only (no database yet).

## Project layout

```
expenses/
  models.py   -> Pydantic models (Create / Update / Public) + validation rules
  service.py  -> business logic + in-memory storage (no FastAPI imports)
  main.py     -> FastAPI app, routes call into service.py
tests/
  test_expenses.py -> 20 tests using FastAPI's TestClient
```

## Setup

```bash
pip install -r requirements.txt
```

## Run the API

```bash
uvicorn expenses.main:app --reload
```

Then open http://127.0.0.1:8000/docs for the interactive API docs.

## Run the tests

```bash
pytest
```

## Endpoints

- `POST /expenses` - create an expense
- `GET /expenses?category=&from=&to=` - list expenses, all filters optional
- `GET /expenses/{id}` - get one expense
- `PATCH /expenses/{id}` - update one or more fields
- `DELETE /expenses/{id}` - delete an expense
- `GET /expenses/summary?from=&to=` - total, total per category, and average per day

## Validation rules

- `amount` must be greater than 0
- `category` must be one of: `food`, `transport`, `entertainment`, `utilities`, `health`, `other`
- `description` must be 1-200 characters
- `spent_on` cannot be a future date
