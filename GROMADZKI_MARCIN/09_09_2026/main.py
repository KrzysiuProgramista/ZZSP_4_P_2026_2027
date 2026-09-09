from datetime import date
from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from services import ExpenseService

app = FastAPI()
service = ExpenseService()

class CategoryEnum(str, Enum):
    food = "Food"
    transport = "Transport"
    bills = "Bills"
    tech = "Tech"
    misc = "Misc"

class Expense(BaseModel):
    amount: float = Field(gt=0)
    category: CategoryEnum
    description: str = Field(min_length=1, max_length=200)
    spent_on: date

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[CategoryEnum] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    spent_on: Optional[date] = None

@app.post("/expenses", status_code=201)
def create_expense(expense: Expense):
    try:
        return service.create_expense(
            amount=expense.amount,
            category=expense.category.value,
            description=expense.description,
            spent_on=expense.spent_on,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/expenses")
def get_expenses(
    category: Optional[CategoryEnum] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = None,
):
    cat_str = category.value if category else None
    return service.get_expenses(category=cat_str, from_date=from_date, to_date=to_date)

@app.get("/expenses/summary")
def get_summary(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = None,
):
    return service.get_summary(from_date=from_date, to_date=to_date)

@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int):
    try:
        return service.get_expense(expense_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Not found")

@app.patch("/expenses/{expense_id}")
def update_expense(expense_id: int, update_data: ExpenseUpdate):
    try:
        data = update_data.model_dump(exclude_unset=True)
        if "category" in data and data["category"]:
            data["category"] = data["category"].value
        return service.update_expense(expense_id, **data)
    except KeyError:
        raise HTTPException(status_code=404, detail="Not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    try:
        service.delete_expense(expense_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Not found")