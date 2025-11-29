import ipaddress
import tkinter as tk
from tkinter import ttk, messagebox
import math
import random

def calculate_detailed():
    ip_input = entry_detailed_ip.get().strip()
    try:
        if '/' not in ip_input:
            messagebox.showerror("Error", "Formato inválido. Usa IP/CIDR (ej: 192.168.0.11/24)")
            return
        ip_part, cidr_part = ip_input.split('/')
        cidr = int(cidr_part)
        if cidr < 0 or cidr > 32:
            raise ValueError("CIDR debe estar entre 0 y 32")
        ip_obj = ipaddress.IPv4Address(ip_part)
        network = ipaddress.IPv4Network(ip_input, strict=False)
    except ValueError as e:
        messagebox.showerror("Error", f"IP o máscara inválida: {e}")
        return
    
    detailed_text.delete('1.0', tk.END)
    ip_octets = [int(x) for x in ip_part.split('.')]
    mask_int = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    mask_octets = [(mask_int >> 24) & 0xFF, (mask_int >> 16) & 0xFF, (mask_int >> 8) & 0xFF, mask_int & 0xFF]
    mask_str = '.'.join(map(str, mask_octets))
    network_int = int(ip_obj) & mask_int
    network_octets = [(network_int >> 24) & 0xFF, (network_int >> 16) & 0xFF, (network_int >> 8) & 0xFF, network_int & 0xFF]
    network_addr = '.'.join(map(str, network_octets))
    wildcard_int = 0xFFFFFFFF ^ mask_int
    broadcast_int = network_int | wildcard_int
    broadcast_octets = [(broadcast_int >> 24) & 0xFF, (broadcast_int >> 16) & 0xFF, (broadcast_int >> 8) & 0xFF, broadcast_int & 0xFF]
    broadcast_addr = '.'.join(map(str, broadcast_octets))
    determining_octet = next((i for i in range(3, -1, -1) if mask_octets[i] != 255), -1)
    
    output = "=" * 80 + "\nCALCULO DETALLADO DE RED\n" + "=" * 80 + "\n\n"
    output += f"IP: {ip_part}/{cidr}\n\n"
    output += "PASO 1: MASCARA DE RED\n" + "-" * 40 + "\n"
    output += f"/{cidr} = {cidr} bits en 1\n"
    mask_binary = '.'.join([format(mask_int >> (24-i*8) & 0xFF, '08b') for i in range(4)])
    output += f"Binario: {mask_binary}\n"
    output += f"Decimal: {mask_str}\n\n"
    
    output += "PASO 2: DIRECCION DE RED\n" + "-" * 40 + "\n"
    output += "AND entre IP y Mascara\n"
    output += f"Resultado: {network_addr}/{cidr}\n\n"
    
    output += "PASO 3: SALTO DE BLOQUE\n" + "-" * 40 + "\n"
    if determining_octet >= 0:
        output += f"256 - {mask_octets[determining_octet]} = {256 - mask_octets[determining_octet]}\n\n"
    
    output += "PASO 4: BROADCAST\n" + "-" * 40 + "\n"
    wildcard_octets = [255 - m for m in mask_octets]
    output += f"Wildcard: {'.'.join(map(str, wildcard_octets))}\n"
    output += f"Broadcast: {broadcast_addr}\n\n"
    
    output += "RESUMEN\n" + "=" * 80 + "\n"
    output += f"Red: {network_addr}/{cidr}\n"
    output += f"Mascara: {mask_str}\n"
    output += f"Broadcast: {broadcast_addr}\n"
    output += f"Hosts: {2**(32-cidr) - 2}\n"
    detailed_text.insert('1.0', output)

