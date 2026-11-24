import ast
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def _payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "amount": 25.50,
        "category": "food",
        "description": "Lunch at bistro",
        "spent_on": date.today().isoformat(),
    }
    base.update(overrides)
    return base


def test_create_expense_success(client: TestClient) -> None:
    resp = client.post("/expenses", json=_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount"] == 25.50
    assert data["category"] == "food"
    assert data["description"] == "Lunch at bistro"
    assert data["spent_on"] == date.today().isoformat()
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.parametrize("bad_amount", [0, -10, -0.01])
def test_create_expense_rejects_non_positive_amount(
    client: TestClient, bad_amount: float
) -> None:
    resp = client.post("/expenses", json=_payload(amount=bad_amount))
    assert resp.status_code == 422


def test_create_expense_rejects_invalid_category(client: TestClient) -> None:
    resp = client.post("/expenses", json=_payload(category="luxury_yachts"))
    assert resp.status_code == 422


@pytest.mark.parametrize("bad_desc", ["", "   ", "x" * 201])
def test_create_expense_rejects_invalid_description(
    client: TestClient, bad_desc: str
) -> None:
    resp = client.post("/expenses", json=_payload(description=bad_desc))
    assert resp.status_code == 422


def test_create_expense_rejects_future_date(client: TestClient) -> None:
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    resp = client.post("/expenses", json=_payload(spent_on=tomorrow))
    assert resp.status_code == 422


def test_get_expense_by_id_and_not_found(client: TestClient) -> None:
    created = client.post("/expenses", json=_payload()).json()

    resp = client.get(f"/expenses/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]

    missing = client.get(f"/expenses/{uuid4()}")
    assert missing.status_code == 404


def test_list_expenses_with_category_and_date_filters(
    client: TestClient,
) -> None:
    d1 = (date.today() - timedelta(days=10)).isoformat()
    d2 = (date.today() - timedelta(days=5)).isoformat()
    d3 = date.today().isoformat()

    client.post("/expenses", json=_payload(category="food", spent_on=d1, amount=10))
    client.post(
        "/expenses", json=_payload(category="transport", spent_on=d2, amount=20)
    )
    client.post("/expenses", json=_payload(category="food", spent_on=d2, amount=30))
    client.post("/expenses", json=_payload(category="food", spent_on=d3, amount=40))

    all_items = client.get("/expenses").json()
    assert len(all_items) == 4

    food_items = client.get("/expenses", params={"category": "food"}).json()
    assert len(food_items) == 3
    assert all(item["category"] == "food" for item in food_items)

    filtered = client.get(
        "/expenses",
        params={"category": "food", "from": d2, "to": d2},
    ).json()
    assert len(filtered) == 1
    assert filtered[0]["amount"] == 30


def test_list_expenses_rejects_inverted_date_range(client: TestClient) -> None:
    today = date.today()
    resp = client.get(
        "/expenses",
        params={
            "from": today.isoformat(),
            "to": (today - timedelta(days=1)).isoformat(),
        },
    )
    assert resp.status_code == 422


def test_patch_expense_partial_update_and_validation(
    client: TestClient,
) -> None:
    created = client.post(
        "/expenses",
        json=_payload(amount=15.0, category="food", description="Coffee"),
    ).json()

    patch_resp = client.patch(
        f"/expenses/{created['id']}",
        json={"amount": 18.5, "description": "Coffee and pastry"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["amount"] == 18.5
    assert updated["description"] == "Coffee and pastry"
    assert updated["category"] == "food"

    null_resp = client.patch(
        f"/expenses/{created['id']}",
        json={"amount": None},
    )
    assert null_resp.status_code == 422

    missing_resp = client.patch(f"/expenses/{uuid4()}", json={"amount": 5})
    assert missing_resp.status_code == 404


def test_delete_expense_and_not_found(client: TestClient) -> None:
    created = client.post("/expenses", json=_payload()).json()

    del_resp = client.delete(f"/expenses/{created['id']}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/expenses/{created['id']}")
    assert get_resp.status_code == 404

    del_missing = client.delete(f"/expenses/{uuid4()}")
    assert del_missing.status_code == 404


def test_summary_over_requested_range(client: TestClient) -> None:
    today = date.today()
    d_start = today - timedelta(days=3)  # 4-day inclusive range: [today-3, today]
    d_mid = today - timedelta(days=1)
    d_before = today - timedelta(days=10)

    client.post(
        "/expenses",
        json=_payload(amount=100.0, category="housing", spent_on=d_before.isoformat()),
    )
    client.post(
        "/expenses",
        json=_payload(amount=10.1, category="food", spent_on=d_start.isoformat()),
    )
    client.post(
        "/expenses",
        json=_payload(amount=20.2, category="food", spent_on=d_mid.isoformat()),
    )
    client.post(
        "/expenses",
        json=_payload(amount=9.7, category="transport", spent_on=today.isoformat()),
    )

    resp = client.get(
        "/expenses/summary",
        params={"from": d_start.isoformat(), "to": today.isoformat()},
    )
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["total"] == 40.0
    assert summary["total_per_category"] == {"food": 30.3, "transport": 9.7}
    assert summary["days"] == 4
    assert summary["average_per_day"] == 10.0
    assert summary["count"] == 3


def test_summary_empty_and_implicit_range(client: TestClient) -> None:
    empty = client.get("/expenses/summary").json()
    assert empty["total"] == 0.0
    assert empty["total_per_category"] == {}
    assert empty["average_per_day"] == 0.0
    assert empty["days"] == 0
    assert empty["count"] == 0

    today = date.today()
    earlier = today - timedelta(days=4)
    client.post(
        "/expenses",
        json=_payload(amount=25.0, category="food", spent_on=earlier.isoformat()),
    )
    client.post(
        "/expenses",
        json=_payload(amount=25.0, category="health", spent_on=today.isoformat()),
    )

    summary = client.get("/expenses/summary").json()
    assert summary["total"] == 50.0
    assert summary["days"] == 5
    assert summary["average_per_day"] == 10.0


def test_service_layer_has_no_fastapi_imports() -> None:
    service_path = Path(__file__).resolve().parent.parent / "app" / "service.py"
    tree = ast.parse(service_path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module.split(".")[0])

    assert "fastapi" not in imported_modules
    assert "starlette" not in imported_modules