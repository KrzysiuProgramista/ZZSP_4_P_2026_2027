
from .models import ExpensePublic


class ExpenseStorage:
    def __init__(self):
        self._expenses: dict[int, ExpensePublic] = {}
        self._next_id = 1

    def create(
        self,
        amount,
        category,
        description,
        spent_on,
    ) -> ExpensePublic:
        expense = ExpensePublic(
            id=self._next_id,
            amount=amount,
            category=category,
            description=description,
            spent_on=spent_on,
        )

        self._expenses[expense.id] = expense
        self._next_id += 1

        return expense

    def get(self, expense_id: int) -> ExpensePublic | None:
        return self._expenses.get(expense_id)

    def list(self) -> list[ExpensePublic]:
        return list(self._expenses.values())

    def update(self, expense: ExpensePublic) -> ExpensePublic:
        self._expenses[expense.id] = expense
        return expense

    def delete(self, expense_id: int) -> bool:
        return self._expenses.pop(expense_id, None) is not None

    def clear(self):
        self._expenses.clear()
        self._next_id = 1

