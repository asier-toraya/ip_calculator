"""Tab 2: guided practice exercises."""

from __future__ import annotations

import ipaddress
import math
import random
import tkinter as tk
from tkinter import ttk

from utils import validators

from .theme import configure_output_text
from .ui_utils import clear_entries, copy_text_to_clipboard, set_text_output


class PracticeTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, style="App.TFrame", padding=16)
        self.state = {
            "mode": None,
            "ip": None,
            "cidr": None,
            "network": None,
            "num_subnets": None,
        }
        self._create_widgets()

    def _create_widgets(self):
        title_row = ttk.Frame(self.frame, style="App.TFrame")
        title_row.pack(fill=tk.X)

        ttk.Label(title_row, text="Practica Manual Guiada", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            title_row,
            text="Entrena calculos de red y subnetting con verificacion inmediata.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        button_row = ttk.Frame(self.frame, style="App.TFrame")
        button_row.pack(fill=tk.X, pady=(10, 12))

        ttk.Button(
            button_row,
            text="Nuevo ejercicio basico",
            command=self._start_basic,
            style="Primary.TButton",
        ).pack(side=tk.LEFT)
        ttk.Button(
            button_row,
            text="Nuevo ejercicio de subredes",
            command=self._start_subnets,
            style="Secondary.TButton",
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(
            button_row,
            text="Copiar retroalimentacion",
            command=self._copy_feedback,
            style="Secondary.TButton",
        ).pack(side=tk.RIGHT)

        content = ttk.Panedwindow(self.frame, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(content, style="App.TFrame")
        right = ttk.Frame(content, style="App.TFrame")
        content.add(left, weight=1)
        content.add(right, weight=1)

        self._create_answer_inputs(left)
        self._create_feedback_panel(right)

    def _create_answer_inputs(self, parent):
        basic_frame = ttk.LabelFrame(parent, text="Ejercicio basico", padding=10)
        basic_frame.pack(fill=tk.X)

        labels = ["Mascara", "Red", "Broadcast", "Salto", "Primer host", "Ultimo host"]
        self.basic_entries = []
        for row, label in enumerate(labels):
            ttk.Label(basic_frame, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=3)
            entry = tk.Entry(basic_frame, width=24)
            entry.grid(row=row, column=1, padx=(8, 0), pady=3)
            self.basic_entries.append(entry)

        ttk.Button(
            basic_frame,
            text="Verificar respuestas basicas",
            command=self._verify_basic,
            style="Secondary.TButton",
        ).grid(row=len(labels), column=0, columnspan=2, pady=(10, 0), sticky="we")

        subnet_frame = ttk.LabelFrame(parent, text="Ejercicio de subredes", padding=10)
        subnet_frame.pack(fill=tk.X, pady=(10, 0))

        subnet_labels = ["Bits", "Nueva mascara", "Hosts por subred"]
        self.subnet_entries = []
        for row, label in enumerate(subnet_labels):
            ttk.Label(subnet_frame, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=3)
            entry = tk.Entry(subnet_frame, width=24)
            entry.grid(row=row, column=1, padx=(8, 0), pady=3)
            self.subnet_entries.append(entry)

        ttk.Button(
            subnet_frame,
            text="Verificar respuestas de subredes",
            command=self._verify_subnets,
            style="Secondary.TButton",
        ).grid(row=len(subnet_labels), column=0, columnspan=2, pady=(10, 0), sticky="we")

    def _create_feedback_panel(self, parent):
        feedback_frame = ttk.LabelFrame(parent, text="Instrucciones y retroalimentacion", padding=8)
        feedback_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(feedback_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.feedback_text = tk.Text(
            feedback_frame,
            height=25,
            wrap=tk.WORD,
            font=("Cascadia Mono", 9),
            yscrollcommand=scrollbar.set,
        )
        self.feedback_text.pack(fill=tk.BOTH, expand=True)
        configure_output_text(self.feedback_text)
        scrollbar.config(command=self.feedback_text.yview)

        set_text_output(
            self.feedback_text,
            (
                "PRACTICA GUIADA\n\n"
                "1) Elige un tipo de ejercicio.\n"
                "2) Resuelve manualmente.\n"
                "3) Pulsa verificar.\n\n"
                "Los campos correctos se marcan en verde y los incorrectos en rojo."
            ),
        )

    def _copy_feedback(self):
        copied = copy_text_to_clipboard(self.frame.winfo_toplevel(), self.feedback_text)
        if copied:
            validators.show_info("Retroalimentacion copiada al portapapeles.")
        else:
            validators.show_warning("No hay texto para copiar.")

    def _set_entries_color(self, entries, color):
        for entry in entries:
            entry.configure(bg=color)

    def _start_basic(self):
        self.state["mode"] = "basic"
        octets = [random.randint(1, 254) for _ in range(4)]
        ip = ".".join(map(str, octets))
        cidr = random.choice([8, 16, 24, 25, 26, 27, 28, 29, 30])

        self.state["ip"] = ip
        self.state["cidr"] = cidr
        self.state["network"] = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)

        clear_entries(self.basic_entries)
        self._set_entries_color(self.basic_entries, "white")

        guide = [
            "EJERCICIO BASICO",
            "=" * 80,
            "",
            f"IP: {ip}/{cidr}",
            "",
            "Calcula:",
            "1. Mascara de red",
            "   Tip: /CIDR -> octetos completos en 255 y el parcial con tabla 128,192,224,240,248,252,254.",
            "2. Direccion de red",
            "   Tip: IP AND Mascara; donde la mascara es 255 se conserva, donde es 0 se vuelve 0.",
            "3. Broadcast",
            "   Tip: Broadcast = Red + Wildcard (o poner en 255 todos los bits de host).",
            "4. Salto de bloque",
            "   Tip: Salto = 256 - octeto de mascara que no sea 255.",
            "5. Primer host",
            "   Tip: Primer host = Direccion de red + 1.",
            "6. Ultimo host",
            "   Tip: Ultimo host = Broadcast - 1.",
        ]
        set_text_output(self.feedback_text, "\n".join(guide))

    def _start_subnets(self):
        self.state["mode"] = "subnets"
        octets = [random.randint(1, 254) for _ in range(4)]
        ip = ".".join(map(str, octets))
        cidr = random.choice([16, 20, 24])
        num_subnets = random.randint(2, 8)

        self.state["ip"] = ip
        self.state["cidr"] = cidr
        self.state["num_subnets"] = num_subnets

        clear_entries(self.subnet_entries)
        self._set_entries_color(self.subnet_entries, "white")

        guide = [
            "EJERCICIO DE SUBREDES",
            "=" * 80,
            "",
            f"Red base: {ip}/{cidr}",
            f"Subredes solicitadas: {num_subnets}",
            "",
            "Calcula:",
            "1. Bits necesarios",
            "2. Nueva mascara (/XX)",
            "3. Hosts por subred",
            "",
            "Formula rapida: bits = ceil(log2(subredes))",
        ]
        set_text_output(self.feedback_text, "\n".join(guide))

    def _verify_basic(self):
        if self.state["mode"] != "basic":
            validators.show_warning("Primero inicia un ejercicio basico.")
            return

        network = self.state["network"]
        mask_octets = [int(value) for value in str(network.netmask).split(".")]
        determining_octet = next((idx for idx in range(3, -1, -1) if mask_octets[idx] != 255), -1)

        correct = [
            str(network.netmask),
            str(network.network_address),
            str(network.broadcast_address),
            str(256 - mask_octets[determining_octet] if determining_octet >= 0 else 256),
            str(network.network_address + 1),
            str(network.broadcast_address - 1),
        ]
        labels = ["Mascara", "Red", "Broadcast", "Salto", "Primer host", "Ultimo host"]

        all_correct = True
        rows = ["RESULTADOS", "=" * 80, ""]

        for entry, expected, label in zip(self.basic_entries, correct, labels):
            user_value = entry.get().strip()
            if user_value == expected:
                entry.configure(bg="#D8F5D0")
                rows.append(f"OK {label}: correcto")
            else:
                entry.configure(bg="#FAD7D7")
                rows.append(f"ERROR {label}: tu valor '{user_value}' | esperado '{expected}'")
                all_correct = False

        rows.append("")
        rows.append("Excelente, todo correcto." if all_correct else "Corrige los campos marcados en rojo.")
        set_text_output(self.feedback_text, "\n".join(rows))

    def _verify_subnets(self):
        if self.state["mode"] != "subnets":
            validators.show_warning("Primero inicia un ejercicio de subredes.")
            return

        num_subnets = self.state["num_subnets"]
        base_cidr = self.state["cidr"]

        bits = math.ceil(math.log2(num_subnets))
        correct = [str(bits), f"/{base_cidr + bits}", str((2 ** (32 - (base_cidr + bits))) - 2)]
        labels = ["Bits", "Mascara", "Hosts"]

        all_correct = True
        rows = ["RESULTADOS", "=" * 80, ""]

        for entry, expected, label in zip(self.subnet_entries, correct, labels):
            user_value = entry.get().strip()
            if user_value == expected:
                entry.configure(bg="#D8F5D0")
                rows.append(f"OK {label}: correcto")
            else:
                entry.configure(bg="#FAD7D7")
                rows.append(f"ERROR {label}: tu valor '{user_value}' | esperado '{expected}'")
                all_correct = False

        rows.append("")
        rows.append("Excelente, todo correcto." if all_correct else "Corrige los campos marcados en rojo.")
        set_text_output(self.feedback_text, "\n".join(rows))
