-- Automotive Service Management System
-- Sample data for the student assessment.
-- Run schema.sql first, then execute this file once.
-- Dates are fixed around 2026-11-25 so that the "last 12 months" task
-- has predictable results during the assessment.

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- -----------------------------------------------------------------------------
-- CUSTOMERS
-- -----------------------------------------------------------------------------
INSERT INTO customers (id, first_name, last_name, phone, email) VALUES
    (1, 'Krzysztof', 'Nowicki',   '+48 501 100 101', 'krzysztof.nowicki@example.com'),
    (2, 'Anna',      'Kowalska',  '+48 501 100 102', 'anna.kowalska@example.com'),
    (3, 'Piotr',     'Zieliński', '+48 501 100 103', 'piotr.zielinski@example.com'),
    (4, 'Marta',     'Wiśniewska','+48 501 100 104', 'marta.wisniewska@example.com'),
    (5, 'Tomasz',    'Wójcik',    '+48 501 100 105', 'tomasz.wojcik@example.com'),
    (6, 'Joanna',    'Kamińska',  '+48 501 100 106', 'joanna.kaminska@example.com'),
    (7, 'Michał',    'Lewandowski','+48 501 100 107', 'michal.lewandowski@example.com'),
    (8, 'Ewa',       'Dąbrowska', '+48 501 100 108', 'ewa.dabrowska@example.com');

-- -----------------------------------------------------------------------------
-- VEHICLES
-- Vehicle 12 intentionally has no service order (never serviced).
-- -----------------------------------------------------------------------------
INSERT INTO vehicles (id, customer_id, brand, model, year, registration_no, vin) VALUES
    (1,  1, 'BMW',       '330i',       2018, 'EL 1001A', 'WBA8B9C50JAE10001'),
    (2,  1, 'Audi',      'A4',         2017, 'EL 1002A', 'WAUZZZF40HN100002'),
    (3,  2, 'Toyota',    'Corolla',    2020, 'EL 2001A', 'JTDEPRAE0LJ100003'),
    (4,  3, 'Porsche',   'Cayman',     2016, 'EL 3001A', 'WP0AA2A80GK100004'),
    (5,  4, 'Fiat',      'Tipo',       2019, 'EL 4001A', 'ZFA35600006A10005'),
    (6,  5, 'Škoda',     'Octavia',    2015, 'EL 5001A', 'TMBJG7NE5F0100006'),
    (7,  6, 'Volkswagen','Golf',       2014, 'EL 6001A', 'WVWZZZAUZEP100007'),
    (8,  7, 'Ford',      'Focus',      2018, 'EL 7001A', 'WF0KXXGCBKJ100008'),
    (9,  8, 'Honda',     'Civic',      2019, 'EL 8001A', 'SHHFK7760KU100009'),
    (10, 2, 'Renault',   'Clio',       2021, 'EL 2002A', 'VF1RJA006ML100010'),
    (11, 3, 'Mazda',     '6',          2017, 'EL 3002A', 'JMZGL123001100011'),
    (12, 4, 'Mercedes-Benz', 'C 200',  2022, 'EL 4002A', 'W1KWF8EB2NR100012');

-- -----------------------------------------------------------------------------
-- MECHANICS
-- Mechanic 4 has no orders; mechanic 5 is inactive and has no orders.
-- -----------------------------------------------------------------------------
INSERT INTO mechanics (id, first_name, last_name, specialization, active) VALUES
    (1, 'Adam',   'Mazur',      'General mechanics', 1),
    (2, 'Paweł',  'Kaczmarek',  'Diagnostics',       1),
    (3, 'Marek',  'Szymański',  'Brakes and tyres',  1),
    (4, 'Julia',  'Woźniak',    'Car electronics',  1),
    (5, 'Robert', 'Król',       'Engine repairs',    0);

-- -----------------------------------------------------------------------------
-- SERVICES
-- -----------------------------------------------------------------------------
INSERT INTO services (id, name, base_price) VALUES
    (1,  'Engine oil and filter change',  280.00),
    (2,  'Brake pads replacement',        620.00),
    (3,  'Computer diagnostics',           160.00),
    (4,  'Seasonal tyre change',           180.00),
    (5,  'Timing belt replacement',       1350.00),
    (6,  'Air conditioning service',       240.00),
    (7,  'Clutch replacement',            1750.00),
    (8,  'Battery replacement',            420.00),
    (9,  'Suspension repair',              850.00),
    (10, 'Vehicle inspection',              220.00);

-- -----------------------------------------------------------------------------
-- SERVICE ORDERS
-- Status values used in this dataset: open, in_progress, completed, cancelled.
-- completed_at is NULL for open, in-progress and cancelled orders.
-- -----------------------------------------------------------------------------
INSERT INTO service_orders
    (id, vehicle_id, mechanic_id, received_at, completed_at, status, description)
