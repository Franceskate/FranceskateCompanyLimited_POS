import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = "pos_system.db"

BG      = "#F0F4F8"
ACCENT  = "#1565C0"
ACCENT2 = "#E3F2FD"
SUCCESS = "#2E7D32"
DANGER  = "#C62828"
WARNING = "#F9A825"
WHITE   = "#FFFFFF"
TEXT    = "#212121"
SUBTEXT = "#546E7A"
BORDER  = "#CFD8DC"
CARD    = "#FFFFFF"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

try:
    import cv2
    from pyzbar import pyzbar
    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False


class BarcodeScanner:
    def __init__(self, parent, callback):
        self.callback = callback
        self.running = True
        if not SCANNER_AVAILABLE:
            messagebox.showerror("Scanner Not Available",
                "Please install required libraries:\n\npip install opencv-python pyzbar")
            return
        self.win = tk.Toplevel(parent)
        self.win.title("Barcode Scanner")
        self.win.geometry("520x430")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        tk.Label(self.win, text="Barcode Scanner", font=("Helvetica", 14, "bold"), bg=BG, fg=TEXT).pack(pady=(15, 5))
        tk.Label(self.win, text="Point camera at barcode...", font=("Helvetica", 10), bg=BG, fg=SUBTEXT).pack()
        from PIL import Image, ImageTk
        self.ImageTk = ImageTk; self.Image = Image
        self.canvas = tk.Canvas(self.win, width=480, height=320, bg="#000000", highlightthickness=0)
        self.canvas.pack(pady=10, padx=15)
        self.status_var = tk.StringVar(value="Scanning...")
        tk.Label(self.win, textvariable=self.status_var, font=("Helvetica", 10), bg=BG, fg=SUCCESS).pack()
        tk.Button(self.win, text="Cancel", font=("Helvetica", 10, "bold"), bg=DANGER, fg=WHITE,
                  relief="flat", command=self.stop).pack(pady=8, ipady=4, ipadx=20)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Could not open webcam.")
            self.win.destroy(); return
        self.scan_frame()

    def scan_frame(self):
        if not self.running: return
        ret, frame = self.cap.read()
        if ret:
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.status_var.set(f"Scanned: {barcode_data}")
                self.stop(); self.callback(barcode_data); return
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (480, 320))
            img = self.Image.fromarray(frame_resized)
            self.photo = self.ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        if self.running:
            self.win.after(30, self.scan_frame)

    def stop(self):
        self.running = False
        if hasattr(self, "cap") and self.cap: self.cap.release()
        if hasattr(self, "win") and self.win.winfo_exists(): self.win.destroy()


