"""Reusable GUI helpers for text output and clipboard actions."""

from __future__ import annotations

import tkinter as tk


def set_text_output(text_widget: tk.Text, content: str):
    """Replace text widget content and reset the scroll position."""
    text_widget.configure(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", content)
    text_widget.see("1.0")


def clear_entries(entries):
    """Clear a list of entry widgets."""
    for entry in entries:
        entry.delete(0, tk.END)


def copy_text_to_clipboard(root: tk.Tk, text_widget: tk.Text):
    """Copy current text widget content to clipboard."""
    content = text_widget.get("1.0", tk.END).strip()
    if not content:
        return False

    root.clipboard_clear()
    root.clipboard_append(content)
    root.update_idletasks()
    return True
