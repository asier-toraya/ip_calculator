"""
Pestaña 2: Práctica Manual Guiada
"""
import tkinter as tk
from tkinter import ttk
import ipaddress
import math
import random
from utils import validators


class PracticeTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.state = {'mode': None, 'ip': None, 'cidr': None, 'network': None, 'num_subnets': None}
        self._create_widgets()
    
    def _create_widgets(self):
        main = tk.Frame(self.frame, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main, text="PRACTICA MANUAL GUIADA", font=('Arial', 16, 'bold'), 
                fg='#2196F3').pack(pady=10)
        tk.Label(main, text="Aprende calculando con retroalimentacion inmediata", 
                font=('Arial', 10, 'italic')).pack(pady=5)
        
        ttk.Separator(main, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Botones
        button_frame = tk.Frame(main)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Nuevo Ejercicio Basico", command=self._start_basic,
                 bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'), 
                 padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Nuevo Ejercicio de Subredes", command=self._start_subnets,
                 bg='#2196F3', fg='white', font=('Arial', 11, 'bold'), 
                 padx=20, pady=10).pack(side=tk.LEFT, padx=10)
        
        # Área de práctica
        practice_area = tk.Frame(main)
        practice_area.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame de inputs
        input_frame = tk.LabelFrame(practice_area, text="Tus Respuestas", 
                                    font=('Arial', 11, 'bold'), padx=15, pady=15)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Ejercicio básico
        self._create_basic_inputs(input_frame)
        
        # Ejercicio de subredes
        self._create_subnet_inputs(input_frame)
        
        # Frame de feedback
        feedback_frame = tk.LabelFrame(practice_area, text="Instrucciones y Retroalimentacion", 
                                      font=('Arial', 11, 'bold'), padx=10, pady=10)
        feedback_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(feedback_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.feedback_text = tk.Text(feedback_frame, height=25, wrap=tk.WORD, 
                                     font=('Courier New', 9), yscrollcommand=scrollbar.set)
        self.feedback_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.feedback_text.yview)
        
        # Mensaje inicial
        initial_msg = """BIENVENIDO A LA PRACTICA GUIADA

OBJETIVO: Aprender a calcular parametros de red manualmente

EJERCICIOS:
1. BASICO: Calcula mascara, red, broadcast, salto y rango de hosts
2. SUBREDES: Calcula bits, nueva mascara y hosts por subred

COMO USAR:
1. Presiona un boton para generar un ejercicio
2. Calcula manualmente (usa papel si lo necesitas)
3. Ingresa tus respuestas
4. Presiona "Verificar"
5. Los campos correctos se marcan en VERDE
6. Los incorrectos en ROJO con la respuesta correcta

Presiona un boton arriba para comenzar!
"""
        self.feedback_text.insert('1.0', initial_msg)
    
    def _create_basic_inputs(self, parent):
        """Crea inputs para ejercicio básico"""
        frame = tk.LabelFrame(parent, text="Ejercicio Basico", padx=10, pady=10)
        frame.pack(fill=tk.X, pady=5)
        
        labels = ["Mascara:", "Red:", "Broadcast:", "Salto:", "Primer host:", "Ultimo host:"]
        self.basic_entries = []
        
        for i, label in enumerate(labels):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky='w', pady=3)
            entry = tk.Entry(frame, width=20)
            entry.grid(row=i, column=1, pady=3, padx=5)
            self.basic_entries.append(entry)
        
        tk.Button(frame, text="Verificar Respuestas", command=self._verify_basic,
                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'), 
                 padx=15, pady=5).grid(row=len(labels), column=0, columnspan=2, pady=10)
    
    def _create_subnet_inputs(self, parent):
        """Crea inputs para ejercicio de subredes"""
        frame = tk.LabelFrame(parent, text="Ejercicio de Subredes", padx=10, pady=10)
        frame.pack(fill=tk.X, pady=5)
        
        labels = ["Bits:", "Nueva mascara:", "Hosts/subred:"]
        self.subnet_entries = []
        
        for i, label in enumerate(labels):
            tk.Label(frame, text=label).grid(row=i, column=0, sticky='w', pady=3)
            entry = tk.Entry(frame, width=20)
            entry.grid(row=i, column=1, pady=3, padx=5)
            self.subnet_entries.append(entry)
        
        tk.Button(frame, text="Verificar Subredes", command=self._verify_subnets,
                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'), 
                 padx=15, pady=5).grid(row=len(labels), column=0, columnspan=2, pady=10)
    
    def _start_basic(self):
        """Inicia ejercicio básico"""
        self.state['mode'] = 'basic'
        octets = [random.randint(1, 254) for _ in range(4)]
        ip = '.'.join(map(str, octets))
        cidr = random.choice([8, 16, 24, 25, 26, 27, 28, 29, 30])
        self.state['ip'] = ip
        self.state['cidr'] = cidr
        self.state['network'] = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)
        
        for entry in self.basic_entries:
            entry.delete(0, tk.END)
            entry.config(bg='white')
        
        self.feedback_text.delete('1.0', tk.END)
        output = f"EJERCICIO BASICO\n{'=' * 80}\n\nIP: {ip}/{cidr}\n\n"
        output += "CALCULA:\n1. Mascara de red\n2. Direccion de red\n3. Broadcast\n"
        output += "4. Salto de bloque\n5. Primer host\n6. Ultimo host\n\n"
        output += "GUIA DE CALCULO RAPIDO\n" + "=" * 80 + "\n\n"
        output += "TABLA DE REFERENCIA:\n"
        output += "/8  -> 255.0.0.0       | /24 -> 255.255.255.0\n"
        output += "/16 -> 255.255.0.0     | /25 -> 255.255.255.128\n"
        output += "/26 -> 255.255.255.192 | /27 -> 255.255.255.224\n"
        output += "/28 -> 255.255.255.240 | /29 -> 255.255.255.248\n"
        output += "/30 -> 255.255.255.252\n"
        
        self.feedback_text.insert('1.0', output)
    
    def _start_subnets(self):
        """Inicia ejercicio de subredes"""
        self.state['mode'] = 'subnets'
        octets = [random.randint(1, 254) for _ in range(4)]
        ip = '.'.join(map(str, octets))
        cidr = random.choice([16, 20, 24])
        num_subnets = random.randint(2, 8)
        
        self.state['ip'] = ip
        self.state['cidr'] = cidr
        self.state['num_subnets'] = num_subnets
        
        for entry in self.subnet_entries:
            entry.delete(0, tk.END)
            entry.config(bg='white')
        
        self.feedback_text.delete('1.0', tk.END)
        output = f"EJERCICIO DE SUBREDES\n{'=' * 80}\n\n"
        output += f"Red base: {ip}/{cidr}\n"
        output += f"Numero de subredes necesarias: {num_subnets}\n\n"
        output += "CALCULA:\n1. Bits necesarios\n2. Nueva mascara (formato /XX)\n3. Hosts por subred\n"
        
        self.feedback_text.insert('1.0', output)
    
    def _verify_basic(self):
        """Verifica respuestas del ejercicio básico"""
        if self.state['mode'] != 'basic':
            validators.show_warning("Primero inicia un ejercicio basico")
            return
        
        network = self.state['network']
        mask_octets = [int(x) for x in str(network.netmask).split('.')]
        determining_octet = next((i for i in range(3, -1, -1) if mask_octets[i] != 255), -1)
        
        correct = [
            str(network.netmask),
            str(network.network_address),
            str(network.broadcast_address),
            str(256 - mask_octets[determining_octet] if determining_octet >= 0 else 256),
            str(network.network_address + 1),
            str(network.broadcast_address - 1)
        ]
        
        labels = ['Mascara', 'Red', 'Broadcast', 'Salto', 'Primer host', 'Ultimo host']
        results = []
        all_correct = True
        
        for i, (entry, correct_val, label) in enumerate(zip(self.basic_entries, correct, labels)):
            user_val = entry.get().strip()
            if user_val == correct_val:
                entry.config(bg='lightgreen')
                results.append(f"✅ {label}: CORRECTO")
            else:
                entry.config(bg='lightcoral')
                results.append(f"❌ {label}: Tu respuesta: {user_val}, Correcta: {correct_val}")
                all_correct = False
        
        self.feedback_text.delete('1.0', tk.END)
        output = "RESULTADOS\n" + "=" * 80 + "\n\n"
        output += "\n".join(results) + "\n\n"
        output += "EXCELENTE! Todas correctas.\n" if all_correct else "Revisa las respuestas en rojo.\n"
        self.feedback_text.insert('1.0', output)
    
    def _verify_subnets(self):
        """Verifica respuestas del ejercicio de subredes"""
        if self.state['mode'] != 'subnets':
            validators.show_warning("Primero inicia un ejercicio de subredes")
            return
        
        num_subnets = self.state['num_subnets']
        base_cidr = self.state['cidr']
        
        correct_bits = str(math.ceil(math.log2(num_subnets)))
        correct_newmask = f"/{base_cidr + int(correct_bits)}"
        correct_hosts = str(2**(32 - (base_cidr + int(correct_bits))) - 2)
        
        correct = [correct_bits, correct_newmask, correct_hosts]
        labels = ['Bits', 'Mascara', 'Hosts']
        results = []
        all_correct = True
        
        for entry, correct_val, label in zip(self.subnet_entries, correct, labels):
            user_val = entry.get().strip()
            if user_val == correct_val:
                entry.config(bg='lightgreen')
                results.append(f"✅ {label}: CORRECTO")
            else:
                entry.config(bg='lightcoral')
                results.append(f"❌ {label}: {user_val} -> Correcta: {correct_val}")
                all_correct = False
        
        self.feedback_text.delete('1.0', tk.END)
        output = "RESULTADOS\n" + "=" * 80 + "\n\n"
        output += "\n".join(results) + "\n\n"
        output += "EXCELENTE! Todas correctas.\n" if all_correct else "Revisa las respuestas en rojo.\n"
        self.feedback_text.insert('1.0', output)
