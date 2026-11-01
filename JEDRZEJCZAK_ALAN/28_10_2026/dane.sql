-- Zadanie 2, slajd 26. Dane deterministyczne; wszystkie osoby i adresy są fikcyjne.

-- 6 kategorii, 20 produktów, 10 klientów, 25 zamówień, 60 pozycji.

-- Waluta: PLN. Stany stock to stan bieżący po historycznych zamówieniach.

-- Nie odejmujemy ponownie historycznych ilości podczas importu.

-- Klienci 9 i 10 bez zamówień; produkty 18 i 20 nigdy niezamawiane.

-- Klient 8 ma tylko pending/cancelled. Remisy cen: 2/4 i 11/12.

-- Część cen historycznych jest o 10% niższa od obecnej ceny katalogowej.

PRAGMA foreign_keys = ON;
BEGIN;

INSERT INTO categories (category_id, name) VALUES
    (1, 'Elektronika'),
    (2, 'Dom'),
    (3, 'Książki'),
    (4, 'Sport'),
    (5, 'Uroda'),
    (6, 'Ogród');


INSERT INTO customers (customer_id, full_name, email) VALUES
    (1, 'Anna Nowak', 'anna.nowak@example.com'),
    (2, 'Jan Kowalski', 'jan.kowalski@example.com'),
    (3, 'Olga Wiśniewska', 'olga.wisniewska@gmail.com'),
    (4, 'Piotr Wójcik', 'piotr.wojcik@example.com'),
    (5, 'Ewa Kamińska', 'ewa.kaminska@outlook.com'),
    (6, 'Michał Lewandowski', 'michal.lewandowski@example.com'),
    (7, 'Zofia Zielińska', 'zofia.zielinska@gmail.com'),
    (8, 'Tomasz Szymański', 'tomasz.szymanski@example.com'),
    (9, 'Alicja Woźniak', 'alicja.wozniak@example.com'),
    (10, 'Kamil Dąbrowski', 'kamil.dabrowski@outlook.com');


INSERT INTO products (product_id, category_id, code, name, price, stock) VALUES
    (1, 1, 'P-00001', 'Smartfon', 1499, 30),
    (2, 1, 'P-00002', 'Słuchawki', 249, 80),
    (3, 1, 'P-00003', 'Klawiatura', 149, 60),
    (4, 1, 'P-00004', 'Mysz bezprzewodowa', 249, 70),
    (5, 1, 'P-00005', 'Ładowarka USB-C', 79, 100),
    (6, 2, 'P-00006', 'Lampka biurkowa', 89, 50),
    (7, 2, 'P-00007', 'Czajnik', 129, 40),
    (8, 2, 'P-00008', 'Kubek termiczny', 49, 90),
    (9, 2, 'P-00009', 'Komplet pościeli', 199, 35),
    (10, 3, 'P-00010', 'Podstawy SQL', 39, 100),
    (11, 3, 'P-00011', 'Python od podstaw', 59, 75),
    (12, 3, 'P-00012', 'Algorytmy w praktyce', 59, 70),
    (13, 3, 'P-00013', 'Projektowanie baz danych', 89, 65),
    (14, 4, 'P-00014', 'Mata treningowa', 299, 40),
    (15, 4, 'P-00015', 'Bidon', 69, 120),
    (16, 4, 'P-00016', 'Hantle 2 kg', 129, 60),
    (17, 5, 'P-00017', 'Krem do twarzy', 45, 80),
    (18, 5, 'P-00018', 'Szampon', 25, 100),
    (19, 6, 'P-00019', 'Donica ceramiczna', 99, 50),
    (20, 6, 'P-00020', 'Zestaw narzędzi ogrodowych', 159, 45);


