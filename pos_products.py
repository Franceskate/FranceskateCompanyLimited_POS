import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "pos_system.db"
BG=("#F0F4F8");SIDEBAR=("#1A237E");ACCENT=("#1565C0");ACCENT2=("#E3F2FD");SUCCESS=("#2E7D32");DANGER=("#C62828");WARNING=("#F9A825");WHITE=("#FFFFFF");TEXT=("#212121");SUBTEXT=("#546E7A");BORDER=("#CFD8DC");CARD=("#FFFFFF")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def styled_btn(parent, text, color, command, width=None):
    kwargs = dict(text=text, font=("Helvetica", 10, "bold"), bg=color, fg=WHITE,
                  relief="flat", cursor="hand2", activeforeground=WHITE,
                  activebackground=color, command=command)
    if width: kwargs["width"] = width
    return tk.Button(parent, **kwargs)

class ProductManagement:
    def __init__(self, root, embedded=False):
        self.root = root
        self.embedded = embedded
        if not embedded:
            self.root.title("Product Management")
        if not embedded: self.root.geometry("1000x620")
        if not embedded: self.root.resizable(True, True)
        self.root.configure(bg=BG)
        self.selected_id = None
        self.build_ui()
        self.load_products()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=WHITE, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="Product Management", font=("Helvetica", 17, "bold"), bg=WHITE, fg=TEXT).pack(side="left", padx=25)
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=15)

        # LEFT form
        form_frame = tk.Frame(main, bg=CARD, width=270, highlightbackground=BORDER, highlightthickness=1)
        form_frame.pack(side="left", fill="y", padx=(0,15))
        form_frame.pack_propagate(False)

        tk.Label(form_frame, text="Product Details", font=("Helvetica", 12, "bold"), bg=CARD, fg=TEXT).pack(pady=(18,5), padx=20, anchor="w")
        tk.Frame(form_frame, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0,10))

        fields = [("Product Name","name"),("Category","category"),("Price (GHS)","price"),("Quantity","quantity"),("Barcode","barcode"),("Supplier","supplier")]
        self.vars = {}
        for label, key in fields:
            tk.Label(form_frame, text=label, font=("Helvetica", 9, "bold"), bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=20, pady=(8,2))
            var = tk.StringVar()
            e = tk.Entry(form_frame, textvariable=var, font=("Helvetica", 11), bg=BG, fg=TEXT, relief="flat", bd=0, insertbackground=TEXT)
            e.pack(fill="x", padx=20, ipady=7)
            tk.Frame(form_frame, bg=BORDER, height=1).pack(fill="x", padx=20)
            self.vars[key] = var

        btn_frame = tk.Frame(form_frame, bg=CARD)
        btn_frame.pack(fill="x", padx=20, pady=15)
        styled_btn(btn_frame, "Add Product", SUCCESS, self.add_product).pack(fill="x", ipady=7, pady=2)
        styled_btn(btn_frame, "Update Product", ACCENT, self.update_product).pack(fill="x", ipady=7, pady=2)
        styled_btn(btn_frame, "Delete Product", DANGER, self.delete_product).pack(fill="x", ipady=7, pady=2)
        tk.Button(btn_frame, text="Clear Form", font=("Helvetica", 10), bg=BG, fg=SUBTEXT, relief="flat", cursor="hand2", command=self.clear_form).pack(fill="x", ipady=6, pady=2)

        # RIGHT table
        right_frame = tk.Frame(main, bg=BG)
        right_frame.pack(side="left", fill="both", expand=True)

        search_frame = tk.Frame(right_frame, bg=BG)
        search_frame.pack(fill="x", pady=(0,10))
        tk.Label(search_frame, text="Search:", font=("Helvetica", 11), bg=BG, fg=SUBTEXT).pack(side="left", padx=(0,8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.load_products())
        se = tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 11), bg=CARD, fg=TEXT, relief="flat", bd=0, width=30, insertbackground=TEXT)
        se.pack(side="left", ipady=7)
        tk.Frame(search_frame, bg=BORDER, height=2, width=300).pack(side="left", anchor="s")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Pro.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=30, font=("Helvetica", 10))
        style.configure("Pro.Treeview.Heading", background=ACCENT2, foreground=ACCENT, font=("Helvetica", 10, "bold"), relief="flat")
        style.map("Pro.Treeview", background=[("selected", ACCENT2)], foreground=[("selected", ACCENT)])

        cols = ("ID","Name","Category","Price","Qty","Barcode","Supplier")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=18, style="Pro.Treeview")
        for col, w in zip(cols, [40,170,110,75,55,110,110]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self.root, textvariable=self.status_var, font=("Helvetica", 9), bg=WHITE, fg=SUCCESS, anchor="w").pack(fill="x", padx=15, pady=5)

    def load_products(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        search = self.search_var.get().strip()
        conn = get_connection(); cursor = conn.cursor()
        if search:
            cursor.execute("SELECT product_id,product_name,category,price,quantity,barcode,supplier FROM Products WHERE product_name LIKE ? OR category LIKE ? OR barcode LIKE ?", (f"%{search}%",f"%{search}%",f"%{search}%"))
        else:
            cursor.execute("SELECT product_id,product_name,category,price,quantity,barcode,supplier FROM Products")
        rows = cursor.fetchall(); conn.close()
        for row in rows: self.tree.insert("","end",values=row)
        self.status_var.set(f"{len(rows)} product(s) found.")

    def add_product(self):
        name=self.vars["name"].get().strip(); category=self.vars["category"].get().strip()
        price=self.vars["price"].get().strip(); quantity=self.vars["quantity"].get().strip()
        barcode=self.vars["barcode"].get().strip(); supplier=self.vars["supplier"].get().strip()
        if not name or not price or not quantity:
            messagebox.showwarning("Missing Fields","Name, Price, and Quantity are required."); return
        try: price=float(price); quantity=int(quantity)
        except ValueError: messagebox.showerror("Invalid Input","Price must be a number and Quantity must be whole."); return
        try:
            conn=get_connection(); cursor=conn.cursor()
            cursor.execute("INSERT INTO Products (product_name,category,price,quantity,barcode,supplier) VALUES (?,?,?,?,?,?)",(name,category,price,quantity,barcode or None,supplier or None))
            conn.commit(); conn.close(); self.clear_form(); self.load_products()
            self.status_var.set(f"✓ Product '{name}' added.")
        except sqlite3.IntegrityError: messagebox.showerror("Duplicate Barcode","A product with this barcode already exists.")

    def update_product(self):
        if not self.selected_id: messagebox.showwarning("No Selection","Please select a product."); return
        name=self.vars["name"].get().strip(); category=self.vars["category"].get().strip()
        price=self.vars["price"].get().strip(); quantity=self.vars["quantity"].get().strip()
        barcode=self.vars["barcode"].get().strip(); supplier=self.vars["supplier"].get().strip()
        if not name or not price or not quantity: messagebox.showwarning("Missing Fields","Name, Price, and Quantity are required."); return
        try: price=float(price); quantity=int(quantity)
        except ValueError: messagebox.showerror("Invalid Input","Price must be a number and Quantity must be whole."); return
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("UPDATE Products SET product_name=?,category=?,price=?,quantity=?,barcode=?,supplier=? WHERE product_id=?",(name,category,price,quantity,barcode or None,supplier or None,self.selected_id))
        conn.commit(); conn.close(); self.clear_form(); self.load_products()
        self.status_var.set("✓ Product updated.")

    def delete_product(self):
        if not self.selected_id: messagebox.showwarning("No Selection","Please select a product."); return
        if not messagebox.askyesno("Confirm Delete","Are you sure?"): return
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("DELETE FROM Products WHERE product_id=?",(self.selected_id,))
        conn.commit(); conn.close(); self.clear_form(); self.load_products()
        self.status_var.set("✓ Product deleted.")

    def on_select(self, event):
        selected=self.tree.selection()
        if not selected: return
        values=self.tree.item(selected[0],"values")
        self.selected_id=values[0]
        for i,key in enumerate(["name","category","price","quantity","barcode","supplier"]):
            self.vars[key].set(values[i+1])

    def clear_form(self):
        for var in self.vars.values(): var.set("")
        self.selected_id=None

if __name__ == "__main__":
    root=tk.Tk(); ProductManagement(root); root.mainloop()
