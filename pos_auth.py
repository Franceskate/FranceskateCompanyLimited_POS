import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib

DB_NAME = "pos_system.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, full_name, role FROM Users WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return user


# ─────────────────────────────────────────────
#  Dashboard placeholders
# ─────────────────────────────────────────────

def open_dashboard(root, user):
    # Destroy login window completely
    root.destroy()

    dash = tk.Tk()
    dash.resizable(False, False)
    dash.configure(bg="#1e1e2e")

    role = user[2]

    if role == "Admin":
        dash.title("Admin Dashboard")
        dash.geometry("500x300")
        tk.Label(dash, text="👑 Welcome, " + user[1] + "!",
                 font=("Helvetica", 18, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(pady=30)
        tk.Label(dash, text="Role: Administrator", font=("Helvetica", 12),
                 bg="#1e1e2e", fg="#a6e3a1").pack()
        tk.Label(dash, text="Full system access granted.", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#89b4fa").pack(pady=10)

    elif role == "Manager":
        dash.title("Manager Dashboard")
        dash.geometry("500x300")
        tk.Label(dash, text="📊 Welcome, " + user[1] + "!",
                 font=("Helvetica", 18, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(pady=30)
        tk.Label(dash, text="Role: Manager", font=("Helvetica", 12),
                 bg="#1e1e2e", fg="#f9e2af").pack()
        tk.Label(dash, text="Reports and inventory access granted.", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#89b4fa").pack(pady=10)

    else:
        dash.title("Cashier Dashboard")
        dash.geometry("500x300")
        tk.Label(dash, text="🧾 Welcome, " + user[1] + "!",
                 font=("Helvetica", 18, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(pady=30)
        tk.Label(dash, text="Role: Cashier", font=("Helvetica", 12),
                 bg="#1e1e2e", fg="#89dceb").pack()
        tk.Label(dash, text="Sales processing access granted.", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#89b4fa").pack(pady=10)

    dash.mainloop()


# ─────────────────────────────────────────────
#  Login Window
# ─────────────────────────────────────────────

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POS System — Login")
        self.root.geometry("420x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.attempts = 0
        self.max_attempts = 3
        self.build_ui()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#181825", pady=20)
        header.pack(fill="x")

        tk.Label(header, text="🛒", font=("Helvetica", 36),
                 bg="#181825").pack()
        tk.Label(header, text="POS System", font=("Helvetica", 20, "bold"),
                 bg="#181825", fg="#cdd6f4").pack()
        tk.Label(header, text="Please sign in to continue", font=("Helvetica", 10),
                 bg="#181825", fg="#6c7086").pack(pady=(2, 0))

        # Form
        form = tk.Frame(self.root, bg="#1e1e2e", padx=40)
        form.pack(fill="both", expand=True, pady=20)

        tk.Label(form, text="Username", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#bac2de", anchor="w").pack(fill="x", pady=(10, 3))
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(form, textvariable=self.username_var,
                                  font=("Helvetica", 12), bg="#313244",
                                  fg="#cdd6f4", insertbackground="#cdd6f4",
                                  relief="flat", bd=8)
        username_entry.pack(fill="x", ipady=6)
        username_entry.focus()

        tk.Label(form, text="Password", font=("Helvetica", 11),
                 bg="#1e1e2e", fg="#bac2de", anchor="w").pack(fill="x", pady=(15, 3))
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(form, textvariable=self.password_var,
                                       show="*", font=("Helvetica", 12),
                                       bg="#313244", fg="#cdd6f4",
                                       insertbackground="#cdd6f4",
                                       relief="flat", bd=8)
        self.password_entry.pack(fill="x", ipady=6)

        self.show_pw = tk.BooleanVar()
        tk.Checkbutton(form, text="Show password", variable=self.show_pw,
                       command=self.toggle_password,
                       bg="#1e1e2e", fg="#6c7086",
                       selectcolor="#313244",
                       activebackground="#1e1e2e").pack(anchor="w", pady=(5, 0))

        self.status_var = tk.StringVar()
        tk.Label(form, textvariable=self.status_var, font=("Helvetica", 10),
                 bg="#1e1e2e", fg="#f38ba8").pack(pady=(8, 0))

        self.login_btn = tk.Button(form, text="Login", font=("Helvetica", 13, "bold"),
                                   bg="#89b4fa", fg="#1e1e2e", relief="flat",
                                   cursor="hand2", activebackground="#b4d0fb",
                                   command=self.handle_login)
        self.login_btn.pack(fill="x", ipady=8, pady=(10, 0))

        self.root.bind("<Return>", lambda e: self.handle_login())

        tk.Label(self.root, text="© 2025 POS Student Project",
                 font=("Helvetica", 9), bg="#1e1e2e", fg="#45475a").pack(pady=10)

    def toggle_password(self):
        self.password_entry.config(show="" if self.show_pw.get() else "*")

    def handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.status_var.set("⚠ Please enter username and password.")
            return

        user = authenticate(username, password)

        if user:
            self.attempts = 0
            self.status_var.set("")
            # Open dashboard (destroys login window and opens new one)
            open_dashboard(self.root, user)

        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts
            if remaining > 0:
                self.status_var.set(f"❌ Invalid credentials. {remaining} attempt(s) left.")
                self.password_var.set("")
            else:
                self.status_var.set("🔒 Too many failed attempts. Exiting.")
                self.login_btn.config(state="disabled")
                self.root.after(2000, self.root.destroy)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