def calculate_detailed_subnets():
    ip_input = entry_detailed_ip.get().strip()
    try:
        if '/' not in ip_input:
            messagebox.showerror("Error", "Primero ingresa una IP con mascara")
            return
        network = ipaddress.IPv4Network(ip_input, strict=False)
        num_subnets = int(entry_detailed_subnets.get())
        if num_subnets < 1:
            raise ValueError("Debe ser mayor a 0")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
    
    detailed_text.delete('1.0', tk.END)
    bits_needed = math.ceil(math.log2(num_subnets))
    new_prefix = network.prefixlen + bits_needed
    
    if new_prefix > 32:
        detailed_text.insert('1.0', f"ERROR: /{new_prefix} excede /32")
        return
    
    output = "CALCULO DE SUBREDES\n" + "=" * 80 + "\n\n"
    output += f"Red base: {network}\nSubredes: {num_subnets}\n\n"
    output += f"Bits necesarios: {bits_needed} (2^{bits_needed} = {2**bits_needed})\n"
    output += f"Nueva mascara: /{new_prefix}\n"
    output += f"Hosts/subred: {2**(32 - new_prefix) - 2}\n\n"
    
    subnets = list(network.subnets(new_prefix=new_prefix))
    for i, subnet in enumerate(subnets[:num_subnets], 1):
        output += f"{i}. {subnet.network_address}/{new_prefix} - {subnet.broadcast_address}\n"
    detailed_text.insert('1.0', output)

def calculate_detailed_devices():
    ip_input = entry_detailed_ip.get().strip()
    try:
        if '/' not in ip_input:
            messagebox.showerror("Error", "Primero ingresa una IP")
            return
        base_network = ipaddress.IPv4Network(ip_input, strict=False)
        devices_list = [int(x.strip()) for x in entry_detailed_devices.get().split(',') if x.strip()]
        if not devices_list or any(d < 1 for d in devices_list):
            raise ValueError("Numeros invalidos")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
    
    detailed_text.delete('1.0', tk.END)
    devices_list_sorted = sorted(devices_list, reverse=True)
    output = "SUBREDES POR DISPOSITIVOS\n" + "=" * 80 + "\n\n"
    next_addr = base_network.network_address
    
    for idx, num_dev in enumerate(devices_list_sorted, 1):
        needed = num_dev + 2
        bits = math.ceil(math.log2(needed))
        prefix = 32 - bits
        
        if prefix < base_network.prefixlen:
            output += f"{idx}. {num_dev} dispositivos: ERROR (muy grande)\n"
            continue
        
        try:
            subnet = ipaddress.IPv4Network(f"{next_addr}/{prefix}", strict=True)
            if subnet.subnet_of(base_network):
                output += f"{idx}. {num_dev} disp: {subnet.network_address}/{prefix} - {subnet.broadcast_address}\n"
                output += f"    Hosts: {subnet.num_addresses - 2} (desperdiciados: {subnet.num_addresses - 2 - num_dev})\n"
                next_addr = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)
            else:
                output += f"{idx}. ERROR: Excede red base\n"
        except:
            output += f"{idx}. ERROR\n"
    
    detailed_text.insert('1.0', output)

practice_state = {'mode': None, 'ip': None, 'cidr': None, 'network': None, 'num_subnets': None}

