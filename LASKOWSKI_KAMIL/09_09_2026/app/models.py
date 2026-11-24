from datetime import date, datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


class ExpenseCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    OTHER = "other"


PositiveAmount = Annotated[float, Field(gt=0, allow_inf_nan=False)]
DescriptionStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


def _validate_spent_on_not_in_future(value: date | None) -> date | None:
    if value is not None and value > date.today():
        raise ValueError("spent_on cannot be in the future")
    return value


class ExpenseCreate(BaseModel):
    amount: PositiveAmount
    category: ExpenseCategory
    description: DescriptionStr
    spent_on: date

    @field_validator("spent_on")
    @classmethod
    def check_spent_on(cls, value: date) -> date:
        validated = _validate_spent_on_not_in_future(value)
        assert validated is not None
        return validated


class ExpenseUpdate(BaseModel):
    amount: PositiveAmount | None = None
    category: ExpenseCategory | None = None
    description: DescriptionStr | None = None
    spent_on: date | None = None

    @field_validator("spent_on")
    @classmethod
    def check_spent_on(cls, value: date | None) -> date | None:
        return _validate_spent_on_not_in_future(value)

    @model_validator(mode="after")
    def reject_explicit_nulls(self) -> "ExpenseUpdate":
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"'{field_name}' cannot be null")
        return self


class ExpensePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: float
    category: ExpenseCategory
    description: str
    spent_on: date
    created_at: datetime
    updated_at: datetime


class ExpenseSummary(BaseModel):
    total: float
    total_per_category: dict[ExpenseCategory, float]
    average_per_day: float
    count: int
    days: int
    from_date: date | None
    to_date: date | None