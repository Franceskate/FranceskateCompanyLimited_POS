import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = "pos_system.db"
BG=("#F0F4F8");SIDEBAR=("#1A237E");ACCENT=("#1565C0");ACCENT2=("#E3F2FD");SUCCESS=("#2E7D32");DANGER=("#C62828");WARNING=("#F9A825");WHITE=("#FFFFFF");TEXT=("#212121");SUBTEXT=("#546E7A");BORDER=("#CFD8DC");CARD=("#FFFFFF")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

class Reports:
    def __init__(self, root, embedded=False):
        self.root = root
        self.embedded = embedded
        if not embedded:
            self.root.title("Reports & Analytics")
        if not embedded: self.root.geometry("1050x650")
        if not embedded: self.root.resizable(True, True)
        self.root.configure(bg=BG)
        self.build_ui()
        self.show_daily_report()

    def build_ui(self):
        header = tk.Frame(self.root, bg=WHITE, pady=16)
        header.pack(fill="x")
        tk.Label(header, text="Reports & Analytics", font=("Helvetica", 17, "bold"), bg=WHITE, fg=TEXT).pack(side="left", padx=25)
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        # Tab bar
        tab_bar = tk.Frame(self.root, bg=BG, pady=12)
        tab_bar.pack(fill="x", padx=20)
        self.tab_btns = {}
        tabs = [("Daily Sales","daily"),("Weekly Sales","weekly"),("Top Products","products"),("Inventory","inventory"),("Cashier Report","cashier")]
        for label, key in tabs:
            btn = tk.Button(tab_bar, text=label, font=("Helvetica", 10, "bold"),
                            bg=CARD, fg=SUBTEXT, relief="flat", cursor="hand2",
                            activebackground=ACCENT2, activeforeground=ACCENT,
                            highlightbackground=BORDER, highlightthickness=1,
                            command=lambda k=key, l=label: self.switch_tab(k, l))
            btn.pack(side="left", padx=(0,8), ipady=7, ipadx=14)
            self.tab_btns[key] = btn

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill="both", expand=True, padx=20, pady=(5,15))

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self.root, textvariable=self.status_var, font=("Helvetica", 9), bg=WHITE, fg=SUCCESS, anchor="w").pack(fill="x", padx=15, pady=5)

    def switch_tab(self, key, label=None):
        for k, btn in self.tab_btns.items():
            btn.config(bg=CARD, fg=SUBTEXT)
        self.tab_btns[key].config(bg=ACCENT, fg=WHITE)
        {"daily":self.show_daily_report,"weekly":self.show_weekly_report,"products":self.show_top_products,"inventory":self.show_inventory_report,"cashier":self.show_cashier_report}[key]()

    def clear_content(self):
        for w in self.content.winfo_children(): w.destroy()

    def summary_cards(self, parent, cards):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", pady=(0,15))
        colors = [ACCENT, SUCCESS, WARNING, DANGER]
        icons  = ["📊","💰","📦","👥"]
        for (label, value), color, icon in zip(cards, colors, icons):
            card = tk.Frame(frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            card.pack(side="left", padx=(0,12), fill="y")
            tk.Frame(card, bg=color, width=5).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=CARD, padx=18, pady=14)
            inner.pack(side="left")
            tk.Label(inner, text=icon+"  "+label, font=("Helvetica", 9), bg=CARD, fg=SUBTEXT).pack(anchor="w")
            tk.Label(inner, text=value, font=("Helvetica", 18, "bold"), bg=CARD, fg=color).pack(anchor="w", pady=(4,0))

    def make_table(self, parent, columns, widths, data, height=14):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Pro.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=30, font=("Helvetica", 10))
        style.configure("Pro.Treeview.Heading", background=ACCENT2, foreground=ACCENT, font=("Helvetica", 10, "bold"), relief="flat")
        style.map("Pro.Treeview", background=[("selected", ACCENT2)], foreground=[("selected", ACCENT)])
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height, style="Pro.Treeview")
        for col, w in zip(columns, widths):
            tree.heading(col, text=col); tree.column(col, width=w, anchor="center")
        for row in data: tree.insert("","end",values=row)
        tree.pack(fill="both", expand=True)
        return tree

    def show_daily_report(self):
        self.clear_content()
        self.switch_tab.__func__  # just highlight
        today = datetime.now().strftime("%Y-%m-%d")
        tk.Label(self.content, text=f"Daily Sales — {today}", font=("Helvetica", 13, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,12))
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("SELECT COUNT(*),COALESCE(SUM(total_amount),0),COALESCE(SUM(discount),0) FROM Sales WHERE DATE(date)=?",(today,))
        count,revenue,discounts=cursor.fetchone()
        cursor.execute("SELECT COALESCE(SUM(si.quantity),0) FROM Sales s JOIN Sales_Items si ON s.sale_id=si.sale_id WHERE DATE(s.date)=?",(today,))
        items=cursor.fetchone()[0]
        self.summary_cards(self.content,[("Total Sales",str(count)),("Revenue",f"GHS {revenue:.2f}"),("Items Sold",str(items)),("Discounts",f"GHS {discounts:.2f}")])
        cursor.execute("SELECT s.sale_id,s.date,u.full_name,s.total_amount,s.payment_method FROM Sales s JOIN Users u ON s.user_id=u.user_id WHERE DATE(s.date)=? ORDER BY s.sale_id DESC",(today,))
        rows=[(r[0],r[1][:16],r[2],f"GHS {r[3]:.2f}",r[4]) for r in cursor.fetchall()]; conn.close()
        self.make_table(self.content,("Sale ID","Time","Cashier","Total","Method"),[80,150,180,110,130],rows)
        self.status_var.set(f"Daily report — {count} sale(s) today.")
        self.tab_btns["daily"].config(bg=ACCENT, fg=WHITE)

    def show_weekly_report(self):
        self.clear_content()
        tk.Label(self.content, text="Weekly Sales — Last 7 Days", font=("Helvetica", 13, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,12))
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("SELECT COUNT(*),COALESCE(SUM(total_amount),0) FROM Sales WHERE date>=datetime('now','-7 days')")
        count,revenue=cursor.fetchone()
        cursor.execute("SELECT COALESCE(SUM(si.quantity),0) FROM Sales s JOIN Sales_Items si ON s.sale_id=si.sale_id WHERE s.date>=datetime('now','-7 days')")
        items=cursor.fetchone()[0]; avg=revenue/count if count>0 else 0
        self.summary_cards(self.content,[("Total Sales",str(count)),("Revenue",f"GHS {revenue:.2f}"),("Items Sold",str(items)),("Avg Sale",f"GHS {avg:.2f}")])
        cursor.execute("SELECT DATE(date),COUNT(*),COALESCE(SUM(total_amount),0) FROM Sales WHERE date>=datetime('now','-7 days') GROUP BY DATE(date) ORDER BY DATE(date) DESC")
        rows=[(r[0],r[1],f"GHS {r[2]:.2f}") for r in cursor.fetchall()]; conn.close()
        self.make_table(self.content,("Date","No. of Sales","Revenue"),[200,220,220],rows)
        self.status_var.set(f"Weekly report — {count} sale(s) in last 7 days.")

    def show_top_products(self):
        self.clear_content()
        tk.Label(self.content, text="Top Selling Products", font=("Helvetica", 13, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,12))
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("SELECT p.product_name,p.category,SUM(si.quantity),SUM(si.subtotal) FROM Sales_Items si JOIN Products p ON si.product_id=p.product_id GROUP BY si.product_id ORDER BY SUM(si.quantity) DESC")
        rows=[(r[0],r[1],r[2],f"GHS {r[3]:.2f}") for r in cursor.fetchall()]
        cursor.execute("SELECT COALESCE(SUM(subtotal),0) FROM Sales_Items"); total_rev=cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(quantity),0) FROM Sales_Items"); total_qty=cursor.fetchone()[0]; conn.close()
        self.summary_cards(self.content,[("Products Sold",str(len(rows))),("Total Revenue",f"GHS {total_rev:.2f}"),("Units Sold",str(total_qty)),("Top Product",rows[0][0][:12] if rows else "N/A")])
        self.make_table(self.content,("Product","Category","Units Sold","Revenue"),[230,160,130,140],rows)
        self.status_var.set(f"Product report — {len(rows)} product(s).")

    def show_inventory_report(self):
        self.clear_content()
        tk.Label(self.content, text="Inventory Report", font=("Helvetica", 13, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,12))
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products"); total=cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Products WHERE quantity=0"); out=cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Products WHERE quantity>0 AND quantity<10"); low=cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Products WHERE quantity>=10"); ok=cursor.fetchone()[0]
        self.summary_cards(self.content,[("Total Products",str(total)),("In Stock",str(ok)),("Low Stock (<10)",str(low)),("Out of Stock",str(out))])
        cursor.execute("SELECT product_name,category,price,quantity,CASE WHEN quantity=0 THEN 'Out of Stock' WHEN quantity<10 THEN 'Low Stock' ELSE 'OK' END FROM Products ORDER BY quantity ASC")
        rows=[(r[0],r[1],f"GHS {r[2]:.2f}",r[3],r[4]) for r in cursor.fetchall()]; conn.close()
        self.make_table(self.content,("Product","Category","Price","Qty","Status"),[220,150,110,80,110],rows)
        self.status_var.set(f"Inventory report — {total} product(s).")

    def show_cashier_report(self):
        self.clear_content()
        tk.Label(self.content, text="Cashier Performance Report", font=("Helvetica", 13, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,12))
        conn=get_connection(); cursor=conn.cursor()
        cursor.execute("SELECT u.full_name,u.role,COUNT(s.sale_id),COALESCE(SUM(s.total_amount),0) FROM Users u LEFT JOIN Sales s ON u.user_id=s.user_id GROUP BY u.user_id ORDER BY SUM(s.total_amount) DESC")
        rows=[(r[0],r[1],r[2],f"GHS {r[3]:.2f}") for r in cursor.fetchall()]
        cursor.execute("SELECT COUNT(*) FROM Users"); total_users=cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(total_amount),0) FROM Sales"); total_rev=cursor.fetchone()[0]; conn.close()
        self.summary_cards(self.content,[("Total Staff",str(total_users)),("Total Revenue",f"GHS {total_rev:.2f}"),("Top Cashier",rows[0][0].split()[0] if rows else "N/A"),("","—")])
        self.make_table(self.content,("Cashier","Role","Sales Made","Revenue Generated"),[210,140,140,170],rows)
        self.status_var.set(f"Cashier report — {total_users} staff member(s).")

if __name__ == "__main__":
    root=tk.Tk(); Reports(root); root.mainloop()
