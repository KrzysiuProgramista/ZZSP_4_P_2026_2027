import sqlite3
from typing import Any


class NotFoundError(LookupError):
    """Raised when a referenced database record does not exist."""


class ConflictError(ValueError):
    """Raised when an operation conflicts with the current business state."""


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_order(
    conn: sqlite3.Connection,
    vehicle_id: int,
    mechanic_id: int,
    description: str,
) -> int:
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Order description must be a non-empty string.")

    cleaned_description = description.strip()

    started_tx = False
    if not conn.in_transaction:
        conn.execute("BEGIN")
        started_tx = True

    try:
        vehicle_row = conn.execute(
            "SELECT id FROM vehicles WHERE id = ?;",
            (vehicle_id,),
        ).fetchone()
        if vehicle_row is None:
            raise NotFoundError(f"Vehicle with id={vehicle_id} does not exist.")

        mechanic_row = conn.execute(
            "SELECT active FROM mechanics WHERE id = ?;",
            (mechanic_id,),
        ).fetchone()
        if mechanic_row is None:
            raise NotFoundError(f"Mechanic with id={mechanic_id} does not exist.")
        if mechanic_row[0] != 1:
            raise ConflictError(f"Mechanic with id={mechanic_id} is inactive.")

        cursor = conn.execute(
            """
            INSERT INTO service_orders (
                vehicle_id,
                mechanic_id,
                received_at,
                completed_at,
                status,
                description
            )
            VALUES (?, ?, datetime('now'), NULL, 'received', ?);
            """,
            (vehicle_id, mechanic_id, cleaned_description),
        )
        order_id = cursor.lastrowid
        if order_id is None:
            raise RuntimeError("Failed to retrieve created service order ID.")

        if started_tx:
            conn.commit()
        return int(order_id)
    except Exception:
        if started_tx and conn.in_transaction:
            conn.rollback()
        raise


def add_service_to_order(
    conn: sqlite3.Connection,
    order_id: int,
    service_id: int,
    hours_worked: float,
    final_price: float,
) -> None:
    if hours_worked <= 0:
        raise ValueError("hours_worked must be greater than 0.")
    if final_price < 0:
        raise ValueError("final_price must not be negative.")

    started_tx = False
    if not conn.in_transaction:
        conn.execute("BEGIN")
        started_tx = True

    try:
        order_row = conn.execute(
            "SELECT status FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        if order_row is None:
            raise NotFoundError(f"Service order with id={order_id} does not exist.")

        order_status = order_row[0]
        if order_status in ("completed", "cancelled"):
            raise ConflictError(
                f"Cannot add services to order id={order_id} with status '{order_status}'."
            )

        service_row = conn.execute(
            "SELECT id FROM services WHERE id = ?;",
            (service_id,),
        ).fetchone()
        if service_row is None:
            raise NotFoundError(f"Service with id={service_id} does not exist.")

        existing_line = conn.execute(
            "SELECT 1 FROM order_services WHERE order_id = ? AND service_id = ?;",
            (order_id, service_id),
        ).fetchone()
        if existing_line is not None:
            raise ConflictError(
                f"Service id={service_id} is already assigned to order id={order_id}."
            )

        conn.execute(
            """
            INSERT INTO order_services (order_id, service_id, hours_worked, final_price)
            VALUES (?, ?, ?, ?);
            """,
            (order_id, service_id, float(hours_worked), float(final_price)),
        )

        conn.execute(
            """
            UPDATE service_orders
            SET status = 'in_progress'
            WHERE id = ?;
            """,
            (order_id,),
        )

        if started_tx:
            conn.commit()
    except Exception:
        if started_tx and conn.in_transaction:
            conn.rollback()
        raise


def complete_order(conn: sqlite3.Connection, order_id: int) -> None:
    started_tx = False
    if not conn.in_transaction:
        conn.execute("BEGIN")
        started_tx = True

    try:
        order_row = conn.execute(
            "SELECT status FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        if order_row is None:
            raise NotFoundError(f"Service order with id={order_id} does not exist.")

        order_status = order_row[0]
        if order_status in ("completed", "cancelled"):
            raise ConflictError(
                f"Order id={order_id} is already '{order_status}' and cannot be completed."
            )

        line_count_row = conn.execute(
            "SELECT COUNT(*) FROM order_services WHERE order_id = ?;",
            (order_id,),
        ).fetchone()
        line_count = line_count_row[0] if line_count_row is not None else 0
        if line_count == 0:
            raise ConflictError(
                f"Order id={order_id} has no service lines and cannot be completed."
            )

        conn.execute(
            """
            UPDATE service_orders
            SET status = 'completed',
                completed_at = datetime('now')
            WHERE id = ?;
            """,
            (order_id,),
        )

        if started_tx:
            conn.commit()
    except Exception:
        if started_tx and conn.in_transaction:
            conn.rollback()
        raise


def get_order_details(conn: sqlite3.Connection, order_id: int) -> dict[str, Any]:
    order_row = conn.execute(
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

    if order_row is None:
        raise NotFoundError(f"Service order with id={order_id} does not exist.")

    service_rows = conn.execute(
        """
        SELECT
            os.service_id,
            s.name,
            os.hours_worked,
            os.final_price
        FROM order_services os
        JOIN services s ON s.id = os.service_id
        WHERE os.order_id = ?
        ORDER BY os.service_id ASC;
        """,
        (order_id,),
    ).fetchall()

    services = [
        {
            "service_id": row[0],
            "service_name": row[1],
            "hours_worked": row[2],
            "final_price": row[3],
        }
        for row in service_rows
    ]

    total_price = round(sum(item["final_price"] for item in services), 2)

    return {
        "id": order_row[0],
        "vehicle_id": order_row[1],
        "mechanic_id": order_row[2],
        "received_at": order_row[3],
        "completed_at": order_row[4],
        "status": order_row[5],
        "description": order_row[6],
        "total_price": total_price,
        "services": services,
    }