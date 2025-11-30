"""
Pestaña 1: Cálculo Detallado Paso a Paso
"""
import tkinter as tk
from tkinter import ttk
from core import network_calc, subnet_calc
from utils import validators


class DetailedTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        # Frame de entrada
        frame_input = tk.Frame(self.frame, pady=10)
        frame_input.pack(fill=tk.X, padx=20)
        
        tk.Label(frame_input, text="IP con mascara (ej: 192.168.0.11/24):", 
                font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
        self.entry_ip = tk.Entry(frame_input, width=40, font=('Arial', 12))
        self.entry_ip.pack(pady=5, fill=tk.X)
        
        tk.Button(frame_input, text="Calcular Detallado", command=self._calculate_detailed, 
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), 
                 padx=20, pady=5).pack(pady=10)
        
        ttk.Separator(self.frame, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Frame de subredes
        frame_subnets = tk.LabelFrame(self.frame, text="Calculo de Subredes", padx=10, pady=10)
        frame_subnets.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_subnets, text="Numero de subredes:").pack(side=tk.LEFT, padx=5)
        self.entry_subnets = tk.Entry(frame_subnets, width=10)
        self.entry_subnets.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_subnets, text="Calcular Subredes", command=self._calculate_subnets,
                 bg='#2196F3', fg='white', font=('Arial', 9, 'bold'), 
                 padx=15, pady=3).pack(side=tk.LEFT, padx=10)
        
        ttk.Separator(self.frame, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Frame de dispositivos
        frame_devices = tk.LabelFrame(self.frame, text="Subredes por Dispositivos", padx=10, pady=10)
        frame_devices.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_devices, text="Dispositivos (separados por coma):").pack(side=tk.LEFT, padx=5)
        self.entry_devices = tk.Entry(frame_devices, width=25)
        self.entry_devices.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_devices, text="Calcular por Dispositivos", command=self._calculate_devices,
                 bg='#FF9800', fg='white', font=('Arial', 9, 'bold'), 
                 padx=15, pady=3).pack(side=tk.LEFT, padx=10)
        
        # Frame de resultados
        frame_results = tk.Frame(self.frame, padx=10, pady=10)
        frame_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_results)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_output = tk.Text(frame_results, height=30, wrap=tk.WORD, 
                                   font=('Courier New', 9), yscrollcommand=scrollbar.set)
        self.text_output.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_output.yview)
        
        # Instrucciones iniciales
        instructions = """CALCULADORA DE RED - MODO DETALLADO

Ingresa una IP/CIDR (ej: 192.168.0.11/24) y presiona los botones para ver:
  - Calculo detallado de mascara, red, broadcast y salto de bloque
  - Division en subredes con explicacion paso a paso
  - Subredes optimizadas por numero de dispositivos
"""
        self.text_output.insert('1.0', instructions)
    
    def _calculate_detailed(self):
        """Calcula detalles de la red"""
        ip_input = self.entry_ip.get().strip()
        valid, network, error = validators.validate_ip_cidr(ip_input)
        
        if not valid:
            validators.show_error(error)
            return
        
        try:
            details = network_calc.calculate_network_details(ip_input)
            output = network_calc.format_detailed_output(details)
            self.text_output.delete('1.0', tk.END)
            self.text_output.insert('1.0', output)
        except Exception as e:
            validators.show_error(f"Error al calcular: {e}")
    
    def _calculate_subnets(self):
        """Calcula división en subredes"""
        ip_input = self.entry_ip.get().strip()
        valid, network, error = validators.validate_ip_cidr(ip_input)
        
        if not valid:
            validators.show_error(error)
            return
        
        valid, num_subnets, error = validators.validate_positive_int(
            self.entry_subnets.get(), "Numero de subredes")
        
        if not valid:
            validators.show_error(error)
            return
        
        try:
            subnet_info, error = subnet_calc.calculate_subnets(network, num_subnets)
            if error:
                self.text_output.delete('1.0', tk.END)
                self.text_output.insert('1.0', error)
                return
            
            output = subnet_calc.format_subnets_output(network, num_subnets, subnet_info)
            self.text_output.delete('1.0', tk.END)
            self.text_output.insert('1.0', output)
        except Exception as e:
            validators.show_error(f"Error al calcular: {e}")
    
    def _calculate_devices(self):
        """Calcula subredes por dispositivos"""
        ip_input = self.entry_ip.get().strip()
        valid, network, error = validators.validate_ip_cidr(ip_input)
        
        if not valid:
            validators.show_error(error)
            return
        
        devices_str = self.entry_devices.get().strip()
        try:
            devices_list = [int(x.strip()) for x in devices_str.split(',') if x.strip()]
            if not devices_list or any(d < 1 for d in devices_list):
                raise ValueError("Todos los valores deben ser mayores a 0")
        except ValueError as e:
            validators.show_error(f"Valores invalidos: {e}")
            return
        
        try:
            results = subnet_calc.calculate_subnets_by_devices(network, devices_list)
            output = subnet_calc.format_devices_output(network, devices_list, results)
            self.text_output.delete('1.0', tk.END)
            self.text_output.insert('1.0', output)
        except Exception as e:
            validators.show_error(f"Error al calcular: {e}")
