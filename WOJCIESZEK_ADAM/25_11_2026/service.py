from datetime import datetime, timezone
import sqlite3
from typing import Any
from pathlib import Path


class NotFoundError(LookupError):
    """Raised when a required database record does not exist."""


class ConflictError(ValueError):
    """Raised when an operation violates current business state or uniqueness rules."""


class InvalidInputError(ValueError):
    """Raised when input arguments fail domain validation."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def get_connection(db_path: str = "service.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_order(conn: sqlite3.Connection, vehicle_id: int, mechanic_id: int, description: str) -> int:
    if not isinstance(vehicle_id, int) or vehicle_id <= 0:
        raise InvalidInputError("vehicle_id must be a positive integer.")
    if not isinstance(mechanic_id, int) or mechanic_id <= 0:
        raise InvalidInputError("mechanic_id must be a positive integer.")
    if not isinstance(description, str) or not description.strip():
        raise InvalidInputError("description must be a non-empty string.")

    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("BEGIN;")

        vehicle = conn.execute(
            "SELECT id FROM vehicles WHERE id = ?;",
            (vehicle_id,),
        ).fetchone()
        if vehicle is None:
            raise NotFoundError(f"Vehicle with id={vehicle_id} does not exist.")

        mechanic = conn.execute(
            "SELECT id, active FROM mechanics WHERE id = ?;",
            (mechanic_id,),
        ).fetchone()
        if mechanic is None:
            raise NotFoundError(f"Mechanic with id={mechanic_id} does not exist.")
        if mechanic["active"] != 1:
            raise ConflictError(f"Mechanic with id={mechanic_id} is inactive.")

        received_at = _now_iso()
        cursor = conn.execute(
            """
            INSERT INTO service_orders (
                vehicle_id, mechanic_id, received_at, completed_at, status, description
            )
            VALUES (?, ?, ?, NULL, 'received', ?);
            """,
            (vehicle_id, mechanic_id, received_at, description.strip()),
        )
        conn.execute("COMMIT;")
        return int(cursor.lastrowid)
    except Exception:
        if conn.in_transaction:
            conn.execute("ROLLBACK;")
        raise


def add_service_to_order(
    conn: sqlite3.Connection,
    order_id: int,
    service_id: int,
    hours_worked: float,
    final_price: float,
) -> None:
    if not isinstance(order_id, int) or order_id <= 0:
        raise InvalidInputError("order_id must be a positive integer.")
    if not isinstance(service_id, int) or service_id <= 0:
        raise InvalidInputError("service_id must be a positive integer.")
    if hours_worked is None or isinstance(hours_worked, bool) or hours_worked <= 0:
        raise InvalidInputError("hours_worked must be greater than 0.")
    if final_price is None or isinstance(final_price, bool) or final_price < 0:
        raise InvalidInputError("final_price must be greater than or equal to 0.")

    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("BEGIN;")

        order = conn.execute(
            "SELECT id, status FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        if order is None:
            raise NotFoundError(f"Service order with id={order_id} does not exist.")

        if order["status"] in ("completed", "cancelled"):
            raise ConflictError(f"Cannot add services to an order with status '{order['status']}'.")

        service = conn.execute(
            "SELECT id FROM services WHERE id = ?;",
            (service_id,),
        ).fetchone()
        if service is None:
            raise NotFoundError(f"Service with id={service_id} does not exist.")

        existing_line = conn.execute(
            "SELECT 1 FROM order_services WHERE order_id = ? AND service_id = ?;",
            (order_id, service_id),
        ).fetchone()
        if existing_line is not None:
            raise ConflictError(
                f"Service with id={service_id} is already added to order id={order_id}."
            )

        conn.execute(
            """
            INSERT INTO order_services (order_id, service_id, hours_worked, final_price)
            VALUES (?, ?, ?, ?);
            """,
            (order_id, service_id, float(hours_worked), float(final_price)),
        )
        conn.execute(
            "UPDATE service_orders SET status = 'in_progress' WHERE id = ?;",
            (order_id,),
        )
        conn.execute("COMMIT;")
    except Exception:
        if conn.in_transaction:
            conn.execute("ROLLBACK;")
        raise


def complete_order(conn: sqlite3.Connection, order_id: int) -> None:
    if not isinstance(order_id, int) or order_id <= 0:
        raise InvalidInputError("order_id must be a positive integer.")

    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("BEGIN;")

        order = conn.execute(
            "SELECT id, status FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        if order is None:
            raise NotFoundError(f"Service order with id={order_id} does not exist.")

        if order["status"] in ("completed", "cancelled"):
            raise ConflictError(f"Cannot complete an order with status '{order['status']}'.")

        service_count_row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM order_services WHERE order_id = ?;",
            (order_id,),
        ).fetchone()
        if int(service_count_row["cnt"]) == 0:
            raise ConflictError(f"Cannot complete order id={order_id} without any service lines.")

        completed_at = _now_iso()
        conn.execute(
            """
            UPDATE service_orders
            SET status = 'completed', completed_at = ?
            WHERE id = ?;
            """,
            (completed_at, order_id),
        )
        conn.execute("COMMIT;")
    except Exception:
        if conn.in_transaction:
            conn.execute("ROLLBACK;")
        raise


def get_order_details(conn: sqlite3.Connection, order_id: int) -> dict[str, Any]:
    if not isinstance(order_id, int) or order_id <= 0:
        raise InvalidInputError("order_id must be a positive integer.")

    conn.execute("PRAGMA foreign_keys = ON;")
    previous_row_factory = conn.row_factory
    conn.row_factory = sqlite3.Row
    try:
        order = conn.execute(
            """
            SELECT
                id,
                vehicle_id,
                mechanic_id,
                received_at,
                completed_at,
                status,
                description
            FROM service_orders
            WHERE id = ?;
            """,
            (order_id,),
        ).fetchone()
        if order is None:
            raise NotFoundError(f"Service order with id={order_id} does not exist.")

        lines = conn.execute(
            """
            SELECT
                os.service_id,
                s.name AS service_name,
                os.hours_worked,
                os.final_price
            FROM order_services AS os
            JOIN services AS s ON s.id = os.service_id
            WHERE os.order_id = ?
            ORDER BY os.service_id ASC;
            """,
            (order_id,),
        ).fetchall()

        services_list = [
            {
                "service_id": int(row["service_id"]),
                "service_name": row["service_name"],
                "hours_worked": float(row["hours_worked"]),
                "final_price": float(row["final_price"]),
            }
            for row in lines
        ]
        total_price = sum(item["final_price"] for item in services_list)

        return {
            "id": int(order["id"]),
            "vehicle_id": int(order["vehicle_id"]),
            "mechanic_id": int(order["mechanic_id"]),
            "received_at": order["received_at"],
            "completed_at": order["completed_at"],
            "status": order["status"],
            "description": order["description"],
            "services": services_list,
            "total_price": float(total_price),
        }
    finally:
        conn.row_factory = previous_row_factory