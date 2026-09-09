from datetime import date
from decimal import Decimal, ROUND_HALF_UP


class ExpenseNotFoundError(Exception):
    pass


class InvalidDateRangeError(Exception):
    pass


def money(value: Decimal) -> Decimal:
    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


class ExpenseService:
    def __init__(self, expenses: dict):
        self.expenses = expenses
        self.next_id = 1

    def create(
        self,
        amount: Decimal,
        category: str,
        description: str,
        spent_on: date,
    ):
        expense = {
            "id": self.next_id,
            "amount": money(amount),
            "category": category,
            "description": description,
            "spent_on": spent_on,
        }

        self.expenses[self.next_id] = expense
        self.next_id += 1

        return expense

    def get(self, expense_id: int):
        expense = self.expenses.get(expense_id)

        if expense is None:
            raise ExpenseNotFoundError()

        return expense

    def list(
        self,
        category=None,
        from_date=None,
        to_date=None,
    ):
        self._validate_range(from_date, to_date)

        result = list(self.expenses.values())

        if category is not None:
            result = [
                expense
                for expense in result
                if expense["category"] == category
            ]

        if from_date is not None:
            result = [
                expense
                for expense in result
                if expense["spent_on"] >= from_date
            ]

        if to_date is not None:
            result = [
                expense
                for expense in result
                if expense["spent_on"] <= to_date
            ]

        return sorted(
            result,
            key=lambda expense: expense["spent_on"],
        )

    def update(self, expense_id: int, changes: dict):
        expense = self.get(expense_id)

        if "amount" in changes:
            changes["amount"] = money(
                changes["amount"]
            )

        for key, value in changes.items():
            expense[key] = value

        return expense

    def delete(self, expense_id: int):
        if expense_id not in self.expenses:
            raise ExpenseNotFoundError()

        del self.expenses[expense_id]

    def summary(
        self,
        category=None,
        from_date=None,
        to_date=None,
    ):
        expenses = self.list(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )

        total = sum(
            (
                expense["amount"]
                for expense in expenses
            ),
            Decimal("0.00"),
        )

        total = money(total)

        category_totals = {}

        for expense in expenses:
            expense_category = expense["category"]

            category_totals[expense_category] = money(
                category_totals.get(
                    expense_category,
                    Decimal("0.00"),
                )
                + expense["amount"]
            )

        if from_date is not None and to_date is not None:
            days = (to_date - from_date).days + 1

        elif expenses:
            first = min(
                expense["spent_on"]
                for expense in expenses
            )
            last = max(
                expense["spent_on"]
                for expense in expenses
            )

            days = (last - first).days + 1

        else:
            days = 0

        if days > 0:
            average = money(
                total / Decimal(days)
            )
        else:
            average = Decimal("0.00")

        return {
            "total": total,
            "total_per_category": [
                {
                    "category": category,
                    "total": amount,
                }
                for category, amount
                in sorted(category_totals.items())
            ],
            "average_per_day": average,
        }

    @staticmethod
    def _validate_range(from_date, to_date):
        if (
            from_date is not None
            and to_date is not None
            and from_date > to_date
        ):
            raise InvalidDateRangeError(
                "from must be before or equal to to"
            )