PRAGMA foreign_keys = ON;

CREATE TABLE customers (
 id INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL,
 phone TEXT NOT NULL, email TEXT
);
CREATE TABLE vehicles (
 id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id),
 brand TEXT NOT NULL, model TEXT NOT NULL,
 year INTEGER NOT NULL CHECK (year BETWEEN 1886 AND 2100),
 registration_no TEXT NOT NULL UNIQUE, vin TEXT NOT NULL UNIQUE
);
CREATE TABLE mechanics (
 id INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL,
 specialization TEXT NOT NULL, active INTEGER NOT NULL CHECK (active IN (0, 1))
);
CREATE TABLE service_orders (
 id INTEGER PRIMARY KEY, vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
 mechanic_id INTEGER NOT NULL REFERENCES mechanics(id),
 received_at TEXT NOT NULL, completed_at TEXT,
 status TEXT NOT NULL CHECK (status IN ('received','in_progress','completed','cancelled')),
 description TEXT NOT NULL
);
CREATE TABLE services (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE,
 base_price REAL NOT NULL CHECK (base_price >= 0)
);
CREATE TABLE order_services (
 order_id INTEGER NOT NULL REFERENCES service_orders(id),
 service_id INTEGER NOT NULL REFERENCES services(id),
 hours_worked REAL NOT NULL CHECK (hours_worked > 0),
 final_price REAL NOT NULL CHECK (final_price >= 0),
 PRIMARY KEY (order_id, service_id)
);
-- Speeds up looking up all orders for a vehicle and customer order history.
CREATE INDEX idx_orders_vehicle ON service_orders(vehicle_id);
-- Speeds up monthly revenue filtering by status and completion date.
CREATE INDEX idx_orders_status_completed ON service_orders(status, completed_at);
-- Speeds up order counts for every mechanic.
CREATE INDEX idx_orders_mechanic ON service_orders(mechanic_id);
-- Speeds up counting how often a particular service was performed.
CREATE INDEX idx_order_services_service ON order_services(service_id);
