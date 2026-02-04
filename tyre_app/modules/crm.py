import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from tyre_app.core.storage import Database

BRANDS = [
    "Kumho",
    "Hankook",
    "Fulda",
    "Uniroyal",
    "Falken",
    "Nexen",
    "Firestone",
]


class CRMModule(ttk.Frame):
    def __init__(self, parent: tk.Misc, database: Database) -> None:
        super().__init__(parent)
        self.database = database
        self._build_layout()
        self._refresh_tables()

    def _build_layout(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.rep_frame = ttk.Frame(notebook)
        self.notes_frame = ttk.Frame(notebook)
        self.orders_frame = ttk.Frame(notebook)

        notebook.add(self.rep_frame, text="Brand Representatives")
        notebook.add(self.notes_frame, text="Meeting Notes")
        notebook.add(self.orders_frame, text="Internal Orders")

        self._build_representatives_tab()
        self._build_notes_tab()
        self._build_orders_tab()

    def _build_representatives_tab(self) -> None:
        form = ttk.LabelFrame(self.rep_frame, text="Add Representative")
        form.pack(fill=tk.X, padx=12, pady=10)

        self.rep_brand = tk.StringVar(value=BRANDS[0])
        self.rep_name = tk.StringVar()
        self.rep_email = tk.StringVar()
        self.rep_phone = tk.StringVar()
        self.rep_last_contact = tk.StringVar(value=datetime.today().date().isoformat())

        self._add_labeled_entry(form, "Brand", ttk.Combobox(form, values=BRANDS, textvariable=self.rep_brand, state="readonly"), 0)
        self._add_labeled_entry(form, "Name", ttk.Entry(form, textvariable=self.rep_name), 1)
        self._add_labeled_entry(form, "Email", ttk.Entry(form, textvariable=self.rep_email), 2)
        self._add_labeled_entry(form, "Phone", ttk.Entry(form, textvariable=self.rep_phone), 3)
        self._add_labeled_entry(form, "Last Contact", ttk.Entry(form, textvariable=self.rep_last_contact), 4)

        action = ttk.Button(form, text="Save Representative", command=self._save_representative)
        action.grid(row=5, column=1, sticky=tk.W, pady=8)

        self.rep_table = self._build_table(
            self.rep_frame,
            columns=("brand", "name", "email", "phone", "last_contact"),
            headings=("Brand", "Name", "Email", "Phone", "Last Contact"),
        )

    def _build_notes_tab(self) -> None:
        form = ttk.LabelFrame(self.notes_frame, text="Log Meeting Notes")
        form.pack(fill=tk.X, padx=12, pady=10)

        self.note_brand = tk.StringVar(value=BRANDS[0])
        self.note_date = tk.StringVar(value=datetime.today().date().isoformat())
        self.note_text = tk.StringVar()

        self._add_labeled_entry(form, "Brand", ttk.Combobox(form, values=BRANDS, textvariable=self.note_brand, state="readonly"), 0)
        self._add_labeled_entry(form, "Meeting Date", ttk.Entry(form, textvariable=self.note_date), 1)

        ttk.Label(form, text="Notes").grid(row=2, column=0, sticky=tk.W, padx=6, pady=4)
        notes_entry = ttk.Entry(form, textvariable=self.note_text, width=80)
        notes_entry.grid(row=2, column=1, sticky=tk.W, padx=6, pady=4)

        action = ttk.Button(form, text="Save Notes", command=self._save_notes)
        action.grid(row=3, column=1, sticky=tk.W, pady=8)

        self.notes_table = self._build_table(
            self.notes_frame,
            columns=("brand", "meeting_date", "notes"),
            headings=("Brand", "Meeting Date", "Notes"),
        )

    def _build_orders_tab(self) -> None:
        form = ttk.LabelFrame(self.orders_frame, text="Log Internal Order")
        form.pack(fill=tk.X, padx=12, pady=10)

        self.order_brand = tk.StringVar(value=BRANDS[0])
        self.order_date = tk.StringVar(value=datetime.today().date().isoformat())
        self.order_sku = tk.StringVar()
        self.order_quantity = tk.StringVar()
        self.order_status = tk.StringVar(value="Planned")

        self._add_labeled_entry(form, "Brand", ttk.Combobox(form, values=BRANDS, textvariable=self.order_brand, state="readonly"), 0)
        self._add_labeled_entry(form, "Order Date", ttk.Entry(form, textvariable=self.order_date), 1)
        self._add_labeled_entry(form, "SKU", ttk.Entry(form, textvariable=self.order_sku), 2)
        self._add_labeled_entry(form, "Quantity", ttk.Entry(form, textvariable=self.order_quantity), 3)
        self._add_labeled_entry(form, "Status", ttk.Entry(form, textvariable=self.order_status), 4)

        action = ttk.Button(form, text="Save Order", command=self._save_order)
        action.grid(row=5, column=1, sticky=tk.W, pady=8)

        self.orders_table = self._build_table(
            self.orders_frame,
            columns=("brand", "order_date", "sku", "quantity", "status"),
            headings=("Brand", "Order Date", "SKU", "Quantity", "Status"),
        )

    def _add_labeled_entry(self, parent: ttk.Frame, label: str, widget: tk.Widget, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=6, pady=4)
        widget.grid(row=row, column=1, sticky=tk.W, padx=6, pady=4)

    def _build_table(self, parent: ttk.Frame, columns: tuple, headings: tuple) -> ttk.Treeview:
        table = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        for column, heading in zip(columns, headings):
            table.heading(column, text=heading)
            table.column(column, width=140, anchor=tk.W)
        table.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        return table

    def _refresh_tables(self) -> None:
        self._load_table(self.rep_table, "SELECT brand, name, email, phone, last_contact FROM brand_representatives ORDER BY id DESC")
        self._load_table(self.notes_table, "SELECT brand, meeting_date, notes FROM meeting_notes ORDER BY id DESC")
        self._load_table(
            self.orders_table,
            "SELECT brand, order_date, sku, quantity, status FROM internal_orders ORDER BY id DESC",
        )

    def _load_table(self, table: ttk.Treeview, query: str) -> None:
        for item in table.get_children():
            table.delete(item)
        for row in self.database.fetch_all(query):
            table.insert("", tk.END, values=tuple(row))

    def _save_representative(self) -> None:
        if not self.rep_name.get().strip():
            messagebox.showwarning("Missing Data", "Please enter a representative name.")
            return
        self.database.execute(
            "INSERT INTO brand_representatives (brand, name, email, phone, last_contact) VALUES (?, ?, ?, ?, ?)",
            (
                self.rep_brand.get(),
                self.rep_name.get().strip(),
                self.rep_email.get().strip(),
                self.rep_phone.get().strip(),
                self.rep_last_contact.get().strip(),
            ),
        )
        self.rep_name.set("")
        self.rep_email.set("")
        self.rep_phone.set("")
        self._refresh_tables()

    def _save_notes(self) -> None:
        if not self.note_text.get().strip():
            messagebox.showwarning("Missing Data", "Please enter meeting notes.")
            return
        self.database.execute(
            "INSERT INTO meeting_notes (brand, meeting_date, notes) VALUES (?, ?, ?)",
            (
                self.note_brand.get(),
                self.note_date.get().strip(),
                self.note_text.get().strip(),
            ),
        )
        self.note_text.set("")
        self._refresh_tables()

    def _save_order(self) -> None:
        if not self.order_sku.get().strip() or not self.order_quantity.get().strip():
            messagebox.showwarning("Missing Data", "Please enter SKU and quantity.")
            return
        try:
            quantity = int(self.order_quantity.get())
        except ValueError:
            messagebox.showwarning("Invalid Data", "Quantity must be a number.")
            return
        self.database.execute(
            "INSERT INTO internal_orders (brand, order_date, sku, quantity, status) VALUES (?, ?, ?, ?, ?)",
            (
                self.order_brand.get(),
                self.order_date.get().strip(),
                self.order_sku.get().strip(),
                quantity,
                self.order_status.get().strip(),
            ),
        )
        self.order_sku.set("")
        self.order_quantity.set("")
        self._refresh_tables()
