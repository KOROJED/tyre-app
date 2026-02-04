import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from openpyxl import Workbook


@dataclass
class OrderSuggestion:
    sku: str
    brand: str
    annual_sales: float
    stock: float
    unit_cost: float
    sales_value: float
    abc_class: str
    pareto_flag: str
    recommended_order: int


class OrderAssistantModule(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.suggestions: List[OrderSuggestion] = []
        self._build_layout()

    def _build_layout(self) -> None:
        control_frame = ttk.LabelFrame(self, text="Order Composition Assistant")
        control_frame.pack(fill=tk.X, padx=12, pady=10)

        self.lead_time_days = tk.StringVar(value="30")
        self.review_days = tk.StringVar(value="14")

        ttk.Button(control_frame, text="Load ERP CSV", command=self._load_csv).grid(row=0, column=0, padx=6, pady=6)
        ttk.Label(control_frame, text="Lead Time (days)").grid(row=0, column=1, padx=6, pady=6)
        ttk.Entry(control_frame, textvariable=self.lead_time_days, width=8).grid(row=0, column=2, padx=6, pady=6)
        ttk.Label(control_frame, text="Review Period (days)").grid(row=0, column=3, padx=6, pady=6)
        ttk.Entry(control_frame, textvariable=self.review_days, width=8).grid(row=0, column=4, padx=6, pady=6)
        ttk.Button(control_frame, text="Export to Excel", command=self._export_excel).grid(row=0, column=5, padx=6, pady=6)

        self.status_label = ttk.Label(control_frame, text="Load an ERP CSV to generate suggestions.")
        self.status_label.grid(row=1, column=0, columnspan=6, sticky=tk.W, padx=6, pady=4)

        self.table = ttk.Treeview(
            self,
            columns=(
                "sku",
                "brand",
                "annual_sales",
                "stock",
                "unit_cost",
                "sales_value",
                "abc_class",
                "pareto_flag",
                "recommended_order",
            ),
            show="headings",
            height=12,
        )
        headings = (
            "SKU",
            "Brand",
            "Annual Sales",
            "Stock",
            "Unit Cost",
            "Sales Value",
            "ABC",
            "Pareto",
            "Recommended Order",
        )
        for column, heading in zip(self.table["columns"], headings):
            self.table.heading(column, text=heading)
            self.table.column(column, width=120, anchor=tk.W)

        self.table.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

    def _load_csv(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            rows = list(self._read_csv(Path(file_path)))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Load Failed", f"Unable to read CSV: {exc}")
            return
        if not rows:
            messagebox.showwarning("No Data", "The CSV file is empty or missing required columns.")
            return
        self.suggestions = self._generate_suggestions(rows)
        self._refresh_table()
        self.status_label.configure(text=f"Generated {len(self.suggestions)} suggestions from {Path(file_path).name}.")

    def _read_csv(self, path: Path) -> Iterable[Dict[str, str]]:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            headers = self._normalize_headers(reader.fieldnames or [])
            for row in reader:
                normalized_row = {headers.get(key, key): value for key, value in row.items()}
                yield normalized_row

    @staticmethod
    def _normalize_headers(headers: List[str]) -> Dict[str, str]:
        mapping = {}
        for header in headers:
            normalized = header.strip().lower().replace(" ", "_")
            if normalized in {"sku", "item", "item_code"}:
                mapping[header] = "sku"
            elif normalized in {"brand", "manufacturer"}:
                mapping[header] = "brand"
            elif normalized in {"annual_sales", "sales", "qty_sold", "units_sold"}:
                mapping[header] = "annual_sales"
            elif normalized in {"stock", "on_hand", "inventory"}:
                mapping[header] = "stock"
            elif normalized in {"unit_cost", "price", "cost"}:
                mapping[header] = "unit_cost"
            elif normalized in {"lead_time", "lead_time_days"}:
                mapping[header] = "lead_time_days"
        return mapping

    def _generate_suggestions(self, rows: Iterable[Dict[str, str]]) -> List[OrderSuggestion]:
        parsed_rows = []
        for row in rows:
            sku = row.get("sku", "").strip()
            if not sku:
                continue
            brand = row.get("brand", "Unknown").strip() or "Unknown"
            annual_sales = self._to_float(row.get("annual_sales"), 0.0)
            stock = self._to_float(row.get("stock"), 0.0)
            unit_cost = self._to_float(row.get("unit_cost"), 0.0)
            lead_time_days = self._to_float(row.get("lead_time_days"), self._lead_time_default())
            parsed_rows.append({
                "sku": sku,
                "brand": brand,
                "annual_sales": annual_sales,
                "stock": stock,
                "unit_cost": unit_cost,
                "lead_time_days": lead_time_days,
            })

        sales_values = [row["annual_sales"] * (row["unit_cost"] or 1.0) for row in parsed_rows]
        total_value = sum(sales_values) or 1.0

        ranked_rows = sorted(
            zip(parsed_rows, sales_values),
            key=lambda item: item[1],
            reverse=True,
        )

        suggestions: List[OrderSuggestion] = []
        cumulative = 0.0
        pareto_cutoff = max(1, int(len(ranked_rows) * 0.2))
        for index, (row, sales_value) in enumerate(ranked_rows, start=1):
            cumulative += sales_value
            cumulative_pct = cumulative / total_value
            abc_class = self._classify_abc(cumulative_pct)
            pareto_flag = "Top 20%" if index <= pareto_cutoff else "Standard"

            recommended = self._recommend_order(
                annual_sales=row["annual_sales"],
                stock=row["stock"],
                lead_time=row["lead_time_days"],
                abc_class=abc_class,
            )

            suggestions.append(
                OrderSuggestion(
                    sku=row["sku"],
                    brand=row["brand"],
                    annual_sales=row["annual_sales"],
                    stock=row["stock"],
                    unit_cost=row["unit_cost"],
                    sales_value=sales_value,
                    abc_class=abc_class,
                    pareto_flag=pareto_flag,
                    recommended_order=recommended,
                )
            )

        return suggestions

    def _recommend_order(self, annual_sales: float, stock: float, lead_time: float, abc_class: str) -> int:
        review_period = self._review_default()
        daily_sales = annual_sales / 365 if annual_sales > 0 else 0
        multiplier = {"A": 1.3, "B": 1.1, "C": 0.9}.get(abc_class, 1.0)
        target_stock = daily_sales * (lead_time + review_period) * multiplier
        recommended = max(target_stock - stock, 0)
        return int(round(recommended))

    @staticmethod
    def _classify_abc(cumulative_pct: float) -> str:
        if cumulative_pct <= 0.8:
            return "A"
        if cumulative_pct <= 0.95:
            return "B"
        return "C"

    def _lead_time_default(self) -> float:
        return self._to_float(self.lead_time_days.get(), 30.0)

    def _review_default(self) -> float:
        return self._to_float(self.review_days.get(), 14.0)

    @staticmethod
    def _to_float(value: Optional[str], default: float) -> float:
        try:
            if value is None:
                return default
            return float(str(value).strip() or default)
        except ValueError:
            return default

    def _refresh_table(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)
        for suggestion in self.suggestions:
            self.table.insert(
                "",
                tk.END,
                values=(
                    suggestion.sku,
                    suggestion.brand,
                    f"{suggestion.annual_sales:.1f}",
                    f"{suggestion.stock:.1f}",
                    f"{suggestion.unit_cost:.2f}",
                    f"{suggestion.sales_value:.2f}",
                    suggestion.abc_class,
                    suggestion.pareto_flag,
                    suggestion.recommended_order,
                ),
            )

    def _export_excel(self) -> None:
        if not self.suggestions:
            messagebox.showwarning("No Data", "Generate suggestions before exporting.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
        )
        if not file_path:
            return
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Order Suggestions"
        headers = [
            "SKU",
            "Brand",
            "Annual Sales",
            "Stock",
            "Unit Cost",
            "Sales Value",
            "ABC Class",
            "Pareto Flag",
            "Recommended Order",
        ]
        sheet.append(headers)
        for suggestion in self.suggestions:
            sheet.append(
                [
                    suggestion.sku,
                    suggestion.brand,
                    suggestion.annual_sales,
                    suggestion.stock,
                    suggestion.unit_cost,
                    suggestion.sales_value,
                    suggestion.abc_class,
                    suggestion.pareto_flag,
                    suggestion.recommended_order,
                ]
            )
        workbook.save(file_path)
        messagebox.showinfo("Export Complete", f"Saved suggestions to {file_path}.")
