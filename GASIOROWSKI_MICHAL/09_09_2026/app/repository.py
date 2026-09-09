from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .models import ExpenseCategory


@dataclass
class ExpenseRecord:
    id: int
    amount: Decimal
    category: ExpenseCategory
    description: str
    spent_on: date


class InMemoryExpenseRepository:
    def __init__(self) -> None:
        self._expenses: dict[int, ExpenseRecord] = {}
        self._next_id = 1

    def create(
        self,
        *,
        amount: Decimal,
        category: ExpenseCategory,
        description: str,
        spent_on: date,
    ) -> ExpenseRecord:
        expense = ExpenseRecord(
            id=self._next_id,
            amount=amount,
            category=category,
            description=description,
            spent_on=spent_on,
        )
        self._expenses[expense.id] = expense
        self._next_id += 1
        return expense

    def get(self, expense_id: int) -> ExpenseRecord | None:
        return self._expenses.get(expense_id)

    def list(
        self,
        *,
        category: ExpenseCategory | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExpenseRecord]:
        records = list(self._expenses.values())

        if category is not None:
            records = [item for item in records if item.category == category]

        if from_date is not None:
            records = [item for item in records if item.spent_on >= from_date]

        if to_date is not None:
            records = [item for item in records if item.spent_on <= to_date]

        return sorted(records, key=lambda item: (item.spent_on, item.id))

    def update(
        self,
        expense_id: int,
        *,
        amount: Decimal | None = None,
        category: ExpenseCategory | None = None,
        description: str | None = None,
        spent_on: date | None = None,
    ) -> ExpenseRecord | None:
        expense = self._expenses.get(expense_id)

        if expense is None:
            return None

        if amount is not None:
            expense.amount = amount
        if category is not None:
            expense.category = category
        if description is not None:
            expense.description = description
        if spent_on is not None:
            expense.spent_on = spent_on

        return expense

    def delete(self, expense_id: int) -> bool:
        return self._expenses.pop(expense_id, None) is not None

    def clear(self) -> None:
        self._expenses.clear()
        self._next_id = 1
