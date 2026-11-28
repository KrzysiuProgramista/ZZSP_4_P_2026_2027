from datetime import datetime, timezone
import sqlite3


class NotFoundError(LookupError):
    pass


class ConflictError(ValueError):
    pass


def get_connection(db_path: str = "workshop.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_order(conn: sqlite3.Connection, vehicle_id: int, mechanic_id: int, description: str) -> int:
    if not description or not description.strip():
        raise ValueError("Order description must not be empty.")

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

        received_at = _utc_now_iso()
        cursor = conn.execute(
            """
            INSERT INTO service_orders (
                vehicle_id, mechanic_id, received_at, completed_at, status, description
            ) VALUES (?, ?, ?, NULL, 'received', ?);
            """,
            (vehicle_id, mechanic_id, received_at, description.strip()),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception:
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
        raise ValueError("final_price must be greater than or equal to 0.")

    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("BEGIN;")

        order = conn.execute(
            "SELECT id, status FROM service_orders WHERE id = ?;",
            (order_id,),
        ).fetchone()
        if order is None:
            raise NotFoundError(f"Service order with id={order_id} does not exist.")

        service = conn.execute(
            "SELECT id FROM services WHERE id = ?;",
            (service_id,),
        ).fetchone()
        if service is None:
            raise NotFoundError(f"Service with id={service_id} does not exist.")

        if order["status"] in ("completed", "cancelled"):
            raise ConflictError(f"Cannot add services to an order with status '{order['status']}'.")

        existing_line = conn.execute(
            "SELECT 1 FROM order_services WHERE order_id = ? AND service_id = ?;",
            (order_id, service_id),
        ).fetchone()
        if existing_line is not None:
            raise ConflictError(f"Service id={service_id} is already added to order id={order_id}.")

        conn.execute(
            """
            INSERT INTO order_services (order_id, service_id, hours_worked, final_price)
            VALUES (?, ?, ?, ?);
            """,
            (order_id, service_id, hours_worked, final_price),
        )
        conn.execute(
            "UPDATE service_orders SET status = 'in_progress' WHERE id = ?;",
            (order_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def complete_order(conn: sqlite3.Connection, order_id: int) -> None:
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
            raise ConflictError(f"Order id={order_id} is already '{order['status']}'.")

        line_count = conn.execute(
            "SELECT COUNT(*) AS cnt FROM order_services WHERE order_id = ?;",
            (order_id,),
        ).fetchone()["cnt"]
        if line_count == 0:
            raise ConflictError(f"Cannot complete order id={order_id} with no service lines.")

        completed_at = _utc_now_iso()
        conn.execute(
            """
            UPDATE service_orders
            SET status = 'completed', completed_at = ?
            WHERE id = ?;
            """,
            (completed_at, order_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def get_order_details(conn: sqlite3.Connection, order_id: int) -> dict:
    conn.execute("PRAGMA foreign_keys = ON;")
    order = conn.execute(
        """
        SELECT
            id, vehicle_id, mechanic_id, received_at, completed_at, status, description
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
        FROM order_services os
        JOIN services s ON os.service_id = s.id
        WHERE os.order_id = ?
        ORDER BY os.service_id ASC;
        """,
        (order_id,),
    ).fetchall()

    services_list = [dict(row) for row in lines]
    total_price = sum(item["final_price"] for item in services_list)

    return {
        "id": order["id"],
        "vehicle_id": order["vehicle_id"],
        "mechanic_id": order["mechanic_id"],
        "received_at": order["received_at"],
        "completed_at": order["completed_at"],
        "status": order["status"],
        "description": order["description"],
        "services": services_list,
        "total_price": total_price,
    }
