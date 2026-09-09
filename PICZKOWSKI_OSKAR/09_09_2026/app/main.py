from datetime import date

from fastapi import FastAPI, HTTPException, Query, Response, status

from .schemas import (
    Category,
    ExpenseCreate,
    ExpensePublic,
    ExpenseSummary,
    ExpenseUpdate,
)
from .service import (
    ExpenseNotFoundError,
    ExpenseService,
    InvalidDateRangeError,
)


app = FastAPI(title="Expenses API")


# In-memory storage
expenses_db = {}

# SERVICE MUSI BYĆ UTWORZONY TUTAJ
service = ExpenseService(expenses_db)


def to_public(expense):
    return ExpensePublic(
        id=expense["id"],
        amount=expense["amount"],
        category=expense["category"],
        description=expense["description"],
        spent_on=expense["spent_on"],
    )


@app.post(
    "/expenses",
    response_model=ExpensePublic,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(payload: ExpenseCreate):
    expense = service.create(
        amount=payload.amount,
        category=payload.category.value,
        description=payload.description,
        spent_on=payload.spent_on,
    )

    return to_public(expense)


@app.get(
    "/expenses",
    response_model=list[ExpensePublic],
)
def list_expenses(
    category: Category | None = None,
    from_date: date | None = Query(
        default=None,
        alias="from",
    ),
    to_date: date | None = Query(
        default=None,
        alias="to",
    ),
):
    try:
        expenses = service.list(
            category=(
                category.value
                if category is not None
                else None
            ),
            from_date=from_date,
            to_date=to_date,
        )

        return [
            to_public(expense)
            for expense in expenses
        ]

    except InvalidDateRangeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get(
    "/expenses/summary",
    response_model=ExpenseSummary,
)
def expense_summary(
    category: Category | None = None,
    from_date: date | None = Query(
        default=None,
        alias="from",
    ),
    to_date: date | None = Query(
        default=None,
        alias="to",
    ),
):
    try:
        return service.summary(
            category=(
                category.value
                if category is not None
                else None
            ),
            from_date=from_date,
            to_date=to_date,
        )

    except InvalidDateRangeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@app.get(
    "/expenses/{expense_id}",
    response_model=ExpensePublic,
)
def get_expense(expense_id: int):
    try:
        expense = service.get(expense_id)
        return to_public(expense)

    except ExpenseNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )


@app.patch(
    "/expenses/{expense_id}",
    response_model=ExpensePublic,
)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
):
    try:
        changes = payload.model_dump(
            exclude_unset=True
        )

        if "category" in changes:
            changes["category"] = (
                changes["category"].value
            )

        expense = service.update(
            expense_id,
            changes,
        )

        return to_public(expense)

    except ExpenseNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )


@app.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(expense_id: int):
    try:
        service.delete(expense_id)

    except ExpenseNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
