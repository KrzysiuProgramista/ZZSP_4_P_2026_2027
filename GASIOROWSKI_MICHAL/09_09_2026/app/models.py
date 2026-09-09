from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpenseCategory(str, Enum):
    food = "food"
    transport = "transport"
    housing = "housing"
    utilities = "utilities"
    health = "health"
    entertainment = "entertainment"
    other = "other"


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    category: ExpenseCategory
    description: str = Field(min_length=1, max_length=200)
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def spent_on_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("spent_on cannot be in the future")
        return value


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    category: ExpenseCategory | None = None
    description: str | None = Field(default=None, min_length=1, max_length=200)
    spent_on: date | None = None

    @field_validator("spent_on")
    @classmethod
    def spent_on_not_in_future(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("spent_on cannot be in the future")
        return value


class ExpensePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category: ExpenseCategory
    description: str
    spent_on: date


class ExpenseSummary(BaseModel):
    total: Decimal
    total_per_category: dict[ExpenseCategory, Decimal]
    average_per_day: Decimal
