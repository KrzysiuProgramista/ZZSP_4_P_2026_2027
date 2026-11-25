from contextlib import closing
import os
import sqlite3
from fastapi import FastAPI, HTTPException, Path, status

from models import (
    AddServiceRequest,
    MessageResponse,
    OrderCreateRequest,
    OrderCreatedResponse,
    OrderDetailsResponse,
)
import service

DB_PATH = os.getenv("DB_PATH", "workshop.db")

app = FastAPI(title="Automotive Service Management System")

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@app.post(
    "/orders",
    response_model=OrderCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(payload: OrderCreateRequest) -> OrderCreatedResponse:
    try:
        with closing(_get_conn()) as conn:
            order_id = service.create_order(
                conn=conn,
                vehicle_id=payload.vehicle_id,
                mechanic_id=payload.mechanic_id,
                description=payload.description,
            )
            return OrderCreatedResponse(id=order_id, status="received")
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@app.post(
    "/orders/{order_id}/services",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_service_endpoint(
    payload: AddServiceRequest,
    order_id: int = Path(..., gt=0),
) -> MessageResponse:
    try:
        with closing(_get_conn()) as conn:
            service.add_service_to_order(
                conn=conn,
                order_id=order_id,
                service_id=payload.service_id,
                hours_worked=payload.hours_worked,
                final_price=payload.final_price,
            )
            return MessageResponse(message="Service added to order.")
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@app.post(
    "/orders/{order_id}/complete",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def complete_order_endpoint(order_id: int = Path(..., gt=0)) -> MessageResponse:
    try:
        with closing(_get_conn()) as conn:
            service.complete_order(conn=conn, order_id=order_id)
            return MessageResponse(message="Order completed.")
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@app.get(
    "/orders/{order_id}",
    response_model=OrderDetailsResponse,
    status_code=status.HTTP_200_OK,
)
def get_order_endpoint(order_id: int = Path(..., gt=0)) -> OrderDetailsResponse:
    try:
        with closing(_get_conn()) as conn:
            details = service.get_order_details(conn=conn, order_id=order_id)
            return OrderDetailsResponse(**details)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc