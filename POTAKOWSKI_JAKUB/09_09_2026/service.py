from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from models import CATEGORIES, ExpenseCreate, ExpensePublic, ExpenseSummary, ExpenseUpdate


class ExpenseService:
    """In-memory expense operations without FastAPI dependencies."""

    def __init__(self) -> None:
        self._expenses: Dict[UUID, ExpensePublic] = {}

    def create(self, expense: ExpenseCreate) -> ExpensePublic:
        saved = ExpensePublic(id=uuid4(), **expense.dict())
        self._expenses[saved.id] = saved
        return saved

    def list(self, category: Optional[str], from_date: Optional[date], to_date: Optional[date]) -> List[ExpensePublic]:
        return [
            expense
            for expense in self._expenses.values()
            if (category is None or expense.category == category)
            and (from_date is None or expense.spent_on >= from_date)
            and (to_date is None or expense.spent_on <= to_date)
        ]

    def get(self, expense_id: UUID) -> Optional[ExpensePublic]:
        return self._expenses.get(expense_id)

    def update(self, expense_id: UUID, changes: ExpenseUpdate) -> Optional[ExpensePublic]:
        current = self.get(expense_id)
        if current is None:
            return None
        updated = current.copy(update=changes.dict(exclude_unset=True))
        self._expenses[expense_id] = updated
        return updated

    def delete(self, expense_id: UUID) -> bool:
        return self._expenses.pop(expense_id, None) is not None

    def summary(self, from_date: Optional[date], to_date: Optional[date]) -> ExpenseSummary:
        expenses = self.list(None, from_date, to_date)
        total = sum((expense.amount for expense in expenses), Decimal("0"))
        totals = {category: Decimal("0") for category in sorted(CATEGORIES)}
        for expense in expenses:
            totals[expense.category] += expense.amount

        start = from_date or min((expense.spent_on for expense in expenses), default=date.today())
        end = to_date or max((expense.spent_on for expense in expenses), default=start)
        days = (end - start).days + 1
        return ExpenseSummary(total=total, total_per_category=totals, average_per_day=total / days)