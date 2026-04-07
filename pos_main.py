import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib

DB_NAME = "pos_system.db"

BG          = "#F0F4F8"
SIDEBAR     = "#1A237E"
SIDEBAR_HVR = "#283593"
ACCENT      = "#1565C0"
ACCENT2     = "#E3F2FD"
SUCCESS     = "#2E7D32"
DANGER      = "#C62828"
WARNING     = "#F9A825"
WHITE       = "#FFFFFF"
TEXT        = "#212121"
SUBTEXT     = "#546E7A"
BORDER      = "#CFD8DC"
CARD        = "#FFFFFF"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, full_name, role FROM Users WHERE username = ? AND password = ?",
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Franceskate Company Limited — POS")
        self.root.geometry("900x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.attempts = 0
        self.build_ui()

    def build_ui(self):
        left = tk.Frame(self.root, bg=SIDEBAR, width=420)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Frame(left, bg=SIDEBAR).pack(expand=True)
        tk.Label(left, text="🛒", font=("Helvetica", 48), bg=SIDEBAR, fg=WHITE).pack(pady=(0, 8))
        tk.Label(left, text="Franceskate Company", font=("Helvetica", 18, "bold"), bg=SIDEBAR, fg=WHITE).pack()
        tk.Label(left, text="Limited", font=("Helvetica", 18, "bold"), bg=SIDEBAR, fg=WHITE).pack()
        tk.Label(left, text="Point of Sale System", font=("Helvetica", 11), bg=SIDEBAR, fg="#90CAF9").pack(pady=(6, 0))
        tk.Frame(left, bg="#3949AB", height=2).pack(fill="x", padx=40, pady=25)
        for f in ["✓  Sales Processing", "✓  Inventory Management", "✓  Customer Tracking", "✓  Reports & Analytics"]:
            tk.Label(left, text=f, font=("Helvetica", 11), bg=SIDEBAR, fg="#BBDEFB").pack(anchor="w", padx=50, pady=3)
        tk.Frame(left, bg=SIDEBAR).pack(expand=True)
        tk.Label(left, text="© 2025 Franceskate Company Limited", font=("Helvetica", 9), bg=SIDEBAR, fg="#5C6BC0").pack(pady=20)

        right = tk.Frame(self.root, bg=WHITE)
        right.pack(side="left", fill="both", expand=True)

        form_wrap = tk.Frame(right, bg=WHITE)
        form_wrap.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form_wrap, text="Welcome Back", font=("Helvetica", 22, "bold"), bg=WHITE, fg=TEXT).pack(anchor="w")
        tk.Label(form_wrap, text="Sign in to your account to continue", font=("Helvetica", 11), bg=WHITE, fg=SUBTEXT).pack(anchor="w", pady=(4, 25))

        tk.Label(form_wrap, text="USERNAME", font=("Helvetica", 9, "bold"), bg=WHITE, fg=SUBTEXT).pack(anchor="w")
        self.username_var = tk.StringVar()
        user_entry = tk.Entry(form_wrap, textvariable=self.username_var, font=("Helvetica", 12),
                              bg=BG, fg=TEXT, relief="flat", bd=0, width=28, insertbackground=TEXT)
        user_entry.pack(fill="x", ipady=10, pady=(4, 0))
        tk.Frame(form_wrap, bg=BORDER, height=2).pack(fill="x")
        user_entry.focus()

        tk.Label(form_wrap, text="PASSWORD", font=("Helvetica", 9, "bold"), bg=WHITE, fg=SUBTEXT).pack(anchor="w", pady=(20, 0))
        self.password_var = tk.StringVar()
        self.pw_entry = tk.Entry(form_wrap, textvariable=self.password_var, show="*",
                                 font=("Helvetica", 12), bg=BG, fg=TEXT, relief="flat", bd=0,
                                 width=28, insertbackground=TEXT)
        self.pw_entry.pack(fill="x", ipady=10, pady=(4, 0))
        tk.Frame(form_wrap, bg=BORDER, height=2).pack(fill="x")

        self.show_pw = tk.BooleanVar()
        tk.Checkbutton(form_wrap, text="Show password", variable=self.show_pw,
                       command=self.toggle_pw, bg=WHITE, fg=SUBTEXT, selectcolor=WHITE,
                       activebackground=WHITE, font=("Helvetica", 10), cursor="hand2").pack(anchor="w", pady=(8, 0))

        self.status_var = tk.StringVar()
        tk.Label(form_wrap, textvariable=self.status_var, font=("Helvetica", 10),
                 bg=WHITE, fg=DANGER).pack(pady=(8, 0))

        self.login_btn = tk.Button(form_wrap, text="SIGN IN", font=("Helvetica", 12, "bold"),
                                   bg=ACCENT, fg=WHITE, relief="flat", cursor="hand2",
                                   activebackground=SIDEBAR, activeforeground=WHITE,
                                   command=self.handle_login)
        self.login_btn.pack(fill="x", ipady=12, pady=(15, 0))
        self.root.bind("<Return>", lambda e: self.handle_login())

    def toggle_pw(self):
        self.pw_entry.config(show="" if self.show_pw.get() else "*")

    def handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            self.status_var.set("⚠  Please enter username and password.")
            return
        user = authenticate(username, password)
        if user:
            self.root.destroy()
            launch_dashboard(user)
        else:
            self.attempts += 1
            remaining = 3 - self.attempts
            if remaining > 0:
                self.status_var.set(f"❌  Invalid credentials. {remaining} attempt(s) left.")
                self.password_var.set("")
            else:
                self.status_var.set("🔒  Too many failed attempts. Exiting.")
                self.login_btn.config(state="disabled")
                self.root.after(2000, self.root.destroy)


class Dashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("Franceskate Company Limited — POS System")
        self.root.geometry("1250x720")
        self.root.resizable(True, True)
        self.root.configure(bg=BG)
        self.build_ui()

    def build_ui(self):
        # ── Sidebar ──
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(self.sidebar, bg="#0D1B6E", pady=15)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="🛒", font=("Helvetica", 22), bg="#0D1B6E", fg=WHITE).pack()
        tk.Label(logo_frame, text="Franceskate Company", font=("Helvetica", 10, "bold"), bg="#0D1B6E", fg=WHITE).pack()
        tk.Label(logo_frame, text="Limited", font=("Helvetica", 10, "bold"), bg="#0D1B6E", fg=WHITE).pack()

        # User info
        user_frame = tk.Frame(self.sidebar, bg=SIDEBAR, pady=12)
        user_frame.pack(fill="x")
        tk.Frame(user_frame, bg="#3949AB", height=1).pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(user_frame, text=self.user[1], font=("Helvetica", 10, "bold"), bg=SIDEBAR, fg=WHITE).pack(padx=15, anchor="w")
        tk.Label(user_frame, text=self.user[2], font=("Helvetica", 9), bg=SIDEBAR, fg="#90CAF9").pack(padx=15, anchor="w")
        tk.Frame(user_frame, bg="#3949AB", height=1).pack(fill="x", padx=15, pady=(10, 0))

        # Nav buttons
        self.nav_buttons = {}
        for label, icon, command in self.get_nav_items():
            btn = tk.Button(self.sidebar, text=f"   {icon}   {label}",
                            font=("Helvetica", 11), bg=SIDEBAR, fg="#BBDEFB",
                            relief="flat", anchor="w", cursor="hand2",
                            activebackground=SIDEBAR_HVR, activeforeground=WHITE,
                            command=lambda c=command, l=label: self.nav_click(c, l))
            btn.pack(fill="x", padx=8, pady=2, ipady=10)
            self.nav_buttons[label] = btn

        tk.Frame(self.sidebar, bg="#3949AB", height=1).pack(fill="x", padx=15, pady=10)
        tk.Button(self.sidebar, text="   →   Logout", font=("Helvetica", 11),
                  bg=SIDEBAR, fg="#EF9A9A", relief="flat", anchor="w", cursor="hand2",
                  activebackground="#B71C1C", activeforeground=WHITE,
                  command=self.logout).pack(fill="x", padx=8, pady=2, ipady=10)

        tk.Frame(self.sidebar, bg=SIDEBAR).pack(expand=True)
        tk.Label(self.sidebar, text="© 2025 Franceskate Co. Ltd",
                 font=("Helvetica", 8), bg=SIDEBAR, fg="#3949AB").pack(pady=10)

        # ── Content area ──
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.nav_click(self.show_home, "Dashboard")

    def nav_click(self, command, label):
        for lbl, btn in self.nav_buttons.items():
            btn.config(bg=SIDEBAR, fg="#BBDEFB")
        if label in self.nav_buttons:
            self.nav_buttons[label].config(bg=SIDEBAR_HVR, fg=WHITE)
        command()

    def get_nav_items(self):
        role = self.user[2]
        items = [("Dashboard", "⊞", self.show_home), ("Sales", "🧾", self.show_sales)]
        if role in ("Admin", "Manager"):
            items += [("Products", "📦", self.show_products),
                      ("Customers", "👥", self.show_customers),
                      ("Reports", "📊", self.show_reports)]
        return items

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def make_header(self, title, subtitle=""):
        header = tk.Frame(self.content, bg=WHITE, pady=18)
        header.pack(fill="x")
        tk.Label(header, text=title, font=("Helvetica", 18, "bold"), bg=WHITE, fg=TEXT).pack(anchor="w", padx=25)
        if subtitle:
            tk.Label(header, text=subtitle, font=("Helvetica", 10), bg=WHITE, fg=SUBTEXT).pack(anchor="w", padx=25)
        tk.Frame(self.content, bg=BORDER, height=1).pack(fill="x")

    # ── Dashboard Home ──
    def show_home(self):
        self.clear_content()
        self.make_header("Dashboard", f"Welcome back, {self.user[1]}!")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True, padx=25, pady=20)

        stats = self.get_stats()
        colors = [ACCENT, SUCCESS, WARNING, DANGER]
        icons  = ["📦", "🧾", "💰", "👥"]
        cards_frame = tk.Frame(body, bg=BG)
        cards_frame.pack(fill="x", pady=(0, 20))
        for (label, value), color, icon in zip(stats, colors, icons):
            card = tk.Frame(cards_frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            card.pack(side="left", padx=(0, 15), fill="y")
            tk.Frame(card, bg=color, width=5).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=CARD, padx=20, pady=18)
            inner.pack(side="left")
            tk.Label(inner, text=icon + "  " + label, font=("Helvetica", 10), bg=CARD, fg=SUBTEXT).pack(anchor="w")
            tk.Label(inner, text=value, font=("Helvetica", 22, "bold"), bg=CARD, fg=color).pack(anchor="w", pady=(5, 0))

        tk.Label(body, text="Recent Sales", font=("Helvetica", 13, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(10, 8))
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Pro.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=30, font=("Helvetica", 10))
        style.configure("Pro.Treeview.Heading", background=ACCENT2, foreground=ACCENT, font=("Helvetica", 10, "bold"), relief="flat")
        style.map("Pro.Treeview", background=[("selected", ACCENT2)], foreground=[("selected", ACCENT)])

        cols = ("Sale ID", "Date", "Cashier", "Total", "Method")
        tree = ttk.Treeview(body, columns=cols, show="headings", height=8, style="Pro.Treeview")
        for col, w in zip(cols, [80, 160, 180, 120, 130]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute('''SELECT s.sale_id,s.date,u.full_name,s.total_amount,s.payment_method
                          FROM Sales s JOIN Users u ON s.user_id=u.user_id
                          ORDER BY s.sale_id DESC LIMIT 8''')
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[0], row[1][:16], row[2], f"GHS {row[3]:.2f}", row[4]))
        conn.close()
        tree.pack(fill="both", expand=True)

    def get_stats(self):
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products"); products = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Sales"); sales = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM Sales"); revenue = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Customers"); customers = cursor.fetchone()[0]
        conn.close()
        return [("Products", str(products)), ("Total Sales", str(sales)),
                ("Revenue", f"GHS {revenue:.0f}"), ("Customers", str(customers))]

    # ── Sales — embedded in content area ──
    def show_sales(self):
        self.clear_content()
        self.make_header("Sales Processing", f"Cashier: {self.user[1]}")
        from pos_sales import SalesProcessing
        SalesProcessing(self.content, self.user, embedded=True)

    # ── Products — embedded ──
    def show_products(self):
        self.clear_content()
        from pos_products import ProductManagement
        ProductManagement(self.content, embedded=True)

    # ── Customers — embedded ──
    def show_customers(self):
        self.clear_content()
        from pos_customers import CustomerManagement
        CustomerManagement(self.content, embedded=True)

    # ── Reports — embedded ──
    def show_reports(self):
        self.clear_content()
        from pos_reports import Reports
        Reports(self.content, embedded=True)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            start_login()


def launch_dashboard(user):
    root = tk.Tk()
    Dashboard(root, user)
    root.mainloop()

def start_login():
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    start_login()
