import unittest
from fastapi.testclient import TestClient
from main import app, service


class TestExpensesAPI(unittest.TestCase):
    def setUp(self):
        """Resetowanie pamięci podręcznej przed każdym testem."""
        service._storage.clear()
        service._counter = 1
        self.client = TestClient(app)

    def test_create_expense_success(self):
        payload = {
            "amount": 45.50,
            "category": "food",
            "description": "Zakupy spożywcze",
            "spent_on": "2026-09-01",
        }
        response = self.client.post("/expenses", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["amount"], 45.50)

    def test_create_expense_invalid_amount(self):
        payload = {
            "amount": -10,
            "category": "food",
            "description": "Test",
            "spent_on": "2026-09-01",
        }
        response = self.client.post("/expenses", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_create_expense_future_date(self):
        payload = {
            "amount": 20,
            "category": "food",
            "description": "Przyszłość",
            "spent_on": "2099-01-01",
        }
        response = self.client.post("/expenses", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_get_expenses_list_and_filter(self):
        self.client.post("/expenses", json={"amount": 10, "category": "food", "description": "Obiad", "spent_on": "2026-09-01"})
        self.client.post("/expenses", json={"amount": 50, "category": "transport", "description": "Bilet", "spent_on": "2026-09-05"})

        res_all = self.client.get("/expenses")
        self.assertEqual(len(res_all.json()), 2)

        res_food = self.client.get("/expenses?category=food")
        self.assertEqual(len(res_food.json()), 1)
        self.assertEqual(res_food.json()[0]["category"], "food")

        res_date = self.client.get("/expenses?from=2026-09-02&to=2026-09-06")
        self.assertEqual(len(res_date.json()), 1)
        self.assertEqual(res_date.json()[0]["category"], "transport")

    def test_get_expense_by_id(self):
        self.client.post("/expenses", json={"amount": 15, "category": "other", "description": "Kawa", "spent_on": "2026-09-01"})
        res = self.client.get("/expenses/1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["description"], "Kawa")

    def test_get_expense_not_found(self):
        res = self.client.get("/expenses/999")
        self.assertEqual(res.status_code, 404)

    def test_patch_expense(self):
        self.client.post("/expenses", json={"amount": 100, "category": "utilities", "description": "Prąd", "spent_on": "2026-09-01"})
        res = self.client.patch("/expenses/1", json={"amount": 120.0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["amount"], 120.0)

    def test_patch_expense_not_found(self):
        res = self.client.patch("/expenses/999", json={"amount": 50})
        self.assertEqual(res.status_code, 404)

    def test_delete_expense(self):
        self.client.post("/expenses", json={"amount": 20, "category": "entertainment", "description": "Kino", "spent_on": "2026-09-01"})
        del_res = self.client.delete("/expenses/1")
        self.assertEqual(del_res.status_code, 204)

        get_res = self.client.get("/expenses/1")
        self.assertEqual(get_res.status_code, 404)

    def test_delete_expense_not_found(self):
        res = self.client.delete("/expenses/999")
        self.assertEqual(res.status_code, 404)

    def test_get_summary(self):
        self.client.post("/expenses", json={"amount": 100, "category": "food", "description": "A", "spent_on": "2026-09-01"})
        self.client.post("/expenses", json={"amount": 50, "category": "food", "description": "B", "spent_on": "2026-09-03"})
        self.client.post("/expenses", json={"amount": 30, "category": "transport", "description": "C", "spent_on": "2026-09-03"})

        res = self.client.get("/expenses/summary?from=2026-09-01&to=2026-09-03")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 180.0)
        self.assertEqual(data["total_per_category"]["food"], 150.0)
        self.assertEqual(data["total_per_category"]["transport"], 30.0)
        self.assertEqual(data["average_per_day"], 60.0)  # 180 / 3 dni


if __name__ == "__main__":
    unittest.main()