def start_basic_practice():
    practice_state['mode'] = 'basic'
    octets = [random.randint(1, 254) for _ in range(4)]
    ip = '.'.join(map(str, octets))
    cidr = random.choice([8, 16, 24, 25, 26, 27, 28, 29, 30])
    practice_state['ip'] = ip
    practice_state['cidr'] = cidr
    practice_state['network'] = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)
    
    for entry in [practice_mask_entry, practice_network_entry, practice_broadcast_entry, 
                  practice_block_entry, practice_first_host_entry, practice_last_host_entry]:
        entry.delete(0, tk.END)
        entry.config(bg='white')
    
    practice_feedback.delete('1.0', tk.END)
    output = f"EJERCICIO BASICO\n{'=' * 80}\n\nIP: {ip}/{cidr}\n\n"
    output += "CALCULA:\n1. Mascara de red\n2. Direccion de red\n3. Broadcast\n"
    output += "4. Salto de bloque\n5. Primer host\n6. Ultimo host\n\n"
    
    output += "GUIA DE CALCULO RAPIDO\n" + "=" * 80 + "\n\n"
    output += "1. MASCARA DE RED:\n"
    output += f"   /{cidr} = {cidr} bits en 1\n"
    output += f"   {cidr} / 8 = {cidr // 8} octetos completos en 255\n"
    if cidr % 8 != 0:
        remaining = cidr % 8
        values = [128, 192, 224, 240, 248, 252, 254, 255]
        output += f"   Quedan {remaining} bits -> Octeto {cidr // 8 + 1} = {values[remaining - 1]}\n"
    output += "   Resto de octetos = 0\n\n"
    
    output += "2. DIRECCION DE RED:\n"
    output += "   Haz AND entre IP y Mascara (bit a bit)\n"
    output += "   TRUCO: Octetos con mascara 255 quedan igual\n"
    output += "          Octetos con mascara 0 se vuelven 0\n\n"
    
    output += "3. BROADCAST:\n"
    output += "   Wildcard = 255.255.255.255 - Mascara\n"
    output += "   Broadcast = Red + Wildcard\n"
    output += "   TRUCO: Donde mascara es 0, broadcast es 255\n\n"
    
    output += "4. SALTO DE BLOQUE:\n"
    output += "   Busca ultimo octeto de mascara que NO sea 255\n"
    output += "   Salto = 256 - ese octeto\n\n"
    
    output += "5-6. HOSTS:\n"
    output += "   Primer host = Red + 1\n"
    output += "   Ultimo host = Broadcast - 1\n\n"
    
    output += "TABLA DE REFERENCIA:\n"
    output += "/8  -> 255.0.0.0       | /24 -> 255.255.255.0\n"
    output += "/16 -> 255.255.0.0     | /25 -> 255.255.255.128\n"
    output += "/26 -> 255.255.255.192 | /27 -> 255.255.255.224\n"
    output += "/28 -> 255.255.255.240 | /29 -> 255.255.255.248\n"
    output += "/30 -> 255.255.255.252\n\n"
    output += "Completa los campos y presiona 'Verificar'!\n"
    practice_feedback.insert('1.0', output)

def start_subnet_practice():
    practice_state['mode'] = 'subnets'
    base_cidr = random.choice([16, 24])
    ip = f"172.{random.randint(16, 31)}.0.0" if base_cidr == 16 else f"192.168.{random.randint(1, 254)}.0"
    num_subnets = random.choice([2, 4, 8, 16])
    practice_state['ip'] = ip
    practice_state['cidr'] = base_cidr
    practice_state['num_subnets'] = num_subnets
    practice_state['network'] = ipaddress.IPv4Network(f"{ip}/{base_cidr}", strict=False)
    
    for entry in [practice_subnet_bits_entry, practice_subnet_newmask_entry, practice_subnet_hosts_entry]:
        entry.delete(0, tk.END)
        entry.config(bg='white')
    
    practice_feedback.delete('1.0', tk.END)
    output = f"EJERCICIO DE SUBREDES\n{'=' * 80}\n\n"
    output += f"Red base: {ip}/{base_cidr}\nSubredes a crear: {num_subnets}\n\n"
    output += "CALCULA:\n1. Bits necesarios\n2. Nueva mascara (/XX)\n3. Hosts por subred\n\n"
    
    output += "GUIA DE CALCULO:\n" + "=" * 80 + "\n\n"
    output += "1. BITS NECESARIOS:\n"
    output += f"   Formula: 2^n >= {num_subnets}\n"
    output += "   Prueba: 2^1=2, 2^2=4, 2^3=8, 2^4=16...\n"
    output += "   Usa el primer valor que sea >= al numero de subredes\n\n"
    
    output += "2. NUEVA MASCARA:\n"
    output += f"   Nueva mascara = /{base_cidr} + bits necesarios\n"
    output += "   Ejemplo: Si necesitas 3 bits, nueva mascara = /{base_cidr + 3}\n\n"
    
    output += "3. HOSTS POR SUBRED:\n"
    output += "   Formula: 2^(32 - nueva_mascara) - 2\n"
    output += "   El -2 es por red y broadcast\n\n"
    output += "Completa y presiona 'Verificar'!\n"
    practice_feedback.insert('1.0', output)

