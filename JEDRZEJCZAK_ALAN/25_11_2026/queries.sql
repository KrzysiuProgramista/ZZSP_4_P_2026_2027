-- 1. List all unfinished orders with customer, vehicle and assigned mechanic details.
SELECT o.id AS order_id, o.received_at, o.status, o.description,
 c.id AS customer_id, c.first_name AS customer_first_name, c.last_name AS customer_last_name, c.phone, c.email,
 v.id AS vehicle_id, v.brand, v.model, v.year, v.registration_no, v.vin,
 m.id AS mechanic_id, m.first_name AS mechanic_first_name, m.last_name AS mechanic_last_name, m.specialization
FROM service_orders AS o
JOIN vehicles AS v ON v.id = o.vehicle_id
JOIN customers AS c ON c.id = v.customer_id
JOIN mechanics AS m ON m.id = o.mechanic_id
WHERE o.status IN ('received', 'in_progress') ORDER BY o.received_at, o.id;

-- 2. Count orders handled by each mechanic, including mechanics with zero orders.
SELECT m.id, m.first_name, m.last_name, COUNT(o.id) AS order_count
FROM mechanics AS m LEFT JOIN service_orders AS o ON o.mechanic_id = m.id
GROUP BY m.id, m.first_name, m.last_name ORDER BY m.id;

-- 3. Find all vehicles that have never had a service order.
SELECT v.id, v.customer_id, v.brand, v.model, v.registration_no, v.vin
FROM vehicles AS v WHERE NOT EXISTS (SELECT 1 FROM service_orders AS o WHERE o.vehicle_id = v.id)
ORDER BY v.id;

-- 4. Calculate total value of every order, including orders without service lines.
SELECT o.id AS order_id, o.status, COALESCE(SUM(os.final_price), 0) AS total_value
FROM service_orders AS o LEFT JOIN order_services AS os ON os.order_id = o.id
GROUP BY o.id, o.status ORDER BY o.id;

-- 5. Find the three services performed most often, ranked by number of orders.
SELECT s.id, s.name, COUNT(os.order_id) AS orders_count
FROM services AS s JOIN order_services AS os ON os.service_id = s.id
GROUP BY s.id, s.name ORDER BY orders_count DESC, s.id LIMIT 3;

-- 6. Calculate revenue for each completion month, counting completed orders only.
SELECT strftime('%Y-%m', o.completed_at) AS completion_month,
 COALESCE(SUM(os.final_price), 0) AS revenue
FROM service_orders AS o LEFT JOIN order_services AS os ON os.order_id = o.id
WHERE o.status = 'completed' AND o.completed_at IS NOT NULL
GROUP BY strftime('%Y-%m', o.completed_at) ORDER BY completion_month;

-- 7. Find customers with more than two non-cancelled orders received in the last 12 months.
SELECT c.id, c.first_name, c.last_name, COUNT(o.id) AS order_count
FROM customers AS c JOIN vehicles AS v ON v.customer_id = c.id
JOIN service_orders AS o ON o.vehicle_id = v.id
WHERE o.status <> 'cancelled' AND datetime(o.received_at) >= datetime('now', '-12 months')
 AND datetime(o.received_at) <= datetime('now')
GROUP BY c.id, c.first_name, c.last_name HAVING COUNT(o.id) > 2
ORDER BY order_count DESC, c.id;
