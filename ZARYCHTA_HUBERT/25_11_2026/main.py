import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path as RoutePath

from models import OrderInput, LineInput, OrderOutput, AddedOutput, FinishedOutput
from service import create_order, add_service_to_order, complete_order, get_order

app = FastAPI(title='Workshop orders')
DEFAULT_DB = Path(__file__).resolve().parent/'database'/'workshop.db'
OrderId = Annotated[int, RoutePath(gt=0)]


@contextmanager
def session():
    db = sqlite3.connect(os.environ.get('WORKSHOP_DB', str(DEFAULT_DB)))
    db.execute('PRAGMA foreign_keys=ON')
    try:
        yield db
    finally:
        db.close()


def http_error(exc):
    code = 404 if isinstance(exc, LookupError) else 409
    raise HTTPException(status_code=code, detail=str(exc)) from exc


@app.post('/orders', status_code=201, response_model=OrderOutput)
def create(payload: OrderInput):
    with session() as db:
        try:
            order_id = create_order(db, payload.vehicle_id, payload.mechanic_id, payload.description)
            return get_order(db, order_id)
        except (LookupError, ValueError) as exc:
            http_error(exc)


@app.post('/orders/{order_id}/services', status_code=201, response_model=AddedOutput)
def append_service(order_id: OrderId, payload: LineInput):
    with session() as db:
        try:
            add_service_to_order(db, order_id, payload.service_id, payload.hours_worked, payload.final_price)
            return AddedOutput(order_id=order_id,service_id=payload.service_id,status='in_progress')
        except (LookupError, ValueError) as exc:
            http_error(exc)


@app.post('/orders/{order_id}/complete', status_code=200, response_model=FinishedOutput)
def finish(order_id: OrderId):
    with session() as db:
        try:
            complete_order(db, order_id)
            info = get_order(db, order_id)
            return FinishedOutput(order_id=order_id,status=info['status'],completed_at=info['completed_at'])
        except (LookupError, ValueError) as exc:
            http_error(exc)


@app.get('/orders/{order_id}', status_code=200, response_model=OrderOutput)
def inspect(order_id: OrderId):
    with session() as db:
        try:
            return get_order(db, order_id)
        except (LookupError, ValueError) as exc:
            http_error(exc)
