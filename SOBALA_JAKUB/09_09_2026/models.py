from datetime import date
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

CategoryType = Literal["Food", "Transport", "Utilities", "Entertainment", "Other"]

class ExpenseCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount must be greater than 0")
    category: CategoryType
    description: str = Field(..., min_length=1, max_length=200, description="Description between 1-200 characters")
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def validate_spent_on(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("spent_on date cannot be in the future")
        return value

class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    category: Optional[CategoryType] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    spent_on: Optional[date] = None

    @field_validator("spent_on")
    @classmethod
    def validate_spent_on(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value > date.today():
            raise ValueError("spent_on date cannot be in the future")
        return value

class ExpensePublic(BaseModel):
    id: int
    amount: Decimal
    category: CategoryType
    description: str
    spent_on: date

    class Config:
        from_attributes = True

class CategorySummary(BaseModel):
    category: CategoryType
    total: Decimal

class ExpenseSummary(BaseModel):
    total: Decimal
    per_category: list[CategorySummary]
    average_per_day: Decimal
    range_start: Optional[date] = None
    range_end: Optional[date] = None