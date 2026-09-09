from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, status

from models import CATEGORIES, ExpenseCreate, ExpensePublic, ExpenseSummary, ExpenseUpdate
from service import ExpenseService


app = FastAPI()
service = ExpenseService()


def validate_range(from_date: Optional[date], to_date: Optional[date]) -> None:
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="from must not be after to")


@app.post("/expenses", response_model=ExpensePublic, status_code=status.HTTP_201_CREATED)
def create_expense(expense: ExpenseCreate) -> ExpensePublic:
    return service.create(expense)


@app.get("/expenses", response_model=List[ExpensePublic])
def list_expenses(
    category: Optional[str] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
) -> List[ExpensePublic]:
    validate_range(from_date, to_date)
    if category is not None and category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="unsupported category")
    return service.list(category, from_date, to_date)


@app.get("/expenses/summary", response_model=ExpenseSummary)
def get_summary(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
) -> ExpenseSummary:
    validate_range(from_date, to_date)
    return service.summary(from_date, to_date)


@app.get("/expenses/{expense_id}", response_model=ExpensePublic)
def get_expense(expense_id: UUID) -> ExpensePublic:
    expense = service.get(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="expense not found")
    return expense


@app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
def update_expense(expense_id: UUID, changes: ExpenseUpdate) -> ExpensePublic:
    expense = service.update(expense_id, changes)
    if expense is None:
        raise HTTPException(status_code=404, detail="expense not found")
    return expense


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: UUID) -> None:
    if not service.delete(expense_id):
        raise HTTPException(status_code=404, detail="expense not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
