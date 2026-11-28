SELECT
    so.id AS order_id,
    so.status,
    so.received_at,
    so.completed_at,
    so.description,
    c.id AS customer_id,
    c.first_name AS customer_first_name,
    c.last_name AS customer_last_name,
    c.phone AS customer_phone,
    c.email AS customer_email,
    v.id AS vehicle_id,
    v.brand,
    v.model,
    v.year,
    v.registration_no,
    v.vin,
    m.id AS mechanic_id,
    m.first_name AS mechanic_first_name,
    m.last_name AS mechanic_last_name,
    m.specialization
FROM service_orders so
JOIN vehicles v ON so.vehicle_id = v.id
JOIN customers c ON v.customer_id = c.id
JOIN mechanics m ON so.mechanic_id = m.id
WHERE so.status IN ('received', 'in_progress')
ORDER BY so.received_at ASC, so.id ASC;

SELECT
    m.id,
    m.first_name,
    m.last_name,
    m.specialization,
    m.active,
    COUNT(so.id) AS order_count
FROM mechanics m
LEFT JOIN service_orders so ON m.id = so.mechanic_id
GROUP BY m.id, m.first_name, m.last_name, m.specialization, m.active
ORDER BY order_count DESC, m.id ASC;

SELECT
    v.id,
    v.customer_id,
    v.brand,
    v.model,
    v.year,
    v.registration_no,
    v.vin
FROM vehicles v
LEFT JOIN service_orders so ON v.id = so.vehicle_id
WHERE so.id IS NULL
ORDER BY v.id ASC;

SELECT
    so.id AS order_id,
    so.status,
    COALESCE(SUM(os.final_price), 0) AS total_value
FROM service_orders so
LEFT JOIN order_services os ON so.id = os.order_id
GROUP BY so.id, so.status
ORDER BY so.id ASC;

SELECT
    s.id,
    s.name,
    s.base_price,
    COUNT(os.order_id) AS orders_count
FROM services s
JOIN order_services os ON s.id = os.service_id
GROUP BY s.id, s.name, s.base_price
ORDER BY orders_count DESC, s.id ASC
LIMIT 3;

SELECT
    strftime('%Y-%m', so.completed_at) AS completion_month,
    COALESCE(SUM(os.final_price), 0) AS revenue
FROM service_orders so
LEFT JOIN order_services os ON so.id = os.order_id
WHERE so.status = 'completed'
  AND so.completed_at IS NOT NULL
GROUP BY strftime('%Y-%m', so.completed_at)
ORDER BY completion_month ASC;

SELECT
    c.id,
    c.first_name,
    c.last_name,
    c.phone,
    c.email,
    COUNT(so.id) AS orders_last_12_months
FROM customers c
JOIN vehicles v ON c.id = v.customer_id
JOIN service_orders so ON v.id = so.vehicle_id
WHERE so.status != 'cancelled'
  AND datetime(so.received_at) >= datetime('now', '-12 months')
GROUP BY c.id, c.first_name, c.last_name, c.phone, c.email
HAVING COUNT(so.id) > 2
ORDER BY orders_last_12_months DESC, c.id ASC;
