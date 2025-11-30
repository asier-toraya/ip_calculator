"""
Pestaña 3: Generador de Esquemas para Cisco Packet Tracer
"""
import tkinter as tk
from tkinter import ttk
from core import cpt_generator
from utils import validators


class CPTTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        main = tk.Frame(self.frame, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main, text="GENERADOR DE ESQUEMAS PARA CISCO PACKET TRACER", 
                font=('Arial', 16, 'bold'), fg='#FF6600').pack(pady=10)
        tk.Label(main, text="Genera configuraciones detalladas listas para implementar", 
                font=('Arial', 10, 'italic')).pack(pady=5)
        
        ttk.Separator(main, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Frame de inputs
        input_frame = tk.LabelFrame(main, text="Parametros de Red", 
                                   font=('Arial', 11, 'bold'), padx=15, pady=15)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Grid de inputs
        tk.Label(input_frame, text="Direccion IP base (ej: 192.168.1.0/24):", 
                font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.entry_ip = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.entry_ip.grid(row=0, column=1, pady=5, padx=10)
        self.entry_ip.insert(0, "192.168.1.0/24")
        
        tk.Label(input_frame, text="Numero de subredes:", 
                font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.entry_subnets = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.entry_subnets.grid(row=1, column=1, pady=5, padx=10)
        self.entry_subnets.insert(0, "4")
        
        tk.Label(input_frame, text="Numero de routers:", 
                font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        self.entry_routers = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.entry_routers.grid(row=2, column=1, pady=5, padx=10)
        self.entry_routers.insert(0, "2")
        
        tk.Label(input_frame, text="Numero de switches:", 
                font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=5)
        self.entry_switches = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.entry_switches.grid(row=3, column=1, pady=5, padx=10)
        self.entry_switches.insert(0, "4")
        
        tk.Label(input_frame, text="Dispositivos por subred (separados por coma):", 
                font=('Arial', 10)).grid(row=4, column=0, sticky='w', pady=5)
        self.entry_devices = tk.Entry(input_frame, width=30, font=('Arial', 10))
        self.entry_devices.grid(row=4, column=1, pady=5, padx=10)
        self.entry_devices.insert(0, "10,15,8,12")
        
        tk.Button(input_frame, text="Generar Esquema CPT", command=self._generate_schema,
                 bg='#FF6600', fg='white', font=('Arial', 11, 'bold'), 
                 padx=20, pady=10).grid(row=5, column=0, columnspan=2, pady=15)
        
        # Frame de resultados
        result_frame = tk.Frame(main, padx=10, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_output = tk.Text(result_frame, height=25, wrap=tk.WORD, 
                                   font=('Courier New', 9), yscrollcommand=scrollbar.set)
        self.text_output.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_output.yview)
        
        # Instrucciones iniciales
        instructions = """BIENVENIDO AL GENERADOR DE ESQUEMAS CPT

Este generador crea configuraciones detalladas para implementar en Cisco Packet Tracer.

INSTRUCCIONES:
1. Ingresa la direccion IP base con mascara CIDR (ej: 192.168.1.0/24)
2. Especifica el numero de subredes que necesitas
3. Indica cuantos routers y switches tendras
4. Ingresa el numero de dispositivos por subred separados por comas
   (debe coincidir con el numero de subredes)

EJEMPLO:
- IP base: 192.168.1.0/24
- Subredes: 4
- Routers: 2
- Switches: 4
- Dispositivos: 10,15,8,12

El sistema generara:
✓ Configuracion detallada de cada subred
✓ Asignacion de IPs para routers (gateways)
✓ Configuracion de switches con VLANs
✓ Asignacion de IPs para todos los dispositivos
✓ Topologia de conexiones

Presiona "Generar Esquema CPT" para comenzar!
"""
        self.text_output.insert('1.0', instructions)
    
    def _generate_schema(self):
        """Genera el esquema CPT"""
        # Validar IP
        ip_input = self.entry_ip.get().strip()
        valid, network, error = validators.validate_ip_cidr(ip_input)
        if not valid:
            validators.show_error(error)
            return
        
        # Validar número de subredes
        valid, num_subnets, error = validators.validate_positive_int(
            self.entry_subnets.get(), "Numero de subredes")
        if not valid:
            validators.show_error(error)
            return
        
        # Validar número de routers
        valid, num_routers, error = validators.validate_positive_int(
            self.entry_routers.get(), "Numero de routers")
        if not valid:
            validators.show_error(error)
            return
        
        # Validar número de switches
        valid, num_switches, error = validators.validate_positive_int(
            self.entry_switches.get(), "Numero de switches")
        if not valid:
            validators.show_error(error)
            return
        
        # Validar lista de dispositivos
        valid, devices_list, error = validators.validate_device_list(
            self.entry_devices.get(), num_subnets)
        if not valid:
            validators.show_error(error)
            return
        
        # Generar esquema
        try:
            output, error = cpt_generator.generate_cpt_topology(
                network, num_subnets, num_routers, num_switches, devices_list)
            
            if error:
                validators.show_error(error)
                return
            
            self.text_output.delete('1.0', tk.END)
            self.text_output.insert('1.0', output)
        except Exception as e:
            validators.show_error(f"Error al generar esquema: {e}")
