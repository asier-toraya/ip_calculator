"""Validation helpers used by the GUI and core entry points."""

from __future__ import annotations

import ipaddress
from tkinter import messagebox


def validate_ip_cidr(ip_input: str):
    """Validate ``IP/CIDR`` input and return an IPv4 network."""
    normalized = (ip_input or "").strip()
    if not normalized or "/" not in normalized:
        return False, None, "Formato invalido. Usa IP/CIDR (ej: 192.168.0.11/24)."

    try:
        network = ipaddress.IPv4Network(normalized, strict=False)
    except ValueError as error:
        return False, None, f"IP o mascara invalida: {error}"

    return True, network, ""


def validate_positive_int(value: str, field_name: str = "Valor"):
    """Validate a strict positive integer."""
    try:
        number = int(str(value).strip())
    except ValueError:
        return False, None, f"{field_name} debe ser un numero entero valido."

    if number < 1:
        return False, None, f"{field_name} debe ser mayor a 0."

    return True, number, ""


def validate_non_negative_int(value: str, field_name: str = "Valor"):
    """Validate a non-negative integer (0 allowed)."""
    try:
        number = int(str(value).strip())
    except ValueError:
        return False, None, f"{field_name} debe ser un numero entero valido."

    if number < 0:
        return False, None, f"{field_name} debe ser mayor o igual a 0."

    return True, number, ""


def parse_int_list(values: str):
    """Parse comma-separated integer values."""
    parsed = []
    for raw in str(values).split(","):
        value = raw.strip()
        if not value:
            continue
        parsed.append(int(value))
    return parsed


def validate_device_list(devices_str: str, expected_count: int):
    """Validate a device list that must match ``expected_count``."""
    try:
        devices = parse_int_list(devices_str)
    except ValueError:
        return False, None, "Los valores deben ser numeros enteros validos."

    if len(devices) != expected_count:
        return (
            False,
            None,
            f"Debes especificar {expected_count} valores separados por comas. "
            f"Ingresaste {len(devices)}.",
        )

    if any(device < 1 for device in devices):
        return False, None, "Todos los valores deben ser mayores a 0."

    return True, devices, ""


def show_error(message: str):
    """Show an error dialog."""
    messagebox.showerror("Error", message)


def show_warning(message: str):
    """Show a warning dialog."""
    messagebox.showwarning("Aviso", message)


def show_info(message: str):
    """Show an informational dialog."""
    messagebox.showinfo("Informacion", message)
