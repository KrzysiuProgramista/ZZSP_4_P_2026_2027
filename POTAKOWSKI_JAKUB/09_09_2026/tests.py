from uuid import uuid4

from fastapi.testclient import TestClient

from main import app, service


def client() -> TestClient:
    service._expenses.clear() 
    return TestClient(app)


def payload(**overrides):
    value = {"amount": "10.50", "category": "food", "description": "Lunch", "spent_on": "2026-09-01"}
    value.update(overrides)
    return value


def test_create_expense():
    assert client().post("/expenses", json=payload()).status_code == 201


def test_create_rejects_non_positive_amount():
    assert client().post("/expenses", json=payload(amount=0)).status_code == 422


def test_create_rejects_unknown_category():
    assert client().post("/expenses", json=payload(category="travel")).status_code == 422


def test_create_rejects_future_date():
    assert client().post("/expenses", json=payload(spent_on="2999-01-01")).status_code == 422


def test_create_rejects_long_description():
    assert client().post("/expenses", json=payload(description="x" * 201)).status_code == 422


def test_list_filters_by_category_and_date():
    test_client = client()
    test_client.post("/expenses", json=payload(category="food", spent_on="2026-09-01"))
    test_client.post("/expenses", json=payload(category="health", spent_on="2026-09-03"))
    response = test_client.get("/expenses?category=food&from=2026-09-01&to=2026-09-02")
    assert len(response.json()) == 1


def test_get_expense():
    test_client = client()
    expense_id = test_client.post("/expenses", json=payload()).json()["id"]
    assert test_client.get(f"/expenses/{expense_id}").status_code == 200


def test_get_missing_expense():
    assert client().get(f"/expenses/{uuid4()}").status_code == 404


def test_patch_expense():
    test_client = client()
    expense_id = test_client.post("/expenses", json=payload()).json()["id"]
    response = test_client.patch(f"/expenses/{expense_id}", json={"amount": "12.00"})
    assert response.status_code == 200 and response.json()["amount"] == "12.00"


def test_delete_expense():
    test_client = client()
    expense_id = test_client.post("/expenses", json=payload()).json()["id"]
    assert test_client.delete(f"/expenses/{expense_id}").status_code == 204


def test_summary():
    test_client = client()
    test_client.post("/expenses", json=payload(amount="10", spent_on="2026-09-01"))
    test_client.post("/expenses", json=payload(amount="20", category="health", spent_on="2026-09-02"))
    response = test_client.get("/expenses/summary?from=2026-09-01&to=2026-09-02")
    assert response.json()["total"] == "30" and response.json()["average_per_day"] == "15"


def test_summary_rejects_invalid_range():
    response = client().get("/expenses/summary?from=2026-09-03&to=2026-09-01")
    assert response.status_code == 400