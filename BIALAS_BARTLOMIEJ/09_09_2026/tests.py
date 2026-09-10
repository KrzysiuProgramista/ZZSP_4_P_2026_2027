from datetime import date, timedelta

from fastapi.testclient import TestClient

from main import app, service

client = TestClient(app)


def setup_function():
    service.expenses.clear()
    service.next_id = 1


def expense(**overrides):
    data = {
        "amount": 10,
        "category": "food",
        "description": "Lunch",
        "spent_on": "2026-09-01",
    }
    data.update(overrides)
    return data


def test_create():
    response = client.post("/expenses", json=expense())
    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_amount_must_be_positive():
    response = client.post("/expenses", json=expense(amount=0))
    assert response.status_code == 422


def test_category_must_be_valid():
    response = client.post("/expenses", json=expense(category="invalid"))
    assert response.status_code == 422


def test_description_max_length():
    response = client.post("/expenses", json=expense(description="x" * 201))
    assert response.status_code == 422


def test_spent_on_cannot_be_future():
    future = (date.today() + timedelta(days=1)).isoformat()
    response = client.post("/expenses", json=expense(spent_on=future))
    assert response.status_code == 422


def test_list():
    client.post("/expenses", json=expense())
    client.post("/expenses", json=expense(category="transport"))

    response = client.get("/expenses")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_category_filter():
    client.post("/expenses", json=expense())
    client.post("/expenses", json=expense(category="transport"))

    response = client.get("/expenses?category=food")

    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "food"


def test_date_filter():
    client.post("/expenses", json=expense(spent_on="2026-09-01"))
    client.post("/expenses", json=expense(spent_on="2026-09-10"))

    response = client.get("/expenses?from=2026-09-05&to=2026-09-15")

    assert len(response.json()) == 1


def test_get():
    created = client.post("/expenses", json=expense()).json()

    response = client.get(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert response.json()["amount"] == 10


def test_get_missing():
    response = client.get("/expenses/999")
    assert response.status_code == 404


def test_patch():
    created = client.post("/expenses", json=expense()).json()

    response = client.patch(
        f"/expenses/{created['id']}",
        json={"amount": 25},
    )

    assert response.status_code == 200
    assert response.json()["amount"] == 25


def test_delete():
    created = client.post("/expenses", json=expense()).json()

    response = client.delete(f"/expenses/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/expenses/{created['id']}").status_code == 404


def test_summary():
    client.post(
        "/expenses",
        json=expense(amount=10, category="food", spent_on="2026-09-01"),
    )
    client.post(
        "/expenses",
        json=expense(amount=20, category="transport", spent_on="2026-09-02"),
    )

    response = client.get(
        "/expenses/summary?from=2026-09-01&to=2026-09-02"
    )

    assert response.status_code == 200
    assert response.json()["total"] == 30
    assert response.json()["total_per_category"] == {
        "food": 10,
        "transport": 20,
    }
    assert response.json()["average_per_day"] == 15


def test_invalid_date_range():
    response = client.get(
        "/expenses?from=2026-09-10&to=2026-09-01"
    )

    assert response.status_code == 400
