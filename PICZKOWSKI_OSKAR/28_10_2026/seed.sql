-- seed.sql

-- Deterministyczne dane testowe: 6 kategorii, 20 produktów, 10 klientów, 25 zamówień, 60 pozycji.

PRAGMA foreign_keys = ON;

BEGIN;

INSERT INTO categories(category_id,name) VALUES
(1,'Electronics'),
(2,'Accessories'),
(3,'Office'),
(4,'Computers'),
(5,'Audio'),
(6,'Home');

INSERT INTO customers(customer_id,name,email) VALUES
(1,'Ava Lee','ava@example.com'),
(2,'Noah Smith','noah@example.com'),
(3,'Mia Chen','mia@example.com'),
(4,'Liam Brown','liam@example.com'),
(5,'Emma Wilson','emma@example.com'),
(6,'Oliver Jones','oliver@example.com'),
(7,'Sophia Davis','sophia@example.com'),
(8,'Lucas Miller','lucas@example.com'),
(9,'Isla Taylor','isla@example.com'),
(10,'Ethan Moore','ethan@example.com');

INSERT INTO products(product_id,category_id,product_code,name,price,stock) VALUES
(1,1,'P-001','USB-C cable',19.99,120),
(2,2,'P-002','Wireless mouse',49.99,80),
(3,3,'P-003','Keyboard',89.0,45),
(4,4,'P-004','Monitor',799.0,20),
(5,5,'P-005','Notebook',12.5,200),
(6,6,'P-006','Desk lamp',59.9,35),
(7,1,'P-007','Webcam',149.0,30),
(8,2,'P-008','Mouse pad',15.0,150),
(9,3,'P-009','Laptop stand',129.0,40),
(10,4,'P-010','Mini PC',1299.0,12),
(11,5,'P-011','Pen set',8.99,300),
(12,6,'P-012','Desk organizer',34.5,65),
(13,1,'P-013','USB hub',79.0,55),
(14,2,'P-014','HDMI cable',24.0,100),
(15,3,'P-015','Office chair',499.0,18),
(16,4,'P-016','Laptop',3499.0,8),
(17,5,'P-017','Printer paper',22.0,250),
(18,6,'P-018','Water bottle',29.0,90),
(19,1,'P-019','Microphone',219.0,25),
(20,2,'P-020','Cable clips',6.5,400);

INSERT INTO orders(order_id,customer_id,status,order_date) VALUES
(1,3,'paid','2026-01-07'),
(2,6,'shipped','2026-01-14'),
(3,1,'pending','2026-01-21'),
(4,4,'cancelled','2026-02-03'),
(5,7,'paid','2026-02-10'),
(6,2,'paid','2026-02-17'),
(7,5,'shipped','2026-03-24'),
(8,8,'pending','2026-03-06'),
(9,3,'cancelled','2026-03-13'),
(10,6,'paid','2026-04-20'),
(11,1,'paid','2026-04-02'),
(12,4,'shipped','2026-04-09'),
(13,7,'pending','2026-05-16'),
(14,2,'cancelled','2026-05-23'),
(15,5,'paid','2026-05-05'),
(16,8,'paid','2026-06-12'),
(17,3,'shipped','2026-06-19'),
(18,6,'pending','2026-06-01'),
(19,1,'cancelled','2026-07-08'),
(20,4,'paid','2026-07-15'),
(21,7,'paid','2026-07-22'),
(22,2,'shipped','2026-08-04'),
(23,5,'pending','2026-08-11'),
(24,8,'cancelled','2026-08-18'),
(25,3,'paid','2026-09-25');

INSERT INTO order_items(order_item_id,order_id,product_id,quantity,unit_price) VALUES
(1,1,5,2,12.5),
(2,1,12,3,34.5),
(3,2,10,3,1299.0),
(4,2,17,4,22.0),
(5,3,15,4,499.0),
(6,3,4,1,799.0),
(7,4,2,1,49.99),
(8,4,9,2,129.0),
(9,5,7,2,149.0),
(10,5,14,3,24.0),
(11,6,12,3,34.5),
(12,6,1,4,19.99),
(13,7,17,4,22.0),
(14,7,6,1,59.9),
(15,8,4,1,799.0),
(16,8,11,2,8.99),
(17,9,9,2,129.0),
(18,9,16,3,3499.0),
(19,10,14,3,24.0),
(20,10,3,4,89.0),
(21,11,1,4,19.99),
(22,11,8,1,15.0),
(23,12,6,1,59.9),
(24,12,13,2,79.0),
(25,13,11,2,8.99),
(26,13,18,3,29.0),
(27,14,16,3,3499.0),
(28,14,5,4,12.5),
(29,15,3,4,89.0),
(30,15,10,1,1299.0),
(31,16,8,1,15.0),
(32,16,15,2,499.0),
(33,16,4,3,799.0),
(34,17,13,2,79.0),
(35,17,2,3,49.99),
(36,17,9,4,129.0),
(37,18,18,3,29.0),
(38,18,7,4,149.0),
(39,18,14,1,24.0),
(40,19,5,4,12.5),
(41,19,12,1,34.5),
(42,19,1,2,19.99),
(43,20,10,1,1299.0),
(44,20,17,2,22.0),
(45,20,6,3,59.9),
(46,21,15,2,499.0),
(47,21,4,3,799.0),
(48,21,11,4,8.99),
(49,22,2,3,49.99),
(50,22,9,4,129.0),
(51,22,16,1,3499.0),
(52,23,7,4,149.0),
(53,23,14,1,24.0),
(54,23,3,2,89.0),
(55,24,12,1,34.5),
(56,24,1,2,19.99),
(57,24,8,3,15.0),
(58,25,17,2,22.0),
(59,25,6,3,59.9),
(60,25,13,4,79.0);

COMMIT;



-- Kontrola liczebności: powinno zwrócić odpowiednio 6, 20, 10, 25, 60.

SELECT 'categories' AS table_name, COUNT(*) AS row_count FROM categories

UNION ALL SELECT 'products', COUNT(*) FROM products

UNION ALL SELECT 'customers', COUNT(*) FROM customers

UNION ALL SELECT 'orders', COUNT(*) FROM orders

UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;
