from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ExpenseCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    BILLS = "bills"
    OTHER = "other"


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: ExpenseCategory
    description: str = Field(min_length=1, max_length=200)
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def spent_on_cannot_be_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("spent_on cannot be in the future")
        return value


class ExpenseUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    category: ExpenseCategory | None = None
    description: str | None = Field(default=None, min_length=1, max_length=200)
    spent_on: date | None = None

    @field_validator("spent_on")
    @classmethod
    def spent_on_cannot_be_future(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("spent_on cannot be in the future")
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
