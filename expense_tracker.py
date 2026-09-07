import sqlite3
import datetime
import customtkinter as ctk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Visual Palette
ctk.set_appearance_mode("Dark")

BG_COLOR = "#0D1117"          # Dark canvas background
PANEL_BG = "#161B22"          # Sleek card container color
ACCENT_CYAN = "#00D2FF"       # Vibrant electric blue
ACCENT_GREEN = "#10B981"      # Emerald green
ACCENT_ROSE = "#F43F5E"       # Crisp red/rose
ACCENT_PURPLE = "#8B5CF6"     # Modern violet

CHART_PALETTE = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]

DB_NAME = "expenses.db"

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_expense_db(amount, category, description, date_str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                (amount, category, description, date_str))
    conn.commit()
    conn.close()

def delete_expense_db(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def fetch_all_expenses():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, date, category, amount, description FROM expenses ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_category_breakdown():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_monthly_breakdown():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT strftime('%Y-%m', date) as month, SUM(amount) FROM expenses GROUP BY month ORDER BY month ASC")
    rows = cur.fetchall()
    conn.close()
    return rows

# --- App Application ---
class VibrantExpenseTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aura Financial Dashboard")
        self.geometry("1180, 760")
        self.minsize(1050, 680)
        self.configure(fg_color=BG_COLOR)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        self.refresh_data()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=310, corner_radius=18, fg_color=PANEL_BG)
        self.sidebar.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")

        title_badge = ctk.CTkLabel(
            self.sidebar, 
            text="✨ EXPENSES", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ACCENT_CYAN
        )
        title_badge.pack(padx=20, pady=(25, 4))

        subtitle = ctk.CTkLabel(
            self.sidebar, 
            text="Smart Expense Tracker", 
            font=ctk.CTkFont(size=12), 
            text_color="#8B949E"
        )
        subtitle.pack(padx=20, pady=(0, 20))

        # Inputs
        self.entry_amount = ctk.CTkEntry(
            self.sidebar, placeholder_text="Amount (Rs.)", height=42, 
            corner_radius=10, fg_color="#0D1117", border_color="#30363D"
        )
        self.entry_amount.pack(padx=20, pady=8, fill="x")

        categories = ["Food & Dining", "Transport", "Shopping", "Bills & Utilities", "Entertainment", "Other"]
        self.category_opt = ctk.CTkOptionMenu(
            self.sidebar, values=categories, height=42, corner_radius=10,
            fg_color="#21262D", button_color="#30363D", text_color="white"
        )
        self.category_opt.pack(padx=20, pady=8, fill="x")

        self.entry_desc = ctk.CTkEntry(
            self.sidebar, placeholder_text="Note / Description", height=42,
            corner_radius=10, fg_color="#0D1117", border_color="#30363D"
        )
        self.entry_desc.pack(padx=20, pady=8, fill="x")

        today = datetime.date.today().strftime("%Y-%m-%d")
        self.entry_date = ctk.CTkEntry(
            self.sidebar, placeholder_text="YYYY-MM-DD", height=42,
            corner_radius=10, fg_color="#0D1117", border_color="#30363D"
        )
        self.entry_date.insert(0, today)
        self.entry_date.pack(padx=20, pady=8, fill="x")

        # Action Buttons
        btn_add = ctk.CTkButton(
            self.sidebar, text="+ Add Transaction", height=44, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", command=self.handle_add_expense
        )
        btn_add.pack(padx=20, pady=(18, 8), fill="x")

        btn_del = ctk.CTkButton(
            self.sidebar, text="Delete Entry", height=38, corner_radius=10,
            fg_color="#30363D", hover_color=ACCENT_ROSE, text_color="#E6EDF3",
            command=self.handle_delete_expense
        )
        btn_del.pack(padx=20, pady=6, fill="x")

        # Highlight Stat Card
        self.summary_box = ctk.CTkFrame(self.sidebar, corner_radius=14, fg_color="#0D1117")
        self.summary_box.pack(side="bottom", padx=20, pady=20, fill="x")

        lbl_header = ctk.CTkLabel(self.summary_box, text="TOTAL EXPENDITURE", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8B949E")
        lbl_header.pack(pady=(15, 2))

        self.lbl_total_sum = ctk.CTkLabel(self.summary_box, text="Rs. 0.00", font=ctk.CTkFont(size=24, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_total_sum.pack(pady=(0, 15))

    def setup_main_area(self):
        self.main_container = ctk.CTkFrame(self, corner_radius=18, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Top Metric Cards
        self.metrics_frame = ctk.CTkFrame(self.main_container, corner_radius=14, fg_color="transparent")
        self.metrics_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.metrics_frame.grid_columnconfigure((0, 1), weight=1)

        # Card 1: Count
        card_trans = ctk.CTkFrame(self.metrics_frame, corner_radius=14, fg_color=PANEL_BG)
        card_trans.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ctk.CTkLabel(card_trans, text="Logged Transactions", font=ctk.CTkFont(size=12), text_color="#8B949E").pack(pady=(12, 0))
        self.lbl_trans_count = ctk.CTkLabel(card_trans, text="0", font=ctk.CTkFont(size=22, weight="bold"), text_color=ACCENT_CYAN)
        self.lbl_trans_count.pack(pady=(0, 12))

        # Card 2: Top Category
        card_top = ctk.CTkFrame(self.metrics_frame, corner_radius=14, fg_color=PANEL_BG)
        card_top.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        ctk.CTkLabel(card_top, text="Top Spending Sector", font=ctk.CTkFont(size=12), text_color="#8B949E").pack(pady=(12, 0))
        self.lbl_top_cat = ctk.CTkLabel(card_top, text="None", font=ctk.CTkFont(size=20, weight="bold"), text_color=ACCENT_PURPLE)
        self.lbl_top_cat.pack(pady=(0, 12))

        # Tabs
        self.tabview = ctk.CTkTabview(
            self.main_container, corner_radius=14, fg_color=PANEL_BG, 
            segmented_button_selected_color=ACCENT_CYAN, 
            segmented_button_selected_hover_color="#00AEE0"
        )
        self.tabview.grid(row=1, column=0, sticky="nsew")

        self.tab_charts = self.tabview.add("Visual Analytics")
        self.tab_table = self.tabview.add("Transaction Registry")

        # --- Chart Setup ---
        self.tab_charts.grid_columnconfigure((0, 1), weight=1)
        self.tab_charts.grid_rowconfigure(0, weight=1)

        self.chart_frame_left = ctk.CTkFrame(self.tab_charts, corner_radius=12, fg_color="#0D1117")
        self.chart_frame_left.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")

        self.chart_frame_right = ctk.CTkFrame(self.tab_charts, corner_radius=12, fg_color="#0D1117")
        self.chart_frame_right.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")

        self.canvas_pie = None
        self.canvas_bar = None

        # --- Table Setup ---
        self.tab_table.grid_columnconfigure(0, weight=1)
        self.tab_table.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", 
            background="#161B22", 
            foreground="#E6EDF3", 
            fieldbackground="#161B22", 
            rowheight=34, 
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure("Treeview.Heading", background="#21262D", foreground="#00D2FF", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#1F6AA5")])

        cols = ("id", "date", "category", "amount", "description")
        self.tree = ttk.Treeview(self.tab_table, columns=cols, show="headings")
        self.tree.heading("id", text="#")
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("description", text="Description")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("category", width=140, anchor="w")
        self.tree.column("amount", width=110, anchor="e")
        self.tree.column("description", width=260, anchor="w")

        scroll = ttk.Scrollbar(self.tab_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scroll.grid(row=0, column=1, sticky="ns", pady=10, padx=(0, 10))

    def handle_add_expense(self):
        val = self.entry_amount.get().strip()
        cat = self.category_opt.get()
        desc = self.entry_desc.get().strip()
        d_str = self.entry_date.get().strip()

        try:
            amt = float(val)
            if amt <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount.")
            return

        try:
            datetime.date.fromisoformat(d_str)
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be formatted YYYY-MM-DD.")
            return

        add_expense_db(amt, cat, desc, d_str)
        self.entry_amount.delete(0, 'end')
        self.entry_desc.delete(0, 'end')
        self.refresh_data()

    def handle_delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Row", "Please click an entry on the table first.")
            return

        for item in selected:
            vals = self.tree.item(item, 'values')
            delete_expense_db(vals[0])

        self.refresh_data()

    def refresh_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        records = fetch_all_expenses()
        total = 0.0
        for row in records:
            total += float(row[3])
            self.tree.insert("", "end", values=(row[0], row[1], row[2], f"Rs. {float(row[3]):,.2f}", row[4]))

        self.lbl_total_sum.configure(text=f"Rs. {total:,.2f}")
        self.lbl_trans_count.configure(text=str(len(records)))

        cat_breakdown = fetch_category_breakdown()
        top_cat_name = cat_breakdown[0][0] if cat_breakdown else "None"
        self.lbl_top_cat.configure(text=top_cat_name)

        self.render_visualizations(cat_breakdown, fetch_monthly_breakdown())

    def render_visualizations(self, cat_data, month_data):
        if self.canvas_pie: self.canvas_pie.get_tk_widget().destroy()
        if self.canvas_bar: self.canvas_bar.get_tk_widget().destroy()

        plt.style.use("dark_background")

        # --- 1. Donut Chart (Categories) ---
        fig_pie, ax_pie = plt.subplots(figsize=(4.2, 4.2), facecolor="#0D1117")
        ax_pie.set_facecolor("#0D1117")

        if cat_data:
            labels = [c[0] for c in cat_data]
            values = [c[1] for c in cat_data]
            wedges, texts, autotexts = ax_pie.pie(
                values, labels=labels, autopct='%1.1f%%', startangle=90,
                pctdistance=0.75, colors=CHART_PALETTE,
                wedgeprops=dict(width=0.45, edgecolor='#0D1117', linewidth=2)
            )
            for text in texts: text.set_color('#C9D1D9')
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
                autotext.set_fontsize(9)
            ax_pie.set_title("Allocation by Category", color=ACCENT_CYAN, fontsize=12, weight='bold', pad=14)
        else:
            ax_pie.text(0.5, 0.5, "No Data Logged", horizontalalignment='center', color='#8B949E')
            ax_pie.axis('off')

        self.canvas_pie = FigureCanvasTkAgg(fig_pie, master=self.chart_frame_left)
        self.canvas_pie.draw()
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        plt.close(fig_pie)

        # --- 2. Bar Chart (Timeline) ---
        fig_bar, ax_bar = plt.subplots(figsize=(4.2, 4.2), facecolor="#0D1117")
        ax_bar.set_facecolor("#0D1117")

        if month_data:
            months = [m[0] for m in month_data]
            totals = [m[1] for m in month_data]

            bars = ax_bar.bar(months, totals, color=ACCENT_CYAN, width=0.45, edgecolor="#00AEE0")
            ax_bar.set_title("Monthly Trend", color=ACCENT_CYAN, fontsize=12, weight='bold', pad=14)
            ax_bar.tick_params(axis='x', rotation=25, labelsize=9, colors='#8B949E')
            ax_bar.tick_params(axis='y', labelsize=9, colors='#8B949E')

            # Clean borders & dashed reference lines
            ax_bar.spines['top'].set_visible(False)
            ax_bar.spines['right'].set_visible(False)
            ax_bar.spines['left'].set_color('#30363D')
            ax_bar.spines['bottom'].set_color('#30363D')
            ax_bar.grid(axis='y', linestyle=':', alpha=0.35, color='#8B949E')

            for bar in bars:
                height = bar.get_height()
                ax_bar.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, color="#C9D1D9"
                )
        else:
            ax_bar.text(0.5, 0.5, "No Data Logged", horizontalalignment='center', color='#8B949E')
            ax_bar.axis('off')

        self.canvas_bar = FigureCanvasTkAgg(fig_bar, master=self.chart_frame_right)
        self.canvas_bar.draw()
        self.canvas_bar.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        plt.close(fig_bar)

if __name__ == "__main__":
    init_db()
    app = VibrantExpenseTracker()
    app.mainloop()