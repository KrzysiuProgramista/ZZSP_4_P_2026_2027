from collections.abc import Generator
import os
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, Path, status

from models import (
    AddServiceRequest,
    OrderCreateRequest,
    OrderCreatedResponse,
    OrderDetailResponse,
    OrderStatusResponse,
)
from service import (
    ConflictError,
    InvalidInputError,
    NotFoundError,
    add_service_to_order,
    complete_order,
    create_order,
    get_connection,
    get_order_details
)

DB_PATH = os.getenv("DATABASE_PATH", "service.db")

app = FastAPI(title="Automotive Service Management System")


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def _handle_service_error(exc: Exception) -> HTTPException:
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, InvalidInputError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error")


@app.post("/orders", response_model=OrderCreatedResponse, status_code=status.HTTP_201_CREATED)
def api_create_order(
    payload: OrderCreateRequest,
    conn: sqlite3.Connection = Depends(get_db),
) -> OrderCreatedResponse:
    try:
        order_id = create_order(
            conn=conn,
            vehicle_id=payload.vehicle_id,
            mechanic_id=payload.mechanic_id,
            description=payload.description,
        )
        return OrderCreatedResponse(id=order_id)
    except Exception as exc:
        raise _handle_service_error(exc) from exc


@app.post(
    "/orders/{order_id}/services",
    status_code=status.HTTP_201_CREATED,
)
def api_add_service_to_order(
    payload: AddServiceRequest,
    order_id: int = Path(..., gt=0),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict[str, str]:
    try:
        add_service_to_order(
            conn=conn,
            order_id=order_id,
            service_id=payload.service_id,
            hours_worked=payload.hours_worked,
            final_price=payload.final_price,
        )
        return {"detail": "Service added to order."}
    except Exception as exc:
        raise _handle_service_error(exc) from exc


@app.post(
    "/orders/{order_id}/complete",
    response_model=OrderStatusResponse,
    status_code=status.HTTP_200_OK,
)
def api_complete_order(
    order_id: int = Path(..., gt=0),
    conn: sqlite3.Connection = Depends(get_db),
) -> OrderStatusResponse:
    try:
        complete_order(conn=conn, order_id=order_id)
        details = get_order_details(conn=conn, order_id=order_id)
        return OrderStatusResponse(id=details["id"], status=details["status"])
    except Exception as exc:
        raise _handle_service_error(exc) from exc


@app.get(
    "/orders/{order_id}",
    response_model=OrderDetailResponse,
    status_code=status.HTTP_200_OK,
)
def api_get_order(
    order_id: int = Path(..., gt=0),
    conn: sqlite3.Connection = Depends(get_db),
) -> OrderDetailResponse:
    try:
        details = get_order_details(conn=conn, order_id=order_id)
        return OrderDetailResponse(**details)
    except Exception as exc:
        raise _handle_service_error(exc) from exc