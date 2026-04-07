import sqlite3
import hashlib

DB_NAME = "pos_system.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ── New products to add ──
new_products = [
    ("Milo 400g",          "Beverages",    28.00,  60,  "555666777"),
    ("Sugar 1kg",          "Groceries",    14.00, 100,  "666777888"),
    ("Cooking Oil 1L",     "Groceries",    22.00,  80,  "777888999"),
    ("Tuna Can 170g",      "Canned Foods", 12.00,  90,  "888999000"),
    ("Cabin Biscuits",     "Snacks",        5.00, 120,  "100200300"),
    ("Indomie Noodles",    "Groceries",     6.00, 150,  "200300400"),
    ("Tomato Paste 70g",   "Canned Foods",  4.50, 200,  "300400500"),
    ("Canola Soap",        "Household",     3.00, 100,  "400500600"),
    ("Detergent 500g",     "Household",    18.00,  70,  "500600700"),
    ("Bottled Water 500ml","Beverages",     3.00, 200,  "600700800"),
]

def add_products():
    conn = get_connection()
    cursor = conn.cursor()

    added   = 0
    skipped = 0

    for name, category, price, quantity, barcode in new_products:
        try:
            cursor.execute('''
                INSERT INTO Products (product_name, category, price, quantity, barcode)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, category, price, quantity, barcode))
            print(f"[OK] Added: {name}")
            added += 1
        except sqlite3.IntegrityError:
            print(f"[SKIP] Already exists: {name} (barcode conflict)")
            skipped += 1

    conn.commit()
    conn.close()
    print(f"\n✅ Done! {added} product(s) added, {skipped} skipped.")

    # Show all products
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, product_name, category, price, quantity, barcode FROM Products")
    rows = cursor.fetchall()
    conn.close()

    print(f"\n{'─'*70}")
    print(f"{'ID':<5} {'Name':<22} {'Category':<14} {'Price':>8}  {'Qty':>5}  {'Barcode'}")
    print(f"{'─'*70}")
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<22} {row[2]:<14} GHS {row[3]:>6.2f}  {row[4]:>5}  {row[5]}")
    print(f"{'─'*70}")
    print(f"Total: {len(rows)} products in database.")

if __name__ == "__main__":
    print("Adding new products to POS database...\n")
    add_products()
