import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "pos_system.db"
BG=("#F0F4F8");ACCENT=("#1565C0");ACCENT2=("#E3F2FD");SUCCESS=("#2E7D32");DANGER=("#C62828");WARNING=("#F9A825");WHITE=("#FFFFFF");TEXT=("#212121");SUBTEXT=("#546E7A");BORDER=("#CFD8DC");CARD=("#FFFFFF")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

class CustomerManagement:
    def __init__(self, root, embedded=False):
        self.root = root
        self.embedded = embedded
        if not embedded:
            self.root.title("Customer Management")
        if not embedded: self.root.geometry("1050x620")
        if not embedded: self.root.resizable(True, True)
        self.root.configure(bg=BG)
        self.selected_id = None
        self.build_ui()
        self.load_customers()

    def build_ui(self):
        header = tk.Frame(self.root, bg=WHITE, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="Customer Management", font=("Helvetica", 17, "bold"), bg=WHITE, fg=TEXT).pack(side="left", padx=25)
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=15)

        # LEFT form
        form_frame = tk.Frame(main, bg=CARD, width=270, highlightbackground=BORDER, highlightthickness=1)
        form_frame.pack(side="left", fill="y", padx=(0,15))
        form_frame.pack_propagate(False)

        tk.Label(form_frame, text="Customer Details", font=("Helvetica", 12, "bold"), bg=CARD, fg=TEXT).pack(pady=(18,5), padx=20, anchor="w")
        tk.Frame(form_frame, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0,10))

        self.vars = {}
        for label, key in [("Full Name","name"),("Phone Number","phone"),("Email","email"),("Address","address"),("Loyalty Points","loyalty")]:
            tk.Label(form_frame, text=label, font=("Helvetica", 9, "bold"), bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=20, pady=(8,2))
            var = tk.StringVar()
            tk.Entry(form_frame, textvariable=var, font=("Helvetica", 11), bg=BG, fg=TEXT, relief="flat", bd=0, insertbackground=TEXT).pack(fill="x", padx=20, ipady=7)
            tk.Frame(form_frame, bg=BORDER, height=1).pack(fill="x", padx=20)
            self.vars[key] = var

        btn_frame = tk.Frame(form_frame, bg=CARD)
        btn_frame.pack(fill="x", padx=20, pady=15)
        for text, color, cmd in [("Add Customer",SUCCESS,self.add_customer),("Update Customer",ACCENT,self.update_customer),("Delete Customer",DANGER,self.delete_customer),("View History",WARNING,self.view_history)]:
            tk.Button(btn_frame, text=text, font=("Helvetica", 10, "bold"), bg=color, fg=WHITE, relief="flat", cursor="hand2", command=cmd).pack(fill="x", ipady=7, pady=2)
        tk.Button(btn_frame, text="Clear Form", font=("Helvetica", 10), bg=BG, fg=SUBTEXT, relief="flat", cursor="hand2", command=self.clear_form).pack(fill="x", ipady=6, pady=2)

        # RIGHT table
        right_frame = tk.Frame(main, bg=BG)
        right_frame.pack(side="left", fill="both", expand=True)

        sf = tk.Frame(right_frame, bg=BG)
        sf.pack(fill="x", pady=(0,10))
        tk.Label(sf, text="Search:", font=("Helvetica", 11), bg=BG, fg=SUBTEXT).pack(side="left", padx=(0,8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.load_customers())
        tk.Entry(sf, textvariable=self.search_var, font=("Helvetica", 11), bg=CARD, fg=TEXT, relief="flat", bd=0, width=30, insertbackground=TEXT).pack(side="left", ipady=7)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Pro.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=30, font=("Helvetica", 10))
        style.configure("Pro.Treeview.Heading", background=ACCENT2, foreground=ACCENT, font=("Helvetica", 10, "bold"), relief="flat")
        style.map("Pro.Treeview", background=[("selected", ACCENT2)], foreground=[("selected", ACCENT)])

        cols = ("ID","Name","Phone","Email","Address","Points")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=18, style="Pro.Treeview")
        for col, w in zip(cols, [40,170,120,180,140,70]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self.root, textvariable=self.status_var, font=("Helvetica", 9), bg=WHITE, fg=SUCCESS, anchor="w").pack(fill="x", padx=15, pady=5)

    def load_customers(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        search = self.search_var.get().strip()
        conn = get_connection(); cursor = conn.cursor()
        if search:
            cursor.execute("SELECT customer_id,name,phone,email,address,loyalty_points FROM Customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?", (f"%{search}%",f"%{search}%",f"%{search}%"))
        else:
            cursor.execute("SELECT customer_id,name,phone,email,address,loyalty_points FROM Customers ORDER BY customer_id DESC")
        rows = cursor.fetchall(); conn.close()
        for row in rows: self.tree.insert("","end",values=row)
        self.status_var.set(f"{len(rows)} customer(s) found.")

    def add_customer(self):
        name=self.vars["name"].get().strip()
        if not name: messagebox.showwarning("Missing Field","Customer name is required."); return
        loyalty=self.vars["loyalty"].get().strip() or "0"
        try: loyalty=int(loyalty)
        except ValueError: messagebox.showerror("Invalid Input","Loyalty points must be a whole number."); return
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("INSERT INTO Customers (name,phone,email,address,loyalty_points) VALUES (?,?,?,?,?)",(name,self.vars["phone"].get().strip() or None,self.vars["email"].get().strip() or None,self.vars["address"].get().strip() or None,loyalty))
        conn.commit(); conn.close(); self.clear_form(); self.load_customers()
        self.status_var.set(f"✓ Customer '{name}' added.")

    def update_customer(self):
        if not self.selected_id: messagebox.showwarning("No Selection","Please select a customer."); return
        name=self.vars["name"].get().strip()
        if not name: messagebox.showwarning("Missing Field","Customer name is required."); return
        try: loyalty=int(self.vars["loyalty"].get().strip() or "0")
        except ValueError: messagebox.showerror("Invalid Input","Loyalty points must be a whole number."); return
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("UPDATE Customers SET name=?,phone=?,email=?,address=?,loyalty_points=? WHERE customer_id=?",(name,self.vars["phone"].get().strip() or None,self.vars["email"].get().strip() or None,self.vars["address"].get().strip() or None,loyalty,self.selected_id))
        conn.commit(); conn.close(); self.clear_form(); self.load_customers()
        self.status_var.set("✓ Customer updated.")

    def delete_customer(self):
        if not self.selected_id: messagebox.showwarning("No Selection","Please select a customer."); return
        if not messagebox.askyesno("Confirm Delete","Are you sure?"): return
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("DELETE FROM Customers WHERE customer_id=?",(self.selected_id,))
        conn.commit(); conn.close(); self.clear_form(); self.load_customers()
        self.status_var.set("✓ Customer deleted.")

    def view_history(self):
        if not self.selected_id: messagebox.showwarning("No Selection","Please select a customer."); return
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("SELECT name FROM Customers WHERE customer_id=?",(self.selected_id,))
        customer_name=cursor.fetchone()[0]
        cursor.execute('''SELECT s.sale_id,s.date,s.total_amount,s.payment_method,COUNT(si.sale_item_id) FROM Sales s JOIN Sales_Items si ON s.sale_id=si.sale_id WHERE s.customer_id=? GROUP BY s.sale_id ORDER BY s.sale_id DESC''',(self.selected_id,))
        rows=cursor.fetchall(); conn.close()

        win=tk.Toplevel(self.root); win.title(f"History - {customer_name}"); win.geometry("600x380"); win.configure(bg=BG)
        tk.Label(win, text=f"Purchase History: {customer_name}", font=("Helvetica", 13, "bold"), bg=BG, fg=TEXT).pack(pady=15, padx=15, anchor="w")
        if not rows:
            tk.Label(win, text="No purchase history found.", font=("Helvetica", 11), bg=BG, fg=SUBTEXT).pack(pady=20)
        else:
            cols=("Sale ID","Date","Total","Method","Items")
            tree=ttk.Treeview(win, columns=cols, show="headings", height=10, style="Pro.Treeview")
            for col,w in zip(cols,[80,160,120,130,70]):
                tree.heading(col,text=col); tree.column(col,width=w,anchor="center")
            for row in rows: tree.insert("","end",values=(row[0],row[1][:16],f"GHS {row[2]:.2f}",row[3],row[4]))
            tree.pack(fill="both", expand=True, padx=15)
        tk.Button(win, text="Close", font=("Helvetica", 10, "bold"), bg=DANGER, fg=WHITE, relief="flat", command=win.destroy).pack(fill="x", padx=15, pady=10, ipady=6)

    def on_select(self, event):
        selected=self.tree.selection()
        if not selected: return
        values=self.tree.item(selected[0],"values")
        self.selected_id=values[0]
        for i,key in enumerate(["name","phone","email","address","loyalty"]):
            self.vars[key].set(values[i+1])

    def clear_form(self):
        for var in self.vars.values(): var.set("")
        self.selected_id=None

if __name__ == "__main__":
    root=tk.Tk(); CustomerManagement(root); root.mainloop()
