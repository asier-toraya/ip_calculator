"""Shared Tk/ttk style configuration."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

COLORS = {
    "bg": "#F4F6FB",
    "surface": "#FFFFFF",
    "text": "#1F2937",
    "muted": "#5B6475",
    "primary": "#0F4C81",
    "secondary": "#E9EEF7",
}


def apply_theme(root: tk.Tk):
    """Apply application-wide colors and ttk styles."""
    root.configure(bg=COLORS["bg"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("App.TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["surface"])

    style.configure(
        "Title.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 18, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Section.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 11, "bold"),
    )

    style.configure(
        "TNotebook",
        background=COLORS["bg"],
        borderwidth=0,
        tabmargins=(5, 5, 5, 0),
    )
    style.configure(
        "TNotebook.Tab",
        padding=(12, 8),
        font=("Segoe UI", 10, "bold"),
    )

    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
    style.configure("TLabelframe", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("TLabelframe.Label", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10, "bold"))
    style.configure("TEntry", fieldbackground=COLORS["surface"], foreground=COLORS["text"], padding=4)

    style.configure(
        "Primary.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(12, 7),
    )
    style.map(
        "Primary.TButton",
        foreground=[("!disabled", "#FFFFFF")],
        background=[("!disabled", COLORS["primary"])],
    )

    style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(10, 6))

    style.configure(
        "Status.TLabel",
        background=COLORS["secondary"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 9),
        padding=(10, 6),
    )


def configure_output_text(widget: tk.Text):
    """Apply consistent text area style."""
    widget.configure(
        bg="#FCFDFE",
        fg=COLORS["text"],
        relief=tk.FLAT,
        borderwidth=1,
        padx=8,
        pady=8,
        insertbackground=COLORS["text"],
    )
