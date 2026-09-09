from datetime import date
from enum import Enum
from statistics import mean

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field


class Category(str, Enum):
    food = "food"
    transport = "transport"
    housing = "housing"
    entertainment = "entertainment"
    health = "health"
    other = "other"


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: Category
    description: str = Field(min_length=1, max_length=200)
    spent_on: date


class ExpenseUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    category: Category | None = None
    description: str | None = Field(default=None, min_length=1, max_length=200)
    spent_on: date | None = None


class ExpensePublic(ExpenseCreate):
    id: int


class ExpenseService:
    def __init__(self):
        self.expenses: dict[int, ExpensePublic] = {}
        self.next_id = 1

    def create(self, data: ExpenseCreate) -> ExpensePublic:
        if data.spent_on > date.today():
            raise ValueError("spent_on cannot be in the future")

        expense = ExpensePublic(id=self.next_id, **data.model_dump())
        self.expenses[self.next_id] = expense
        self.next_id += 1
        return expense

    def list(
        self,
        category: Category | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExpensePublic]:
        expenses = list(self.expenses.values())

        if category:
            expenses = [e for e in expenses if e.category == category]
        if from_date:
            expenses = [e for e in expenses if e.spent_on >= from_date]
        if to_date:
            expenses = [e for e in expenses if e.spent_on <= to_date]

        return expenses

    def get(self, expense_id: int) -> ExpensePublic | None:
        return self.expenses.get(expense_id)

    def update(self, expense_id: int, data: ExpenseUpdate) -> ExpensePublic | None:
        expense = self.get(expense_id)

        if not expense:
            return None

        values = data.model_dump(exclude_unset=True)

        if "spent_on" in values and values["spent_on"] > date.today():
            raise ValueError("spent_on cannot be in the future")

        updated = expense.model_copy(update=values)
        self.expenses[expense_id] = updated

        return updated

    def delete(self, expense_id: int) -> bool:
        return self.expenses.pop(expense_id, None) is not None

    def summary(
        self,
        category: Category | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ):
        expenses = self.list(category, from_date, to_date)

        total = sum(e.amount for e in expenses)

        total_per_category = {}
        for expense in expenses:
            key = expense.category.value
            total_per_category[key] = total_per_category.get(key, 0) + expense.amount

        if from_date and to_date:
            days = (to_date - from_date).days + 1
        elif expenses:
            days = (
                max(e.spent_on for e in expenses)
                - min(e.spent_on for e in expenses)
            ).days + 1
        else:
            days = 0

        return {
            "total": total,
            "total_per_category": total_per_category,
            "average_per_day": total / days if days else 0,
        }


app = FastAPI()
service = ExpenseService()


@app.post("/expenses", response_model=ExpensePublic, status_code=201)
def create_expense(expense: ExpenseCreate):
    try:
        return service.create(expense)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/expenses", response_model=list[ExpensePublic])
def list_expenses(
    category: Category | None = None,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(400, "from cannot be after to")

    return service.list(category, from_date, to_date)


@app.get("/expenses/summary")
def expense_summary(
    category: Category | None = None,
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(400, "from cannot be after to")

    return service.summary(category, from_date, to_date)


@app.get("/expenses/{expense_id}", response_model=ExpensePublic)
def get_expense(expense_id: int):
    expense = service.get(expense_id)

    if not expense:
        raise HTTPException(404, "Expense not found")

    return expense


@app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
def update_expense(expense_id: int, data: ExpenseUpdate):
    try:
        expense = service.update(expense_id, data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not expense:
        raise HTTPException(404, "Expense not found")

    return expense


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    if not service.delete(expense_id):
        raise HTTPException(404, "Expense not found")

    return Response(status_code=204)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
