-- 1. Which received/in-progress orders show their customer, vehicle and mechanic?
SELECT o.id AS order_id, o.received_at, o.status, o.description,
 customer.id AS customer_id, customer.first_name AS customer_first_name,
 customer.last_name AS customer_last_name, customer.phone, customer.email,
 vehicle.id AS vehicle_id, vehicle.brand, vehicle.model, vehicle.year,
 vehicle.registration_no, vehicle.vin, mechanic.id AS mechanic_id,
 mechanic.first_name AS mechanic_first_name, mechanic.last_name AS mechanic_last_name,
 mechanic.specialization
FROM service_orders o
INNER JOIN mechanics mechanic ON o.mechanic_id=mechanic.id
INNER JOIN vehicles vehicle ON o.vehicle_id=vehicle.id
INNER JOIN customers customer ON vehicle.customer_id=customer.id
WHERE o.status IN ('received','in_progress') ORDER BY o.id;

-- 2. How many orders were assigned to each mechanic, including zero?
WITH assignments AS (
 SELECT mechanic_id, COUNT(*) AS qty FROM service_orders GROUP BY mechanic_id
)
SELECT m.id, m.first_name, m.last_name, IFNULL(a.qty,0) AS order_count
FROM mechanics m LEFT JOIN assignments a ON a.mechanic_id=m.id ORDER BY m.id;

-- 3. Which vehicles were never assigned a service order?
SELECT v.id, v.customer_id, v.brand, v.model, v.year, v.registration_no, v.vin
FROM vehicles v WHERE v.id NOT IN (SELECT o.vehicle_id FROM service_orders o) ORDER BY v.id;

-- 4. What is the total charged for each order, even an order with no lines?
WITH prices AS (
 SELECT order_id, SUM(final_price) AS charge FROM order_services GROUP BY order_id
)
SELECT o.id AS order_id, o.status, IFNULL(p.charge,0) AS total_value
FROM service_orders o LEFT JOIN prices p ON p.order_id=o.id ORDER BY o.id;

-- 5. Which three services were performed in the most distinct orders?
SELECT s.id, s.name, COUNT(DISTINCT os.order_id) AS orders_count
FROM services s INNER JOIN order_services os ON os.service_id=s.id
GROUP BY s.id, s.name ORDER BY orders_count DESC,s.id LIMIT 3;

-- 6. What revenue did completed orders bring in by completion month?
WITH completed_orders AS (
 SELECT id, strftime('%Y-%m',completed_at) AS month_key
 FROM service_orders WHERE status='completed' AND completed_at IS NOT NULL
)
SELECT c.month_key AS completion_month, IFNULL(SUM(l.final_price),0) AS revenue
FROM completed_orders c LEFT JOIN order_services l ON l.order_id=c.id
GROUP BY c.month_key ORDER BY c.month_key;

-- 7. Who placed over two non-cancelled service orders in the past 12 months?
SELECT c.id, c.first_name, c.last_name, COUNT(*) AS order_count
FROM service_orders o
JOIN vehicles v ON v.id=o.vehicle_id
JOIN customers c ON c.id=v.customer_id
WHERE o.status IN ('received','in_progress','completed')
 AND julianday(o.received_at) BETWEEN julianday('now','-12 months') AND julianday('now')
GROUP BY c.id, c.first_name, c.last_name
HAVING COUNT(*)>=3 ORDER BY order_count DESC,c.id;
