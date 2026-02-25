# Calculadora de Red IP

Aplicacion de escritorio en Python + Tkinter para practicar y automatizar calculos de redes IPv4.

## Que incluye

- Calculo detallado de una red (`IP/CIDR`): mascara, red, broadcast, wildcard, hosts y rango util.
- Subnetting fijo por numero de subredes.
- VLSM por numero de dispositivos por subred.
- Modo de practica guiada con verificacion instantanea.
- Generador de esquemas para Cisco Packet Tracer (basico y avanzado).
- Interfaz unificada con tema visual consistente y utilidades de copiar salida.

## Estructura del proyecto

```text
ip_calculator/
|-- main.py
|-- run.bat
|-- build_exe.bat
|-- requirements-dev.txt
|-- core/
|   |-- __init__.py
|   |-- ip_tools.py
|   |-- network_calc.py
|   |-- subnet_calc.py
|   |-- cpt_generator.py
|   `-- cpt_advanced_generator.py
|-- gui/
|   |-- __init__.py
|   |-- main_window.py
|   |-- theme.py
|   |-- ui_utils.py
|   |-- tab_detailed.py
|   |-- tab_practice.py
|   |-- tab_cpt.py
|   `-- tab_cpt_advanced.py
|-- utils/
|   |-- __init__.py
|   `-- validators.py
`-- tests/
    `-- test_core.py
```

## Requisitos

- Python 3.10+ (probado con 3.14)
- Tkinter (incluido normalmente con Python en Windows)

## Formas rapidas de ejecutar

### Opcion 1: doble clic (Windows)

1. Ejecuta `run.bat`.
2. El script usa `.venv\Scripts\python.exe` si existe; si no, usa `python` del sistema.

### Opcion 2: terminal

```bash
python main.py
```

## Generar ejecutable (.exe)

> Requiere `pyinstaller`.

1. Instalar dependencia:

```bash
python -m pip install -r requirements-dev.txt
```

2. Generar ejecutable:

```bash
build_exe.bat
```

3. Resultado esperado: `dist/ip-calculator.exe`

## Paquete portable

Se genera tambien un paquete comprimido listo para compartir:

- `dist/ip-calculator-portable.zip`
- Incluye `ip-calculator.exe` y `README.md`

## Generar instalador (Setup)

Se incluye configuracion para Inno Setup:

- Script: `installer/ip_calculator.iss`
- Lanzador: `installer/build_installer.bat`

Requisitos:

1. Tener Inno Setup instalado (`iscc` disponible en `PATH`).
2. Tener generado antes `dist/ip-calculator.exe`.

Salida esperada:

- `dist/ip-calculator-setup.exe`

## Testing

Ejecuta tests unitarios:

```bash
python -m unittest discover -s tests -v
```

## Flujo recomendado de uso

1. En **Calculo Detallado**, valida red base y resultado rapido.
2. Si necesitas reparto fijo, usa **Dividir en subredes**.
3. Si necesitas optimizacion por hosts, usa **VLSM por dispositivos**.
4. Para laboratorio, pasa a **CPT Basico** o **CPT Avanzado** y copia la salida.

## Notas

- El proyecto conserva archivos historicos (`ip_calc.py`, backups) para referencia, pero el punto de entrada oficial es `main.py`.
- `logs/` y artefactos de build quedan ignorados por `.gitignore`.
