"""
Utilidades de validación para la calculadora de red IP
"""
import ipaddress
from tkinter import messagebox


def validate_ip_cidr(ip_input):
    """
    Valida que el input sea una IP válida con formato CIDR
    Returns: (bool, ipaddress.IPv4Network or None, str error_message)
    """
    if not ip_input or '/' not in ip_input:
        return False, None, "Formato inválido. Usa IP/CIDR (ej: 192.168.0.11/24)"
    
    try:
        network = ipaddress.IPv4Network(ip_input, strict=False)
        return True, network, ""
    except ValueError as e:
        return False, None, f"IP o máscara inválida: {e}"


def validate_positive_int(value, field_name="Valor"):
    """
    Valida que el valor sea un entero positivo
    Returns: (bool, int or None, str error_message)
    """
    try:
        num = int(value)
        if num < 1:
            return False, None, f"{field_name} debe ser mayor a 0"
        return True, num, ""
    except ValueError:
        return False, None, f"{field_name} debe ser un número entero válido"


def validate_device_list(devices_str, expected_count):
    """
    Valida una lista de dispositivos separados por comas
    Returns: (bool, list or None, str error_message)
    """
    try:
        devices_list = [int(x.strip()) for x in devices_str.split(',') if x.strip()]
        
        if len(devices_list) != expected_count:
            return False, None, f"Debes especificar {expected_count} valores separados por comas. Ingresaste {len(devices_list)}"
        
        if any(d < 1 for d in devices_list):
            return False, None, "Todos los valores deben ser mayores a 0"
        
        return True, devices_list, ""
    except ValueError:
        return False, None, "Los valores deben ser números enteros válidos"


def show_error(message):
    """Muestra un mensaje de error"""
    messagebox.showerror("Error", message)


def show_warning(message):
    """Muestra un mensaje de advertencia"""
    messagebox.showwarning("Aviso", message)
