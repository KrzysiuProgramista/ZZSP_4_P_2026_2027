from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status

from models import ExpenseCreate, ExpensePublic, ExpenseSummary, ExpenseUpdate
from service import ExpenseService

app = FastAPI(title="Expense Service API")
expense_service = ExpenseService()


@app.post("/expenses", response_model=ExpensePublic, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate):
    return expense_service.create_expense(payload)


@app.get("/expenses", response_model=list[ExpensePublic])
def list_expenses(
    category: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
):
    return expense_service.list_expenses(category=category, date_from=date_from, date_to=date_to)


@app.get("/expenses/summary", response_model=ExpenseSummary)
def get_expenses_summary(
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
):
    return expense_service.get_summary(date_from=date_from, date_to=date_to)


@app.get("/expenses/{id}", response_model=ExpensePublic)
def get_expense(id: int):
    expense = expense_service.get_expense(id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.patch("/expenses/{id}", response_model=ExpensePublic)
def update_expense(id: int, payload: ExpenseUpdate):
    updated = expense_service.update_expense(id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated


@app.delete("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(id: int):
    success = expense_service.delete_expense(id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None