"""IP network calculator application entry point."""

from __future__ import annotations

from gui import CPTAdvancedTab, CPTTab, DetailedTab, MainWindow, PracticeTab


def main():
    """Create main window, register tabs and start the app."""
    app = MainWindow()

    app.add_tab(DetailedTab(app.notebook), "Calculo Detallado")
    app.add_tab(PracticeTab(app.notebook), "Practica Guiada")
    app.add_tab(CPTTab(app.notebook), "CPT Basico")
    app.add_tab(CPTAdvancedTab(app.notebook), "CPT Avanzado")

    app.run()


if __name__ == "__main__":
    main()
