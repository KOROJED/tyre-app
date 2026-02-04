# Tyre Purchasing Suite

Desktop application for a tyre distributor purchasing team. It includes:

- **CRM module** for brand representatives, meeting notes, and internal order tracking.
- **Order Composition Assistant** that ingests ERP CSV exports, performs ABC/Pareto analysis, and outputs recommended order quantities that can be exported to Excel.
- **Modular architecture** via a registry that makes it easy to add new tabs/modules.

## Quick Start

```bash
python app.py
```

## CSV Inputs for the Order Composition Assistant

The assistant expects a CSV with headers similar to:

- `sku` (or `item`, `item_code`)
- `brand` (or `manufacturer`)
- `annual_sales` (or `sales`, `qty_sold`, `units_sold`)
- `stock` (or `on_hand`, `inventory`)
- `unit_cost` (or `price`, `cost`)
- Optional: `lead_time_days`

## Adding New Modules

1. Create a new module in `tyre_app/modules` that subclasses `ttk.Frame`.
2. Register it in `tyre_app/app.py` via `build_registry`.

## Dependencies

- Python 3.10+
- `openpyxl` for Excel export
