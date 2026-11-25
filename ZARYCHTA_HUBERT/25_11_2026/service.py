import sqlite3
from datetime import datetime, timezone
from math import isfinite


def _check_id(number, field):
    if isinstance(number, bool) or not isinstance(number, int) or number < 1:
        raise ValueError(f'{field}: expected positive integer')


def _time_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


class Workshop:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _exists(self, table, item_id, label):
        # 'table' is passed only as a fixed literal by our own code, never from a user.
        if table == 'vehicles':
            sql = 'SELECT 1 FROM vehicles WHERE id=?'
        elif table == 'services':
            sql = 'SELECT 1 FROM services WHERE id=?'
        else:
            raise RuntimeError('Unsupported table')
        if self.conn.execute(sql, (item_id,)).fetchone() is None:
            raise LookupError(f'{label} not found')

    def create(self, vehicle_id, mechanic_id, description):
        _check_id(vehicle_id, 'vehicle_id')
        _check_id(mechanic_id, 'mechanic_id')
        if not isinstance(description, str) or not description.strip():
            raise ValueError('description is required')
        with self.conn:
            self._exists('vehicles', vehicle_id, 'vehicle')
            mechanic = self.conn.execute('SELECT active FROM mechanics WHERE id=?', (mechanic_id,)).fetchone()
            if mechanic is None:
                raise LookupError('mechanic not found')
            if mechanic[0] != 1:
                raise ValueError('mechanic is inactive')
            cur = self.conn.execute('INSERT INTO service_orders '
                                    '(vehicle_id,mechanic_id,received_at,completed_at,status,description) '
                                    'VALUES (?,?,?,NULL,?,?)',
                                    (vehicle_id, mechanic_id, _time_now(), 'received', description.strip()))
            return cur.lastrowid

    def add_line(self, order_id, service_id, hours_worked, final_price):
        _check_id(order_id, 'order_id')
        _check_id(service_id, 'service_id')
        if type(hours_worked) not in (float,int) or not isfinite(hours_worked) or hours_worked <= 0:
            raise ValueError('hours_worked must be finite and positive')
        if type(final_price) not in (float,int) or not isfinite(final_price) or final_price < 0:
            raise ValueError('final_price must be finite and non-negative')
        with self.conn:
            record = self.conn.execute('SELECT status FROM service_orders WHERE id=?', (order_id,)).fetchone()
            if record is None:
                raise LookupError('order not found')
            self._exists('services', service_id, 'service')
            if record[0] not in ('received','in_progress'):
                raise ValueError('closed orders cannot receive service lines')
            duplicate = self.conn.execute('SELECT 1 FROM order_services WHERE order_id=? AND service_id=?',
                                          (order_id, service_id)).fetchone()
            if duplicate:
                raise ValueError('service is already assigned to this order')
            self.conn.execute('INSERT INTO order_services (order_id,service_id,hours_worked,final_price) '
                              'VALUES (?,?,?,?)', (order_id,service_id,hours_worked,final_price))
            self.conn.execute('UPDATE service_orders SET status=? WHERE id=? AND status IN (?,?)',
                              ('in_progress',order_id,'received','in_progress'))

    def finish(self, order_id):
        _check_id(order_id, 'order_id')
        with self.conn:
            row = self.conn.execute('SELECT status FROM service_orders WHERE id=?', (order_id,)).fetchone()
            if row is None:
                raise LookupError('order not found')
            if row[0] not in ('received','in_progress'):
                raise ValueError('order is already closed')
            line = self.conn.execute('SELECT 1 FROM order_services WHERE order_id=? LIMIT 1',
                                     (order_id,)).fetchone()
            if line is None:
                raise ValueError('order requires at least one service')
            self.conn.execute('UPDATE service_orders SET status=?,completed_at=? WHERE id=? AND status IN (?,?)',
                              ('completed',_time_now(),order_id,'received','in_progress'))

    def details(self, order_id):
        _check_id(order_id, 'order_id')
        self.conn.row_factory = sqlite3.Row
        order = self.conn.execute('SELECT id,vehicle_id,mechanic_id,received_at,completed_at,status,description '
                                  'FROM service_orders WHERE id=?', (order_id,)).fetchone()
        if order is None:
            raise LookupError('order not found')
        details = dict(order)
        lines = self.conn.execute('SELECT os.service_id,s.name AS service_name,os.hours_worked,os.final_price '
                                  'FROM services s JOIN order_services os ON s.id=os.service_id '
                                  'WHERE os.order_id=? ORDER BY os.service_id', (order_id,)).fetchall()
        details['services'] = [dict(line) for line in lines]
        details['total_price'] = round(sum(line['final_price'] for line in lines),2)
        return details


def create_order(conn, vehicle_id, mechanic_id, description) -> int:
    return Workshop(conn).create(vehicle_id, mechanic_id, description)


def add_service_to_order(conn, order_id, service_id, hours_worked, final_price) -> None:
    Workshop(conn).add_line(order_id, service_id, hours_worked, final_price)


def complete_order(conn, order_id) -> None:
    Workshop(conn).finish(order_id)


def get_order(conn, order_id) -> dict:
    return Workshop(conn).details(order_id)
