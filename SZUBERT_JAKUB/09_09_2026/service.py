from datetime import date
from typing import Optional
from models import ExpenseCreate, ExpensePublic, ExpenseUpdate, CategoryEnum


class ExpenseService:
    def __init__(self):
        self._storage: dict[int, dict] = {}
        self._counter: int = 1

    def create_expense(self, data: ExpenseCreate) -> ExpensePublic:
        expense_id = self._counter
        self._counter += 1
        record = {"id": expense_id, **data.model_dump()}
        self._storage[expense_id] = record
        return ExpensePublic(**record)

    def get_expenses(
        self,
        category: Optional[CategoryEnum] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[ExpensePublic]:
        results = list(self._storage.values())

        if category is not None:
            results = [e for e in results if e["category"] == category]
        if from_date is not None:
            results = [e for e in results if e["spent_on"] >= from_date]
        if to_date is not None:
            results = [e for e in results if e["spent_on"] <= to_date]

        return [ExpensePublic(**e) for e in results]

    def get_expense(self, expense_id: int) -> Optional[ExpensePublic]:
        record = self._storage.get(expense_id)
        if not record:
            return None
        return ExpensePublic(**record)

    def update_expense(self, expense_id: int, data: ExpenseUpdate) -> Optional[ExpensePublic]:
        record = self._storage.get(expense_id)
        if not record:
            return None

        update_data = data.model_dump(exclude_unset=True)
        record.update(update_data)
        return ExpensePublic(**record)

    def delete_expense(self, expense_id: int) -> bool:
        if expense_id in self._storage:
            del self._storage[expense_id]
            return True
        return False

    def get_summary(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> dict:
        filtered = list(self._storage.values())
        if from_date is not None:
            filtered = [e for e in filtered if e["spent_on"] >= from_date]
        if to_date is not None:
            filtered = [e for e in filtered if e["spent_on"] <= to_date]

        total = sum(e["amount"] for e in filtered)

        total_per_category: dict[str, float] = {}
        for e in filtered:
            cat = e["category"].value if isinstance(e["category"], CategoryEnum) else e["category"]
            total_per_category[cat] = total_per_category.get(cat, 0.0) + e["amount"]

        if from_date and to_date:
            days = (to_date - from_date).days + 1
        elif filtered:
            dates = [e["spent_on"] for e in filtered]
            min_date, max_date = min(dates), max(dates)
            days = (max_date - min_date).days + 1
        else:
            days = 1

        days = max(days, 1)
        avg_per_day = total / days if filtered else 0.0

        return {
            "total": round(total, 2),
            "total_per_category": {k: round(v, 2) for k, v in total_per_category.items()},
            "average_per_day": round(avg_per_day, 2),
        }