INSERT INTO orders (order_id, customer_id, ordered_at, status) VALUES
    (1, 1, '2026-09-01 10:00:00', 'paid'),
    (2, 2, '2026-09-01 12:00:00', 'shipped'),
    (3, 3, '2026-09-03 09:00:00', 'pending'),
    (4, 1, '2026-09-05 14:00:00', 'cancelled'),
    (5, 4, '2026-09-08 11:00:00', 'paid'),
    (6, 5, '2026-09-10 16:00:00', 'shipped'),
    (7, 2, '2026-09-12 10:00:00', 'paid'),
    (8, 6, '2026-09-15 12:00:00', 'pending'),
    (9, 7, '2026-09-18 09:00:00', 'shipped'),
    (10, 3, '2026-09-20 18:00:00', 'paid'),
    (11, 1, '2026-10-01 10:00:00', 'shipped'),
    (12, 4, '2026-10-02 11:00:00', 'paid'),
    (13, 5, '2026-10-04 13:00:00', 'cancelled'),
    (14, 6, '2026-10-06 09:00:00', 'shipped'),
    (15, 7, '2026-10-08 10:00:00', 'paid'),
    (16, 8, '2026-10-10 15:00:00', 'pending'),
    (17, 2, '2026-10-12 12:00:00', 'shipped'),
    (18, 3, '2026-10-15 17:00:00', 'paid'),
    (19, 4, '2026-10-18 10:00:00', 'pending'),
    (20, 1, '2026-10-20 13:00:00', 'shipped'),
    (21, 5, '2026-10-22 16:00:00', 'paid'),
    (22, 6, '2026-10-24 10:00:00', 'cancelled'),
    (23, 7, '2026-10-26 12:00:00', 'shipped'),
    (24, 8, '2026-10-28 10:00:00', 'cancelled'),
    (25, 1, '2026-10-20 13:00:00', 'paid');


INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 2, 1499.00),
    (1, 6, 3, 89.00),
    (1, 11, 4, 59.00),
    (2, 4, 3, 249.00),
    (2, 9, 4, 199.00),
    (2, 14, 1, 269.10),
    (3, 7, 4, 129.00),
    (3, 12, 1, 53.10),
    (3, 17, 2, 45.00),
    (4, 10, 1, 35.10),
    (4, 15, 2, 69.00),
    (4, 2, 3, 249.00),
    (5, 13, 2, 89.00),
    (5, 19, 3, 99.00),
    (5, 5, 4, 79.00),
    (6, 16, 3, 129.00),
    (6, 3, 4, 149.00),
    (6, 8, 1, 44.10),
    (7, 1, 4, 1499.00),
    (7, 6, 1, 80.10),
    (7, 11, 2, 59.00),
    (8, 4, 1, 224.10),
    (8, 9, 2, 199.00),
    (8, 14, 3, 299.00),
    (9, 7, 2, 129.00),
    (9, 12, 3, 59.00),
    (9, 17, 4, 45.00),
    (10, 10, 3, 39.00),
    (10, 15, 4, 69.00),
    (10, 2, 1, 224.10),
    (11, 13, 4, 89.00),
    (11, 19, 1, 89.10),
    (12, 16, 1, 116.10),
    (12, 3, 2, 149.00),
    (13, 1, 2, 1499.00),
    (13, 6, 3, 89.00),
    (14, 4, 3, 249.00),
    (14, 9, 4, 199.00),
    (15, 7, 4, 129.00),
    (15, 12, 1, 53.10),
    (16, 10, 1, 35.10),
    (16, 15, 2, 69.00),
    (17, 13, 2, 89.00),
    (17, 19, 3, 99.00),
    (18, 16, 3, 129.00),
    (18, 3, 4, 149.00),
    (19, 1, 4, 1499.00),
    (19, 6, 1, 80.10),
    (20, 4, 1, 224.10),
    (20, 9, 2, 199.00),
    (21, 7, 2, 129.00),
    (21, 12, 3, 59.00),
    (22, 10, 3, 39.00),
    (22, 15, 4, 69.00),
    (23, 13, 4, 89.00),
    (23, 19, 1, 89.10),
    (24, 16, 1, 116.10),
    (24, 3, 2, 149.00),
    (25, 1, 2, 1499.00),
    (25, 6, 3, 89.00);


COMMIT;
