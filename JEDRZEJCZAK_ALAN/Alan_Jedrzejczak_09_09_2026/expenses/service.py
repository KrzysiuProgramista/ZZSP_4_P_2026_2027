from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional

from .models import Category, ExpenseCreate, ExpenseUpdate


@dataclass
class Expense:
    id: int
    amount: float
    category: Category
    description: str
    spent_on: date


class ExpenseNotFoundError(Exception):
    def __init__(self, expense_id: int):
        self.expense_id = expense_id
        super().__init__(f"Expense {expense_id} not found")


class ExpenseService:
    def __init__(self) -> None:
        self._expenses: Dict[int, Expense] = {}
        self._next_id: int = 1

    def create(self, data: ExpenseCreate) -> Expense:
        expense = Expense(
            id=self._next_id,
            amount=data.amount,
            category=data.category,
            description=data.description,
            spent_on=data.spent_on,
        )
        self._expenses[expense.id] = expense
        self._next_id += 1
        return expense

    def list(
        self,
        category: Optional[Category] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Expense]:
        result = list(self._expenses.values())

        if category is not None:
            result = [e for e in result if e.category == category]
        if date_from is not None:
            result = [e for e in result if e.spent_on >= date_from]
        if date_to is not None:
            result = [e for e in result if e.spent_on <= date_to]

        return sorted(result, key=lambda e: e.id)

    def get(self, expense_id: int) -> Expense:
        expense = self._expenses.get(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(expense_id)
        return expense

    def update(self, expense_id: int, data: ExpenseUpdate) -> Expense:
        expense = self.get(expense_id)
        changes = data.model_dump(exclude_unset=True)
        for field_name, value in changes.items():
            setattr(expense, field_name, value)
        return expense

    def delete(self, expense_id: int) -> None:
        expense = self.get(expense_id)
        del self._expenses[expense.id]

    def summary(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> dict:
        expenses = self.list(date_from=date_from, date_to=date_to)

        total = sum(e.amount for e in expenses)

        total_per_category: Dict[str, float] = {}
        for e in expenses:
            key = e.category.value
            total_per_category[key] = total_per_category.get(key, 0.0) + e.amount

        if date_from is not None and date_to is not None:
            days = (date_to - date_from).days + 1
        elif expenses:
            spent_dates = [e.spent_on for e in expenses]
            days = (max(spent_dates) - min(spent_dates)).days + 1
        else:
            days = 0

        average_per_day = (total / days) if days > 0 else 0.0

        return {
            "total": total,
            "total_per_category": total_per_category,
            "average_per_day": average_per_day,
        }
