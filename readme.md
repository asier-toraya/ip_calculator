# Calculadora de Red IP

Aplicación completa para cálculos de redes IP con interfaz gráfica.

## Características

- **Cálculo Detallado**: Cálculos paso a paso de máscaras, redes, broadcast y subredes
- **Práctica Guiada**: Ejercicios interactivos con retroalimentación inmediata
- **Generador CPT**: Crea esquemas completos para Cisco Packet Tracer

## Estructura del Proyecto

```
DecToBin/
├── main.py                    # Punto de entrada principal
├── gui/                       # Interfaz gráfica
│   ├── __init__.py
│   ├── main_window.py        # Ventana principal
│   ├── tab_detailed.py       # Pestaña de cálculo detallado
│   ├── tab_practice.py       # Pestaña de práctica
│   └── tab_cpt.py            # Pestaña de Cisco Packet Tracer
├── core/                      # Lógica de negocio
│   ├── __init__.py
│   ├── network_calc.py       # Cálculos de red
│   ├── subnet_calc.py        # Cálculos de subredes
│   └── cpt_generator.py      # Generador de esquemas CPT
└── utils/                     # Utilidades
    ├── __init__.py
    └── validators.py         # Validaciones de entrada
```

## Uso

Ejecutar el programa:
```bash
python main.py
```

## Requisitos

- Python 3.6+
- tkinter (incluido en Python estándar)
- ipaddress (incluido en Python estándar)

## Funcionalidades

### Pestaña 1: Cálculo Detallado
- Cálculo detallado de parámetros de red
- División en subredes
- Optimización por número de dispositivos

### Pestaña 2: Práctica Manual
- Ejercicios básicos de redes
- Ejercicios de subredes
- Verificación automática de respuestas

### Pestaña 3: Cisco Packet Tracer
- Generación automática de topologías
- Configuración detallada de routers
- Configuración de switches con VLANs
- Asignación automática de IPs
