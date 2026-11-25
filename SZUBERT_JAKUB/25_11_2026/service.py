from datetime import datetime, timezone
import sqlite3
from typing import Any

class ConflictError(ValueError):
	""" Error in bizness status (e.g. order closed, mechanic is not active, etc.)"""

def init_db(conn: sqlite3.Connection, schema_path: str = "database/schema.sql") -> None:
	conn.execute("PRAGMA foreign_keys = ON;")
	with open(schema_path, "r", encoding="utf-8") as f:
		conn.executescript(f.read())


def get_datetime() -> str:
	return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def create_order(
		conn: sqlite3.Connection,
		vehicle_id: int,
		mechanic_id: int,
		description: str,
	) -> int:
		if not description or not description.strip():
			raise ValueError("Description of the order cannot be empty")
		conn.execute("PRAGMA foreign_keys = ON;")
		received_at = get_datetime()

		try:
			 with conn:
					vehicle = conn.execute(
						"SELECT id FROM vehicles WHERE id = ?;",
						(vehicle_id,),
						).fetchone()

					if vehicle is None:
						raise LookupError(f"Vechicle with id: '{vehicle_id}' doesn't exist")

					mechanic = conn.execute(
						 "SELECT id, active FROM mechanics WHERE id = ?;",
						 (mechanic_id,),
					).fetchone()

					if mechanic is None:
						raise LookupError(f"Mechanic with id: '{mechanic_id}' doesn't exist")
					if int(mechanic["active"]) != 1:
						raise ConflictError(f"Mechanic with id: '{vehicle_id}' is not active")

					cur = conn.execute(
						"""
						INSERT INTO service_orders (
							vehicle_id, mechanic_id, received_at, completed_at, status, description
						)
						VALUES (?, ?, ?, NULL, 'received', ?);
						""",
						(vehicle_id, mechanic_id, received_at, description.strip()),
					)

					return int(cur.lastrowid)
		except sqlite3.IntegrityError as exc:
			raise ValueError(f"Integrity error of database: {exc}") from exc

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
        raise ValueError("final_price cannot be negative number.")

    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        with conn:
            order = conn.execute(
                "SELECT id, status FROM service_orders WHERE id = ?;",
                (order_id,),
            ).fetchone()
            if order is None:
                raise LookupError(f"Order with id: '{order_id}' doesn't exist.")

            if order["status"] in ("completed", "cancelled"):
                raise ConflictError(
                    f"Cannot add service with status: '{order['status']}'."
                )

            service = conn.execute(
                "SELECT id FROM services WHERE id = ?;",
                (service_id,),
            ).fetchone()
            if service is None:
                raise LookupError(f"Service with id: '{service_id}' doesn't exist.")

            duplicate = conn.execute(
                "SELECT 1 FROM order_services WHERE order_id = ? AND service_id = ?;",
                (order_id, service_id),
            ).fetchone()
            if duplicate is not None:
                raise ConflictError(
                    f"Service with id: '{service_id}' is already assigned to order with id: '{order_id}'."
                )

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
    except sqlite3.IntegrityError as exc:
        raise ConflictError(f"Integrity error of data: {exc}") from exc

def complete_order(conn: sqlite3.Connection, order_id: int) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")
    completed_at = get_datetime()

    try:
        with conn:
            order = conn.execute(
                "SELECT id, status FROM service_orders WHERE id = ?;",
                (order_id,),
            ).fetchone()
            if order is None:
                raise LookupError(f"Order with id: '{order_id}' doesn't exist.")

            if order["status"] in ("completed", "cancelled"):
                raise ConflictError(
                    f"Order with id: '{order_id}' has already '{order['status']}' status."
                )

            lines_count = conn.execute(
                "SELECT COUNT(*) AS cnt FROM order_services WHERE order_id = ?;",
                (order_id,),
            ).fetchone()["cnt"]
            if int(lines_count) == 0:
                raise ConflictError(
                    f"Order with id:'{order_id}' doesn't have any services and cannot be done."
                )

            conn.execute(
                """
                UPDATE service_orders
                SET status = 'completed', completed_at = ?
                WHERE id = ?;
                """,
                (completed_at, order_id),
            )
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"Order clsoing error: {exc}") from exc


def get_order_details(conn: sqlite3.Connection, order_id: int) -> dict[str, Any]:
    conn.execute("PRAGMA foreign_keys = ON;")

    order = conn.execute(
        """
        SELECT
            so.id,
            so.vehicle_id,
            so.mechanic_id,
            so.received_at,
            so.completed_at,
            so.status,
            so.description,
            v.brand AS vehicle_brand,
            v.model AS vehicle_model,
            v.registration_no,
            c.first_name || ' ' || c.last_name AS customer_name,
            m.first_name || ' ' || m.last_name AS mechanic_name
        FROM service_orders AS so
        JOIN vehicles AS v ON v.id = so.vehicle_id
        JOIN customers AS c ON c.id = v.customer_id
        JOIN mechanics AS m ON m.id = so.mechanic_id
        WHERE so.id = ?;
        """,
        (order_id,),
    ).fetchone()

    if order is None:
        raise LookupError(f"Order with id: '{order_id}' doesn't exist.")

    rows = conn.execute(
        """
        SELECT
            os.service_id,
            s.name AS service_name,
            os.hours_worked,
            os.final_price
        FROM order_services AS os
        JOIN services AS s ON s.id = os.service_id
        WHERE os.order_id = ?
        ORDER BY s.id ASC;
        """,
        (order_id,),
    ).fetchall()

    services_list = [
        {
            "service_id": int(r["service_id"]),
            "service_name": r["service_name"],
            "hours_worked": float(r["hours_worked"]),
            "final_price": float(r["final_price"]),
        }
        for r in rows
    ]

    return {
        "id": int(order["id"]),
        "vehicle_id": int(order["vehicle_id"]),
        "mechanic_id": int(order["mechanic_id"]),
        "customer_name": order["customer_name"],
        "mechanic_name": order["mechanic_name"],
        "vehicle_brand": order["vehicle_brand"],
        "vehicle_model": order["vehicle_model"],
        "registration_no": order["registration_no"],
        "received_at": order["received_at"],
        "completed_at": order["completed_at"],
        "status": order["status"],
        "description": order["description"],
        "services": services_list,
        "total_price": sum(item["final_price"] for item in services_list),
    }