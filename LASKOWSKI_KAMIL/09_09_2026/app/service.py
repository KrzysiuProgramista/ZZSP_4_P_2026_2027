from datetime import date, datetime, timezone
from decimal import Decimal
from threading import Lock
from typing import Protocol
from uuid import UUID, uuid4

from app.models import (
    ExpenseCategory,
    ExpenseCreate,
    ExpensePublic,
    ExpenseSummary,
    ExpenseUpdate,
)


class ExpenseNotFoundError(Exception):
    def __init__(self, expense_id: UUID) -> None:
        self.expense_id = expense_id
        super().__init__(f"Expense {expense_id} not found")


class InvalidDateRangeError(Exception):
    def __init__(self, from_date: date, to_date: date) -> None:
        self.from_date = from_date
        self.to_date = to_date
        super().__init__(f"'from' ({from_date}) cannot be after 'to' ({to_date})")


class ExpenseRepository(Protocol):
    def add(self, expense: ExpensePublic) -> ExpensePublic: ...

    def get(self, expense_id: UUID) -> ExpensePublic | None: ...

    def list(
        self,
        *,
        category: ExpenseCategory | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExpensePublic]: ...

    def update(self, expense: ExpensePublic) -> ExpensePublic: ...

    def delete(self, expense_id: UUID) -> bool: ...


class InMemoryExpenseRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, ExpensePublic] = {}
        self._lock = Lock()

    def add(self, expense: ExpensePublic) -> ExpensePublic:
        with self._lock:
            self._items[expense.id] = expense
            return expense

    def get(self, expense_id: UUID) -> ExpensePublic | None:
        with self._lock:
            return self._items.get(expense_id)

    def list(
        self,
        *,
        category: ExpenseCategory | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExpensePublic]:
        with self._lock:
            results: list[ExpensePublic] = []
            for item in self._items.values():
                if category is not None and item.category != category:
                    continue
                if from_date is not None and item.spent_on < from_date:
                    continue
                if to_date is not None and item.spent_on > to_date:
                    continue
                results.append(item)
            results.sort(key=lambda e: (e.spent_on, e.created_at), reverse=True)
            return results

    def update(self, expense: ExpensePublic) -> ExpensePublic:
        with self._lock:
            if expense.id not in self._items:
                raise ExpenseNotFoundError(expense.id)
            self._items[expense.id] = expense
            return expense

    def delete(self, expense_id: UUID) -> bool:
        with self._lock:
            return self._items.pop(expense_id, None) is not None


class ExpenseService:
    def __init__(self, repository: ExpenseRepository | None = None) -> None:
        self._repo: ExpenseRepository = repository or InMemoryExpenseRepository()

    def create_expense(self, payload: ExpenseCreate) -> ExpensePublic:
        now = datetime.now(timezone.utc)
        expense = ExpensePublic(
            id=uuid4(),
            amount=payload.amount,
            category=payload.category,
            description=payload.description,
            spent_on=payload.spent_on,
            created_at=now,
            updated_at=now,
        )
        return self._repo.add(expense)

    def get_expense(self, expense_id: UUID) -> ExpensePublic:
        expense = self._repo.get(expense_id)
        if expense is None:
            raise ExpenseNotFoundError(expense_id)
        return expense

    def list_expenses(
        self,
        *,
        category: ExpenseCategory | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[ExpensePublic]:
        if from_date is not None and to_date is not None and from_date > to_date:
            raise InvalidDateRangeError(from_date, to_date)
        return self._repo.list(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )

    def update_expense(
        self, expense_id: UUID, payload: ExpenseUpdate
    ) -> ExpensePublic:
        existing = self.get_expense(expense_id)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return existing
        updates["updated_at"] = datetime.now(timezone.utc)
        updated = existing.model_copy(update=updates)
        return self._repo.update(updated)

    def delete_expense(self, expense_id: UUID) -> None:
        deleted = self._repo.delete(expense_id)
        if not deleted:
            raise ExpenseNotFoundError(expense_id)

    def get_summary(
        self,
        *,
        category: ExpenseCategory | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> ExpenseSummary:
        expenses = self.list_expenses(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )

        total_dec = Decimal("0")
        per_cat_dec: dict[ExpenseCategory, Decimal] = {}
        for exp in expenses:
            amt = Decimal(str(exp.amount))
            total_dec += amt
            per_cat_dec[exp.category] = per_cat_dec.get(exp.category, Decimal("0")) + amt

        effective_from, effective_to, days = self._resolve_range(
            expenses, from_date, to_date
        )
        average_per_day = (
            float(total_dec / Decimal(days)) if days > 0 else 0.0
        )

        return ExpenseSummary(
            total=float(total_dec),
            total_per_category={k: float(v) for k, v in per_cat_dec.items()},
            average_per_day=average_per_day,
            count=len(expenses),
            days=days,
            from_date=effective_from,
            to_date=effective_to,
        )

    @staticmethod
    def _resolve_range(
        expenses: list[ExpensePublic],
        from_date: date | None,
        to_date: date | None,
    ) -> tuple[date | None, date | None, int]:
        if from_date is not None and to_date is not None:
            return from_date, to_date, (to_date - from_date).days + 1

        if from_date is not None:
            today = date.today()
            if from_date > today:
                return from_date, None, 0
            return from_date, today, (today - from_date).days + 1

        if not expenses:
            return None, to_date, 0

        min_spent = min(e.spent_on for e in expenses)
        if to_date is not None:
            return min_spent, to_date, (to_date - min_spent).days + 1

        max_spent = max(e.spent_on for e in expenses)
        return min_spent, max_spent, (max_spent - min_spent).days + 1