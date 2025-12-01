"""
Pestaña 4: CPT Avanzado - Configuración detallada por subred
"""
import tkinter as tk
from tkinter import ttk, messagebox
from core import cpt_advanced_generator
from utils import validators


class CPTAdvancedTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.subnet_frames = []
        self.subnet_entries = []
        self._create_widgets()
    
    def _create_widgets(self):
        main = tk.Frame(self.frame, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(main, text="CPT AVANZADO - CONFIGURACION POR SUBRED", 
                font=('Arial', 16, 'bold'), fg='#FF6600').pack(pady=10)
        tk.Label(main, text="Configura cada subred individualmente con sus elementos específicos", 
                font=('Arial', 10, 'italic')).pack(pady=5)
        
        ttk.Separator(main, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Frame de configuración general
        config_frame = tk.LabelFrame(main, text="Configuración General", 
                                    font=('Arial', 11, 'bold'), padx=15, pady=15)
        config_frame.pack(fill=tk.X, pady=10)
        
        # IP Base
        tk.Label(config_frame, text="IP Base (ej: 192.168.1.0/16):", 
                font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        self.entry_base_ip = tk.Entry(config_frame, width=25, font=('Arial', 10))
        self.entry_base_ip.grid(row=0, column=1, pady=5, padx=10, sticky='w')
        self.entry_base_ip.insert(0, "192.168.1.0/16")
        
        # Número de subredes
        tk.Label(config_frame, text="Número de subredes:", 
                font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        self.entry_num_subnets = tk.Entry(config_frame, width=10, font=('Arial', 10))
        self.entry_num_subnets.grid(row=1, column=1, pady=5, padx=10, sticky='w')
        self.entry_num_subnets.insert(0, "3")
        
        tk.Button(config_frame, text="Generar Campos de Subredes", 
                 command=self._generate_subnet_fields,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'), 
                 padx=15, pady=5).grid(row=1, column=2, padx=10)
        
        # Tipo de enrutamiento
        tk.Label(config_frame, text="Tipo de enrutamiento:", 
                font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        self.routing_var = tk.StringVar(value="estatico")
        routing_frame = tk.Frame(config_frame)
        routing_frame.grid(row=2, column=1, columnspan=2, sticky='w', padx=10)
        
        tk.Radiobutton(routing_frame, text="Estático", variable=self.routing_var, 
                      value="estatico").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(routing_frame, text="RIP", variable=self.routing_var, 
                      value="rip").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(routing_frame, text="OSPF", variable=self.routing_var, 
                      value="ospf").pack(side=tk.LEFT, padx=5)
        
        # Frame para subredes (scrollable)
        subnets_container = tk.Frame(main)
        subnets_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(subnets_container, text="Configuración de Subredes", 
                font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Canvas con scrollbar para subredes
        canvas = tk.Canvas(subnets_container, height=200)
        scrollbar = tk.Scrollbar(subnets_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón generar
        tk.Button(main, text="Generar Esquema CPT Avanzado", 
                 command=self._generate_schema,
                 bg='#FF6600', fg='white', font=('Arial', 12, 'bold'), 
                 padx=20, pady=10).pack(pady=15)
        
        # Frame de resultados
        result_frame = tk.Frame(main)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_result = tk.Scrollbar(result_frame)
        scrollbar_result.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_output = tk.Text(result_frame, height=15, wrap=tk.WORD, 
                                   font=('Courier New', 9), yscrollcommand=scrollbar_result.set)
        self.text_output.pack(fill=tk.BOTH, expand=True)
        scrollbar_result.config(command=self.text_output.yview)
        
        # Instrucciones iniciales
        instructions = """BIENVENIDO AL GENERADOR CPT AVANZADO

INSTRUCCIONES:
1. Ingresa la IP base con máscara CIDR (ej: 192.168.1.0/16)
2. Especifica el número de subredes que necesitas
3. Presiona "Generar Campos de Subredes"
4. Configura cada subred individualmente:
   - Subred 0: RED PRINCIPAL (donde el router se conecta a Internet)
   - Otras subredes: Redes internas
5. Para cada subred indica:
   - Número de Routers
   - Número de Switches
   - Número de Hosts/Dispositivos
6. Selecciona el tipo de enrutamiento (Estático, RIP u OSPF)
7. Presiona "Generar Esquema CPT Avanzado"

El sistema generará:
✓ Configuración detallada de VLANs
✓ IPs de todos los dispositivos
✓ Configuración de puertos (Access/Trunk)
✓ Comandos de enrutamiento
✓ Gateway y máscaras de subred

NOTA: Solo se mostrarán los primeros 4 hosts por subred para mantener 
      el esquema legible.
"""
        self.text_output.insert('1.0', instructions)
    
    def _generate_subnet_fields(self):
        """Genera campos dinámicos para configurar cada subred"""
        # Limpiar campos anteriores
        for frame in self.subnet_frames:
            frame.destroy()
        self.subnet_frames.clear()
        self.subnet_entries.clear()
        
        # Validar número de subredes
        try:
            num_subnets = int(self.entry_num_subnets.get())
            if num_subnets < 1 or num_subnets > 10:
                messagebox.showerror("Error", "El número de subredes debe estar entre 1 y 10")
                return
        except ValueError:
            messagebox.showerror("Error", "Número de subredes inválido")
            return
        
        # Crear campos para cada subred
        for i in range(num_subnets):
            frame = tk.LabelFrame(self.scrollable_frame, 
                                 text=f"Subred {i}" + (" - RED PRINCIPAL" if i == 0 else ""),
                                 font=('Arial', 10, 'bold'),
                                 padx=10, pady=10,
                                 bg='#FFF3E0' if i == 0 else 'white')
            frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Routers
            tk.Label(frame, text="Routers:", bg=frame['bg']).grid(row=0, column=0, sticky='w', padx=5)
            entry_routers = tk.Entry(frame, width=10)
            entry_routers.grid(row=0, column=1, padx=5)
            entry_routers.insert(0, "1" if i == 0 else "0")
            
            # Switches
            tk.Label(frame, text="Switches:", bg=frame['bg']).grid(row=0, column=2, sticky='w', padx=5)
            entry_switches = tk.Entry(frame, width=10)
            entry_switches.grid(row=0, column=3, padx=5)
            entry_switches.insert(0, "1")
            
            # Hosts
            tk.Label(frame, text="Hosts:", bg=frame['bg']).grid(row=0, column=4, sticky='w', padx=5)
            entry_hosts = tk.Entry(frame, width=10)
            entry_hosts.grid(row=0, column=5, padx=5)
            entry_hosts.insert(0, "10" if i == 0 else "5")
            
            self.subnet_frames.append(frame)
            self.subnet_entries.append({
                'routers': entry_routers,
                'switches': entry_switches,
                'hosts': entry_hosts
            })
    
    def _generate_schema(self):
        """Genera el esquema CPT avanzado"""
        # Validar IP base
        base_ip = self.entry_base_ip.get().strip()
        valid, network, error = validators.validate_ip_cidr(base_ip)
        if not valid:
            validators.show_error(error)
            return
        
        # Validar que se hayan generado los campos
        if not self.subnet_entries:
            validators.show_error("Primero genera los campos de subredes")
            return
        
        # Recopilar configuración de cada subred
        subnet_configs = []
        for i, entries in enumerate(self.subnet_entries):
            try:
                routers = int(entries['routers'].get())
                switches = int(entries['switches'].get())
                hosts = int(entries['hosts'].get())
                
                if routers < 0 or switches < 0 or hosts < 0:
                    raise ValueError(f"Los valores de la subred {i} deben ser >= 0")
                
                subnet_configs.append({
                    'routers': routers,
                    'switches': switches,
                    'hosts': hosts
                })
            except ValueError as e:
                validators.show_error(f"Error en subred {i}: {e}")
                return
        
        # Obtener tipo de enrutamiento
        routing_type = self.routing_var.get()
        
        # Generar esquema
        try:
            output, error = cpt_advanced_generator.generate_advanced_cpt(
                network, subnet_configs, routing_type)
            
            if error:
                validators.show_error(error)
                return
            
            self.text_output.delete('1.0', tk.END)
            self.text_output.insert('1.0', output)
        except Exception as e:
            validators.show_error(f"Error al generar esquema: {e}")
