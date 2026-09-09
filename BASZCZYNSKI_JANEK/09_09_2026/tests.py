from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def testCreateExpense():
    response = client.post("/expenses", json={
        "amount": 50,
        "category": "ExpenseA",
        "desc": "Test coffee",
        "spent_on": "2026-09-01"
    })

    assert response.status_code == 200


def testGetExpenses():
    response = client.get("/expenses")

    assert response.status_code == 200


def testGetExpensesByCategory():
    response = client.get("/expenses?category=ExpenseA")

    assert response.status_code == 200


def testGetExpensesByDate():
    response = client.get(
        "/expenses?from=2026-09-01&to=2026-09-08"
    )

    assert response.status_code == 200


def testGetExpense():
    response = client.get("/expenses/1")

    assert response.status_code == 200


def testGetMissingExpense():
    response = client.get("/expenses/999")

    assert response.status_code == 404


def testGetSummary():
    response = client.get("/expenses/summary")

    assert response.status_code == 200


def testGetSummaryWithDate():
    response = client.get(
        "/expenses/summary?from=2026-09-01&to=2026-09-08"
    )

    assert response.status_code == 200


def testUpdateExpense():
    response = client.patch("/expenses/1", json={
        "amount": 100,
        "category": "ExpenseB",
        "desc": "Updated expense",
        "spent_on": "2026-09-01"
    })

    assert response.status_code == 200


def testDeleteExpense():
    response = client.delete("/expenses/6")

    assert response.status_code == 200
