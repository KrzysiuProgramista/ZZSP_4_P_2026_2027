PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT    NOT NULL,
    last_name  TEXT    NOT NULL,
    phone      TEXT    NOT NULL,
    email      TEXT
);

CREATE TABLE vehicles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     INTEGER NOT NULL,
    brand           TEXT    NOT NULL,
    model           TEXT    NOT NULL,
    year            INTEGER NOT NULL CHECK (year BETWEEN 1886 AND 2100),
    registration_no TEXT    NOT NULL UNIQUE,
    vin             TEXT    NOT NULL UNIQUE,
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

CREATE TABLE mechanics (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name     TEXT    NOT NULL,
    last_name      TEXT    NOT NULL,
    specialization TEXT    NOT NULL,
    active         INTEGER NOT NULL CHECK (active IN (0, 1))
);

CREATE TABLE services (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    base_price REAL    NOT NULL CHECK (base_price >= 0)
);

CREATE TABLE service_orders (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id   INTEGER NOT NULL,
    mechanic_id  INTEGER NOT NULL,
    received_at  TEXT    NOT NULL,
    completed_at TEXT,
    status       TEXT    NOT NULL CHECK (status IN ('received', 'in_progress', 'completed', 'cancelled')),
    description  TEXT    NOT NULL,
    FOREIGN KEY (vehicle_id)  REFERENCES vehicles (id),
    FOREIGN KEY (mechanic_id) REFERENCES mechanics (id)
);

CREATE TABLE order_services (
    order_id     INTEGER NOT NULL,
    service_id   INTEGER NOT NULL,
    hours_worked REAL    NOT NULL CHECK (hours_worked > 0),
    final_price  REAL    NOT NULL CHECK (final_price >= 0),
    PRIMARY KEY (order_id, service_id),
    FOREIGN KEY (order_id)   REFERENCES service_orders (id),
    FOREIGN KEY (service_id) REFERENCES services (id)
);


CREATE INDEX idx_service_orders_status_received_at
    ON service_orders (status, received_at);


CREATE INDEX idx_service_orders_vehicle_id
    ON service_orders (vehicle_id);

CREATE INDEX idx_service_orders_mechanic_id
    ON service_orders (mechanic_id);

CREATE INDEX idx_vehicles_customer_id
    ON vehicles (customer_id);