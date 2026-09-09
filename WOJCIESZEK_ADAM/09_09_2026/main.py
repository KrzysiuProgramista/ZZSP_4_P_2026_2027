from datetime import date, datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

# ==========================================
# CONSTANTS & ENUMS
# ==========================================
VALID_CATEGORIES = {"Food", "Transport", "Entertainment", "Utilities", "Other"}

# ==========================================
# a) PYDANTIC MODELS
# ==========================================
class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    category: str = Field(..., description="Category must be from the allowed set")
    description: str = Field(..., min_length=1, max_length=200, description="Description between 1-200 chars")
    spent_on: date

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        if value not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return value

    @field_validator("spent_on")
    @classmethod
    def validate_spent_on(cls, value: date) -> date:
        if value > datetime.utcnow().date():
            raise ValueError("spent_on date cannot be in the future")
        return value


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    spent_on: Optional[date] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return value

    @field_validator("spent_on")
    @classmethod
    def validate_spent_on(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value > datetime.utcnow().date():
            raise ValueError("spent_on date cannot be in the future")
        return value


class ExpensePublic(ExpenseBase):
    id: int


# ==========================================
# d) SERVICE LAYER (NO FASTAPI IMPORTS)
# ==========================================
class ExpenseService:
    def __init__(self):
        self._storage: Dict[int, dict] = {}
        self._counter: int = 1

    def create_expense(self, expense_in: ExpenseCreate) -> ExpensePublic:
        expense_id = self._counter
        self._counter += 1
        
        data = expense_in.model_dump()
        data["id"] = expense_id
        self._storage[expense_id] = data
        return ExpensePublic(**data)

    def get_expense(self, expense_id: int) -> Optional[ExpensePublic]:
        data = self._storage.get(expense_id)
        if not data:
            return None
        return ExpensePublic(**data)

    def list_expenses(
        self,
        category: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[ExpensePublic]:
        results = []
        for data in self._storage.values():
            # Apply category filter
            if category and data["category"] != category:
                continue
            # Apply date range filters
            if date_from and data["spent_on"] < date_from:
                continue
            if date_to and data["spent_on"] > date_to:
                continue
            results.append(ExpensePublic(**data))
        return results

    def update_expense(self, expense_id: int, expense_in: ExpenseUpdate) -> Optional[ExpensePublic]:
        data = self._storage.get(expense_id)
        if not data:
            return None

        update_data = expense_in.model_dump(exclude_unset=True)
        data.update(update_data)
        self._storage[expense_id] = data
        return ExpensePublic(**data)

    def delete_expense(self, expense_id: int) -> bool:
        if expense_id in self._storage:
            del self._storage[expense_id]
            return True
        return False

    def get_summary(
        self,
        category: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> dict:
        matched_expenses = self.list_expenses(category=category, date_from=date_from, date_to=date_to)
        
        total = sum(e.amount for e in matched_expenses)
        
        total_per_category: Dict[str, float] = {}
        for e in matched_expenses:
            total_per_category[e.category] = total_per_category.get(e.category, 0.0) + e.amount

        # Calculate average per day over the requested range
        if date_from and date_to:
            # Inclusive day count
            days = (date_to - date_from).days + 1
        elif matched_expenses:
            # Fallback range: min date to max date present in the filtered result set
            min_date = min(e.spent_on for e in matched_expenses)
            max_date = max(e.spent_on for e in matched_expenses)
            days = (max_date - min_date).days + 1
        else:
            days = 1

        days = max(days, 1) # Prevent division by zero
        average_per_day = total / days

        return {
            "total": total,
            "total_per_category": total_per_category,
            "average_per_day": round(average_per_day, 2),
            "days_counted": days
        }


# Global service instance for in-memory storage
expense_service = ExpenseService()

# ==========================================
# b) & c) FASTAPI ROUTING
# ==========================================
app = FastAPI(title="Expense Service API")


@app.post("/expenses", response_model=ExpensePublic, status_code=status.HTTP_201_CREATED)
def create_expense(expense_in: ExpenseCreate):
    return expense_service.create_expense(expense_in)


@app.get("/expenses", response_model=List[ExpensePublic])
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    from_date: Optional[date] = Query(None, alias="from", description="Filter from date (inclusive)"),
    to_date: Optional[date] = Query(None, alias="to", description="Filter to date (inclusive)"),
):
    return expense_service.list_expenses(category=category, date_from=from_date, date_to=to_date)


@app.get("/expenses/summary", response_model=dict)
def get_expenses_summary(
    category: Optional[str] = Query(None, description="Filter summary by category"),
    from_date: Optional[date] = Query(None, alias="from", description="Filter summary from date"),
    to_date: Optional[date] = Query(None, alias="to", description="Filter summary to date"),
):
    return expense_service.get_summary(category=category, date_from=from_date, date_to=to_date)


@app.get("/expenses/{id}", response_model=ExpensePublic)
def get_expense(id: int):
    expense = expense_service.get_expense(id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.patch("/expenses/{id}", response_model=ExpensePublic)
def update_expense(id: int, expense_in: ExpenseUpdate):
    expense = expense_service.update_expense(id, expense_in)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.delete("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(id: int):
    success = expense_service.delete_expense(id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None