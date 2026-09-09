from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from expenses.main import app, service


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    service._expenses.clear()
    service._next_id = 1


def sample_expense(
    amount=25.50,
    category="food",
    description="Lunch",
    spent_on=None,
):
    return {
        "amount": amount,
        "category": category,
        "description": description,
        "spent_on": spent_on or date.today().isoformat(),
    }


def test_create_expense():
    response = client.post("/expenses", json=sample_expense())

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["amount"] == 25.50


def test_create_rejects_non_positive_amount():
    response = client.post("/expenses", json=sample_expense(amount=0))

    assert response.status_code == 422


def test_create_rejects_future_date():
    future = (date.today() + timedelta(days=1)).isoformat()
    response = client.post(
        "/expenses",
        json=sample_expense(spent_on=future),
    )

    assert response.status_code == 422


def test_create_rejects_invalid_category():
    response = client.post(
        "/expenses",
        json=sample_expense(category="illegal-category"),
    )

    assert response.status_code == 422


def test_create_rejects_description_over_200_chars():
    response = client.post(
        "/expenses",
        json=sample_expense(description="x" * 201),
    )

    assert response.status_code == 422


def test_get_all_expenses():
    client.post("/expenses", json=sample_expense())
    client.post(
        "/expenses",
        json=sample_expense(
            amount=10,
            category="transport",
            description="Bus",
        ),
    )

    response = client.get("/expenses")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_by_category():
    client.post("/expenses", json=sample_expense(category="food"))
    client.post(
        "/expenses",
        json=sample_expense(
            category="transport",
            description="Bus",
        ),
    )

    response = client.get("/expenses?category=food")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "food"


def test_filter_by_date_range():
    client.post(
        "/expenses",
        json=sample_expense(spent_on="2026-09-01"),
    )
    client.post(
        "/expenses",
        json=sample_expense(
            description="Later",
            spent_on="2026-09-05",
        ),
    )

    response = client.get(
        "/expenses?from=2026-09-03&to=2026-09-06"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["description"] == "Later"


def test_get_expense_by_id():
    created = client.post("/expenses", json=sample_expense()).json()

    response = client.get(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert response.json()["description"] == "Lunch"


def test_get_missing_expense_returns_404():
    response = client.get("/expenses/999")

    assert response.status_code == 404


def test_patch_expense():
    created = client.post("/expenses", json=sample_expense()).json()

    response = client.patch(
        f"/expenses/{created['id']}",
        json={"amount": 99.99, "description": "Big lunch"},
    )

    assert response.status_code == 200
    assert response.json()["amount"] == 99.99
    assert response.json()["description"] == "Big lunch"
    assert response.json()["category"] == "food"


def test_delete_expense():
    created = client.post("/expenses", json=sample_expense()).json()

    delete_response = client.delete(f"/expenses/{created['id']}")
    get_response = client.get(f"/expenses/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_summary():
    client.post(
        "/expenses",
        json=sample_expense(
            amount=30,
            category="food",
            spent_on="2026-09-01",
        ),
    )
    client.post(
        "/expenses",
        json=sample_expense(
            amount=20,
            category="transport",
            description="Bus",
            spent_on="2026-09-02",
        ),
    )

    response = client.get(
        "/expenses/summary?from=2026-09-01&to=2026-09-02"
    )

    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 50
    assert data["total_per_category"]["food"] == 30
    assert data["total_per_category"]["transport"] == 20
    assert data["average_per_day"] == 25


def test_invalid_date_range_returns_400():
    response = client.get(
        "/expenses?from=2026-09-10&to=2026-09-01"
    )

    assert response.status_code == 400
