from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app, expenses_db


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    expenses_db.clear()
    yield
    expenses_db.clear()


def create_expense(
    amount="10.00",
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

    assert data["id"] == 1
    assert data["amount"] == "10.00"
    assert data["category"] == "food"
    assert data["description"] == "Lunch"
    assert data["spent_on"] == "2026-09-01"


def test_amount_must_be_positive():
    response = create_expense(amount="0")

    assert response.status_code == 422


def test_negative_amount_is_rejected():
    response = create_expense(amount="-5")

    assert response.status_code == 422


def test_invalid_category_is_rejected():
    response = create_expense(category="invalid")

    assert response.status_code == 422


def test_empty_description_is_rejected():
    response = create_expense(description="")

    assert response.status_code == 422


def test_description_too_long_is_rejected():
    response = create_expense(description="x" * 201)

    assert response.status_code == 422


def test_future_date_is_rejected():
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


def test_get_nonexistent_expense():
    response = client.get("/expenses/999")

    assert response.status_code == 404


def test_list_expenses():
    create_expense(amount="10")
    create_expense(amount="20")

    response = client.get("/expenses")

    assert response.status_code == 200
    assert len(response.json()) == 2


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
    create_expense(
        amount="10",
        spent_on="2026-09-01",
    )
    create_expense(
        amount="20",
        spent_on="2026-09-05",
    )
    create_expense(
        amount="30",
        spent_on="2026-09-10",
    )

    response = client.get(
        "/expenses",
        params={
            "from": "2026-09-02",
            "to": "2026-09-06",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["amount"] == "20.00"


def test_patch_expense():
    created = create_expense().json()

    response = client.patch(
        f"/expenses/{created['id']}",
        json={
            "amount": "25.50",
            "description": "Updated lunch",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == "25.50"
    assert data["description"] == "Updated lunch"


def test_patch_nonexistent_expense():
    response = client.patch(
        "/expenses/999",
        json={"amount": "20"},
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


def test_delete_nonexistent_expense():
    response = client.delete("/expenses/999")

    assert response.status_code == 404


def test_summary():
    create_expense(
        amount="10",
        category="food",
        spent_on="2026-09-01",
    )
    create_expense(
        amount="20",
        category="food",
        spent_on="2026-09-02",
    )
    create_expense(
        amount="30",
        category="transport",
        spent_on="2026-09-03",
    )

    response = client.get(
        "/expenses/summary",
        params={
            "from": "2026-09-01",
            "to": "2026-09-03",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == "60.00"
    assert data["average_per_day"] == "20.00"

    categories = {
        item["category"]: item["total"]
        for item in data["total_per_category"]
    }

    assert categories["food"] == "30.00"
    assert categories["transport"] == "30.00"
