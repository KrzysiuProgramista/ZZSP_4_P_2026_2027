from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Category(str, Enum):
    """Fixed set of allowed categories."""
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTH = "health"
    OTHER = "other"


def _check_not_in_future(value: Optional[date]) -> Optional[date]:
    if value is not None and value > date.today():
        raise ValueError("spent_on cannot be in the future")
    return value


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount spent, must be > 0")
    category: Category
    description: str = Field(..., min_length=1, max_length=200)
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def spent_on_not_in_future(cls, value: date) -> date:
        return _check_not_in_future(value)


class ExpenseUpdate(BaseModel):
    """All fields optional, so the client can send only what changes."""
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[Category] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    spent_on: Optional[date] = None

    @field_validator("spent_on")
    @classmethod
    def spent_on_not_in_future(cls, value: Optional[date]) -> Optional[date]:
        return _check_not_in_future(value)


class ExpensePublic(BaseModel):
    id: int
    amount: float
    category: Category
    description: str
    spent_on: date

    # lets us build this straight from our Expense dataclass
    model_config = ConfigDict(from_attributes=True)