def verify_basic_answers():
    if practice_state['mode'] != 'basic':
        messagebox.showwarning("Aviso", "Primero inicia un ejercicio basico")
        return
    
    network = practice_state['network']
    mask_octets = [int(x) for x in str(network.netmask).split('.')]
    determining_octet = next((i for i in range(3, -1, -1) if mask_octets[i] != 255), -1)
    
    correct = {
        'mask': str(network.netmask),
        'network': str(network.network_address),
        'broadcast': str(network.broadcast_address),
        'block': str(256 - mask_octets[determining_octet] if determining_octet >= 0 else 256),
        'first_host': str(network.network_address + 1),
        'last_host': str(network.broadcast_address - 1)
    }
    
    user = {
        'mask': practice_mask_entry.get().strip(),
        'network': practice_network_entry.get().strip(),
        'broadcast': practice_broadcast_entry.get().strip(),
        'block': practice_block_entry.get().strip(),
        'first_host': practice_first_host_entry.get().strip(),
        'last_host': practice_last_host_entry.get().strip()
    }
    
    entries = [practice_mask_entry, practice_network_entry, practice_broadcast_entry,
               practice_block_entry, practice_first_host_entry, practice_last_host_entry]
    keys = ['mask', 'network', 'broadcast', 'block', 'first_host', 'last_host']
    labels = ['Mascara', 'Red', 'Broadcast', 'Salto', 'Primer host', 'Ultimo host']
    
    results = []
    all_correct = True
    
    for entry, key, label in zip(entries, keys, labels):
        if user[key] == correct[key]:
            entry.config(bg='lightgreen')
            results.append(f"✅ {label}: CORRECTO")
        else:
            entry.config(bg='lightcoral')
            results.append(f"❌ {label}: Tu respuesta: {user[key]}, Correcta: {correct[key]}")
            all_correct = False
    
    practice_feedback.delete('1.0', tk.END)
    output = "RESULTADOS\n" + "=" * 80 + "\n\n"
    output += "\n".join(results) + "\n\n"
    output += "EXCELENTE! Todas correctas.\n" if all_correct else "Revisa las respuestas en rojo.\n"
    practice_feedback.insert('1.0', output)

def verify_subnet_answers():
    if practice_state['mode'] != 'subnets':
        messagebox.showwarning("Aviso", "Primero inicia un ejercicio de subredes")
        return
    
    num_subnets = practice_state['num_subnets']
    base_cidr = practice_state['cidr']
    
    correct_bits = str(math.ceil(math.log2(num_subnets)))
    correct_newmask = f"/{base_cidr + int(correct_bits)}"
    correct_hosts = str(2**(32 - (base_cidr + int(correct_bits))) - 2)
    
    user_bits = practice_subnet_bits_entry.get().strip()
    user_newmask = practice_subnet_newmask_entry.get().strip()
    user_hosts = practice_subnet_hosts_entry.get().strip()
    
    results = []
    all_correct = True
    
    if user_bits == correct_bits:
        practice_subnet_bits_entry.config(bg='lightgreen')
        results.append("✅ Bits: CORRECTO")
    else:
        practice_subnet_bits_entry.config(bg='lightcoral')
        results.append(f"❌ Bits: {user_bits} -> Correcta: {correct_bits}")
        all_correct = False
    
    if user_newmask == correct_newmask:
        practice_subnet_newmask_entry.config(bg='lightgreen')
        results.append("✅ Mascara: CORRECTO")
    else:
        practice_subnet_newmask_entry.config(bg='lightcoral')
        results.append(f"❌ Mascara: {user_newmask} -> Correcta: {correct_newmask}")
        all_correct = False
    
    if user_hosts == correct_hosts:
        practice_subnet_hosts_entry.config(bg='lightgreen')
        results.append("✅ Hosts: CORRECTO")
    else:
        practice_subnet_hosts_entry.config(bg='lightcoral')
        results.append(f"❌ Hosts: {user_hosts} -> Correcta: {correct_hosts}")
        all_correct = False
    
    practice_feedback.delete('1.0', tk.END)
    output = "RESULTADOS\n" + "=" * 80 + "\n\n"
    output += "\n".join(results) + "\n\n"
    output += "EXCELENTE! Todas correctas.\n" if all_correct else "Revisa las respuestas en rojo.\n"
    practice_feedback.insert('1.0', output)

