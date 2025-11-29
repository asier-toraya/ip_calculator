# 🌐 Calculadora de Red IP - IP Network Calculator

Una herramienta educativa completa para aprender y practicar cálculos de redes IP con retroalimentación inmediata.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Descripción

**IP Network Calculator** es una aplicación de escritorio diseñada para ayudar a estudiantes y profesionales de redes a comprender y dominar los cálculos de direccionamiento IP, subnetting y diseño de redes. 

La aplicación combina:
- ✅ **Cálculos automáticos detallados** con explicaciones paso a paso
- ✅ **Práctica interactiva** con ejercicios aleatorios
- ✅ **Guías de cálculo rápido** para resolver problemas eficientemente
- ✅ **Retroalimentación visual inmediata** (verde ✅ / rojo ❌)

## Características Principales

### Pestaña 1: Cálculo Detallado Paso a Paso

Calcula y explica en detalle:

#### 🔹 Cálculo Básico de Red
- **Máscara de red** (conversión binario-decimal)
- **Dirección de red** (operación AND bit a bit)
- **Salto de bloque** (block size)
- **Dirección de broadcast**
- **Rango de hosts utilizables**

#### 🔹 División en Subredes
- Cálculo de bits necesarios (2^n)
- Nueva máscara de subred
- Hosts disponibles por subred
- Listado completo de todas las subredes

#### 🔹 Subredes por Dispositivos
- Optimización automática (ordena de mayor a menor)
- Cálculo de máscara óptima para cada grupo
- Análisis de hosts desperdiciados
- Asignación secuencial sin solapamiento

**Ejemplo de entrada:**
```
IP: 192.168.0.11/24
Subredes: 5
Dispositivos: 100,200,30,50
```

### Pestaña 2: Práctica Manual Guiada

Aprende haciendo con dos tipos de ejercicios:

#### Ejercicio Básico
Calcula manualmente:
1. Máscara de red
2. Dirección de red
3. Broadcast
4. Salto de bloque
5. Primer host utilizable
6. Último host utilizable

**Incluye guías de cálculo rápido:**
- Método para calcular máscara desde CIDR
- Trucos para operación AND
- Atajos para calcular broadcast
- Tabla de referencia rápida (/8, /16, /24, /25, /26, /27, /28, /29, /30)

#### Ejercicio de Subredes
Calcula manualmente:
1. Bits necesarios para N subredes
2. Nueva máscara de subred
3. Hosts por subred

**Incluye guías:**
- Fórmula 2^n >= número_de_subredes
- Cálculo de nueva máscara
- Fórmula de hosts por subred

### Sistema de Retroalimentación

- **Verde (✅)**: Respuesta correcta
- **Rojo (❌)**: Respuesta incorrecta + muestra la respuesta correcta
- **Explicaciones**: Por qué está mal y cómo calcularlo

## Instalación

### Requisitos
- Python 3.7 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)

### Pasos

1. **Clona el repositorio:**
```bash
git clone https://github.com/tu-usuario/ip-calculator.git
cd ip-calculator
```

2. **No requiere instalación de dependencias adicionales** (usa bibliotecas estándar de Python)

3. **Ejecuta la aplicación:**
```bash
python ip_calc.py
```

## Uso

### Cálculo Detallado

1. Abre la pestaña **"Cálculo Detallado Paso a Paso"**
2. Ingresa una IP con máscara en formato CIDR (ej: `192.168.0.11/24`)
3. Presiona **"Calcular Detallado"** para ver el proceso completo
4. Para subredes: ingresa el número y presiona **"Calcular Subredes"**
5. Para dispositivos: ingresa cantidades separadas por comas (ej: `100,200,30,50`)

### Práctica Manual

1. Abre la pestaña **"Práctica Manual Guiada"**
2. Presiona **"Nuevo Ejercicio Básico"** o **"Nuevo Ejercicio de Subredes"**
3. Lee las guías de cálculo proporcionadas
4. Calcula manualmente (usa papel y lápiz)
5. Ingresa tus respuestas en los campos
6. Presiona **"Verificar"** para obtener retroalimentación
7. Revisa las respuestas incorrectas (marcadas en rojo)
8. Genera nuevos ejercicios para seguir practicando

## Guías de Cálculo Rápido

### Máscara de Red
```
/{cidr} ÷ 8 = octetos completos en 255
Bits restantes → valor del siguiente octeto
Resto de octetos = 0
```

### Dirección de Red
```
AND entre IP y Máscara
TRUCO: Octetos con máscara 255 quedan igual
       Octetos con máscara 0 se vuelven 0
```

### Broadcast
```
Wildcard = 255.255.255.255 - Máscara
Broadcast = Red + Wildcard
TRUCO: Donde máscara es 0, broadcast es 255
```

### Salto de Bloque
```
Busca último octeto de máscara que NO sea 255
Salto = 256 - ese octeto
```

## Casos de Uso

### Para Estudiantes
- Preparación para exámenes de certificación (CCNA, Network+)
- Práctica de subnetting
- Comprensión de conceptos de redes

### Para Profesionales
- Diseño rápido de esquemas de red
- Verificación de cálculos
- Planificación de subredes

### Para Educadores
- Herramienta de enseñanza interactiva
- Generación de ejercicios aleatorios
- Explicaciones paso a paso para estudiantes

## Tecnologías Utilizadas

- **Python 3.7+**: Lenguaje de programación
- **Tkinter**: Interfaz gráfica de usuario
- **ipaddress**: Biblioteca estándar para manejo de direcciones IP
- **math**: Cálculos matemáticos
- **random**: Generación de ejercicios aleatorios

## Capturas de Pantalla

### Cálculo Detallado
```
================================================================================
CALCULO DETALLADO DE RED
================================================================================

IP: 192.168.0.11/24

PASO 1: MASCARA DE RED
----------------------------------------
/24 = 24 bits en 1
Binario: 11111111.11111111.11111111.00000000
Decimal: 255.255.255.0

PASO 2: DIRECCION DE RED
----------------------------------------
AND entre IP y Mascara
Resultado: 192.168.0.0/24
...
```

### Práctica Manual
```
EJERCICIO BASICO
================================================================================

IP: 172.16.45.128/26

GUIA DE CALCULO RAPIDO
================================================================================

1. MASCARA DE RED:
   /26 = 26 bits en 1
   26 / 8 = 3 octetos completos en 255
   Quedan 2 bits -> Octeto 4 = 192
   
TABLA DE REFERENCIA:
/24 -> 255.255.255.0
/25 -> 255.255.255.128
/26 -> 255.255.255.192
...
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request



## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Autor

**Asier Gonzalez**

## Agradecimientos
- A mi profesor David R.S por ponerme en la tesitura de tener que hacer este programa


---

⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub!
