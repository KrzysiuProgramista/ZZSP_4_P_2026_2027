from datetime import date
from typing import Optional, Dict, Any, List

class ExpenseService:
    def __init__(self):
        self.db: List[Dict[str, Any]] = []
        self.counter: int = 1

    def create_expense(self, amount: float, category: str, description: str, spent_on: date) -> dict:
        if spent_on > date.today():
            raise ValueError("Date cannot be in the future")

        item = {
            "id": self.counter,
            "amount": amount,
            "category": category,
            "description": description,
            "spent_on": spent_on,
        }
        self.db.append(item)
        self.counter += 1
        return item
    
    def get_expenses(
        self,
        category: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[dict]:
        res = self.db
        if category:
            res = [e for e in res if e["category"] == category]
        if from_date:
            res = [e for e in res if e["spent_on"] >= from_date]
        if to_date:
            res = [e for e in res if e["spent_on"] <= to_date]
        return res

    def get_summary(self, from_date: Optional[date] = None, to_date: Optional[date] = None) -> dict:
        filtered = self.get_expenses(from_date=from_date, to_date=to_date)
        total = sum(e["amount"] for e in filtered)
        
        per_category = {}
        for e in filtered:
            cat = e["category"]
            per_category[cat] = per_category.get(cat, 0) + e["amount"]

        # Calculate average per day over the requested range
        avg_per_day = 0.0
        if from_date and to_date:
            delta_days = (to_date - from_date).days + 1
            if delta_days > 0:
                avg_per_day = total / delta_days

        return {
            "total": total,
            "total_per_category": per_category,
            "average_per_day": avg_per_day
        }

    def get_expense(self, expense_id: int) -> dict:
        for e in self.db:
            if e["id"] == expense_id:
                return e
        raise KeyError("Not found")

    def update_expense(
        self,
        expense_id: int,
        amount: Optional[float] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        spent_on: Optional[date] = None,
    ) -> dict:
        e = self.get_expense(expense_id)
        if spent_on is not None and spent_on > date.today():
            raise ValueError("Date cannot be in the future")

        if amount is not None:
            e["amount"] = amount
        if category is not None:
            e["category"] = category
        if description is not None:
            e["description"] = description
        if spent_on is not None:
            e["spent_on"] = spent_on
            
        return e

    def delete_expense(self, expense_id: int) -> None:
        for i, e in enumerate(self.db):
            if e["id"] == expense_id:
                self.db.pop(i)
                return
        raise KeyError("Not found")