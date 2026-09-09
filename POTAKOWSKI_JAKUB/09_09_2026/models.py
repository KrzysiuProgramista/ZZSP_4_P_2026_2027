from datetime import date
from decimal import Decimal
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


CATEGORIES = {"food", "transport", "housing", "health", "entertainment", "other"}


class ExpenseCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    category: str
    description: str = Field(..., min_length=1, max_length=200)
    spent_on: date

    @validator("category")
    def category_must_be_supported(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError("unsupported category")
        return value

    @validator("spent_on")
    def spent_on_cannot_be_in_the_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("spent_on cannot be in the future")
        return value


class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    spent_on: Optional[date] = None

    @validator("category")
    def category_must_be_supported(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in CATEGORIES:
            raise ValueError("unsupported category")
        return value

    @validator("spent_on")
    def spent_on_cannot_be_in_the_future(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value > date.today():
            raise ValueError("spent_on cannot be in the future")
        return value


class ExpensePublic(ExpenseCreate):
    id: UUID


class ExpenseSummary(BaseModel):
    total: Decimal
    total_per_category: Dict[str, Decimal]
    average_per_day: Decimal