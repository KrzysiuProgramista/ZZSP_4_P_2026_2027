from datetime import date, timedelta
from fastapi.testclient import TestClient
from main import app, expense_service

client = TestClient(app)


def setup_function():
    """Clear in-memory storage before each test."""
    expense_service._storage.clear()
    expense_service._counter = 1


# 1. Test successful creation
def test_create_expense():
    response = client.post(
        "/expenses",
        json={
            "amount": 45.50,
            "category": "Food",
            "description": "Lunch with client",
            "spent_on": str(date.today()),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["amount"] == 45.50
    assert data["category"] == "Food"


# 2. Test validation failure (amount <= 0)
def test_create_expense_invalid_amount():
    response = client.post(
        "/expenses",
        json={
            "amount": 0,
            "category": "Food",
            "description": "Zero amount",
            "spent_on": str(date.today()),
        },
    )
    assert response.status_code == 422


# 3. Test validation failure (invalid category)
def test_create_expense_invalid_category():
    response = client.post(
        "/expenses",
        json={
            "amount": 10.0,
            "category": "InvalidCategory",
            "description": "Test",
            "spent_on": str(date.today()),
        },
    )
    assert response.status_code == 422


# 4. Test validation failure (future date)
def test_create_expense_future_date():
    future_date = date.today() + timedelta(days=1)
    response = client.post(
        "/expenses",
        json={
            "amount": 10.0,
            "category": "Food",
            "description": "Time travel lunch",
            "spent_on": str(future_date),
        },
    )
    assert response.status_code == 422


# 5. Test getting single expense by ID (Success & 404)
def test_get_expense_by_id():
    # Create item first
    res = client.post(
        "/expenses",
        json={
            "amount": 20.0,
            "category": "Transport",
            "description": "Bus ticket",
            "spent_on": str(date.today()),
        },
    )
    expense_id = res.json()["id"]

    # Fetch existing
    get_res = client.get(f"/expenses/{expense_id}")
    assert get_res.status_code == 200
    assert get_res.json()["description"] == "Bus ticket"

    # Fetch non-existent
    not_found_res = client.get("/expenses/999")
    assert not_found_res.status_code == 404


# 6. Test listing expenses with category and date filters
def test_list_expenses_with_filters():
    today = date.today()
    yesterday = today - timedelta(days=1)

    client.post("/expenses", json={"amount": 10, "category": "Food", "description": "A", "spent_on": str(yesterday)})
    client.post("/expenses", json={"amount": 20, "category": "Utilities", "description": "B", "spent_on": str(today)})

    # Filter by category
    res = client.get("/expenses?category=Food")
    assert len(res.json()) == 1
    assert res.json()[0]["description"] == "A"

    # Filter by date range (from / to)
    res_range = client.get(f"/expenses?from={yesterday}&to={yesterday}")
    assert len(res_range.json()) == 1
    assert res_range.json()[0]["description"] == "A"


# 7. Test PATCH update
def test_update_expense():
    res = client.post(
        "/expenses",
        json={
            "amount": 100.0,
            "category": "Entertainment",
            "description": "Movie tickets",
            "spent_on": str(date.today()),
        },
    )
    expense_id = res.json()["id"]

    patch_res = client.patch(
        f"/expenses/{expense_id}",
        json={"amount": 120.0, "description": "IMAX Movie tickets"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["amount"] == 120.0
    assert patch_res.json()["description"] == "IMAX Movie tickets"
    assert patch_res.json()["category"] == "Entertainment"  # unchanged


# 8. Test DELETE expense
def test_delete_expense():
    res = client.post(
        "/expenses",
        json={
            "amount": 5.0,
            "category": "Other",
            "description": "Gum",
            "spent_on": str(date.today()),
        },
    )
    expense_id = res.json()["id"]

    del_res = client.delete(f"/expenses/{expense_id}")
    assert del_res.status_code == 204

    # Verify it's gone
    get_res = client.get(f"/expenses/{expense_id}")
    assert get_res.status_code == 404


# 9. Test summary endpoint (totals, per category, daily average)
def test_expenses_summary():
    today = date.today()
    yesterday = today - timedelta(days=1)

    client.post("/expenses", json={"amount": 50, "category": "Food", "description": "Dinner", "spent_on": str(yesterday)})
    client.post("/expenses", json={"amount": 150, "category": "Utilities", "description": "Power", "spent_on": str(today)})

    res = client.get(f"/expenses/summary?from={yesterday}&to={today}")
    assert res.status_code == 200
    summary = res.json()

    assert summary["total"] == 200.0
    assert summary["total_per_category"]["Food"] == 50.0
    assert summary["total_per_category"]["Utilities"] == 150.0
    # Range is 2 days (yesterday to today inclusive), 200 / 2 = 100.0
    assert summary["average_per_day"] == 100.0


# 10. Test PATCH update returning 404 when item doesn't exist
def test_update_nonexistent_expense():
    res = client.patch("/expenses/999", json={"amount": 50.0})
    assert res.status_code == 404