# GUI
root = tk.Tk()
root.title("Calculadora de Red IP")
root.geometry("1000x900")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# TAB 1
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Calculo Detallado Paso a Paso")

frame_detailed_input = tk.Frame(tab1, pady=10)
frame_detailed_input.pack(fill=tk.X, padx=20)

tk.Label(frame_detailed_input, text="IP con mascara (ej: 192.168.0.11/24):", font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
entry_detailed_ip = tk.Entry(frame_detailed_input, width=40, font=('Arial', 12))
entry_detailed_ip.pack(pady=5, fill=tk.X)

tk.Button(frame_detailed_input, text="Calcular Detallado", command=calculate_detailed, 
          bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=5).pack(pady=10)

ttk.Separator(tab1, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)

frame_detailed_subnets = tk.LabelFrame(tab1, text="Calculo de Subredes", padx=10, pady=10)
frame_detailed_subnets.pack(fill=tk.X, padx=20, pady=10)

tk.Label(frame_detailed_subnets, text="Numero de subredes:").pack(side=tk.LEFT, padx=5)
entry_detailed_subnets = tk.Entry(frame_detailed_subnets, width=10)
entry_detailed_subnets.pack(side=tk.LEFT, padx=5)
tk.Button(frame_detailed_subnets, text="Calcular Subredes", command=calculate_detailed_subnets,
          bg='#2196F3', fg='white', font=('Arial', 9, 'bold'), padx=15, pady=3).pack(side=tk.LEFT, padx=10)

ttk.Separator(tab1, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)

frame_detailed_devices = tk.LabelFrame(tab1, text="Subredes por Dispositivos", padx=10, pady=10)
frame_detailed_devices.pack(fill=tk.X, padx=20, pady=10)

tk.Label(frame_detailed_devices, text="Dispositivos (separados por coma):").pack(side=tk.LEFT, padx=5)
entry_detailed_devices = tk.Entry(frame_detailed_devices, width=25)
entry_detailed_devices.pack(side=tk.LEFT, padx=5)
tk.Button(frame_detailed_devices, text="Calcular por Dispositivos", command=calculate_detailed_devices,
          bg='#FF9800', fg='white', font=('Arial', 9, 'bold'), padx=15, pady=3).pack(side=tk.LEFT, padx=10)

frame_detailed_results = tk.Frame(tab1, padx=10, pady=10)
frame_detailed_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

scrollbar_detailed = tk.Scrollbar(frame_detailed_results)
scrollbar_detailed.pack(side=tk.RIGHT, fill=tk.Y)

detailed_text = tk.Text(frame_detailed_results, height=30, wrap=tk.WORD, font=('Courier New', 9), yscrollcommand=scrollbar_detailed.set)
detailed_text.pack(fill=tk.BOTH, expand=True)
scrollbar_detailed.config(command=detailed_text.yview)

instructions = """CALCULADORA DE RED - MODO DETALLADO

Ingresa una IP/CIDR (ej: 192.168.0.11/24) y presiona los botones para ver:
  - Calculo detallado de mascara, red, broadcast y salto de bloque
  - Division en subredes con explicacion paso a paso
  - Subredes optimizadas por numero de dispositivos
"""
detailed_text.insert('1.0', instructions)

# TAB 2
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Practica Manual Guiada")

practice_main = tk.Frame(tab2, padx=20, pady=20)
practice_main.pack(fill=tk.BOTH, expand=True)

tk.Label(practice_main, text="PRACTICA MANUAL GUIADA", font=('Arial', 16, 'bold'), fg='#2196F3').pack(pady=10)
tk.Label(practice_main, text="Aprende calculando con retroalimentacion inmediata", font=('Arial', 10, 'italic')).pack(pady=5)

ttk.Separator(practice_main, orient='horizontal').pack(fill=tk.X, pady=15)

button_frame = tk.Frame(practice_main)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Nuevo Ejercicio Basico", command=start_basic_practice,
          bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=10).pack(side=tk.LEFT, padx=10)
