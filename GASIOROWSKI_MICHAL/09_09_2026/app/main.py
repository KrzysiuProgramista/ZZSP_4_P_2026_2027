from datetime import date
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Response, status

from .models import (
    ExpenseCategory,
    ExpenseCreate,
    ExpensePublic,
    ExpenseSummary,
    ExpenseUpdate,
)
from .repository import InMemoryExpenseRepository
from .service import (
    ExpenseNotFoundError,
    ExpenseService,
    InvalidDateRangeError,
)

app = FastAPI(title="Expenses API")

repository = InMemoryExpenseRepository()
service = ExpenseService(repository)


CategoryQuery = Annotated[
    ExpenseCategory | None,
    Query(description="Filter by category"),
]

FromQuery = Annotated[
    date | None,
    Query(alias="from", description="Inclusive start date"),
]

ToQuery = Annotated[
    date | None,
    Query(alias="to", description="Inclusive end date"),
]


def handle_service_error(error: Exception) -> None:
    if isinstance(error, ExpenseNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    if isinstance(error, InvalidDateRangeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    raise error


@app.post(
    "/expenses",
    response_model=ExpensePublic,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(payload: ExpenseCreate) -> ExpensePublic:
    return service.create(payload)


@app.get("/expenses", response_model=list[ExpensePublic])
def list_expenses(
    category: CategoryQuery = None,
    from_date: FromQuery = None,
    to_date: ToQuery = None,
) -> list[ExpensePublic]:
    try:
        return service.list(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )
    except InvalidDateRangeError as error:
        handle_service_error(error)


@app.get("/expenses/summary", response_model=ExpenseSummary)
def get_summary(
    category: CategoryQuery = None,
    from_date: FromQuery = None,
    to_date: ToQuery = None,
) -> ExpenseSummary:
    try:
        return service.summary(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )
    except InvalidDateRangeError as error:
        handle_service_error(error)


@app.get("/expenses/{expense_id}", response_model=ExpensePublic)
def get_expense(expense_id: int) -> ExpensePublic:
    try:
        return service.get(expense_id)
    except ExpenseNotFoundError as error:
        handle_service_error(error)


@app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
) -> ExpensePublic:
    try:
        return service.update(expense_id, payload)
    except ExpenseNotFoundError as error:
        handle_service_error(error)


@app.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(expense_id: int) -> Response:
    try:
        service.delete(expense_id)
    except ExpenseNotFoundError as error:
        handle_service_error(error)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
