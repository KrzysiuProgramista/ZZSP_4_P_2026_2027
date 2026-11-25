PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT
);

CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1886 AND 2100),
    registration_no TEXT NOT NULL UNIQUE,
    vin TEXT NOT NULL UNIQUE
);

CREATE TABLE mechanics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0, 1))
);

CREATE TABLE service_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    mechanic_id INTEGER NOT NULL REFERENCES mechanics(id) ON DELETE RESTRICT,
    received_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('received', 'in_progress', 'completed', 'cancelled')),
    description TEXT NOT NULL
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    base_price REAL NOT NULL CHECK (base_price >= 0)
);

CREATE TABLE order_services (
    order_id INTEGER NOT NULL REFERENCES service_orders(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    hours_worked REAL NOT NULL CHECK (hours_worked > 0),
    final_price REAL NOT NULL CHECK (final_price >= 0),
    PRIMARY KEY (order_id, service_id)
);

CREATE INDEX idx_service_orders_status_vehicle ON service_orders(status, vehicle_id);

CREATE INDEX idx_vehicles_customer_id ON vehicles(customer_id);