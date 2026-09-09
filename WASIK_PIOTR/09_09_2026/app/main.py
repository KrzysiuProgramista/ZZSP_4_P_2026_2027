
from datetime import date

from fastapi import FastAPI, HTTPException, Query, status

from .models import (
    Category,
    ExpenseCreate,
    ExpensePublic,
    ExpenseSummary,
    ExpenseUpdate,
)
from .service import ExpenseNotFoundError, ExpenseService
from .storage import ExpenseStorage


app = FastAPI(title="Expenses API")

storage = ExpenseStorage()
service = ExpenseService(storage)


def validate_range(
    from_date: date | None,
    to_date: date | None,
) -> None:
    if (
        from_date is not None
        and to_date is not None
        and from_date > to_date
    ):
        raise HTTPException(
            status_code=422,
            detail="from must be less than or equal to to",
        )


@app.post(
    "/expenses",
    response_model=ExpensePublic,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(data: ExpenseCreate):
    return service.create(data)


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
    validate_range(from_date, to_date)

    return service.list(
        category=category,
        from_date=from_date,
        to_date=to_date,
    )


@app.get(
    "/expenses/summary",
    response_model=ExpenseSummary,
)
def expense_summary(
    from_date: date | None = Query(
        default=None,
        alias="from",
    ),
    to_date: date | None = Query(
        default=None,
        alias="to",
    ),
):
    validate_range(from_date, to_date)

    return service.summary(
        from_date=from_date,
        to_date=to_date,
    )


@app.get(
    "/expenses/{expense_id}",
    response_model=ExpensePublic,
)
def get_expense(expense_id: int):
    try:
        return service.get(expense_id)
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
    data: ExpenseUpdate,
):
    try:
        return service.update(
            expense_id,
            data,
        )
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

