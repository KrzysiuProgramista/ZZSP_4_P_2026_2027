from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from .models import Category, ExpenseCreate, ExpensePublic, ExpenseUpdate
from .service import ExpenseNotFoundError, ExpenseService

app = FastAPI(title="Expenses Service")

# A single, shared, in-memory service instance for the whole app.
service = ExpenseService()


@app.post("/expenses", response_model=ExpensePublic, status_code=201)
def create_expense(data: ExpenseCreate) -> ExpensePublic:
    expense = service.create(data)
    return expense


@app.get("/expenses", response_model=List[ExpensePublic])
def list_expenses(
    category: Optional[Category] = None,
    from_: Optional[date] = Query(None, alias="from"),
    to: Optional[date] = None,
) -> List[ExpensePublic]:
    return service.list(category=category, date_from=from_, date_to=to)

@app.get("/expenses/summary")
def get_summary(
    from_: Optional[date] = Query(None, alias="from"),
    to: Optional[date] = None,
) -> dict:
    return service.summary(date_from=from_, date_to=to)


@app.get("/expenses/{expense_id}", response_model=ExpensePublic)
def get_expense(expense_id: int) -> ExpensePublic:
    try:
        return service.get(expense_id)
    except ExpenseNotFoundError:
        raise HTTPException(status_code=404, detail="Expense not found")


@app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
def update_expense(expense_id: int, data: ExpenseUpdate) -> ExpensePublic:
    try:
        return service.update(expense_id, data)
    except ExpenseNotFoundError:
        raise HTTPException(status_code=404, detail="Expense not found")


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int) -> None:
    try:
        service.delete(expense_id)
    except ExpenseNotFoundError:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None
