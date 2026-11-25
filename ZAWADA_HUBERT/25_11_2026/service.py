from datetime import datetime, timezone
import math
import sqlite3


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open a SQLite connection with Row factory and foreign-key enforcement enabled."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str, schema_path: str = "database/schema.sql") -> None:
    """Initialize database tables from schema.sql if not already present."""
    schema_sql = Path(schema_path).read_text(encoding="utf-8")
    conn = get_connection(db_path)
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


def get_order(conn: sqlite3.Connection, order_id: int) -> dict:
    """
    Fetch full details of one service order, including its service lines and total price.

    Raises:
        LookupError: If the service order does not exist.
    """
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
        WHERE id = ?
        """,
        (order_id,),
    ).fetchone()
    if order_row is None:
        raise LookupError(f"Service order with id {order_id} not found.")

    service_rows = conn.execute(
        """
        SELECT
            os.service_id,
            s.name,
            os.hours_worked,
            os.final_price
        FROM order_services AS os
        JOIN services AS s ON os.service_id = s.id
        WHERE os.order_id = ?
        ORDER BY os.service_id ASC
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
    total_price = sum(item["final_price"] for item in services)

    return {
        "id": order_row[0],
        "vehicle_id": order_row[1],
        "mechanic_id": order_row[2],
        "received_at": order_row[3],
        "completed_at": order_row[4],
        "status": order_row[5],
        "description": order_row[6],
        "services": services,
        "total_price": total_price,
    }


def _current_timestamp() -> str:
    """Return the current UTC timestamp in ISO-8601 format compatible with SQLite datetime()."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _validate_positive_number(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number.")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field_name} must be greater than 0.")
    return float(value)


def _validate_non_negative_number(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number.")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{field_name} must be greater than or equal to 0.")
    return float(value)


def create_order(
    conn: sqlite3.Connection,
    vehicle_id: int,
    mechanic_id: int,
    description: str,
) -> int:
    """
    Create a new service order with status 'received' and return its ID.

    Raises:
        LookupError: If the vehicle or mechanic does not exist.
        ValueError: If the mechanic is inactive or the description is empty.
    """
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Order description must be a non-empty string.")

    try:
        vehicle_row = conn.execute(
            "SELECT id FROM vehicles WHERE id = ?",
            (vehicle_id,),
        ).fetchone()
        if vehicle_row is None:
            raise LookupError(f"Vehicle with id {vehicle_id} not found.")

        mechanic_row = conn.execute(
            "SELECT active FROM mechanics WHERE id = ?",
            (mechanic_id,),
        ).fetchone()
        if mechanic_row is None:
            raise LookupError(f"Mechanic with id {mechanic_id} not found.")
        if mechanic_row[0] != 1:
            raise ValueError(f"Mechanic with id {mechanic_id} is not active.")

        received_at = _current_timestamp()
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
            VALUES (?, ?, ?, NULL, 'received', ?)
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
    """
    Add a service line to an existing order and set the order status to 'in_progress'.

    Raises:
        LookupError: If the order or service does not exist.
        ValueError: If the order is completed/cancelled, inputs are invalid,
                    or the service is already assigned to the order.
    """
    hours = _validate_positive_number(hours_worked, "hours_worked")
    price = _validate_non_negative_number(final_price, "final_price")

    try:
        order_row = conn.execute(
            "SELECT status FROM service_orders WHERE id = ?",
            (order_id,),
        ).fetchone()
        if order_row is None:
            raise LookupError(f"Service order with id {order_id} not found.")

        status = order_row[0]
        if status in ("completed", "cancelled"):
            raise ValueError(
                f"Cannot add services to order {order_id} with status '{status}'."
            )

        service_row = conn.execute(
            "SELECT id FROM services WHERE id = ?",
            (service_id,),
        ).fetchone()
        if service_row is None:
            raise LookupError(f"Service with id {service_id} not found.")

        existing_line = conn.execute(
            """
            SELECT 1
            FROM order_services
            WHERE order_id = ? AND service_id = ?
            """,
            (order_id, service_id),
        ).fetchone()
        if existing_line is not None:
            raise ValueError(
                f"Service {service_id} is already added to order {order_id}."
            )

        conn.execute(
            """
            INSERT INTO order_services (order_id, service_id, hours_worked, final_price)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, service_id, hours, price),
        )
        conn.execute(
            """
            UPDATE service_orders
            SET status = 'in_progress'
            WHERE id = ?
            """,
            (order_id,),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def complete_order(conn: sqlite3.Connection, order_id: int) -> None:
    """
    Mark an order as 'completed' and set completed_at to the current timestamp.

    Raises:
        LookupError: If the order does not exist.
        ValueError: If the order is already completed/cancelled or has no service lines.
    """
    try:
        order_row = conn.execute(
            "SELECT status FROM service_orders WHERE id = ?",
            (order_id,),
        ).fetchone()
        if order_row is None:
            raise LookupError(f"Service order with id {order_id} not found.")

        status = order_row[0]
        if status in ("completed", "cancelled"):
            raise ValueError(
                f"Order {order_id} cannot be completed because its status is '{status}'."
            )

        line_count_row = conn.execute(
            "SELECT COUNT(*) FROM order_services WHERE order_id = ?",
            (order_id,),
        ).fetchone()
        if line_count_row[0] == 0:
            raise ValueError(
                f"Order {order_id} cannot be completed without any service lines."
            )

        completed_at = _current_timestamp()
        conn.execute(
            """
            UPDATE service_orders
            SET status = 'completed',
                completed_at = ?
            WHERE id = ?
            """,
            (completed_at, order_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise