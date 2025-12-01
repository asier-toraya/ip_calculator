import re

# Leer el archivo
with open('ip_calc.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Función generate_cpt_schema que falta
generate_cpt_function = '''
def generate_cpt_schema():
    messagebox.showinfo("Información", "Esta funcionalidad está en desarrollo.\\nPor ahora, usa la pestaña 'Cálculo Detallado' para generar subredes.")
'''

# Añadir la función faltante antes de calculate_vlsm si existe, o antes de # GUI
if 'def calculate_vlsm' in content:
    content = content.replace('def calculate_vlsm', generate_cpt_function + '\ndef calculate_vlsm')
else:
    content = content.replace('# GUI', generate_cpt_function + '\n# GUI')

# Guardar
with open('ip_calc.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Función generate_cpt_schema añadida")
print("✓ Archivo corregido")
