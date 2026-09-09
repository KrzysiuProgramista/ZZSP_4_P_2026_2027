# Expenses API

FastAPI service for storing and summarising expenses.

## Requirements

- Python 3.10+
- pip

## Installation

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the API

From the `09_09_2026` directory:

```bash
uvicorn expenses.main:app --reload
```

Swagger documentation:

- http://127.0.0.1:8000/docs

## Run tests

```bash
pytest -q
```

## Expense categories

- `food`
- `transport`
- `entertainment`
- `shopping`
- `bills`
- `other`

## Endpoints

- `POST /expenses`
- `GET /expenses`
- `GET /expenses/{id}`
- `PATCH /expenses/{id}`
- `DELETE /expenses/{id}`
- `GET /expenses/summary`

### Filters

`GET /expenses` supports:

- `?category=food`
- `?from=2026-09-01`
- `?to=2026-09-09`
- combinations, e.g.:
  `?category=food&from=2026-09-01&to=2026-09-09`

`GET /expenses/summary` supports:

- `?from=2026-09-01&to=2026-09-09`

The summary returns:

- total amount,
- total amount per category,
- average amount per calendar day in the requested range.

Storage is in memory, so data is reset after restarting the application.
