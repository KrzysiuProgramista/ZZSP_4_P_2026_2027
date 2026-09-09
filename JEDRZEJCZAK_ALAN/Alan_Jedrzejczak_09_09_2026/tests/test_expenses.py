

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from expenses.main import app, service

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_service():
    service._expenses.clear()
    service._next_id = 1
    yield


def make_expense(**overrides):
    payload = {
        "amount": 25.5,
        "category": "food",
        "description": "Lunch",
        "spent_on": str(date.today()),
    }
    payload.update(overrides)
    return client.post("/expenses", json=payload)


# ---------- create ----------

def test_create_expense_success():
    response = make_expense()
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["amount"] == 25.5
    assert body["category"] == "food"
    assert body["description"] == "Lunch"


def test_create_expense_rejects_zero_or_negative_amount():
    response = make_expense(amount=0)
    assert response.status_code == 422

    response = make_expense(amount=-10)
    assert response.status_code == 422


def test_create_expense_rejects_unknown_category():
    response = make_expense(category="crypto")
    assert response.status_code == 422


def test_create_expense_rejects_future_date():
    future_date = str(date.today() + timedelta(days=1))
    response = make_expense(spent_on=future_date)
    assert response.status_code == 422


def test_create_expense_rejects_description_too_long():
    response = make_expense(description="x" * 201)
    assert response.status_code == 422


def test_create_expense_rejects_empty_description():
    response = make_expense(description="")
    assert response.status_code == 422


# ---------- list ----------

def test_list_expenses_empty_at_start():
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_list_expenses_returns_created_items():
    make_expense(description="Coffee")
    make_expense(description="Bus ticket", category="transport")

    response = client.get("/expenses")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


def test_list_expenses_filters_by_category():
    make_expense(category="food")
    make_expense(category="transport")

    response = client.get("/expenses", params={"category": "transport"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["category"] == "transport"


def test_list_expenses_filters_by_date_range():
    make_expense(spent_on="2026-01-01")
    make_expense(spent_on="2026-01-15")
    make_expense(spent_on="2026-02-01")

    response = client.get("/expenses", params={"from": "2026-01-01", "to": "2026-01-31"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


# ---------- get by id ----------

def test_get_expense_by_id():
    created = make_expense().json()

    response = client.get(f"/expenses/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_expense_not_found():
    response = client.get("/expenses/999")
    assert response.status_code == 404


# ---------- update ----------

def test_patch_expense_updates_only_given_fields():
    created = make_expense(amount=10, description="Old").json()

    response = client.patch(f"/expenses/{created['id']}", json={"amount": 99})
    assert response.status_code == 200
    body = response.json()
    assert body["amount"] == 99
    assert body["description"] == "Old"  # unchanged


def test_patch_expense_not_found():
    response = client.patch("/expenses/999", json={"amount": 5})
    assert response.status_code == 404


def test_patch_expense_rejects_invalid_amount():
    created = make_expense().json()

    response = client.patch(f"/expenses/{created['id']}", json={"amount": -5})
    assert response.status_code == 422


# ---------- delete ----------

def test_delete_expense():
    created = make_expense().json()

    response = client.delete(f"/expenses/{created['id']}")
    assert response.status_code == 204

    # it's really gone
    response = client.get(f"/expenses/{created['id']}")
    assert response.status_code == 404


def test_delete_expense_not_found():
    response = client.delete("/expenses/999")
    assert response.status_code == 404


# ---------- summary ----------

def test_summary_total_and_per_category():
    make_expense(amount=10, category="food", spent_on="2026-01-01")
    make_expense(amount=20, category="food", spent_on="2026-01-02")
    make_expense(amount=5, category="transport", spent_on="2026-01-02")

    response = client.get("/expenses/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 35
    assert body["total_per_category"] == {"food": 30, "transport": 5}


def test_summary_average_per_day_over_explicit_range():
    make_expense(amount=10, spent_on="2026-01-01")
    make_expense(amount=10, spent_on="2026-01-02")

    # 4-day range (Jan 1 -> Jan 4 inclusive), total 20 -> average 5/day
    response = client.get(
        "/expenses/summary", params={"from": "2026-01-01", "to": "2026-01-04"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 20
    assert body["average_per_day"] == 5.0


def test_summary_with_no_expenses_is_all_zero():
    response = client.get("/expenses/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["total_per_category"] == {}
    assert body["average_per_day"] == 0.0
