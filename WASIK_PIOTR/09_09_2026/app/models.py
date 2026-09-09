
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    OTHER = "other"


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    category: Category
    description: str = Field(min_length=1, max_length=200)
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def spent_on_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("spent_on cannot be in the future")
        return value


class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0)
    category: Optional[Category] = None
    description: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    spent_on: Optional[date] = None

    @field_validator("spent_on")
    @classmethod
    def spent_on_not_in_future(
        cls,
        value: Optional[date],
    ) -> Optional[date]:
        if value is not None and value > date.today():
            raise ValueError("spent_on cannot be in the future")
        return value


class ExpensePublic(BaseModel):
    id: int
    amount: Decimal
    category: Category
    description: str
    spent_on: date


class ExpenseSummary(BaseModel):
    total: Decimal
    total_per_category: dict[Category, Decimal]
    average_per_day: Decimal
