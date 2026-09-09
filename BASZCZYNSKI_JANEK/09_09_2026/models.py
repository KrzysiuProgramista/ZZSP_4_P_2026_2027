from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import date


class Category(Enum):
    ExpenseA = "ExpenseA"
    ExpenseB = "ExpenseB"


class Expense(BaseModel):
    amount: int = Field(..., gt=0)
    category: Category
    desc: str = Field(..., min_length=1, max_length=200)
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def dateNotInFuture(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date cannot be later than today")
        return value