tk.Button(button_frame, text="Nuevo Ejercicio de Subredes", command=start_subnet_practice,
          bg='#2196F3', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=10).pack(side=tk.LEFT, padx=10)

practice_area = tk.Frame(practice_main)
practice_area.pack(fill=tk.BOTH, expand=True, pady=10)

input_frame = tk.LabelFrame(practice_area, text="Tus Respuestas", font=('Arial', 11, 'bold'), padx=15, pady=15)
input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

basic_frame = tk.LabelFrame(input_frame, text="Ejercicio Basico", padx=10, pady=10)
basic_frame.pack(fill=tk.X, pady=5)

tk.Label(basic_frame, text="Mascara:").grid(row=0, column=0, sticky='w', pady=3)
practice_mask_entry = tk.Entry(basic_frame, width=20)
practice_mask_entry.grid(row=0, column=1, pady=3, padx=5)

tk.Label(basic_frame, text="Red:").grid(row=1, column=0, sticky='w', pady=3)
practice_network_entry = tk.Entry(basic_frame, width=20)
practice_network_entry.grid(row=1, column=1, pady=3, padx=5)

tk.Label(basic_frame, text="Broadcast:").grid(row=2, column=0, sticky='w', pady=3)
practice_broadcast_entry = tk.Entry(basic_frame, width=20)
practice_broadcast_entry.grid(row=2, column=1, pady=3, padx=5)

tk.Label(basic_frame, text="Salto:").grid(row=3, column=0, sticky='w', pady=3)
practice_block_entry = tk.Entry(basic_frame, width=20)
practice_block_entry.grid(row=3, column=1, pady=3, padx=5)

tk.Label(basic_frame, text="Primer host:").grid(row=4, column=0, sticky='w', pady=3)
practice_first_host_entry = tk.Entry(basic_frame, width=20)
practice_first_host_entry.grid(row=4, column=1, pady=3, padx=5)

tk.Label(basic_frame, text="Ultimo host:").grid(row=5, column=0, sticky='w', pady=3)
practice_last_host_entry = tk.Entry(basic_frame, width=20)
practice_last_host_entry.grid(row=5, column=1, pady=3, padx=5)

tk.Button(basic_frame, text="Verificar Respuestas", command=verify_basic_answers,
          bg='#FF9800', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).grid(row=6, column=0, columnspan=2, pady=10)

subnet_frame = tk.LabelFrame(input_frame, text="Ejercicio de Subredes", padx=10, pady=10)
subnet_frame.pack(fill=tk.X, pady=5)

tk.Label(subnet_frame, text="Bits:").grid(row=0, column=0, sticky='w', pady=3)
practice_subnet_bits_entry = tk.Entry(subnet_frame, width=20)
practice_subnet_bits_entry.grid(row=0, column=1, pady=3, padx=5)

tk.Label(subnet_frame, text="Nueva mascara:").grid(row=1, column=0, sticky='w', pady=3)
practice_subnet_newmask_entry = tk.Entry(subnet_frame, width=20)
practice_subnet_newmask_entry.grid(row=1, column=1, pady=3, padx=5)

tk.Label(subnet_frame, text="Hosts/subred:").grid(row=2, column=0, sticky='w', pady=3)
practice_subnet_hosts_entry = tk.Entry(subnet_frame, width=20)
practice_subnet_hosts_entry.grid(row=2, column=1, pady=3, padx=5)

tk.Button(subnet_frame, text="Verificar Subredes", command=verify_subnet_answers,
          bg='#FF9800', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5).grid(row=3, column=0, columnspan=2, pady=10)

feedback_frame = tk.LabelFrame(practice_area, text="Instrucciones y Retroalimentacion", font=('Arial', 11, 'bold'), padx=10, pady=10)
feedback_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

practice_scrollbar = tk.Scrollbar(feedback_frame)
practice_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

practice_feedback = tk.Text(feedback_frame, height=25, wrap=tk.WORD, font=('Courier New', 9), yscrollcommand=practice_scrollbar.set)
practice_feedback.pack(fill=tk.BOTH, expand=True)
practice_scrollbar.config(command=practice_feedback.yview)

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
practice_feedback.insert('1.0', initial_msg)

root.mainloop()