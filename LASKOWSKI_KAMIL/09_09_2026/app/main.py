from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Query, Request, Response, status
from fastapi.responses import JSONResponse

from app.models import (
    ExpenseCategory,
    ExpenseCreate,
    ExpensePublic,
    ExpenseSummary,
    ExpenseUpdate,
)
from app.service import (
    ExpenseNotFoundError,
    ExpenseService,
    InvalidDateRangeError,
)

def get_service(request: Request) -> ExpenseService:
    return request.app.state.expense_service

ServiceDep = Annotated[ExpenseService, Depends(get_service)]

def create_app() -> FastAPI:
    app = FastAPI(title="Expenses Service", version="0.1.0")
    @app.exception_handler(ExpenseNotFoundError)
    async def not_found_handler(
        _request: Request, exc: ExpenseNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidDateRangeError)
    async def invalid_range_handler(
        _request: Request, exc: InvalidDateRangeError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )

    @app.post(
        "/expenses",
        response_model=ExpensePublic,
        status_code=status.HTTP_201_CREATED,
    )
    def create_expense(
        payload: ExpenseCreate, svc: ServiceDep
    ) -> ExpensePublic:
        return svc.create_expense(payload)

    @app.get("/expenses", response_model=list[ExpensePublic])
    def list_expenses(
        svc: ServiceDep,
        category: ExpenseCategory | None = Query(default=None),
        from_date: date | None = Query(default=None, alias="from"),
        to_date: date | None = Query(default=None, alias="to"),
    ) -> list[ExpensePublic]:
        return svc.list_expenses(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )

    @app.get("/expenses/summary", response_model=ExpenseSummary)
    def get_summary(
        svc: ServiceDep,
        category: ExpenseCategory | None = Query(default=None),
        from_date: date | None = Query(default=None, alias="from"),
        to_date: date | None = Query(default=None, alias="to"),
    ) -> ExpenseSummary:
        return svc.get_summary(
            category=category,
            from_date=from_date,
            to_date=to_date,
        )

    @app.get("/expenses/{expense_id}", response_model=ExpensePublic)
    def get_expense(expense_id: UUID, svc: ServiceDep) -> ExpensePublic:
        return svc.get_expense(expense_id)

    @app.patch("/expenses/{expense_id}", response_model=ExpensePublic)
    def update_expense(
        expense_id: UUID, payload: ExpenseUpdate, svc: ServiceDep
    ) -> ExpensePublic:
        return svc.update_expense(expense_id, payload)

    @app.delete(
        "/expenses/{expense_id}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def delete_expense(expense_id: UUID, svc: ServiceDep) -> Response:
        svc.delete_expense(expense_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()