from datetime import date
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator


class ExpenseCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    OTHER = "other"


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: ExpenseCategory
    description: str = Field(..., min_length=1, max_length=200)
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def spent_on_cannot_be_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Spent on date can't be in the future")
        return value


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    spent_on: Optional[date] = None

    @field_validator("spent_on")
    @classmethod
    def spent_on_cannot_be_in_future(cls, value: Optional[date]):
        if value is not None and value > date.today():
            raise ValueError("Spent on date can't be in the future")
        return value


class ExpensePublic(BaseModel):
    id: int
    amount: float
    category: ExpenseCategory
    description: str
    spent_on: date


class ExpenseSummary(BaseModel):
    total: float
    total_per_category: dict[ExpenseCategory, float]
    average_per_day: float


class ExpenseNotFound(Exception):
    pass


class ExpenseService:
    def __init__(self):
        self._expenses: dict[int, ExpensePublic] = {}
        self._next_id = 1

    def create(self, data: ExpenseCreate) -> ExpensePublic:
        expense = ExpensePublic(
            id=self._next_id,
            **data.model_dump(),
        )
        self._expenses[self._next_id] = expense
        self._next_id += 1
        return expense

    def list(
        self,
        category: Optional[ExpenseCategory] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[ExpensePublic]:
        expenses = list(self._expenses.values())

        if category is not None:
            expenses = [e for e in expenses if e.category == category]

        if from_date is not None:
            expenses = [e for e in expenses if e.spent_on >= from_date]

        if to_date is not None:
            expenses = [e for e in expenses if e.spent_on <= to_date]

        return expenses

    def get(self, expense_id: int) -> ExpensePublic:
        expense = self._expenses.get(expense_id)
        if expense is None:
            raise ExpenseNotFound()
        return expense

    def update(self, expense_id: int, data: ExpenseUpdate) -> ExpensePublic:
        expense = self.get(expense_id)
        changes = data.model_dump(exclude_unset=True)
        updated = expense.model_copy(update=changes)
        self._expenses[expense_id] = updated
        return updated

    def delete(self, expense_id: int) -> None:
        if expense_id not in self._expenses:
            raise ExpenseNotFound()
        self._expenses.pop(expense_id)

    def summary(
        self,
        category: Optional[ExpenseCategory] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> ExpenseSummary:
        expenses = self.list(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )

        total = sum(expense.amount for expense in expenses)

        totals_by_category: dict[ExpenseCategory, float] = {}
        for expense in expenses:
            totals_by_category[expense.category] = (
                totals_by_category.get(expense.category, 0.0) + expense.amount
            )

        if from_date and to_date:
            days_count = max((to_date - from_date).days + 1, 1)
        elif expenses:
            min_date = min(e.spent_on for e in expenses)
            max_date = max(e.spent_on for e in expenses)
            days_count = max((max_date - min_date).days + 1, 1)
        else:
            days_count = 1

        average_per_day = total / days_count

        return ExpenseSummary(
            total=total,
            total_per_category=totals_by_category,
            average_per_day=round(average_per_day, 2),
        )


service = ExpenseService()
app = FastAPI(title="Expenses API")


@app.post("/expenses", response_model=ExpensePublic, status_code=status.HTTP_201_CREATED)
def create_expense(expense: ExpenseCreate):
    return service.create(expense)


@app.get("/expenses", response_model=list[ExpensePublic])
def list_expenses(
    category: Optional[ExpenseCategory] = None,
    from_: Optional[date] = Query(None, alias="from"),
    to: Optional[date] = None,
):
    return service.list(category=category, from_date=from_, to_date=to)


@app.get("/expenses/summary", response_model=ExpenseSummary)
def expense_summary(
    category: Optional[ExpenseCategory] = None,
    from_: Optional[date] = Query(None, alias="from"),
    to: Optional[date] = None,
):
    if from_ and to and from_ > to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The 'from' date cannot be after the 'to' date.",
        )
    return service.summary(category=category, from_date=from_, to_date=to)


@app.get("/expenses/{expense_id}", response_model=ExpensePublic)
def get_expense(expense_id: int):
    try:
        return service.get(expense_id)
    except ExpenseNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )


@app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
def update_expense(expense_id: int, expense: ExpenseUpdate):
    try:
        return service.update(expense_id, expense)
    except ExpenseNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int):
    try:
        service.delete(expense_id)
    except ExpenseNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )