"""
Ventana principal de la aplicación
"""
import tkinter as tk
from tkinter import ttk


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculadora de Red IP")
        self.root.geometry("1000x900")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tabs = {}
    
    def add_tab(self, tab_instance, title):
        """Añade una pestaña al notebook"""
        self.tabs[title] = tab_instance
        self.notebook.add(tab_instance.frame, text=title)
    
    def run(self):
        """Inicia el loop principal de la aplicación"""
        self.root.mainloop()
