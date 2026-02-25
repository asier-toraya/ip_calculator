"""Tab 3: basic Packet Tracer schema generator."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core import cpt_generator
from utils import validators

from .theme import configure_output_text
from .ui_utils import copy_text_to_clipboard, set_text_output


class CPTTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="App.TFrame", padding=16)
        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(self.frame, text="Generador de Esquemas para Cisco Packet Tracer", style="Section.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            self.frame,
            text="Construye una topologia VLSM con routers, switches, VLANs y gateways.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        input_frame = ttk.LabelFrame(self.frame, text="Parametros de red", padding=12)
        input_frame.pack(fill=tk.X)

        self.entry_ip = self._create_labeled_entry(input_frame, 0, "IP base (ej: 192.168.1.0/24):", "192.168.1.0/24")
        self.entry_subnets = self._create_labeled_entry(input_frame, 1, "Numero de subredes:", "4")
        self.entry_routers = self._create_labeled_entry(input_frame, 2, "Numero de routers:", "2")
        self.entry_switches = self._create_labeled_entry(input_frame, 3, "Numero de switches:", "4")
        self.entry_devices = self._create_labeled_entry(
            input_frame,
            4,
            "Dispositivos por subred (coma):",
            "10,15,8,12",
        )

        input_frame.columnconfigure(1, weight=1)

        actions = ttk.Frame(self.frame, style="App.TFrame")
        actions.pack(fill=tk.X, pady=(10, 8))

        ttk.Button(
            actions,
            text="Generar esquema CPT",
            command=self._generate_schema,
            style="Primary.TButton",
        ).pack(side=tk.LEFT)
        ttk.Button(actions, text="Copiar salida", command=self._copy_output, style="Secondary.TButton").pack(
            side=tk.LEFT, padx=(8, 0)
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
            height=24,
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
                "GENERADOR CPT\n\n"
                "1) Define red base, subredes, routers y switches.\n"
                "2) Especifica hosts por subred (mismo numero que subredes).\n"
                "3) Genera el esquema para copiar en Packet Tracer."
            ),
        )

    def _create_labeled_entry(self, parent, row, label, default):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        entry = ttk.Entry(parent, width=35)
        entry.grid(row=row, column=1, sticky="we", padx=(8, 0), pady=4)
        entry.insert(0, default)
        return entry

    def _copy_output(self):
        copied = copy_text_to_clipboard(self.frame.winfo_toplevel(), self.text_output)
        if copied:
            validators.show_info("Salida copiada al portapapeles.")
        else:
            validators.show_warning("No hay contenido para copiar.")

    def _clear_output(self):
        set_text_output(self.text_output, "")

    def _generate_schema(self):
        valid, network, error = validators.validate_ip_cidr(self.entry_ip.get().strip())
        if not valid:
            validators.show_error(error)
            return

        valid, num_subnets, error = validators.validate_positive_int(self.entry_subnets.get(), "Numero de subredes")
        if not valid:
            validators.show_error(error)
            return

        valid, num_routers, error = validators.validate_positive_int(self.entry_routers.get(), "Numero de routers")
        if not valid:
            validators.show_error(error)
            return

        valid, num_switches, error = validators.validate_positive_int(
            self.entry_switches.get(), "Numero de switches"
        )
        if not valid:
            validators.show_error(error)
            return

        valid, devices_list, error = validators.validate_device_list(self.entry_devices.get(), num_subnets)
        if not valid:
            validators.show_error(error)
            return

        try:
            output, calc_error = cpt_generator.generate_cpt_topology(
                network,
                num_subnets,
                num_routers,
                num_switches,
                devices_list,
            )
        except Exception as error:
            validators.show_error(f"Error al generar esquema: {error}")
            return

        if calc_error:
            validators.show_error(calc_error)
            return

        set_text_output(self.text_output, output)
