from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CategoryEnum(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: CategoryEnum
    description: str = Field(..., min_length=1, max_length=200)
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def validate_spent_on(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("spent_on date cannot be in the future")
        return v


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[CategoryEnum] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    spent_on: Optional[date] = None

    @field_validator("spent_on")
    @classmethod
    def validate_spent_on(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("spent_on date cannot be in the future")
        return v


class ExpensePublic(BaseModel):
    id: int
    amount: float
    category: CategoryEnum
    description: str
    spent_on: date


class SummaryResponse(BaseModel):
    total: float
    total_per_category: dict[str, float]
    average_per_day: float