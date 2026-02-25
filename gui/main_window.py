"""Main application window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .theme import apply_theme


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculadora de Red IP")
        self.root.geometry("1180x860")
        self.root.minsize(980, 700)

        apply_theme(self.root)

        self._build_layout()
        self.tabs = {}

    def _build_layout(self):
        outer = ttk.Frame(self.root, style="App.TFrame", padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(outer, style="App.TFrame")
        header.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(header, text="Calculadora de Redes IP", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Calculo detallado, practica guiada y generacion de esquemas para Packet Tracer.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Listo")
        status = ttk.Label(outer, textvariable=self.status_var, style="Status.TLabel")
        status.pack(fill=tk.X, pady=(8, 0))

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, _event):
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        self.status_var.set(f"Pestana activa: {current_tab}")

    def add_tab(self, tab_instance, title):
        """Add a tab to the notebook."""
        self.tabs[title] = tab_instance
        self.notebook.add(tab_instance.frame, text=title)

    def run(self):
        """Start the Tk event loop."""
        self.root.mainloop()
