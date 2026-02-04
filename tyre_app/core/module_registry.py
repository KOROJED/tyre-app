from dataclasses import dataclass
from typing import Callable, List

import tkinter as tk
from tkinter import ttk


@dataclass
class ModuleDefinition:
    name: str
    factory: Callable[[tk.Misc], ttk.Frame]


class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: List[ModuleDefinition] = []

    def register(self, name: str, factory: Callable[[tk.Misc], ttk.Frame]) -> None:
        self._modules.append(ModuleDefinition(name=name, factory=factory))

    def modules(self) -> List[ModuleDefinition]:
        return list(self._modules)
