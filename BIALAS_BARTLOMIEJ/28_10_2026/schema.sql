-- SQLite schema for a small online store.
-- Enable foreign-key enforcement on every connection that uses this schema.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    email       TEXT NOT NULL COLLATE NOCASE UNIQUE,
    full_name   TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id   INTEGER PRIMARY KEY,
    category_id  INTEGER,
    product_code TEXT NOT NULL UNIQUE,
    name         TEXT NOT NULL,
    price        NUMERIC NOT NULL CHECK (price > 0),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'paid', 'shipped', 'completed', 'cancelled')),
    ordered_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC NOT NULL CHECK (unit_price > 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Supports customer order-history lookups and the orders -> customer FK.
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);

-- Supports finding line items for a product and checks product FK references.
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

-- Supports filtering orders by status and newest-first order lists.
CREATE INDEX IF NOT EXISTS idx_orders_status_ordered_at
    ON orders(status, ordered_at DESC);
