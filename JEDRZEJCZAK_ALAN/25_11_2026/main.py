import os
import sqlite3
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path as ApiPath

from models import OrderCreate, ServiceCreate, ServiceAdded, OrderCompleted, OrderDetails
from service import create_order, add_service_to_order, complete_order, get_order

app = FastAPI(title='Automotive Service API')
DB_FILE = str(Path(__file__).resolve().parent / 'database' / 'workshop.db')


def db_connection():
    conn = sqlite3.connect(os.environ.get('WORKSHOP_DB', DB_FILE))
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
    finally:
        conn.close()


def translate_error(error):
    if isinstance(error, LookupError):
        raise HTTPException(status_code=404, detail=str(error)) from error
    raise HTTPException(status_code=409, detail=str(error)) from error


Conn = Annotated[sqlite3.Connection, Depends(db_connection)]
OrderId = Annotated[int, ApiPath(gt=0)]


@app.post('/orders', response_model=OrderDetails, status_code=201)
def post_order(body: OrderCreate, conn: Conn):
    try:
        order_id = create_order(conn, body.vehicle_id, body.mechanic_id, body.description)
        return get_order(conn, order_id)
    except (LookupError, ValueError) as error:
        translate_error(error)


@app.post('/orders/{order_id}/services', response_model=ServiceAdded, status_code=201)
def post_service(order_id: OrderId, body: ServiceCreate, conn: Conn):
    try:
        add_service_to_order(conn, order_id, body.service_id, body.hours_worked, body.final_price)
        return ServiceAdded(order_id=order_id, service_id=body.service_id, status='in_progress')
    except (LookupError, ValueError) as error:
        translate_error(error)


@app.post('/orders/{order_id}/complete', response_model=OrderCompleted)
def post_complete(order_id: OrderId, conn: Conn):
    try:
        complete_order(conn, order_id)
        order = get_order(conn, order_id)
        return OrderCompleted(order_id=order_id, status=order['status'], completed_at=order['completed_at'])
    except (LookupError, ValueError) as error:
        translate_error(error)


@app.get('/orders/{order_id}', response_model=OrderDetails)
def fetch_order(order_id: OrderId, conn: Conn):
    try:
        return get_order(conn, order_id)
    except (LookupError, ValueError) as error:
        translate_error(error)
