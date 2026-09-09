from datetime import date

from .models import (
    ExpenseCategory,
    ExpenseCreate,
    ExpensePublic,
    ExpenseSummary,
    ExpenseUpdate,
)


class ExpenseNotFoundError(Exception):
    pass


class InvalidDateRangeError(Exception):
    pass


class ExpenseService:
    def __init__(self) -> None:
        self._expenses: dict[int, ExpensePublic] = {}
        self._next_id = 1

    def create(self, data: ExpenseCreate) -> ExpensePublic:
        expense = ExpensePublic(id=self._next_id, **data.model_dump())
        self._expenses[self._next_id] = expense
        self._next_id += 1
        return expense

    def list(
        self,
        category: ExpenseCategory | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExpensePublic]:
        self._validate_range(from_date, to_date)

        result = list(self._expenses.values())

        if category is not None:
            result = [expense for expense in result if expense.category == category]

        if from_date is not None:
            result = [expense for expense in result if expense.spent_on >= from_date]

        if to_date is not None:
            result = [expense for expense in result if expense.spent_on <= to_date]

        return sorted(result, key=lambda expense: expense.id)

    def get(self, expense_id: int) -> ExpensePublic:
        expense = self._expenses.get(expense_id)
        if expense is None:
            raise ExpenseNotFoundError
        return expense

    def update(self, expense_id: int, data: ExpenseUpdate) -> ExpensePublic:
        current = self.get(expense_id)
        changes = data.model_dump(exclude_unset=True)

        updated = current.model_copy(update=changes)
        self._expenses[expense_id] = updated
        return updated

    def delete(self, expense_id: int) -> None:
        self.get(expense_id)
        del self._expenses[expense_id]

    def summary(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> ExpenseSummary:
        self._validate_range(from_date, to_date)

        expenses = self.list(from_date=from_date, to_date=to_date)
        total = sum(expense.amount for expense in expenses)

        totals = {
            category: sum(
                expense.amount
                for expense in expenses
                if expense.category == category
            )
            for category in ExpenseCategory
        }

        if from_date is not None and to_date is not None:
            number_of_days = (to_date - from_date).days + 1
        elif expenses:
            first_day = min(expense.spent_on for expense in expenses)
            last_day = max(expense.spent_on for expense in expenses)
            number_of_days = (last_day - first_day).days + 1
        else:
            number_of_days = 0

        average = total / number_of_days if number_of_days else 0.0

        return ExpenseSummary(
            total=round(total, 2),
            total_per_category={
                category: round(value, 2)
                for category, value in totals.items()
            },
            average_per_day=round(average, 2),
        )

    @staticmethod
    def _validate_range(
        from_date: date | None,
        to_date: date | None,
    ) -> None:
        if from_date is not None and to_date is not None and from_date > to_date:
            raise InvalidDateRangeError
