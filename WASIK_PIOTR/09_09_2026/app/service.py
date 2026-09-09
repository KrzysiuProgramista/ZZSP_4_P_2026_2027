
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from .models import (
    Category,
    ExpenseCreate,
    ExpensePublic,
    ExpenseSummary,
    ExpenseUpdate,
)
from .storage import ExpenseStorage


class ExpenseNotFoundError(Exception):
    pass


class ExpenseService:
    def __init__(self, storage: ExpenseStorage):
        self.storage = storage

    def create(self, data: ExpenseCreate) -> ExpensePublic:
        return self.storage.create(
            amount=data.amount,
            category=data.category,
            description=data.description,
            spent_on=data.spent_on,
        )

    def list(
        self,
        category: Category | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExpensePublic]:
        expenses = self.storage.list()

        if category is not None:
            expenses = [
                expense
                for expense in expenses
                if expense.category == category
            ]

        if from_date is not None:
            expenses = [
                expense
                for expense in expenses
                if expense.spent_on >= from_date
            ]

        if to_date is not None:
            expenses = [
                expense
                for expense in expenses
                if expense.spent_on <= to_date
            ]

        return sorted(
            expenses,
            key=lambda expense: expense.spent_on,
        )

    def get(self, expense_id: int) -> ExpensePublic:
        expense = self.storage.get(expense_id)

        if expense is None:
            raise ExpenseNotFoundError()

        return expense

    def update(
        self,
        expense_id: int,
        data: ExpenseUpdate,
    ) -> ExpensePublic:
        expense = self.get(expense_id)

        changes = data.model_dump(exclude_unset=True)
        updated = expense.model_copy(update=changes)

        updated = ExpensePublic.model_validate(updated)

        return self.storage.update(updated)

    def delete(self, expense_id: int) -> None:
        if not self.storage.delete(expense_id):
            raise ExpenseNotFoundError()

    def summary(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> ExpenseSummary:
        expenses = self.list(
            from_date=from_date,
            to_date=to_date,
        )

        total = sum(
            (expense.amount for expense in expenses),
            Decimal("0"),
        )

        total_per_category = {
            category: sum(
                (
                    expense.amount
                    for expense in expenses
                    if expense.category == category
                ),
                Decimal("0"),
            )
            for category in Category
        }

        if from_date is not None and to_date is not None:
            days = (to_date - from_date).days + 1
        elif expenses:
            first_day = min(
                expense.spent_on
                for expense in expenses
            )
            last_day = max(
                expense.spent_on
                for expense in expenses
            )
            days = (last_day - first_day).days + 1
        else:
            days = 0

        if days > 0:
            average_per_day = total / Decimal(days)
        else:
            average_per_day = Decimal("0")

        average_per_day = average_per_day.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        return ExpenseSummary(
            total=total,
            total_per_category=total_per_category,
            average_per_day=average_per_day,
        )

