from contextlib import asynccontextmanager
import os
from pathlib import Path
import sqlite3
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Path as ApiPath, status

from models import OrderCreateRequest, OrderResponse, OrderServiceAddRequest
import service

DB_PATH = os.getenv("WORKSHOP_DB_PATH", "workshop.db")
SCHEMA_PATH = Path(__file__).resolve().parent / "database" / "schema.sql"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if SCHEMA_PATH.exists():
        service.init_db(DB_PATH, str(SCHEMA_PATH))
    yield


app = FastAPI(title="Car Repair Workshop API", lifespan=lifespan)


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = service.get_connection(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


@app.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(
    payload: OrderCreateRequest,
    conn: sqlite3.Connection = Depends(get_db),
) -> OrderResponse:
    try:
        order_id = service.create_order(
            conn=conn,
            vehicle_id=payload.vehicle_id,
            mechanic_id=payload.mechanic_id,
            description=payload.description,
        )
        order_data = service.get_order(conn, order_id)
        return OrderResponse(**order_data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/orders/{order_id}/services",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_service_to_order_endpoint(
    payload: OrderServiceAddRequest,
    order_id: int = ApiPath(..., gt=0, description="Positive service order ID."),
    conn: sqlite3.Connection = Depends(get_db),
) -> OrderResponse:
    try:
        service.add_service_to_order(
            conn=conn,
            order_id=order_id,
            service_id=payload.service_id,
            hours_worked=payload.hours_worked,
            final_price=payload.final_price,
        )
        order_data = service.get_order(conn, order_id)
        return OrderResponse(**order_data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.post(
    "/orders/{order_id}/complete",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
def complete_order_endpoint(
    order_id: int = ApiPath(..., gt=0, description="Positive service order ID."),
    conn: sqlite3.Connection = Depends(get_db),
) -> OrderResponse:
    try:
        service.complete_order(conn=conn, order_id=order_id)
        order_data = service.get_order(conn, order_id)
        return OrderResponse(**order_data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
def get_order_endpoint(
    order_id: int = ApiPath(..., gt=0, description="Positive service order ID."),
    conn: sqlite3.Connection = Depends(get_db),
) -> OrderResponse:
    try:
        order_data = service.get_order(conn, order_id)
        return OrderResponse(**order_data)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc