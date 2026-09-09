from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app, repository

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    repository.clear()


def expense_payload(
    *,
    amount="12.50",
    category="food",
    description="Lunch",
    spent_on="2026-01-10",
):
    return {
        "amount": amount,
        "category": category,
        "description": description,
        "spent_on": spent_on,
    }


def test_create_expense():
    response = client.post("/expenses", json=expense_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["amount"] == "12.50"
    assert body["category"] == "food"


def test_create_rejects_non_positive_amount():
    response = client.post(
        "/expenses",
        json=expense_payload(amount="0"),
    )

    assert response.status_code == 422


def test_create_rejects_unknown_category():
    response = client.post(
        "/expenses",
        json=expense_payload(category="travel"),
    )

    assert response.status_code == 422


def test_create_rejects_empty_description():
    response = client.post(
        "/expenses",
        json=expense_payload(description=""),
    )

    assert response.status_code == 422


def test_create_rejects_future_date():
    future_date = (date.today() + timedelta(days=1)).isoformat()

    response = client.post(
        "/expenses",
        json=expense_payload(spent_on=future_date),
    )

    assert response.status_code == 422


def test_get_expense():
    created = client.post(
        "/expenses",
        json=expense_payload(),
    ).json()

    response = client.get(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert response.json()["description"] == "Lunch"


def test_get_missing_expense_returns_404():
    response = client.get("/expenses/999")

    assert response.status_code == 404


def test_list_filters_by_category():
    client.post(
        "/expenses",
        json=expense_payload(category="food"),
    )
    client.post(
        "/expenses",
        json=expense_payload(category="transport"),
    )

    response = client.get("/expenses?category=food")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "food"


def test_list_filters_by_date_range():
    client.post(
        "/expenses",
        json=expense_payload(spent_on="2026-01-01"),
    )
    client.post(
        "/expenses",
        json=expense_payload(spent_on="2026-01-15"),
    )
    client.post(
        "/expenses",
        json=expense_payload(spent_on="2026-02-01"),
    )

    response = client.get(
        "/expenses?from=2026-01-01&to=2026-01-31"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_invalid_date_range_returns_400():
    response = client.get(
        "/expenses?from=2026-02-01&to=2026-01-01"
    )

    assert response.status_code == 400


def test_patch_expense():
    created = client.post(
        "/expenses",
        json=expense_payload(),
    ).json()

    response = client.patch(
        f"/expenses/{created['id']}",
        json={
            "amount": "20.00",
            "description": "Dinner",
        },
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "20.00"
    assert response.json()["description"] == "Dinner"


def test_delete_expense():
    created = client.post(
        "/expenses",
        json=expense_payload(),
    ).json()

    response = client.delete(f"/expenses/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/expenses/{created['id']}").status_code == 404


def test_summary():
    client.post(
        "/expenses",
        json=expense_payload(
            amount="10.00",
            category="food",
            spent_on="2026-01-01",
        ),
    )
    client.post(
        "/expenses",
        json=expense_payload(
            amount="20.00",
            category="transport",
            spent_on="2026-01-02",
        ),
    )

    response = client.get(
        "/expenses/summary?from=2026-01-01&to=2026-01-02"
    )

    assert response.status_code == 200

    body = response.json()
    assert body["total"] == "30.00"
    assert body["total_per_category"]["food"] == "10.00"
    assert body["total_per_category"]["transport"] == "20.00"
    assert body["average_per_day"] == "15.00"


def test_summary_can_filter_by_category():
    client.post(
        "/expenses",
        json=expense_payload(
            amount="10.00",
            category="food",
            spent_on="2026-01-01",
        ),
    )
    client.post(
        "/expenses",
        json=expense_payload(
            amount="20.00",
            category="transport",
            spent_on="2026-01-01",
        ),
    )

    response = client.get(
        "/expenses/summary?category=food&from=2026-01-01&to=2026-01-01"
    )

    assert response.status_code == 200
    assert response.json()["total"] == "10.00"
