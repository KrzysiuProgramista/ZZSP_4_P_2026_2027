from collections.abc import Generator
import sqlite3
from fastapi import Depends, FastAPI, HTTPException, Path, status

from models import (
    AddServiceRequest,
    OrderCreateRequest,
    OrderCreateResponse,
    OrderDetailResponse,
)
from service import (
    ConflictError,
    NotFoundError,
    add_service_to_order,
    complete_order,
    create_order,
    get_connection,
    get_order_details,
)

app = FastAPI(title="Automotive Service Management API")


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


@app.post("/orders", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
def api_create_order(payload: OrderCreateRequest, conn: sqlite3.Connection = Depends(get_db)):
    try:
        order_id = create_order(
            conn=conn,
            vehicle_id=payload.vehicle_id,
            mechanic_id=payload.mechanic_id,
            description=payload.description,
        )
        return OrderCreateResponse(id=order_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@app.post("/orders/{order_id}/services", status_code=status.HTTP_201_CREATED)
def api_add_service_to_order(
    payload: AddServiceRequest,
    order_id: int = Path(..., gt=0),
    conn: sqlite3.Connection = Depends(get_db),
):
    try:
        add_service_to_order(
            conn=conn,
            order_id=order_id,
            service_id=payload.service_id,
            hours_worked=payload.hours_worked,
            final_price=payload.final_price,
        )
        return {"status": "added"}
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@app.post("/orders/{order_id}/complete", status_code=status.HTTP_200_OK)
def api_complete_order(
    order_id: int = Path(..., gt=0),
    conn: sqlite3.Connection = Depends(get_db),
):
    try:
        complete_order(conn=conn, order_id=order_id)
        return {"status": "completed"}
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get("/orders/{order_id}", response_model=OrderDetailResponse, status_code=status.HTTP_200_OK)
def api_get_order(
    order_id: int = Path(..., gt=0),
    conn: sqlite3.Connection = Depends(get_db),
):
    try:
        return get_order_details(conn=conn, order_id=order_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
