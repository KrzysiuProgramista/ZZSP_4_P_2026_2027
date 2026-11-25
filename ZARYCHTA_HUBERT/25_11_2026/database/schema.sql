PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    id INTEGER NOT NULL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT
);
CREATE TABLE vehicles (
    id INTEGER NOT NULL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1886 AND 2100),
    registration_no TEXT NOT NULL UNIQUE,
    vin TEXT NOT NULL UNIQUE,
    CONSTRAINT owned_by_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);
CREATE TABLE mechanics (
    id INTEGER NOT NULL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0,1))
);
CREATE TABLE services (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    base_price REAL NOT NULL CHECK (base_price >= 0)
);
CREATE TABLE service_orders (
    id INTEGER NOT NULL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    mechanic_id INTEGER NOT NULL REFERENCES mechanics(id) ON DELETE RESTRICT,
    received_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('received','in_progress','completed','cancelled')),
    description TEXT NOT NULL
);
CREATE TABLE order_services (
    order_id INTEGER NOT NULL REFERENCES service_orders(id) ON DELETE RESTRICT,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    hours_worked REAL NOT NULL CHECK (hours_worked > 0),
    final_price REAL NOT NULL CHECK (final_price >= 0),
    CONSTRAINT one_service_per_order PRIMARY KEY (order_id,service_id)
);
-- Helps list recent orders by receipt time.
CREATE INDEX service_orders_received_idx ON service_orders(received_at);
-- Helps find a mechanic's orders without scanning every order.
CREATE INDEX service_orders_mechanic_idx ON service_orders(mechanic_id);
-- Helps rank services by their number of associated orders.
CREATE INDEX order_services_service_idx ON order_services(service_id);
