-- Zadanie 1, slajdy 24-25. SQLite.
-- Ceny wyrazone w PLN. REAL zgodnie z modelem cwiczenia.
-- Pole stock jest potrzebne do zadania 7 (slajdy 36-37).
-- Wlaczenie kluczy obcych jest wymagane na KAZDYM polaczeniu.
PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL CHECK (length(trim(full_name)) > 0),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(email)) > 0)
);

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL,
    code TEXT NOT NULL UNIQUE CHECK (length(trim(code)) > 0),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    price REAL NOT NULL
        CHECK (typeof(price) IN ('integer', 'real') AND price > 0),
    stock INTEGER NOT NULL DEFAULT 0
        CHECK (typeof(stock) = 'integer' AND stock >= 0),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON DELETE RESTRICT
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    ordered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE RESTRICT
);

CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL
        CHECK (typeof(quantity) = 'integer' AND quantity > 0),
    unit_price REAL NOT NULL
        CHECK (typeof(unit_price) IN ('integer', 'real') AND unit_price > 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- Indeks 1: wyszukiwanie zamowien klienta i laczenie customers z orders.
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
-- Indeks 2: filtrowanie produktow po kategorii i laczenie z categories.
CREATE INDEX idx_products_category_id ON products(category_id);
-- Indeks 3: wyszukiwanie pozycji dla produktu. Zlozony PK zaczyna sie
-- od order_id, wiec nie zastepuje indeksu zaczynajacego sie od product_id.
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- UNIQUE(email), UNIQUE(code), UNIQUE(categories.name) i zlozony PK
-- tworza dodatkowe indeksy automatyczne SQLite.
-- RESTRICT chroni historie zakupow. Usuniecie zamowienia usuwa jego
-- pozycje (CASCADE). unit_price przechowuje cene z chwili zakupu.

-- Walidacja wykonana na danych z dane.sql przy PRAGMA foreign_keys = ON:
-- poprawny klient i zamowienie: OK; duplikat email (takze inna wielkosc
-- liter): odrzucony; cena 0 i ujemna: odrzucone; nieznany customer_id:
-- odrzucony; RESTRICT i CASCADE: zgodne z definicjami.
-- PRAGMA integrity_check = ok; PRAGMA foreign_key_check nie zwraca wierszy.
