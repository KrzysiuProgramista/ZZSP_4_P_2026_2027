from datetime import date

from fastapi import FastAPI, HTTPException, Query, Response, status

from .models import (
    ExpenseCategory,
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
service = ExpenseService()


def not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Expense not found")


def invalid_range() -> HTTPException:
    return HTTPException(
        status_code=400,
        detail="'from' date cannot be later than 'to' date",
    )


@app.post(
    "/expenses",
    response_model=ExpensePublic,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(data: ExpenseCreate) -> ExpensePublic:
    return service.create(data)


@app.get("/expenses", response_model=list[ExpensePublic])
def list_expenses(
    category: ExpenseCategory | None = None,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> list[ExpensePublic]:
    try:
        return service.list(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )
    except InvalidDateRangeError:
        raise invalid_range()


@app.get("/expenses/summary", response_model=ExpenseSummary)
def get_summary(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> ExpenseSummary:
    try:
        return service.summary(from_date=from_date, to_date=to_date)
    except InvalidDateRangeError:
        raise invalid_range()


@app.get("/expenses/{expense_id}", response_model=ExpensePublic)
def get_expense(expense_id: int) -> ExpensePublic:
    try:
        return service.get(expense_id)
    except ExpenseNotFoundError:
        raise not_found()


@app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
) -> ExpensePublic:
    try:
        return service.update(expense_id, data)
    except ExpenseNotFoundError:
        raise not_found()


@app.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(expense_id: int) -> Response:
    try:
        service.delete(expense_id)
    except ExpenseNotFoundError:
        raise not_found()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
