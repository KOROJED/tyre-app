from pathlib import Path
import tkinter as tk
from tkinter import ttk

from tyre_app.core.module_registry import ModuleRegistry
from tyre_app.core.storage import Database
from tyre_app.modules.crm import CRMModule
from tyre_app.modules.order_assistant import OrderAssistantModule


APP_TITLE = "Tyre Purchasing Suite"


def build_registry(database: Database) -> ModuleRegistry:
    registry = ModuleRegistry()
    registry.register("CRM", lambda parent: CRMModule(parent, database))
    registry.register("Order Composition Assistant", lambda parent: OrderAssistantModule(parent))
    return registry


class TyreApp(tk.Tk):
    def __init__(self, database: Database) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1200x720")
        self.minsize(1024, 640)
        self._build_layout(build_registry(database))

    def _build_layout(self, registry: ModuleRegistry) -> None:
        header = ttk.Frame(self, padding=12)
        header.pack(fill=tk.X)
        ttk.Label(
            header,
            text=APP_TITLE,
            font=("Segoe UI", 18, "bold"),
        ).pack(side=tk.LEFT)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        for module in registry.modules():
            frame = module.factory(notebook)
            notebook.add(frame, text=module.name)



def main() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "tyre_app.db"
    database = Database(data_path)
    database.initialize()

    app = TyreApp(database)
    app.mainloop()


if __name__ == "__main__":
    main()
