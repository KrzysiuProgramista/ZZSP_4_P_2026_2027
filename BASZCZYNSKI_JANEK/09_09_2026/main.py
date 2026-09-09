from fastapi import FastAPI, HTTPException, Query
from datetime import date

from models import Expense, Category
import service


app = FastAPI()

expenses = {
    1: Expense(
        amount=25,
        category=Category.ExpenseA,
        desc="Coffee",
        spent_on=date(2026, 9, 1)
    ),
    2: Expense(
        amount=80,
        category=Category.ExpenseB,
        desc="Groceries",
        spent_on=date(2026, 9, 2)
    ),
    3: Expense(
        amount=15,
        category=Category.ExpenseA,
        desc="Lunch",
        spent_on=date(2026, 9, 3)
    ),
    4: Expense(
        amount=120,
        category=Category.ExpenseB,
        desc="New shoes",
        spent_on=date(2026, 9, 5)
    ),
    5: Expense(
        amount=40,
        category=Category.ExpenseA,
        desc="Movie",
        spent_on=date(2026, 9, 6)
    ),
    6: Expense(
        amount=60,
        category=Category.ExpenseB,
        desc="Dinner",
        spent_on=date(2026, 9, 8)
    )
}

nextId = 7


@app.post("/expenses")
async def createExpense(e: Expense):
    global nextId

    expense = service.createExpense(expenses, nextId, e)

    result = {
        "id": nextId,
        **expense.model_dump()
    }

    nextId += 1

    return result


@app.get("/expenses")
async def getExpenses(
    category: Category | None = None,
    from_: date | None = Query(None, alias="from"),
    to: date | None = None
):
    return service.getExpenses(
        expenses,
        category,
        from_,
        to
    )


@app.get("/expenses/summary")
async def getSummary(
    category: Category | None = None,
    from_: date | None = Query(None, alias="from"),
    to: date | None = None
):
    return service.getSummary(
        expenses,
        category,
        from_,
        to
    )


@app.get("/expenses/{id}")
async def getExpense(id: int):
    expense = service.getExpense(expenses, id)

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return {
        "id": id,
        **expense.model_dump()
    }


@app.patch("/expenses/{id}")
async def updateExpense(id: int, e: Expense):
    expense = service.updateExpense(expenses, id, e)

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return {
        "id": id,
        **expense.model_dump()
    }


@app.delete("/expenses/{id}")
async def deleteExpense(id: int):
    deleted = service.deleteExpense(expenses, id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return {
        "message": "Expense deleted"
    }
