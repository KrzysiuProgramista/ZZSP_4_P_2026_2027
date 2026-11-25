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
    m.specialization,
    m.active AS mechanic_active
FROM service_orders AS so
JOIN vehicles AS v ON so.vehicle_id = v.id
JOIN customers AS c ON v.customer_id = c.id
JOIN mechanics AS m ON so.mechanic_id = m.id
WHERE so.status IN ('received', 'in_progress')
ORDER BY so.received_at ASC, so.id ASC;



SELECT
    m.id AS mechanic_id,
    m.first_name,
    m.last_name,
    m.specialization,
    m.active,
    COUNT(so.id) AS order_count
FROM mechanics AS m
LEFT JOIN service_orders AS so ON m.id = so.mechanic_id
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
FROM vehicles AS v
LEFT JOIN service_orders AS so ON v.id = so.vehicle_id
WHERE so.id IS NULL
ORDER BY v.id ASC;



SELECT
    so.id AS order_id,
    so.vehicle_id,
    so.mechanic_id,
    so.received_at,
    so.completed_at,
    so.status,
    so.description,
    COALESCE(SUM(os.final_price), 0) AS total_value
FROM service_orders AS so
LEFT JOIN order_services AS os ON so.id = os.order_id
GROUP BY
    so.id,
    so.vehicle_id,
    so.mechanic_id,
    so.received_at,
    so.completed_at,
    so.status,
    so.description
ORDER BY so.id ASC;



SELECT
    s.id AS service_id,
    s.name,
    s.base_price,
    COUNT(os.order_id) AS order_count
FROM services AS s
JOIN order_services AS os ON s.id = os.service_id
GROUP BY s.id, s.name, s.base_price
ORDER BY order_count DESC, s.id ASC
LIMIT 3;



SELECT
    strftime('%Y-%m', so.completed_at) AS completion_month,
    COALESCE(SUM(os.final_price), 0) AS total_revenue
FROM service_orders AS so
LEFT JOIN order_services AS os ON so.id = os.order_id
WHERE so.status = 'completed'
  AND so.completed_at IS NOT NULL
GROUP BY strftime('%Y-%m', so.completed_at)
ORDER BY completion_month ASC;



SELECT
    c.id AS customer_id,
    c.first_name,
    c.last_name,
    c.phone,
    c.email,
    COUNT(so.id) AS order_count
FROM customers AS c
JOIN vehicles AS v ON c.id = v.customer_id
JOIN service_orders AS so ON v.id = so.vehicle_id
WHERE so.status != 'cancelled'
  AND datetime(so.received_at) >= datetime('now', '-12 months')
GROUP BY c.id, c.first_name, c.last_name, c.phone, c.email
HAVING COUNT(so.id) > 2
ORDER BY order_count DESC, c.id ASC;