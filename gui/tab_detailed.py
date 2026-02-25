"""Tab 1: detailed network calculations."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core import network_calc, subnet_calc
from utils import validators

from .theme import configure_output_text
from .ui_utils import copy_text_to_clipboard, set_text_output


class DetailedTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="App.TFrame", padding=16)
        self._create_widgets()

    def _create_widgets(self):
        input_frame = ttk.LabelFrame(self.frame, text="Parametros de red", padding=12)
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="IP con mascara (ej: 192.168.0.11/24):").grid(
            row=0, column=0, sticky="w"
        )
        self.entry_ip = ttk.Entry(input_frame, width=38)
        self.entry_ip.grid(row=0, column=1, padx=8, sticky="we")
        self.entry_ip.insert(0, "192.168.10.15/24")

        ttk.Button(
            input_frame,
            text="Calcular detallado",
            command=self._calculate_detailed,
            style="Primary.TButton",
        ).grid(row=0, column=2, padx=(6, 0))

        ttk.Label(input_frame, text="Numero de subredes:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.entry_subnets = ttk.Entry(input_frame, width=10)
        self.entry_subnets.grid(row=1, column=1, sticky="w", padx=8, pady=(10, 0))
        self.entry_subnets.insert(0, "4")

        ttk.Button(
            input_frame,
            text="Dividir en subredes",
            command=self._calculate_subnets,
            style="Secondary.TButton",
        ).grid(row=1, column=2, padx=(6, 0), pady=(10, 0))

        ttk.Label(input_frame, text="Dispositivos por subred (coma):").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        self.entry_devices = ttk.Entry(input_frame, width=38)
        self.entry_devices.grid(row=2, column=1, padx=8, sticky="we", pady=(10, 0))
        self.entry_devices.insert(0, "60,30,12")

        ttk.Button(
            input_frame,
            text="VLSM por dispositivos",
            command=self._calculate_devices,
            style="Secondary.TButton",
        ).grid(row=2, column=2, padx=(6, 0), pady=(10, 0))

        input_frame.columnconfigure(1, weight=1)

        actions = ttk.Frame(self.frame, style="App.TFrame")
        actions.pack(fill=tk.X, pady=(10, 8))

        ttk.Button(actions, text="Copiar salida", command=self._copy_output, style="Secondary.TButton").pack(
            side=tk.LEFT
        )
        ttk.Button(actions, text="Limpiar salida", command=self._clear_output, style="Secondary.TButton").pack(
            side=tk.LEFT, padx=(8, 0)
        )

        output_frame = ttk.LabelFrame(self.frame, text="Resultado", padding=8)
        output_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_output = tk.Text(
            output_frame,
            height=28,
            wrap=tk.WORD,
            font=("Cascadia Mono", 9),
            yscrollcommand=scrollbar.set,
        )
        self.text_output.pack(fill=tk.BOTH, expand=True)
        configure_output_text(self.text_output)
        scrollbar.config(command=self.text_output.yview)

        set_text_output(
            self.text_output,
            (
                "CALCULADORA DE RED - MODO DETALLADO\n\n"
                "1) Ingresa una red base en formato IP/CIDR.\n"
                "2) Usa 'Calcular detallado' para ver mascara, red, broadcast y hosts.\n"
                "3) Usa 'Dividir en subredes' para subnetting fijo.\n"
                "4) Usa 'VLSM por dispositivos' para reparto optimizado por hosts."
            ),
        )

    def _copy_output(self):
        copied = copy_text_to_clipboard(self.frame.winfo_toplevel(), self.text_output)
        if copied:
            validators.show_info("Salida copiada al portapapeles.")
        else:
            validators.show_warning("No hay contenido para copiar.")

    def _clear_output(self):
        set_text_output(self.text_output, "")

    def _calculate_detailed(self):
        ip_input = self.entry_ip.get().strip()
        valid, _, error = validators.validate_ip_cidr(ip_input)
        if not valid:
            validators.show_error(error)
            return

        try:
            details = network_calc.calculate_network_details(ip_input)
            output = network_calc.format_detailed_output(details)
        except Exception as error:
            validators.show_error(f"Error al calcular detalles: {error}")
            return

        set_text_output(self.text_output, output)

    def _calculate_subnets(self):
        ip_input = self.entry_ip.get().strip()
        valid, network, error = validators.validate_ip_cidr(ip_input)
        if not valid:
            validators.show_error(error)
            return

        valid, num_subnets, error = validators.validate_positive_int(
            self.entry_subnets.get(), "Numero de subredes"
        )
        if not valid:
            validators.show_error(error)
            return

        try:
            subnet_info, calc_error = subnet_calc.calculate_subnets(network, num_subnets)
            if calc_error:
                set_text_output(self.text_output, calc_error)
                return
            output = subnet_calc.format_subnets_output(network, num_subnets, subnet_info)
        except Exception as error:
            validators.show_error(f"Error al calcular subredes: {error}")
            return

        set_text_output(self.text_output, output)

    def _calculate_devices(self):
        ip_input = self.entry_ip.get().strip()
        valid, network, error = validators.validate_ip_cidr(ip_input)
        if not valid:
            validators.show_error(error)
            return

        try:
            devices_list = validators.parse_int_list(self.entry_devices.get())
        except ValueError:
            validators.show_error("La lista de dispositivos debe contener solo enteros.")
            return

        if not devices_list:
            validators.show_error("Debes ingresar al menos un valor de dispositivos.")
            return

        if any(value < 1 for value in devices_list):
            validators.show_error("Todos los dispositivos deben ser mayores a 0.")
            return

        try:
            results = subnet_calc.calculate_subnets_by_devices(network, devices_list)
            output = subnet_calc.format_devices_output(network, devices_list, results)
        except Exception as error:
            validators.show_error(f"Error al calcular VLSM: {error}")
            return

        set_text_output(self.text_output, output)