class SalesProcessing:
    def __init__(self, root, user=None, embedded=False):
        self.root = root
        self.user = user or (1, "Admin", "Admin")
        self.cart = []
        self.embedded = embedded

        if not embedded:
            self.root.title("Sales Processing — Franceskate Company Limited")
            self.root.geometry("1200x720")
            self.root.resizable(True, True)
            self.root.configure(bg=BG)

        self.build_ui()

    def build_ui(self):
        # Header (only if not embedded — dashboard handles header)
        if not self.embedded:
            header = tk.Frame(self.root, bg=WHITE, pady=16)
            header.pack(fill="x")
            tk.Label(header, text="Sales Processing", font=("Helvetica", 17, "bold"), bg=WHITE, fg=TEXT).pack(side="left", padx=25)
            tk.Label(header, text=f"Cashier: {self.user[1]}", font=("Helvetica", 10), bg=WHITE, fg=SUBTEXT).pack(side="right", padx=25)
            tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=15, pady=10)

        # ── LEFT panel ──
        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Search bar
        search_card = tk.Frame(left, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        search_card.pack(fill="x", pady=(0, 8))
        inner_s = tk.Frame(search_card, bg=CARD, padx=12, pady=10)
        inner_s.pack(fill="x")

        tk.Label(inner_s, text="Search:", font=("Helvetica", 11), bg=CARD, fg=SUBTEXT).pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.search_products())
        tk.Entry(inner_s, textvariable=self.search_var, font=("Helvetica", 11),
                 bg=BG, fg=TEXT, relief="flat", bd=0, width=20,
                 insertbackground=TEXT).pack(side="left", ipady=5)

        tk.Label(inner_s, text="Qty:", font=("Helvetica", 11), bg=CARD, fg=SUBTEXT).pack(side="left", padx=(15, 5))
        self.qty_var = tk.StringVar(value="1")
        tk.Entry(inner_s, textvariable=self.qty_var, font=("Helvetica", 11),
                 bg=BG, fg=TEXT, relief="flat", bd=0, width=5,
                 insertbackground=TEXT).pack(side="left", ipady=5)

        tk.Button(inner_s, text="Add to Cart", font=("Helvetica", 10, "bold"),
                  bg=SUCCESS, fg=WHITE, relief="flat", cursor="hand2",
                  command=self.add_to_cart).pack(side="left", padx=(12, 0), ipady=5, ipadx=8)

        # Barcode entry
        bc_frame = tk.Frame(left, bg=BG)
        bc_frame.pack(fill="x", pady=(0, 8))
        tk.Label(bc_frame, text="Scan / Enter barcode:", font=("Helvetica", 10), bg=BG, fg=SUBTEXT).pack(side="left", padx=(0, 5))
        self.barcode_var = tk.StringVar()
        barcode_entry = tk.Entry(bc_frame, textvariable=self.barcode_var, font=("Helvetica", 11),
                                 bg=CARD, fg=TEXT, relief="flat", bd=0, width=20, insertbackground=TEXT)
        barcode_entry.pack(side="left", ipady=4)
        barcode_entry.bind("<Return>", lambda e: self.lookup_barcode())
        tk.Button(bc_frame, text="Lookup", font=("Helvetica", 10), bg=WARNING, fg=WHITE,
                  relief="flat", cursor="hand2", command=self.lookup_barcode).pack(side="left", padx=(8, 0), ipady=4, ipadx=8)

        # Products table
        tk.Label(left, text="Products", font=("Helvetica", 11, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(4, 4))
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Pro.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=28, font=("Helvetica", 10))
        style.configure("Pro.Treeview.Heading", background=ACCENT2, foreground=ACCENT, font=("Helvetica", 10, "bold"), relief="flat")
        style.map("Pro.Treeview", background=[("selected", ACCENT2)], foreground=[("selected", ACCENT)])

        prod_cols = ("ID", "Name", "Category", "Price", "Stock", "Barcode")
        self.prod_tree = ttk.Treeview(left, columns=prod_cols, show="headings", height=7, style="Pro.Treeview")
        for col, w in zip(prod_cols, [40, 180, 110, 80, 60, 120]):
            self.prod_tree.heading(col, text=col)
            self.prod_tree.column(col, width=w, anchor="center")
        self.prod_tree.pack(fill="x")
        self.load_all_products()

        # Cart
        tk.Label(left, text="Shopping Cart", font=("Helvetica", 11, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(12, 4))
        cart_cols = ("Name", "Price", "Qty", "Subtotal")
        self.cart_tree = ttk.Treeview(left, columns=cart_cols, show="headings", height=6, style="Pro.Treeview")
        for col, w in zip(cart_cols, [240, 90, 70, 110]):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=w, anchor="center")
        self.cart_tree.pack(fill="x")

        # Cart buttons
        cart_btn_frame = tk.Frame(left, bg=BG)
        cart_btn_frame.pack(fill="x", pady=(6, 0))
        tk.Button(cart_btn_frame, text="Remove Selected", font=("Helvetica", 10, "bold"),
                  bg=DANGER, fg=WHITE, relief="flat", cursor="hand2",
                  command=self.remove_from_cart).pack(side="left", ipady=5, ipadx=8)
        tk.Button(cart_btn_frame, text="Clear Cart", font=("Helvetica", 10),
                  bg=SUBTEXT, fg=WHITE, relief="flat", cursor="hand2",
                  command=self.clear_cart).pack(side="left", padx=(8, 0), ipady=5, ipadx=8)

        # ── RIGHT panel: Payment ──
        right = tk.Frame(main, bg=CARD, width=270, padx=15, pady=15,
                         highlightbackground=BORDER, highlightthickness=1)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="Payment", font=("Helvetica", 14, "bold"), bg=CARD, fg=TEXT).pack(pady=(0, 12))
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=(0, 10))

        def summary_row(label, var, color=TEXT):
            f = tk.Frame(right, bg=CARD)
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label, font=("Helvetica", 11), bg=CARD, fg=SUBTEXT).pack(side="left")
            tk.Label(f, textvariable=var, font=("Helvetica", 11, "bold"), bg=CARD, fg=color).pack(side="right")

        self.subtotal_var = tk.StringVar(value="GHS 0.00")
        self.discount_var = tk.StringVar(value="GHS 0.00")
        self.tax_var      = tk.StringVar(value="GHS 0.00")
        self.total_var    = tk.StringVar(value="GHS 0.00")

        summary_row("Subtotal:", self.subtotal_var)
        summary_row("Discount:", self.discount_var, WARNING)
        summary_row("Tax (0%):", self.tax_var, SUBTEXT)
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=8)
        summary_row("TOTAL:", self.total_var, SUCCESS)

        tk.Label(right, text="Discount:", font=("Helvetica", 10, "bold"), bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(12, 3))
        self.discount_type = tk.StringVar(value="fixed")
        disc_row = tk.Frame(right, bg=CARD)
        disc_row.pack(fill="x")
        for label, val in [("GHS (Fixed)", "fixed"), ("% (Percent)", "percent")]:
            tk.Radiobutton(disc_row, text=label, variable=self.discount_type, value=val,
                           bg=CARD, fg=TEXT, selectcolor=CARD, activebackground=CARD,
                           font=("Helvetica", 10)).pack(side="left")

        self.discount_input = tk.StringVar(value="0")
        tk.Entry(right, textvariable=self.discount_input, font=("Helvetica", 11),
                 bg=BG, fg=TEXT, relief="flat", bd=0, insertbackground=TEXT).pack(fill="x", ipady=6, pady=(5, 0))
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x")
        tk.Button(right, text="Apply Discount", font=("Helvetica", 10),
                  bg=WARNING, fg=WHITE, relief="flat", cursor="hand2",
                  command=self.update_totals).pack(fill="x", ipady=5, pady=(6, 0))

        tk.Label(right, text="Payment Method:", font=("Helvetica", 10, "bold"), bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(15, 3))
        self.payment_method = tk.StringVar(value="Cash")
        self.payment_method.trace("w", self.toggle_payment_ui)
        for method in ["Cash", "Mobile Money", "Card"]:
            tk.Radiobutton(right, text=method, variable=self.payment_method, value=method,
                           bg=CARD, fg=TEXT, selectcolor=CARD, activebackground=CARD,
                           font=("Helvetica", 10)).pack(anchor="w")

        # Cash frame
        self.cash_frame = tk.Frame(right, bg=CARD)
        self.cash_frame.pack(fill="x")
        tk.Label(self.cash_frame, text="Amount Paid (GHS):", font=("Helvetica", 10), bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(12, 3))
        self.amount_paid_var = tk.StringVar(value="0")
        tk.Entry(self.cash_frame, textvariable=self.amount_paid_var, font=("Helvetica", 11),
                 bg=BG, fg=TEXT, relief="flat", bd=0, insertbackground=TEXT).pack(fill="x", ipady=6)
        tk.Frame(self.cash_frame, bg=BORDER, height=1).pack(fill="x")
        self.change_var = tk.StringVar(value="Change: GHS 0.00")
        tk.Label(self.cash_frame, textvariable=self.change_var, font=("Helvetica", 11, "bold"),
                 bg=CARD, fg=ACCENT).pack(pady=(8, 0))
        tk.Button(self.cash_frame, text="Calculate Change", font=("Helvetica", 10),
                  bg=ACCENT, fg=WHITE, relief="flat", cursor="hand2",
                  command=self.calculate_change).pack(fill="x", ipady=5, pady=(5, 0))

        # Paystack frame
        self.paystack_frame = tk.Frame(right, bg=CARD)
        self.paystack_frame.pack(fill="x")
        tk.Label(self.paystack_frame, text="Pay via Paystack:", font=("Helvetica", 10, "bold"),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", pady=(12, 3))
        tk.Label(self.paystack_frame, text="Click CHECKOUT to open\nthe Paystack payment page.",
                 font=("Helvetica", 10), bg=CARD, fg=SUBTEXT).pack(anchor="w")
        self.paystack_frame.pack_forget()

        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=10)
        tk.Button(right, text="CHECKOUT", font=("Helvetica", 13, "bold"),
                  bg=SUCCESS, fg=WHITE, relief="flat", cursor="hand2",
                  command=self.checkout).pack(fill="x", ipady=10)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self.root, textvariable=self.status_var, font=("Helvetica", 9),
                 bg=WHITE, fg=SUCCESS, anchor="w").pack(fill="x", padx=10, pady=4)

    def toggle_payment_ui(self, *args):
        method = self.payment_method.get()
        if method == "Cash":
            self.paystack_frame.pack_forget()
            self.cash_frame.pack(fill="x")
        else:
            self.cash_frame.pack_forget()
            self.paystack_frame.pack(fill="x")

    def open_scanner(self):
        BarcodeScanner(self.root, self.on_barcode_scanned)

    def on_barcode_scanned(self, barcode):
        self.barcode_var.set(barcode)
        self.lookup_barcode()

    def lookup_barcode(self):
        barcode = self.barcode_var.get().strip()
        if not barcode: return
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT product_id,product_name,category,price,quantity FROM Products WHERE barcode=?", (barcode,))
        product = cursor.fetchone(); conn.close()
        if not product:
            messagebox.showwarning("Not Found", f"No product found with barcode: {barcode}")
            self.status_var.set(f"Barcode not found: {barcode}"); return
        for item in self.prod_tree.get_children():
            if self.prod_tree.item(item, "values")[0] == str(product[0]):
                self.prod_tree.selection_set(item); self.prod_tree.see(item); break
        self.status_var.set(f"Found: {product[1]} — GHS {product[3]:.2f}")
        self.barcode_var.set(""); self.add_to_cart()

    def load_all_products(self):
        for row in self.prod_tree.get_children(): self.prod_tree.delete(row)
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT product_id,product_name,category,price,quantity,barcode FROM Products")
        for row in cursor.fetchall(): self.prod_tree.insert("", "end", values=row)
        conn.close()

    def search_products(self):
        for row in self.prod_tree.get_children(): self.prod_tree.delete(row)
        search = self.search_var.get().strip()
        conn = get_connection(); cursor = conn.cursor()
        if search:
            cursor.execute("SELECT product_id,product_name,category,price,quantity,barcode FROM Products WHERE product_name LIKE ? OR barcode LIKE ?", (f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("SELECT product_id,product_name,category,price,quantity,barcode FROM Products")
        rows = cursor.fetchall(); conn.close()
        for row in rows: self.prod_tree.insert("", "end", values=row)
        self.status_var.set(f"{len(rows)} product(s) found." if rows else "No products found.")

    def add_to_cart(self):
        selected = self.prod_tree.selection()
        if not selected: self.status_var.set("[!] Please select a product first."); return
        values = self.prod_tree.item(selected[0], "values")
        product_id = int(values[0]); name = values[1]
        price = float(values[3]); stock = int(values[4])
        try:
            qty = int(self.qty_var.get())
            if qty <= 0: raise ValueError
        except ValueError:
            self.status_var.set("[!] Please enter a valid quantity."); return
        for item in self.cart:
            if item["product_id"] == product_id:
                new_qty = item["quantity"] + qty
                if new_qty > stock: self.status_var.set(f"[!] Only {stock} units available."); return
                item["quantity"] = new_qty; item["subtotal"] = round(item["price"] * new_qty, 2)
                self.refresh_cart(); self.status_var.set(f"Updated: {name} x{new_qty}"); return
        if qty > stock: self.status_var.set(f"[!] Only {stock} units available."); return
        self.cart.append({"product_id": product_id, "name": name, "price": price, "quantity": qty, "subtotal": round(price * qty, 2)})
        self.refresh_cart(); self.status_var.set(f"Added: {name} x{qty}")

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected: messagebox.showwarning("No Selection", "Please select an item to remove."); return
        index = self.cart_tree.index(selected[0])
        removed = self.cart.pop(index); self.refresh_cart()
        self.status_var.set(f"Removed: {removed['name']}")

    def refresh_cart(self):
        for row in self.cart_tree.get_children(): self.cart_tree.delete(row)
        for item in self.cart:
            self.cart_tree.insert("", "end", values=(item["name"], f"GHS {item['price']:.2f}", item["quantity"], f"GHS {item['subtotal']:.2f}"))
        self.update_totals()

    def clear_cart(self):
        self.cart.clear(); self.refresh_cart()
        self.amount_paid_var.set("0"); self.change_var.set("Change: GHS 0.00")
        self.status_var.set("Cart cleared.")

    def update_totals(self):
        subtotal = sum(item["subtotal"] for item in self.cart)
        try: disc_value = float(self.discount_input.get())
        except ValueError: disc_value = 0
        discount = round(subtotal * disc_value / 100, 2) if self.discount_type.get() == "percent" else disc_value
        total = max(0, subtotal - discount)
        self.subtotal_var.set(f"GHS {subtotal:.2f}"); self.discount_var.set(f"GHS {discount:.2f}")
        self.tax_var.set("GHS 0.00"); self.total_var.set(f"GHS {total:.2f}")

    def calculate_change(self):
        try:
            total = float(self.total_var.get().replace("GHS ", ""))
            paid  = float(self.amount_paid_var.get())
            change = paid - total
            self.change_var.set(f"Change: GHS {max(0, change):.2f}")
            if change < 0: self.status_var.set(f"[!] Amount short by GHS {abs(change):.2f}")
        except ValueError:
            messagebox.showerror("Error", "Enter a valid amount paid.")

    def checkout(self):
        if not self.cart: messagebox.showwarning("Empty Cart", "Add items to the cart first."); return
        total = float(self.total_var.get().replace("GHS ", ""))
        subtotal = sum(item["subtotal"] for item in self.cart)
        try: disc_value = float(self.discount_input.get())
        except ValueError: disc_value = 0
        discount = round(subtotal * disc_value / 100, 2) if self.discount_type.get() == "percent" else disc_value
        method = self.payment_method.get()
        if method == "Cash":
            paid = float(self.amount_paid_var.get() or 0)
            if paid < total:
                messagebox.showwarning("Insufficient Payment", f"Amount paid is less than total (GHS {total:.2f})."); return
            if not messagebox.askyesno("Confirm Checkout", f"Total: GHS {total:.2f}\nMethod: Cash\n\nProceed?"): return
            self.save_sale(total, discount, paid, method)
        elif method in ("Mobile Money", "Card"):
            if not messagebox.askyesno("Confirm Checkout", f"Total: GHS {total:.2f}\nMethod: {method} (Paystack)\n\nProceed?"): return
            from pos_paystack import PaystackPaymentWindow
            PaystackPaymentWindow(self.root, total,
                on_success=lambda amt, ref: self.on_paystack_success(amt, ref, total, discount, method),
                on_cancel=lambda: self.status_var.set("Payment cancelled."))

    def on_paystack_success(self, amount_paid, reference, total, discount, method):
        self.save_sale(total, discount, amount_paid, method, reference)

    def save_sale(self, total, discount, paid, method, reference=None):
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("INSERT INTO Sales (user_id,total_amount,discount,payment_method) VALUES (?,?,?,?)",
                       (self.user[0], total, discount, method))
        sale_id = cursor.lastrowid
        for item in self.cart:
            cursor.execute("INSERT INTO Sales_Items (sale_id,product_id,quantity,price,subtotal) VALUES (?,?,?,?,?)",
                           (sale_id, item["product_id"], item["quantity"], item["price"], item["subtotal"]))
            cursor.execute("UPDATE Products SET quantity=quantity-? WHERE product_id=?",
                           (item["quantity"], item["product_id"]))
            cursor.execute("INSERT INTO Inventory (product_id,change_type,quantity_change,note) VALUES (?,'Sale',?,?)",
                           (item["product_id"], -item["quantity"], f"Sale ID {sale_id}"))
        change = max(0, paid - total)
        cursor.execute("INSERT INTO Payments (sale_id,amount_paid,change_given,payment_method) VALUES (?,?,?,?)",
                       (sale_id, paid, change, method))
        conn.commit(); conn.close()
        self.show_receipt(sale_id, total, discount, paid, change, method)
        self.clear_cart(); self.load_all_products()
        self.status_var.set(f"✓ Sale #{sale_id} completed.")

    def show_receipt(self, sale_id, total, discount, paid, change, method):
        win = tk.Toplevel(self.root)
        win.title("Receipt — Franceskate Company Limited")
        win.geometry("360x540")
        win.configure(bg=WHITE)
        win.resizable(False, False)

        header = tk.Frame(win, bg=ACCENT, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="🛒 Franceskate Company Limited", font=("Helvetica", 11, "bold"), bg=ACCENT, fg=WHITE).pack()
        tk.Label(header, text="Official Receipt", font=("Helvetica", 9), bg=ACCENT, fg=ACCENT2).pack()

        text = tk.Text(win, bg=WHITE, fg=TEXT, font=("Courier", 10),
                       relief="flat", padx=15, pady=10)
        text.pack(fill="both", expand=True)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "─" * 36,
            f"Date    : {now}",
            f"Sale ID : #{sale_id}",
            f"Cashier : {self.user[1]}",
            "─" * 36,
            f"{'Item':<18} {'Qty':>3} {'Amount':>10}",
            "─" * 36,
        ]
        for item in self.cart:
            lines.append(f"{item['name'][:18]:<18} {item['quantity']:>3} GHS{item['subtotal']:>7.2f}")
        lines += [
            "─" * 36,
            f"{'Subtotal':<24} GHS{sum(i['subtotal'] for i in self.cart):>7.2f}",
            f"{'Discount':<24} GHS{discount:>7.2f}",
            f"{'TOTAL':<24} GHS{total:>7.2f}",
            f"{'Paid':<24} GHS{paid:>7.2f}",
            f"{'Change':<24} GHS{change:>7.2f}",
            f"{'Method':<24} {method}",
            "─" * 36,
            "   Thank you for shopping with us!",
            "      Franceskate Company Ltd",
            "─" * 36,
        ]
        text.insert("end", "\n".join(lines))
        text.config(state="disabled")
        tk.Button(win, text="Close", font=("Helvetica", 10, "bold"),
                  bg=DANGER, fg=WHITE, relief="flat",
                  command=win.destroy).pack(fill="x", padx=15, pady=10, ipady=6)


if __name__ == "__main__":
    root = tk.Tk()
    SalesProcessing(root)
    root.mainloop()
