import os
import sqlite3
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI, Path, Request, status
from fastapi.responses import JSONResponse

import service
from models import (
    OrderCreateRequest,
    OrderDetailsResponse,
    OrderServiceCreateRequest,
)
from service import ConflictError, NotFoundError

DB_PATH = os.getenv("DATABASE_PATH", "workshop.db")

app = FastAPI(title="Automotive Service Management System")


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = service.get_connection(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


@app.exception_handler(NotFoundError)
def not_found_exception_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(ConflictError)
def conflict_exception_handler(_request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )


@app.post(
    "/orders",
    response_model=OrderDetailsResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(
    payload: OrderCreateRequest,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
) -> OrderDetailsResponse:
    order_id = service.create_order(
        conn=conn,
        vehicle_id=payload.vehicle_id,
        mechanic_id=payload.mechanic_id,
        description=payload.description,
    )
    details = service.get_order_details(conn, order_id)
    return OrderDetailsResponse(**details)


@app.post(
    "/orders/{order_id}/services",
    response_model=OrderDetailsResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_service_to_order_endpoint(
    order_id: Annotated[int, Path(gt=0)],
    payload: OrderServiceCreateRequest,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
) -> OrderDetailsResponse:
    service.add_service_to_order(
        conn=conn,
        order_id=order_id,
        service_id=payload.service_id,
        hours_worked=payload.hours_worked,
        final_price=payload.final_price,
    )
    details = service.get_order_details(conn, order_id)
    return OrderDetailsResponse(**details)


@app.post(
    "/orders/{order_id}/complete",
    response_model=OrderDetailsResponse,
    status_code=status.HTTP_200_OK,
)
def complete_order_endpoint(
    order_id: Annotated[int, Path(gt=0)],
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
) -> OrderDetailsResponse:
    service.complete_order(conn=conn, order_id=order_id)
    details = service.get_order_details(conn, order_id)
    return OrderDetailsResponse(**details)


@app.get(
    "/orders/{order_id}",
    response_model=OrderDetailsResponse,
    status_code=status.HTTP_200_OK,
)
def get_order_endpoint(
    order_id: Annotated[int, Path(gt=0)],
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
) -> OrderDetailsResponse:
    details = service.get_order_details(conn, order_id)
    return OrderDetailsResponse(**details)