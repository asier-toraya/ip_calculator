"""
Calculadora de Red IP - Aplicación Principal
Autor: Asier Toraya
Descripción: Calculadora completa de redes IP con funciones de cálculo detallado,
             práctica guiada y generación de esquemas para Cisco Packet Tracer.
"""

from gui import MainWindow, DetailedTab, PracticeTab, CPTTab, CPTAdvancedTab


def main():
    """Función principal de la aplicación"""
    # Crear ventana principal
    app = MainWindow()
    
    # Crear y añadir pestañas
    tab1 = DetailedTab(app.notebook)
    app.add_tab(tab1, "Calculo Detallado Paso a Paso")
    
    tab2 = PracticeTab(app.notebook)
    app.add_tab(tab2, "Practica Manual Guiada")
    
    tab3 = CPTTab(app.notebook)
    app.add_tab(tab3, "CPT - Cisco Packet Tracer")
    
    tab4 = CPTAdvancedTab(app.notebook)
    app.add_tab(tab4, "CPT Avanzado")
    
    # Iniciar aplicación
    app.run()


if __name__ == "__main__":
    main()
