from datetime import date, timedelta
from fastapi.testclient import TestClient
from main import app, expense_service

client = TestClient(app)

def setup_function():
    # Clear out service memory storage between tests
    expense_service._storage.clear()
    expense_service._counter = 1

def test_create_expense_success():
    response = client.post("/expenses", json={
        "amount": 45.50,
        "category": "Food",
        "description": "Lunch with team",
        "spent_on": str(date.today())
    })
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["amount"] == "45.50"
    assert data["category"] == "Food"

def test_create_expense_invalid_future_date():
    future_date = date.today() + timedelta(days=1)
    response = client.post("/expenses", json={
        "amount": 10.00,
        "category": "Transport",
        "description": "Future travel",
        "spent_on": str(future_date)
    })
    assert response.status_code == 422

def test_create_expense_invalid_amount():
    response = client.post("/expenses", json={
        "amount": 0,
        "category": "Utilities",
        "description": "Zero cost item",
        "spent_on": str(date.today())
    })
    assert response.status_code == 422

def test_create_expense_invalid_category():
    response = client.post("/expenses", json={
        "amount": 25.00,
        "category": "InvalidCategory",
        "description": "Bad category test",
        "spent_on": str(date.today())
    })
    assert response.status_code == 422

def test_get_expense_by_id():
    # Create item first
    res = client.post("/expenses", json={
        "amount": 100.00,
        "category": "Entertainment",
        "description": "Concert ticket",
        "spent_on": str(date.today())
    })
    exp_id = res.json()["id"]

    response = client.get(f"/expenses/{exp_id}")
    assert response.status_code == 200
    assert response.json()["description"] == "Concert ticket"

def test_get_expense_not_found():
    response = client.get("/expenses/999")
    assert response.status_code == 404

def test_list_expenses_with_filters():
    today = date.today()
    yesterday = today - timedelta(days=1)

    client.post("/expenses", json={"amount": 15.00, "category": "Food", "description": "Coffee", "spent_on": str(yesterday)})
    client.post("/expenses", json={"amount": 50.00, "category": "Transport", "description": "Gas", "spent_on": str(today)})

    # Filter by category
    response = client.get("/expenses?category=Food")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["description"] == "Coffee"

    # Filter by date range (from / to)
    response_range = client.get(f"/expenses?from={yesterday}&to={yesterday}")
    assert response_range.status_code == 200
    assert len(response_range.json()) == 1
    assert response_range.json()[0]["description"] == "Coffee"

def test_update_expense_patch():
    res = client.post("/expenses", json={
        "amount": 20.00,
        "category": "Other",
        "description": "Misc",
        "spent_on": str(date.today())
    })
    exp_id = res.json()["id"]

    response = client.patch(f"/expenses/{exp_id}", json={"amount": 25.50})
    assert response.status_code == 200
    assert response.json()["amount"] == "25.50"
    assert response.json()["description"] == "Misc"  # Unchanged field

def test_delete_expense():
    res = client.post("/expenses", json={
        "amount": 5.00,
        "category": "Food",
        "description": "Snack",
        "spent_on": str(date.today())
    })
    exp_id = res.json()["id"]

    response = client.delete(f"/expenses/{exp_id}")
    assert response.status_code == 204

    # Verify item is gone
    get_res = client.get(f"/expenses/{exp_id}")
    assert get_res.status_code == 404

def test_expenses_summary():
    today = date.today()
    client.post("/expenses", json={"amount": 100.00, "category": "Food", "description": "Groceries", "spent_on": str(today)})
    client.post("/expenses", json={"amount": 50.00, "category": "Food", "description": "Restaurant", "spent_on": str(today)})
    client.post("/expenses", json={"amount": 200.00, "category": "Utilities", "description": "Electric bill", "spent_on": str(today)})

    response = client.get(f"/expenses/summary?from={today}&to={today}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == "350.00"
    assert data["average_per_day"] == "350.00"
    
    # Check category breakdowns
    categories = {item["category"]: item["total"] for item in data["per_category"]}
    assert categories["Food"] == "150.00"
    assert categories["Utilities"] == "200.00"

service.py

from datetime import date
from decimal import Decimal
from typing import Any, Optional
from models import ExpenseCreate, ExpenseUpdate


class ExpenseService:
    def __init__(self) -> None:
        self._storage: dict[int, dict[str, Any]] = {}
        self._counter: int = 1

    def create_expense(self, data: ExpenseCreate) -> dict[str, Any]:
        expense_id = self._counter
        self._counter += 1

        expense_dict = {
            "id": expense_id,
            "amount": data.amount,
            "category": data.category,
            "description": data.description,
            "spent_on": data.spent_on,
        }
        self._storage[expense_id] = expense_dict
        return expense_dict

    def get_expense(self, expense_id: int) -> Optional[dict[str, Any]]:
        return self._storage.get(expense_id)

    def list_expenses(
        self,
        category: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[dict[str, Any]]:
        results = []
        for expense in self._storage.values():
            if category and expense["category"] != category:
                continue
            if date_from and expense["spent_on"] < date_from:
                continue
            if date_to and expense["spent_on"] > date_to:
                continue
            results.append(expense)
        return sorted(results, key=lambda x: x["spent_on"], reverse=True)

    def update_expense(self, expense_id: int, data: ExpenseUpdate) -> Optional[dict[str, Any]]:
        expense = self._storage.get(expense_id)
        if not expense:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            expense[key] = value

        return expense

    def delete_expense(self, expense_id: int) -> bool:
        if expense_id in self._storage:
            del self._storage[expense_id]
            return True
        return False

    def get_summary(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> dict[str, Any]:
        expenses = self.list_expenses(date_from=date_from, date_to=date_to)

        total = sum((e["amount"] for e in expenses), Decimal("0.00"))

        # Group totals by category
        category_totals: dict[str, Decimal] = {}
        for e in expenses:
            cat = e["category"]
            category_totals[cat] = category_totals.get(cat, Decimal("0.00")) + e["amount"]

        per_category = [{"category": cat, "total": amt} for cat, amt in category_totals.items()]

        # Compute average per day
        if not expenses:
            avg_per_day = Decimal("0.00")
        else:
            if date_from and date_to:
                start_date = date_from
                end_date = date_to
            else:
                # Fallback to range bounds present in data if parameters aren't given
                all_dates = [e["spent_on"] for e in expenses]
                start_date = date_from if date_from else min(all_dates)
                end_date = date_to if date_to else max(all_dates)

            delta_days = (end_date - start_date).days + 1
            if delta_days <= 0:
                delta_days = 1
            
            avg_per_day = (total / Decimal(delta_days)).quantize(Decimal("0.01"))

        return {
            "total": total,
            "per_category": per_category,
            "average_per_day": avg_per_day,
            "range_start": date_from,
            "range_end": date_to,
        }
