
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app, storage


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    storage.clear()
    yield
    storage.clear()


def create_expense(
    amount="25.50",
    category="food",
    description="Lunch",
    spent_on="2026-09-01",
):
    return client.post(
        "/expenses",
        json={
            "amount": amount,
            "category": category,
            "description": description,
            "spent_on": spent_on,
        },
    )


def test_create_expense():
    response = create_expense()

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == "25.50"
    assert data["category"] == "food"
    assert data["description"] == "Lunch"
    assert "id" in data


def test_amount_must_be_positive():
    response = create_expense(amount="0")

    assert response.status_code == 422


def test_category_must_be_valid():
    response = create_expense(category="invalid")

    assert response.status_code == 422


def test_description_must_not_be_empty():
    response = create_expense(description="")

    assert response.status_code == 422


def test_description_max_length():
    response = create_expense(description="x" * 201)

    assert response.status_code == 422


def test_spent_on_cannot_be_in_future():
    future = date.today() + timedelta(days=1)

    response = create_expense(
        spent_on=future.isoformat()
    )

    assert response.status_code == 422


def test_get_expense():
    created = create_expense().json()

    response = client.get(
        f"/expenses/{created['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_expense():
    response = client.get(
        "/expenses/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


def test_filter_by_category():
    create_expense(category="food")
    create_expense(category="transport")

    response = client.get(
        "/expenses?category=food"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "food"


def test_filter_by_date_range():
    create_expense(spent_on="2026-09-01")
    create_expense(spent_on="2026-09-05")
    create_expense(spent_on="2026-09-10")

    response = client.get(
        "/expenses?from=2026-09-02&to=2026-09-06"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["spent_on"] == "2026-09-05"


def test_invalid_date_range():
    response = client.get(
        "/expenses?from=2026-09-10&to=2026-09-01"
    )

    assert response.status_code == 422


def test_patch_expense():
    created = create_expense().json()

    response = client.patch(
        f"/expenses/{created['id']}",
        json={
            "amount": "40.00",
            "description": "Updated lunch",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == "40.00"
    assert data["description"] == "Updated lunch"
    assert data["category"] == "food"


def test_patch_missing_expense():
    response = client.patch(
        "/expenses/00000000-0000-0000-0000-000000000000",
        json={"amount": "10.00"},
    )

    assert response.status_code == 404


def test_delete_expense():
    created = create_expense().json()

    response = client.delete(
        f"/expenses/{created['id']}"
    )

    assert response.status_code == 204

    response = client.get(
        f"/expenses/{created['id']}"
    )

    assert response.status_code == 404


def test_delete_missing_expense():
    response = client.delete(
        "/expenses/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404


def test_summary():
    create_expense(
        amount="10.00",
        category="food",
        spent_on="2026-09-01",
    )

    create_expense(
        amount="20.00",
        category="food",
        spent_on="2026-09-02",
    )

    create_expense(
        amount="30.00",
        category="transport",
        spent_on="2026-09-03",
    )

    response = client.get(
        "/expenses/summary?from=2026-09-01&to=2026-09-03"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == "60.00"
    assert data["total_per_category"]["food"] == "30.00"
    assert data["total_per_category"]["transport"] == "30.00"
    assert data["average_per_day"] == "20.00"


def test_empty_summary():
    response = client.get(
        "/expenses/summary?from=2026-09-01&to=2026-09-03"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == "0"
    assert data["average_per_day"] == "0.00"
