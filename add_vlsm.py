import re

# Leer el archivo original
with open('ip_calc.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Función VLSM a añadir
vlsm_function = '''
def calculate_vlsm():
    try:
        base_ip = entry_vlsm_ip.get().strip()
        if '/' not in base_ip:
            messagebox.showerror("Error", "Formato inválido. Usa IP/CIDR (ej: 192.168.1.0/24)")
            return
        
        base_network = ipaddress.IPv4Network(base_ip, strict=False)
        hosts_input = entry_vlsm_hosts.get().strip()
        hosts_list = [int(x.strip()) for x in hosts_input.split(',') if x.strip()]
        
        if not hosts_list:
            messagebox.showerror("Error", "Ingresa al menos un número de hosts")
            return
        
        if any(h < 1 for h in hosts_list):
            messagebox.showerror("Error", "Todos los valores deben ser mayores a 0")
            return
            
    except ValueError as e:
        messagebox.showerror("Error", f"Valores inválidos: {e}")
        return
    
    vlsm_text.delete('1.0', tk.END)
    
    # Ordenar de mayor a menor
    hosts_sorted = sorted(hosts_list, reverse=True)
    
    output = "=" * 90 + "\\n"
    output += "CALCULO DE VLSM (Variable Length Subnet Mask)\\n"
    output += "=" * 90 + "\\n\\n"
    
    output += f"RED BASE: {base_network}\\n"
    output += f"NUMERO DE SUBREDES: {len(hosts_list)}\\n"
    output += f"HOSTS SOLICITADOS: {', '.join(map(str, hosts_list))}\\n"
    output += f"HOSTS ORDENADOS (mayor a menor): {', '.join(map(str, hosts_sorted))}\\n\\n"
    
    output += "METODOLOGIA VLSM:\\n"
    output += "-" * 90 + "\\n"
    output += "1. Ordenar subredes de MAYOR a MENOR número de hosts\\n"
    output += "2. Para cada subred calcular:\\n"
    output += "   - Bits de host necesarios: menor n donde 2^n - 2 >= H\\n"
    output += "   - Prefijo: 32 - n\\n"
    output += "   - Tamaño de bloque: 2^n\\n"
    output += "   - Asignar rangos secuencialmente\\n\\n"
    
    current_base = base_network.network_address
    base_broadcast = base_network.broadcast_address
    
    for idx, num_hosts in enumerate(hosts_sorted, 1):
        output += "=" * 90 + "\\n"
        output += f"SUBRED {idx}: {num_hosts} hosts necesarios\\n"
        output += "=" * 90 + "\\n\\n"
        
        # Calcular bits necesarios
        needed_addresses = num_hosts + 2  # +2 por network y broadcast
        n = math.ceil(math.log2(needed_addresses))
        prefix = 32 - n
        block_size = 2 ** n
        
        output += "PASO 1: CALCULAR BITS DE HOST\\n"
        output += "-" * 90 + "\\n"
        output += f"Hosts necesarios: {num_hosts}\\n"
        output += f"Direcciones totales necesarias: {num_hosts} + 2 (network + broadcast) = {needed_addresses}\\n"
        output += f"Bits de host (n): menor n donde 2^n >= {needed_addresses}\\n"
        output += f"  2^{n} = {2**n} >= {needed_addresses} ✓\\n"
        output += f"Bits de host: {n}\\n\\n"
        
        output += "PASO 2: CALCULAR PREFIJO Y MASCARA\\n"
        output += "-" * 90 + "\\n"
        output += f"Prefijo: 32 - {n} = /{prefix}\\n"
        
        # Calcular máscara
        mask_int = (0xFFFFFFFF << n) & 0xFFFFFFFF
        mask_octets = [(mask_int >> 24) & 0xFF, (mask_int >> 16) & 0xFF,
                       (mask_int >> 8) & 0xFF, mask_int & 0xFF]
        mask_str = '.'.join(map(str, mask_octets))
        output += f"Máscara de subred: {mask_str}\\n"
        output += f"Tamaño de bloque: 2^{n} = {block_size} direcciones\\n\\n"
        
        # Verificar si cabe en la red base
        if int(current_base) + block_size - 1 > int(base_broadcast):
            output += "ERROR: No hay suficiente espacio en la red base para esta subred\\n"
            output += f"Se necesitan {block_size} direcciones pero solo quedan {int(base_broadcast) - int(current_base) + 1}\\n\\n"
            break
        
        # Asignar rangos
        network = current_base
        first_host = ipaddress.IPv4Address(int(network) + 1)
        broadcast = ipaddress.IPv4Address(int(network) + block_size - 1)
        last_host = ipaddress.IPv4Address(int(broadcast) - 1)
        next_base = ipaddress.IPv4Address(int(network) + block_size)
        
        output += "PASO 3: ASIGNACION DE RANGOS\\n"
        output += "-" * 90 + "\\n"
        output += f"Dirección de red:     {network}/{prefix}\\n"
        output += f"Primera IP usable:    {first_host}\\n"
        output += f"Última IP usable:     {last_host}\\n"
        output += f"Dirección broadcast:  {broadcast}\\n"
        output += f"Siguiente red base:   {next_base}\\n\\n"
        
        output += "CALCULO DETALLADO:\\n"
        output += "-" * 90 + "\\n"
        output += f"network        = {network} (base actual)\\n"
        output += f"first_host     = network + 1 = {network} + 1 = {first_host}\\n"
        output += f"last_host      = network + block_size - 2 = {network} + {block_size} - 2 = {last_host}\\n"
        output += f"broadcast      = network + block_size - 1 = {network} + {block_size} - 1 = {broadcast}\\n"
        output += f"next_base      = network + block_size = {network} + {block_size} = {next_base}\\n\\n"
        
        output += "RESUMEN:\\n"
        output += "-" * 90 + "\\n"
        output += f"Hosts disponibles:    {block_size - 2}\\n"
        output += f"Hosts solicitados:    {num_hosts}\\n"
        output += f"Hosts desperdiciados: {block_size - 2 - num_hosts}\\n"
        output += f"Eficiencia:           {(num_hosts / (block_size - 2) * 100):.2f}%\\n\\n"
        
        current_base = next_base
    
    # Resumen final
    output += "\\n" + "=" * 90 + "\\n"
    output += "RESUMEN FINAL DE SUBREDES\\n"
    output += "=" * 90 + "\\n\\n"
    
    current_base = base_network.network_address
    for idx, num_hosts in enumerate(hosts_sorted, 1):
        needed_addresses = num_hosts + 2
        n = math.ceil(math.log2(needed_addresses))
        prefix = 32 - n
        block_size = 2 ** n
        
        if int(current_base) + block_size - 1 > int(base_broadcast):
            break
            
        network = current_base
        broadcast = ipaddress.IPv4Address(int(network) + block_size - 1)
        
        output += f"Subred {idx}: {network}/{prefix} - {broadcast} ({num_hosts} hosts)\\n"
        current_base = ipaddress.IPv4Address(int(network) + block_size)
    
    vlsm_text.insert('1.0', output)
'''

# Tab VLSM a añadir
vlsm_tab = '''
# TAB 4 - VLSM
tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="VLSM por Hosts")

vlsm_main = tk.Frame(tab4, padx=20, pady=20)
vlsm_main.pack(fill=tk.BOTH, expand=True)

tk.Label(vlsm_main, text="CALCULADORA VLSM POR NUMERO DE HOSTS", 
         font=('Arial', 16, 'bold'), fg='#9C27B0').pack(pady=10)
tk.Label(vlsm_main, text="Calcula subredes de tamaño variable optimizadas", 
         font=('Arial', 10, 'italic')).pack(pady=5)

ttk.Separator(vlsm_main, orient='horizontal').pack(fill=tk.X, pady=15)

input_vlsm_frame = tk.LabelFrame(vlsm_main, text="Parametros de Red", font=('Arial', 11, 'bold'), padx=15, pady=15)
input_vlsm_frame.pack(fill=tk.X, pady=10)

tk.Label(input_vlsm_frame, text="Direccion IP base (ej: 192.168.1.0/24):", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
entry_vlsm_ip = tk.Entry(input_vlsm_frame, width=30, font=('Arial', 10))
entry_vlsm_ip.grid(row=0, column=1, pady=5, padx=10)
entry_vlsm_ip.insert(0, "192.168.1.0/24")

tk.Label(input_vlsm_frame, text="Hosts por subred (separados por coma):", font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
entry_vlsm_hosts = tk.Entry(input_vlsm_frame, width=30, font=('Arial', 10))
entry_vlsm_hosts.grid(row=1, column=1, pady=5, padx=10)
entry_vlsm_hosts.insert(0, "50,30,20,10")

tk.Button(input_vlsm_frame, text="Calcular VLSM", command=calculate_vlsm,
          bg='#9C27B0', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=10).grid(row=2, column=0, columnspan=2, pady=15)

result_vlsm_frame = tk.Frame(vlsm_main, padx=10, pady=10)
result_vlsm_frame.pack(fill=tk.BOTH, expand=True)

vlsm_scrollbar = tk.Scrollbar(result_vlsm_frame)
vlsm_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

vlsm_text = tk.Text(result_vlsm_frame, height=30, wrap=tk.WORD, font=('Courier New', 9), yscrollcommand=vlsm_scrollbar.set)
vlsm_text.pack(fill=tk.BOTH, expand=True)
vlsm_scrollbar.config(command=vlsm_text.yview)

vlsm_instructions = \"\"\"BIENVENIDO A LA CALCULADORA VLSM

Este calculador crea subredes de tamaño variable optimizadas para tus necesidades.

INSTRUCCIONES:
1. Ingresa la dirección IP base con máscara CIDR (ej: 192.168.1.0/24)
2. Ingresa el número de hosts necesarios para cada subred separados por comas
   Ejemplo: 50,30,20,10 creará 4 subredes con esas capacidades

METODOLOGIA VLSM:
- Las subredes se ordenan de MAYOR a MENOR número de hosts
- Para cada subred se calcula:
  * Bits de host necesarios: menor n donde 2^n - 2 >= H
  * Prefijo: 32 - n
  * Tamaño de bloque: 2^n
  * Asignación secuencial de rangos

EJEMPLO:
- IP base: 192.168.1.0/24
- Hosts: 50,30,20,10

El sistema generará:
✓ Cálculo detallado paso a paso para cada subred
✓ Máscaras de subred variables optimizadas
✓ Rangos de IPs asignados secuencialmente
✓ Eficiencia de uso de direcciones

Presiona "Calcular VLSM" para comenzar!
\"\"\"
vlsm_text.insert('1.0', vlsm_instructions)

'''

# Insertar la función antes de # GUI
content = content.replace('# GUI', vlsm_function + '\n# GUI')

# Insertar el tab antes de root.mainloop()
content = content.replace('root.mainloop()', vlsm_tab + '\nroot.mainloop()')

# Guardar el archivo modificado
with open('ip_calc.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Función calculate_vlsm añadida")
print("✓ Pestaña VLSM añadida")
print("✓ Archivo ip_calc.py actualizado correctamente")
