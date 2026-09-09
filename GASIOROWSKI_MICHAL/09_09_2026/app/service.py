from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from .models import (
    ExpenseCategory,
    ExpenseCreate,
    ExpenseSummary,
    ExpenseUpdate,
)
from .repository import ExpenseRecord, InMemoryExpenseRepository


class ExpenseNotFoundError(Exception):
    pass


class InvalidDateRangeError(Exception):
    pass


class ExpenseService:
    def __init__(self, repository: InMemoryExpenseRepository) -> None:
        self.repository = repository

    def create(self, payload: ExpenseCreate) -> ExpenseRecord:
        return self.repository.create(**payload.model_dump())

    def list(
        self,
        *,
        category: ExpenseCategory | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExpenseRecord]:
        self._validate_range(from_date, to_date)

        return self.repository.list(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )

    def get(self, expense_id: int) -> ExpenseRecord:
        expense = self.repository.get(expense_id)

        if expense is None:
            raise ExpenseNotFoundError

        return expense

    def update(
        self,
        expense_id: int,
        payload: ExpenseUpdate,
    ) -> ExpenseRecord:
        self.get(expense_id)

        updated = self.repository.update(
            expense_id,
            **payload.model_dump(exclude_unset=True),
        )

        if updated is None:
            raise ExpenseNotFoundError

        return updated

    def delete(self, expense_id: int) -> None:
        if not self.repository.delete(expense_id):
            raise ExpenseNotFoundError

    def summary(
        self,
        *,
        category: ExpenseCategory | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> ExpenseSummary:
        expenses = self.list(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )

        total = sum(
            (expense.amount for expense in expenses),
            Decimal("0"),
        )

        totals_by_category = {
            expense_category: sum(
                (
                    expense.amount
                    for expense in expenses
                    if expense.category == expense_category
                ),
                Decimal("0"),
            )
            for expense_category in ExpenseCategory
        }

        if from_date is not None and to_date is not None:
            first_day = from_date
            last_day = to_date
        elif expenses:
            first_day = min(expense.spent_on for expense in expenses)
            last_day = max(expense.spent_on for expense in expenses)
        else:
            first_day = last_day = None

        if first_day is None or last_day is None:
            average_per_day = Decimal("0")
        else:
            days = (last_day - first_day).days + 1
            average_per_day = (
                total / Decimal(days)
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return ExpenseSummary(
            total=total,
            total_per_category=totals_by_category,
            average_per_day=average_per_day,
        )

    @staticmethod
    def _validate_range(
        from_date: date | None,
        to_date: date | None,
    ) -> None:
        if from_date is not None and to_date is not None:
            if from_date > to_date:
                raise InvalidDateRangeError(
                    "from must be less than or equal to to"
                )
