from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status

from models import (
    CategoryEnum,
    ExpenseCreate,
    ExpensePublic,
    ExpenseUpdate,
    SummaryResponse,
)
from service import ExpenseService

app = FastAPI(title="Expenses API")
service = ExpenseService()


@app.post("/expenses", response_model=ExpensePublic, status_code=status.HTTP_201_CREATED)
def create_expense(expense: ExpenseCreate):
    return service.create_expense(expense)


@app.get("/expenses/summary", response_model=SummaryResponse)
def get_summary(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    return service.get_summary(from_date=from_date, to_date=to_date)


@app.get("/expenses", response_model=list[ExpensePublic])
def get_expenses(
    category: Optional[CategoryEnum] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    return service.get_expenses(category=category, from_date=from_date, to_date=to_date)


@app.get("/expenses/{expense_id}", response_model=ExpensePublic)
def get_expense(expense_id: int):
    expense = service.get_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
def update_expense(expense_id: int, expense: ExpenseUpdate):
    updated = service.update_expense(expense_id, expense)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int):
    success = service.delete_expense(expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")