VALUES
    (1,  1,  1, '2026-11-03 08:30:00', '2026-11-03 11:45:00', 'completed',   'Routine service and warning light check'),
    (2,  2,  2, '2026-10-15 09:00:00', '2026-10-15 14:20:00', 'completed',   'Front brake pads worn'),
    (3,  1,  3, '2026-08-20 08:00:00', '2026-08-20 10:00:00', 'completed',   'Seasonal tyre change'),
    (4,  3,  1, '2026-11-10 07:45:00', '2026-11-10 10:30:00', 'completed',   'Oil service and general inspection'),
    (5, 10,  2, '2026-10-22 10:15:00', NULL,                  'in_progress', 'Intermittent engine warning light'),
    (6,  3,  3, '2026-06-11 08:15:00', '2026-06-12 13:00:00', 'completed',   'Timing belt replacement'),
    (7,  4,  1, '2026-09-07 09:30:00', '2026-09-07 12:00:00', 'completed',   'Air conditioning not cooling'),
    (8, 11,  2, '2026-07-19 08:00:00', '2026-07-20 15:30:00', 'completed',   'Noise from front suspension'),
    (9,  4,  3, '2026-05-13 10:00:00', '2026-05-13 13:15:00', 'completed',   'Brake pads replacement'),
    (10, 5,  1, '2026-04-12 08:30:00', '2026-04-12 10:00:00', 'completed',   'Pre-trip vehicle inspection'),
    (11, 6,  3, '2026-03-08 09:00:00', '2026-03-08 11:00:00', 'completed',   'Battery no longer holds charge'),
    (12, 7,  1, '2026-03-16 08:00:00', NULL,                  'cancelled',  'Customer cancelled the appointment'),
    (13, 8,  2, '2026-02-17 07:30:00', '2026-02-18 16:00:00', 'completed',   'Clutch slipping'),
    (14, 9,  3, '2026-01-25 09:15:00', '2026-01-25 11:00:00', 'completed',   'Routine oil service'),
    (15, 5,  1, '2026-11-18 08:45:00', NULL,                  'in_progress', 'Air conditioning inspection'),
    (16, 6,  2, '2025-12-05 08:00:00', '2025-12-05 10:00:00', 'completed',   'Seasonal tyre change'),
    (17, 7,  1, '2025-11-30 09:00:00', '2025-11-30 12:00:00', 'completed',   'Brake pads replacement'),
    (18, 8,  2, '2026-10-01 09:00:00', NULL,                  'cancelled',  'Customer could not attend'),
    (19, 9,  3, '2025-11-15 08:30:00', '2025-11-15 10:15:00', 'completed',   'Engine warning light diagnostics'),
    (20,10,  1, '2026-09-29 08:00:00', '2026-09-29 11:30:00', 'completed',   'Routine inspection and oil service');

-- -----------------------------------------------------------------------------
-- SERVICES ASSIGNED TO ORDERS
-- The same service can appear on many orders; an order can contain many services.
-- Orders 12 and 18 are cancelled and intentionally have no service rows.
-- -----------------------------------------------------------------------------
INSERT INTO order_services (order_id, service_id, hours_worked, final_price) VALUES
    (1,  1, 1.2,  310.00),
    (1,  3, 0.8,  150.00),
    (2,  2, 2.5,  690.00),
    (3,  4, 1.5,  180.00),
    (4,  1, 1.1,  300.00),
    (4, 10, 1.0,  220.00),
    (5,  3, 1.0,  180.00),
    (6,  5, 7.0, 1450.00),
    (6,  1, 1.0,  290.00),
    (7,  6, 1.5,  260.00),
    (8,  9, 5.0,  920.00),
    (9,  2, 2.3,  650.00),
    (10, 10, 1.0,  220.00),
    (11,  8, 1.2,  450.00),
    (13,  7, 6.5, 1850.00),
    (14,  1, 1.1,  330.00),
    (15,  6, 1.3,  250.00),
    (16,  4, 1.4,  160.00),
    (17,  2, 2.2,  620.00),
    (19,  3, 0.9,  140.00),
    (20, 10, 1.0,  230.00),
    (20,  1, 1.1,  320.00);

COMMIT;

-- Quick sanity checks (run separately if you want to inspect the loaded data):
-- SELECT COUNT(*) AS customers_count FROM customers;       -- 8
-- SELECT COUNT(*) AS vehicles_count FROM vehicles;         -- 12
-- SELECT COUNT(*) AS mechanics_count FROM mechanics;       -- 5
-- SELECT COUNT(*) AS service_orders_count FROM service_orders; -- 20
-- SELECT COUNT(*) AS services_count FROM services;         -- 10
-- SELECT COUNT(*) AS order_services_count FROM order_services; -- 22
