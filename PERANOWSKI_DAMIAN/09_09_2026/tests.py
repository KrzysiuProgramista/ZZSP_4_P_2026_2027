import unittest
from fastapi.testclient import TestClient
from datetime import timedelta
from main import *

class TestExpensesAPI(unittest.TestCase):
    def setUp(self):
        service._expenses.clear()
        service._next_id = 1
        self.client = TestClient(app)

    def test_create_expense(self):
        response = self.client.post(
            "/expenses",
            json={
                "amount": 15.50,
                "category": "food",
                "description": "Lunch with friends",
                "spent_on": str(date.today()),
            },
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["amount"], 15.50)
        self.assertEqual(data["category"], "food")

    def test_create_expense_future_date_fails(self):
        future_date = date.today() + timedelta(days=2)
        response = self.client.post(
            "/expenses",
            json={
                "amount": 20.00,
                "category": "transport",
                "description": "Future travel",
                "spent_on": str(future_date),
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_get_expense_by_id(self):
        post_res = self.client.post(
            "/expenses",
            json={
                "amount": 100.0,
                "category": "housing",
                "description": "Rent",
                "spent_on": str(date.today()),
            },
        )
        expense_id = post_res.json()["id"]

        response = self.client.get(f"/expenses/{expense_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["description"], "Rent")

    def test_get_expense_not_found(self):
        response = self.client.get("/expenses/999")
        self.assertEqual(response.status_code, 404)

    def test_list_expenses_with_filters(self):
        today = str(date.today())
        self.client.post("/expenses", json={"amount": 10, "category": "food", "description": "Apple", "spent_on": today})
        self.client.post("/expenses", json={"amount": 50, "category": "health", "description": "Medication", "spent_on": today})

        response = self.client.get("/expenses?category=food")
        self.assertEqual(response.status_code, 200)
        items = response.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["description"], "Apple")

    def test_update_expense(self):
        post_res = self.client.post(
            "/expenses",
            json={
                "amount": 12.0,
                "category": "other",
                "description": "Old name",
                "spent_on": str(date.today()),
            },
        )
        expense_id = post_res.json()["id"]

        response = self.client.patch(
            f"/expenses/{expense_id}",
            json={"description": "New name", "amount": 15.0},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["description"], "New name")
        self.assertEqual(data["amount"], 15.0)

    def test_update_expense_not_found(self):
        response = self.client.patch("/expenses/999", json={"amount": 10.0})
        self.assertEqual(response.status_code, 404)

    def test_delete_expense(self):
        post_res = self.client.post(
            "/expenses",
            json={
                "amount": 5.0,
                "category": "food",
                "description": "Coffee",
                "spent_on": str(date.today()),
            },
        )
        expense_id = post_res.json()["id"]

        del_response = self.client.delete(f"/expenses/{expense_id}")
        self.assertEqual(del_response.status_code, 204)

        get_response = self.client.get(f"/expenses/{expense_id}")
        self.assertEqual(get_response.status_code, 404)

    def test_delete_expense_not_found(self):
        response = self.client.delete("/expenses/999")
        self.assertEqual(response.status_code, 404)

    def test_expense_summary(self):
        today = str(date.today())
        self.client.post("/expenses", json={"amount": 40.0, "category": "food", "description": "Dinner", "spent_on": today})
        self.client.post("/expenses", json={"amount": 60.0, "category": "food", "description": "Groceries", "spent_on": today})

        response = self.client.get("/expenses/summary")
        self.assertEqual(response.status_code, 200)
        summary = response.json()
        self.assertEqual(summary["total"], 100.0)
        self.assertEqual(summary["total_per_category"]["food"], 100.0)

    def test_summary_invalid_date_range_fails(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        response = self.client.get(f"/expenses/summary?from={tomorrow}&to={today}")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()