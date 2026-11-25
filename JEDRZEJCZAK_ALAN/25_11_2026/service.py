import sqlite3
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _positive_id(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f'{name} must be a positive integer')


def _row(conn, sql, params):
    return conn.execute(sql, params).fetchone()


def create_order(conn: sqlite3.Connection, vehicle_id: int, mechanic_id: int, description: str) -> int:
    _positive_id(vehicle_id, 'vehicle_id')
    _positive_id(mechanic_id, 'mechanic_id')
    if not isinstance(description, str) or not description.strip():
        raise ValueError('description must not be empty')
    with conn:
        if _row(conn, 'SELECT id FROM vehicles WHERE id = ?', (vehicle_id,)) is None:
            raise LookupError('vehicle does not exist')
        mechanic = _row(conn, 'SELECT active FROM mechanics WHERE id = ?', (mechanic_id,))
        if mechanic is None:
            raise LookupError('mechanic does not exist')
        if mechanic[0] != 1:
            raise ValueError('mechanic is inactive')
        cursor = conn.execute(
            'INSERT INTO service_orders (vehicle_id, mechanic_id, received_at, completed_at, status, description) '
            'VALUES (?, ?, ?, NULL, ?, ?)',
            (vehicle_id, mechanic_id, _now(), 'received', description.strip()),
        )
        return cursor.lastrowid


def add_service_to_order(conn: sqlite3.Connection, order_id: int, service_id: int,
                         hours_worked: float, final_price: float) -> None:
    _positive_id(order_id, 'order_id')
    _positive_id(service_id, 'service_id')
    if isinstance(hours_worked, bool) or not isinstance(hours_worked, (int, float)) or not 0 < hours_worked < float('inf'):
        raise ValueError('hours_worked must be positive and finite')
    if isinstance(final_price, bool) or not isinstance(final_price, (int, float)) or not 0 <= final_price < float('inf'):
        raise ValueError('final_price must be non-negative and finite')
    with conn:
        order = _row(conn, 'SELECT status FROM service_orders WHERE id = ?', (order_id,))
        if order is None:
            raise LookupError('order does not exist')
        if _row(conn, 'SELECT id FROM services WHERE id = ?', (service_id,)) is None:
            raise LookupError('service does not exist')
        if order[0] in ('completed', 'cancelled'):
            raise ValueError('order is closed')
        if _row(conn, 'SELECT 1 FROM order_services WHERE order_id = ? AND service_id = ?', (order_id, service_id)):
            raise ValueError('service is already on the order')
        conn.execute('INSERT INTO order_services (order_id, service_id, hours_worked, final_price) '
                     'VALUES (?, ?, ?, ?)', (order_id, service_id, hours_worked, final_price))
        conn.execute('UPDATE service_orders SET status = ? WHERE id = ?', ('in_progress', order_id))


def complete_order(conn: sqlite3.Connection, order_id: int) -> None:
    _positive_id(order_id, 'order_id')
    with conn:
        order = _row(conn, 'SELECT status FROM service_orders WHERE id = ?', (order_id,))
        if order is None:
            raise LookupError('order does not exist')
        if order[0] in ('completed', 'cancelled'):
            raise ValueError('order is closed')
        if _row(conn, 'SELECT 1 FROM order_services WHERE order_id = ? LIMIT 1', (order_id,)) is None:
            raise ValueError('order has no service lines')
        conn.execute('UPDATE service_orders SET status = ?, completed_at = ? WHERE id = ?',
                     ('completed', _now(), order_id))


def get_order(conn: sqlite3.Connection, order_id: int) -> dict:
    _positive_id(order_id, 'order_id')
    conn.row_factory = sqlite3.Row
    record = conn.execute('SELECT id, vehicle_id, mechanic_id, received_at, completed_at, status, description '
                          'FROM service_orders WHERE id = ?', (order_id,)).fetchone()
    if record is None:
        raise LookupError('order does not exist')
    lines = conn.execute('SELECT os.service_id, s.name AS service_name, os.hours_worked, os.final_price '
                         'FROM order_services AS os JOIN services AS s ON s.id = os.service_id '
                         'WHERE os.order_id = ? ORDER BY os.service_id', (order_id,)).fetchall()
    data = dict(record)
    data['services'] = [dict(line) for line in lines]
    data['total_price'] = round(sum(line['final_price'] for line in lines), 2)
    return data
