PRAGMA foreign_keys = ON;

-- 1. Kategorie
INSERT INTO categories (category_id, name) VALUES
(1, 'Elektronika'),
(2, 'Książki'),
(3, 'Odzież'),
(4, 'Dom i Kuchnia'),
(5, 'Sport'),
(6, 'Zabawki');

-- 2. Klienci (w tym Klienci 9 i 10 bez zamówień)
INSERT INTO customers (customer_id, name, email) VALUES
(1, 'Anna Kowalska', 'anna.kowalska@example.com'),
(2, 'Piotr Nowak', 'piotr.nowak@example.com'),
(3, 'Michał Wiśniewski', 'michal.w@gmail.com'),
(4, 'Katarzyna Wójcik', 'katarzyna.w@yahoo.com'),
(5, 'Tomasz Kamiński', 'tomasz.k@example.com'),
(6, 'Magdalena Lewandowski', 'magda.l@domain.com'),
(7, 'Paweł Zieliński', 'pawel.z@example.com'),
(8, 'Monika Szymańska', 'monika.s@gmail.com'),
(9, 'Grzegorz Dąbrowski', 'grzegorz.d@matrix.com'),
(10, 'Ewa Grabowska', 'ewa.g@hollywood.com');

-- 3. Produkty (w tym P503 i P602 niezamówione)
INSERT INTO products (product_id, product_code, name, price, stock, category_id) VALUES
(1, 'P101', 'Kabel USB-C', 19.99, 100, 1),
(2, 'P102', 'Mysz Bezprzewodowa', 29.99, 50, 1),
(3, 'P103', 'Klawiatura Mechaniczna', 89.00, 30, 1),
(4, 'P104', 'Monitor 4K', 499.99, 15, 1),
(5, 'P105', 'Słuchawki ANC', 199.99, 20, 1),
(6, 'P201', 'Podręcznik SQL', 45.00, 200, 2),
(7, 'P202', 'Python Cookbook', 55.00, 150, 2),
(8, 'P203', 'Wprowadzenie do Algorytmów', 35.00, 80, 2),
(9, 'P204', 'Czysty Kod', 42.50, 100, 2),
(10, 'P301', 'Koszulka Bawełniana', 15.00, 300, 3),
(11, 'P302', 'Spodnie Jeansowe', 59.99, 120, 3),
(12, 'P303', 'Kurtka Zimowa', 129.99, 40, 3),
(13, 'P401', 'Ekspres do Kawy', 79.99, 25, 4),
(14, 'P402', 'Blender', 49.99, 35, 4),
(15, 'P403', 'Frytkownica Beztłuszczowa', 99.99, 18, 4),
(16, 'P501', 'Mata do Jogi', 25.00, 60, 5),
(17, 'P502', 'Hantle 2x5kg', 85.00, 25, 5),
(18, 'P503', 'Bieżnia Elektryczna', 899.00, 5, 5),
(19, 'P601', 'Gra Planszowa', 34.99, 45, 6),
(20, 'P602', 'Zestaw Klocków', 119.99, 10, 6);

-- 4. Zamówienia (25)
INSERT INTO orders (order_id, customer_id, order_date, status) VALUES
(1, 1, '2026-10-01', 'shipped'), (2, 2, '2026-10-02', 'paid'),
(3, 3, '2026-10-03', 'shipped'), (4, 4, '2026-10-04', 'pending'),
(5, 5, '2026-10-05', 'cancelled'), (6, 6, '2026-10-06', 'shipped'),
(7, 7, '2026-10-07', 'paid'), (8, 8, '2026-10-08', 'shipped'),
(9, 1, '2026-10-09', 'paid'), (10, 2, '2026-10-10', 'shipped'),
(11, 3, '2026-10-11', 'pending'), (12, 4, '2026-10-12', 'paid'),
(13, 5, '2026-10-13', 'shipped'), (14, 6, '2026-10-14', 'cancelled'),
(15, 7, '2026-10-15', 'paid'), (16, 8, '2026-10-16', 'shipped'),
(17, 1, '2026-10-17', 'shipped'), (18, 2, '2026-10-18', 'paid'),
(19, 3, '2026-10-19', 'shipped'), (20, 4, '2026-10-20', 'pending'),
(21, 5, '2026-10-21', 'paid'), (22, 6, '2026-10-22', 'shipped'),
(23, 7, '2026-10-23', 'shipped'), (24, 8, '2026-10-24', 'paid'),
(25, 1, '2026-10-25', 'shipped');

-- 5. Pozycje Zamówienia (60)
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 2, 19.99), (1, 4, 1, 499.99), (1, 6, 1, 45.00),
(2, 2, 1, 29.99), (2, 3, 1, 89.00),
(3, 5, 1, 199.99), (3, 7, 2, 55.00),
(4, 8, 1, 35.00), (4, 10, 3, 15.00),
(5, 11, 1, 59.99), (5, 12, 1, 129.99),
(6, 13, 1, 79.99), (6, 14, 2, 49.99),
(7, 15, 1, 99.99), (7, 16, 1, 25.00),
(8, 17, 1, 85.00), (8, 19, 2, 34.99),
(9, 1, 5, 19.99), (9, 2, 2, 29.99),
(10, 3, 1, 89.00), (10, 5, 1, 199.99),
(11, 6, 2, 45.00), (11, 8, 1, 35.00),
(12, 7, 1, 55.00), (12, 9, 2, 42.50),
(13, 10, 4, 15.00), (13, 11, 1, 59.99),
(14, 12, 1, 129.99), (14, 13, 1, 79.99),
(15, 14, 1, 49.99), (15, 15, 2, 99.99),
(16, 16, 2, 25.00), (16, 17, 1, 85.00),
(17, 1, 1, 19.99), (17, 3, 1, 89.00), (17, 6, 1, 45.00),
(18, 2, 3, 29.99), (18, 5, 1, 199.99),
(19, 4, 1, 499.99), (19, 7, 1, 55.00),
(20, 8, 2, 35.00), (20, 9, 1, 42.50),
(21, 10, 2, 15.00), (21, 11, 2, 59.99),
(22, 13, 1, 79.99), (22, 15, 1, 99.99),
(23, 16, 3, 25.00), (23, 17, 1, 85.00),
(24, 1, 2, 19.99), (24, 19, 1, 34.99),
(25, 2, 1, 29.99), (25, 3, 1, 89.00), (25, 6, 2, 45.00);
