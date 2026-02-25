"""Tab 4: advanced CPT generator with per-subnet configuration."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core import cpt_advanced_generator
from utils import validators

from .theme import configure_output_text
from .ui_utils import copy_text_to_clipboard, set_text_output


class CPTAdvancedTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="App.TFrame", padding=16)
        self.subnet_frames = []
        self.subnet_entries = []
        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(self.frame, text="CPT Avanzado: configuracion por subred", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            self.frame,
            text="Define routers, switches y hosts por cada subred con enrutamiento estatico, RIP u OSPF.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        config_frame = ttk.LabelFrame(self.frame, text="Configuracion general", padding=12)
        config_frame.pack(fill=tk.X)

        self.entry_base_ip = self._create_labeled_entry(config_frame, 0, "IP base (ej: 192.168.1.0/16):", "192.168.1.0/16")
        self.entry_num_subnets = self._create_labeled_entry(config_frame, 1, "Numero de subredes:", "3")

        ttk.Button(
            config_frame,
            text="Generar campos de subredes",
            command=self._generate_subnet_fields,
            style="Primary.TButton",
        ).grid(row=1, column=2, padx=(8, 0))

        ttk.Label(config_frame, text="Tipo de enrutamiento:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.routing_var = tk.StringVar(value="estatico")

        routing_frame = ttk.Frame(config_frame, style="App.TFrame")
        routing_frame.grid(row=2, column=1, columnspan=2, sticky="w", pady=(8, 0))

        ttk.Radiobutton(routing_frame, text="Estatico", variable=self.routing_var, value="estatico").pack(
            side=tk.LEFT
        )
        ttk.Radiobutton(routing_frame, text="RIP", variable=self.routing_var, value="rip").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Radiobutton(routing_frame, text="OSPF", variable=self.routing_var, value="ospf").pack(side=tk.LEFT, padx=(8, 0))

        config_frame.columnconfigure(1, weight=1)

        subnets_wrapper = ttk.LabelFrame(self.frame, text="Subredes", padding=8)
        subnets_wrapper.pack(fill=tk.BOTH, expand=False, pady=(10, 8))

        canvas = tk.Canvas(subnets_wrapper, height=210, bg="#FCFDFE", highlightthickness=0)
        scrollbar = ttk.Scrollbar(subnets_wrapper, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style="App.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        action_row = ttk.Frame(self.frame, style="App.TFrame")
        action_row.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(
            action_row,
            text="Generar esquema CPT avanzado",
            command=self._generate_schema,
            style="Primary.TButton",
        ).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Copiar salida", command=self._copy_output, style="Secondary.TButton").pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(action_row, text="Limpiar salida", command=self._clear_output, style="Secondary.TButton").pack(
            side=tk.LEFT, padx=(8, 0)
        )

        result_frame = ttk.LabelFrame(self.frame, text="Resultado", padding=8)
        result_frame.pack(fill=tk.BOTH, expand=True)

        result_scrollbar = ttk.Scrollbar(result_frame)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_output = tk.Text(
            result_frame,
            height=16,
            wrap=tk.WORD,
            font=("Cascadia Mono", 9),
            yscrollcommand=result_scrollbar.set,
        )
        self.text_output.pack(fill=tk.BOTH, expand=True)
        configure_output_text(self.text_output)
        result_scrollbar.config(command=self.text_output.yview)

        set_text_output(
            self.text_output,
            (
                "CPT AVANZADO\n\n"
                "1) Define red base y numero de subredes.\n"
                "2) Genera los campos y configura routers/switches/hosts por subred.\n"
                "3) Selecciona el protocolo de enrutamiento y genera el esquema."
            ),
        )

    def _create_labeled_entry(self, parent, row, label, default):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        entry = ttk.Entry(parent, width=28)
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

    def _generate_subnet_fields(self):
        for frame in self.subnet_frames:
            frame.destroy()

        self.subnet_frames.clear()
        self.subnet_entries.clear()

        valid, num_subnets, error = validators.validate_positive_int(
            self.entry_num_subnets.get(), "Numero de subredes"
        )
        if not valid:
            validators.show_error(error)
            return

        if num_subnets > 12:
            validators.show_error("Para mantener legibilidad, usa un maximo de 12 subredes.")
            return

        for index in range(num_subnets):
            frame = ttk.LabelFrame(
                self.scrollable_frame,
                text=f"Subred {index}" + (" (principal)" if index == 0 else ""),
                padding=8,
            )
            frame.pack(fill=tk.X, padx=6, pady=4)

            ttk.Label(frame, text="Routers:").grid(row=0, column=0, sticky="w")
            entry_routers = ttk.Entry(frame, width=8)
            entry_routers.grid(row=0, column=1, padx=(6, 10))
            entry_routers.insert(0, "1" if index == 0 else "0")

            ttk.Label(frame, text="Switches:").grid(row=0, column=2, sticky="w")
            entry_switches = ttk.Entry(frame, width=8)
            entry_switches.grid(row=0, column=3, padx=(6, 10))
            entry_switches.insert(0, "1")

            ttk.Label(frame, text="Hosts:").grid(row=0, column=4, sticky="w")
            entry_hosts = ttk.Entry(frame, width=8)
            entry_hosts.grid(row=0, column=5, padx=(6, 0))
            entry_hosts.insert(0, "10" if index == 0 else "5")

            self.subnet_frames.append(frame)
            self.subnet_entries.append(
                {
                    "routers": entry_routers,
                    "switches": entry_switches,
                    "hosts": entry_hosts,
                }
            )

    def _generate_schema(self):
        valid, network, error = validators.validate_ip_cidr(self.entry_base_ip.get().strip())
        if not valid:
            validators.show_error(error)
            return

        if not self.subnet_entries:
            validators.show_error("Primero genera los campos de subredes.")
            return

        subnet_configs = []
        for index, entries in enumerate(self.subnet_entries):
            valid, routers, error = validators.validate_non_negative_int(entries["routers"].get(), "Routers")
            if not valid:
                validators.show_error(f"Subred {index}: {error}")
                return

            valid, switches, error = validators.validate_non_negative_int(entries["switches"].get(), "Switches")
            if not valid:
                validators.show_error(f"Subred {index}: {error}")
                return

            valid, hosts, error = validators.validate_non_negative_int(entries["hosts"].get(), "Hosts")
            if not valid:
                validators.show_error(f"Subred {index}: {error}")
                return

            subnet_configs.append({"routers": routers, "switches": switches, "hosts": hosts})

        try:
            output, calc_error = cpt_advanced_generator.generate_advanced_cpt(
                network,
                subnet_configs,
                self.routing_var.get(),
            )
        except Exception as error:
            validators.show_error(f"Error al generar esquema avanzado: {error}")
            return

        if calc_error:
            validators.show_error(calc_error)
            return

        set_text_output(self.text_output, output)
