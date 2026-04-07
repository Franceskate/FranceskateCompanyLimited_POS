import sqlite3
import hashlib
import os

DB_NAME = "pos_system.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT NOT NULL UNIQUE,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL CHECK(role IN ('Admin', 'Manager', 'Cashier')),
            full_name   TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category     TEXT,
            price        REAL NOT NULL CHECK(price >= 0),
            quantity     INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
            barcode      TEXT UNIQUE,
            supplier     TEXT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL,
            phone          TEXT,
            email          TEXT,
            address        TEXT,
            loyalty_points INTEGER DEFAULT 0,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Sales Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sales (
            sale_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            date           DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id        INTEGER NOT NULL,
            customer_id    INTEGER,
            total_amount   REAL NOT NULL,
            discount       REAL DEFAULT 0,
            tax            REAL DEFAULT 0,
            payment_method TEXT NOT NULL CHECK(payment_method IN ('Cash', 'Mobile Money', 'Card')),
            FOREIGN KEY (user_id)     REFERENCES Users(user_id),
            FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        )
    ''')

    # 5. Sales_Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sales_Items (
            sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id      INTEGER NOT NULL,
            product_id   INTEGER NOT NULL,
            quantity     INTEGER NOT NULL CHECK(quantity > 0),
            price        REAL NOT NULL,
            subtotal     REAL NOT NULL,
            FOREIGN KEY (sale_id)    REFERENCES Sales(sale_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        )
    ''')

    # 6. Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Inventory (
            inventory_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id     INTEGER NOT NULL,
            change_type    TEXT NOT NULL CHECK(change_type IN ('Sale', 'Restock', 'Adjustment')),
            quantity_change INTEGER NOT NULL,
            note           TEXT,
            date           DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        )
    ''')

    # 7. Payments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Payments (
            payment_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id        INTEGER NOT NULL,
            amount_paid    REAL NOT NULL,
            change_given   REAL DEFAULT 0,
            payment_method TEXT NOT NULL,
            payment_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES Sales(sale_id)
        )
    ''')

    conn.commit()
    print("[OK] All tables created successfully.")
    return conn

def seed_default_data(conn):
    cursor = conn.cursor()

    # Insert default admin user
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO Users (username, password, role, full_name)
            VALUES (?, ?, ?, ?)
        ''', ("admin", hash_password("admin123"), "Admin", "System Administrator"))

        cursor.execute('''
            INSERT INTO Users (username, password, role, full_name)
            VALUES (?, ?, ?, ?)
        ''', ("cashier1", hash_password("cash123"), "Cashier", "Default Cashier"))

        cursor.execute('''
            INSERT INTO Users (username, password, role, full_name)
            VALUES (?, ?, ?, ?)
        ''', ("manager1", hash_password("manager123"), "Manager", "Default Manager"))

        print("[OK] Default users seeded (admin / admin123)")

    # Insert sample products
    cursor.execute("SELECT COUNT(*) FROM Products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Coca Cola 500ml", "Beverages", 5.00, 100, "123456789"),
            ("Bread Loaf",      "Bakery",    8.50,  50, "987654321"),
            ("Rice 1kg",        "Grains",   12.00, 200, "111222333"),
            ("Milk 1L",         "Dairy",     9.00,  75, "444555666"),
        ]
        cursor.executemany('''
            INSERT INTO Products (product_name, category, price, quantity, barcode)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_products)
        print("[OK] Sample products seeded.")

    conn.commit()

def verify_setup():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\n[>] Tables in database: {', '.join(tables)}")

    cursor.execute("SELECT user_id, username, role FROM Users")
    print("\n[>] Users:")
    for row in cursor.fetchall():
        print(f"   ID:{row[0]} | {row[1]} | Role: {row[2]}")

    cursor.execute("SELECT product_id, product_name, price, quantity FROM Products")
    print("\n[>] Products:")
    for row in cursor.fetchall():
        print(f"   ID:{row[0]} | {row[1]} | GHS {row[2]} | Stock: {row[3]}")
    conn.close()

if __name__ == "__main__":
    print("[*] Setting up POS database...\n")
    conn = create_tables()
    seed_default_data(conn)
    conn.close()
    verify_setup()
    print(f"\n[OK] Database ready: {DB_NAME}")
