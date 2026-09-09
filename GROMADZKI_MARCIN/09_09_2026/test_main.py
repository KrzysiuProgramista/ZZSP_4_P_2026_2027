from datetime import date, timedelta
from fastapi.testclient import TestClient
from main import app, service

def setup_function():
    service.db.clear()
    service.counter = 1

client = TestClient(app)


def test_create_expense_success():
    response = client.post(
        "/expenses",
        json={
            "amount": 45.50,
            "category": "Food",
            "description": "Grocery shopping",
            "spent_on": str(date.today())
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["amount"] == 45.50
    assert data["category"] == "Food"


def test_create_expense_future_date():
    future_date = date.today() + timedelta(days=2)
    response = client.post(
        "/expenses",
        json={
            "amount": 20.0,
            "category": "Transport",
            "description": "Future ticket",
            "spent_on": str(future_date)
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Date cannot be in the future"


def test_create_expense_invalid_amount():
    response = client.post(
        "/expenses",
        json={
            "amount": 0,
            "category": "Bills",
            "description": "Electricity",
            "spent_on": str(date.today())
        }
    )
    assert response.status_code == 422


def test_get_expenses_empty():
    response = client.get("/expenses")
    assert response.status_code == 200
    assert response.json() == []


def test_get_expenses_with_filters():
    client.post("/expenses", json={"amount": 10.0, "category": "Food", "description": "Coffee", "spent_on": str(date.today())})
    client.post("/expenses", json={"amount": 100.0, "category": "Tech", "description": "Mouse", "spent_on": str(date.today())})

    response = client.get("/expenses?category=Food")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Food"

    today_str = str(date.today())
    response = client.get(f"/expenses?from={today_str}")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_single_expense():
    client.post("/expenses", json={"amount": 15.0, "category": "Misc", "description": "Movie", "spent_on": str(date.today())})
    
    response = client.get("/expenses/1")
    assert response.status_code == 200
    assert response.json()["description"] == "Movie"


def test_get_expense_not_found():
    response = client.get("/expenses/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not found"


def test_update_expense():
    client.post("/expenses", json={"amount": 30.0, "category": "Food", "description": "Pills", "spent_on": str(date.today())})
    
    response = client.patch("/expenses/1", json={"amount": 35.0})
    assert response.status_code == 200
    assert response.json()["amount"] == 35.0
    assert response.json()["description"] == "Pills"


def test_delete_expense():
    client.post("/expenses", json={"amount": 5.0, "category": "Misc", "description": "Gum", "spent_on": str(date.today())})
    
    delete_response = client.delete("/expenses/1")
    assert delete_response.status_code == 204

    get_response = client.get("/expenses/1")
    assert get_response.status_code == 404

def test_get_summary():
    client.post("/expenses", json={"amount": 50.0, "category": "Food", "description": "Lunch", "spent_on": str(date.today())})
    response = client.get("/expenses/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 50.0
    assert "Food" in data["total_per_category"]