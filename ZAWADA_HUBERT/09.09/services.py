from datetime import date
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

CATEGORIES = {"food", "transport", "entertainment", "bills", "other"}

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    category: str
    description: str = Field(..., min_length=1, max_length=200)
    spent_on: date

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in CATEGORIES:
            raise ValueError()
        return v

    @field_validator("spent_on")
    @classmethod
    def validate_spent_on(cls, v: date) -> date:
        if v > date.today():
            raise ValueError()
        return v

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    spent_on: Optional[date] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in CATEGORIES:
            raise ValueError()
        return v

    @field_validator("spent_on")
    @classmethod
    def validate_spent_on(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError()
        return v

class ExpensePublic(ExpenseBase):
    id: int

class ExpenseService:
    def __init__(self):
        self._storage: Dict[int, dict] = {}
        self._counter = 1

    def create(self, data: ExpenseCreate) -> dict:
        item = data.model_dump()
        item["id"] = self._counter
        self._storage[self._counter] = item
        self._counter += 1
        return item

    def get_all(self, category: Optional[str] = None, from_date: Optional[date] = None, to_date: Optional[date] = None) -> List[dict]:
        items = list(self._storage.values())
        if category:
            items = [e for e in items if e["category"] == category]
        if from_date:
            items = [e for e in items if e["spent_on"] >= from_date]
        if to_date:
            items = [e for e in items if e["spent_on"] <= to_date]
        return items

    def get_by_id(self, expense_id: int) -> Optional[dict]:
        return self._storage.get(expense_id)

    def update(self, expense_id: int, data: ExpenseUpdate) -> Optional[dict]:
        item = self._storage.get(expense_id)
        if not item:
            return None
        item.update(data.model_dump(exclude_unset=True))
        return item

    def delete(self, expense_id: int) -> bool:
        if expense_id in self._storage:
            del self._storage[expense_id]
            return True
        return False

    def get_summary(self, from_date: Optional[date] = None, to_date: Optional[date] = None) -> dict:
        items = self.get_all(from_date=from_date, to_date=to_date)
        total = sum(e["amount"] for e in items)
        total_per_category = {cat: 0.0 for cat in CATEGORIES}
        for e in items:
            total_per_category[e["category"]] += e["amount"]
        average_per_day = 0.0
        if items and from_date and to_date:
            days = (to_date - from_date).days + 1
            if days > 0:
                average_per_day = total / days
        return {
            "total": total,
            "total_per_category": total_per_category,
            "average_per_day": average_per_day
        }

service = ExpenseService()
app = FastAPI()

@app.post("/expenses", response_model=ExpensePublic, status_code=status.HTTP_201_CREATED)
def create_expense(expense: ExpenseCreate):
    return service.create(expense)

@app.get("/expenses", response_model=List[ExpensePublic])
def list_expenses(
    category: Optional[str] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to")
):
    return service.get_all(category=category, from_date=from_date, to_date=to_date)

@app.get("/expenses/summary")
def get_expenses_summary(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to")
):
    return service.get_summary(from_date=from_date, to_date=to_date)

@app.get("/expenses/{expense_id}", response_model=ExpensePublic)
def get_expense(expense_id: int):
    item = service.get_by_id(expense_id)
    if not item:
        raise HTTPException(status_code=404)
    return item

@app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
def update_expense(expense_id: int, expense: ExpenseUpdate):
    updated = service.update(expense_id, expense)
    if not updated:
        raise HTTPException(status_code=404)
    return updated

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int):
    if not service.delete(expense_id):
        raise HTTPException(status_code=404)