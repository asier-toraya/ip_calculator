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
    output += f"Red base: {base_network}\n"
    output += f"Dispositivos solicitados: {', '.join(map(str, devices_list))}\n"
    output += f"Ordenados (mayor a menor): {', '.join(map(str, devices_list_sorted))}\n\n"
    
    next_addr = base_network.network_address
    
    for idx, num_dev in enumerate(devices_list_sorted, 1):
        needed = num_dev + 2
        bits = math.ceil(math.log2(needed))
        prefix = 32 - bits
        
        output += f"SUBRED {idx}: {num_dev} dispositivos\n"
        output += "-" * 80 + "\n"
        
        if prefix < base_network.prefixlen:
            output += f"ERROR: Subred muy grande para la red base\n\n"
            continue
        
        try:
            subnet = ipaddress.IPv4Network(f"{next_addr}/{prefix}", strict=True)
            if subnet.subnet_of(base_network):
                mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
                mask_octets = [(mask_int >> 24) & 0xFF, (mask_int >> 16) & 0xFF, 
                               (mask_int >> 8) & 0xFF, mask_int & 0xFF]
                mask_str = '.'.join(map(str, mask_octets))
                
                first_host = subnet.network_address + 1
                last_host = subnet.broadcast_address - 1
                
                output += f"Direccion de red:     {subnet.network_address}/{prefix}\n"
                output += f"Mascara de red:       {mask_str}\n"
                output += f"Broadcast:            {subnet.broadcast_address}\n"
                output += f"Hosts disponibles:    {subnet.num_addresses - 2}\n"
                output += f"Primera IP host:      {first_host}\n"
                output += f"Ultima IP host:       {last_host}\n"
                output += f"Hosts desperdiciados: {subnet.num_addresses - 2 - num_dev}\n"
                output += f"Calculo: 2^{bits} - 2 = {2**bits} - 2 = {2**bits - 2} hosts\n\n"
                
                next_addr = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)
            else:
                output += f"ERROR: Excede la red base\n\n"
        except Exception as e:
            output += f"ERROR: {str(e)}\n\n"
    
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
    output += "/30 -> 255.255.255.252\n"
    
    practice_feedback.insert('1.0', output)

def start_subnet_practice():
    practice_state['mode'] = 'subnets'
    octets = [random.randint(1, 254) for _ in range(4)]
    ip = '.'.join(map(str, octets))
    cidr = random.choice([16, 20, 24])
    num_subnets = random.randint(2, 8)
    
    practice_state['ip'] = ip
    practice_state['cidr'] = cidr
    practice_state['num_subnets'] = num_subnets
    
    for entry in [practice_subnet_bits_entry, practice_subnet_newmask_entry, practice_subnet_hosts_entry]:
        entry.delete(0, tk.END)
        entry.config(bg='white')
    
    practice_feedback.delete('1.0', tk.END)
    output = f"EJERCICIO DE SUBREDES\n{'=' * 80}\n\n"
    output += f"Red base: {ip}/{cidr}\n"
    output += f"Numero de subredes necesarias: {num_subnets}\n\n"
    output += "CALCULA:\n1. Bits necesarios para las subredes\n"
    output += "2. Nueva mascara (formato /XX)\n"
    output += "3. Hosts por subred\n\n"
    output += "GUIA:\n"
    output += "1. Bits = log2(subredes) redondeado arriba\n"
    output += "2. Nueva mascara = mascara base + bits\n"
    output += "3. Hosts = 2^(32 - nueva mascara) - 2\n"
    
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
    new_prefix = base_network.prefixlen + bits_needed
    
    if new_prefix > 30:
        cpt_text.insert('1.0', f"ERROR: /{new_prefix} excede el limite practico (/30)")
        return
    
    subnets = list(base_network.subnets(new_prefix=new_prefix))[:num_subnets]
    
    output = "=" * 90 + "\n"
    output += "ESQUEMA DE RED PARA CISCO PACKET TRACER\n"
    output += "=" * 90 + "\n\n"
    
    output += f"RED BASE: {base_network}\n"
    output += f"SUBREDES TOTALES: {num_subnets}\n"
    output += f"ROUTERS: {num_routers}\n"
    output += f"SWITCHES: {num_switches}\n"
    output += f"NUEVA MASCARA: /{new_prefix}\n\n"
    
    mask_int = (0xFFFFFFFF << (32 - new_prefix)) & 0xFFFFFFFF
    mask_octets = [(mask_int >> 24) & 0xFF, (mask_int >> 16) & 0xFF, 
                   (mask_int >> 8) & 0xFF, mask_int & 0xFF]
    subnet_mask = '.'.join(map(str, mask_octets))
    
    output += "=" * 90 + "\n"
    output += "TOPOLOGIA DE RED\n"
    output += "=" * 90 + "\n\n"
    
    switches_per_subnet = num_switches // num_subnets
    extra_switches = num_switches % num_subnets
    
    device_counter = 1
    switch_counter = 1
    
    for subnet_idx, (subnet, num_devices) in enumerate(zip(subnets, devices_list), 1):
        output += f"\n{'#' * 90}\n"
        output += f"SUBRED {subnet_idx}\n"
        output += f"{'#' * 90}\n\n"
        
        output += f"INFORMACION DE LA SUBRED:\n"
        output += f"{'-' * 90}\n"
        output += f"  Direccion de red:     {subnet.network_address}/{new_prefix}\n"
        output += f"  Mascara de subred:    {subnet_mask}\n"
        output += f"  Broadcast:            {subnet.broadcast_address}\n"
        output += f"  Gateway (Router):     {subnet.network_address + 1}\n"
        output += f"  Rango de hosts:       {subnet.network_address + 2} - {subnet.broadcast_address - 1}\n"
        output += f"  Hosts disponibles:    {subnet.num_addresses - 2}\n"
        output += f"  Dispositivos:         {num_devices}\n\n"
        
        router_num = ((subnet_idx - 1) % num_routers) + 1
        router_ip = subnet.network_address + 1
        
        output += f"ROUTER {router_num} (Interfaz GigabitEthernet 0/{subnet_idx - 1}):\n"
        output += f"{'-' * 90}\n"
        output += f"  IPv4 Address:         {router_ip}\n"
        output += f"  Subnet Mask:          {subnet_mask}\n"
        output += f"  Tx Ring Limit:        10000\n"
        output += f"  Conectado a:          Switch {switch_counter}\n"
        output += f"  Descripcion:          Gateway para Subred {subnet_idx}\n\n"
        
        num_switches_here = switches_per_subnet + (1 if subnet_idx <= extra_switches else 0)
        switches_in_subnet = []
        
        for sw_idx in range(num_switches_here):
            sw_num = switch_counter + sw_idx
            switches_in_subnet.append(sw_num)
            
            output += f"SWITCH {sw_num} (Switch2960):\n"
            output += f"{'-' * 90}\n"
            output += f"  VLAN 1:               Activa (Default)\n"
            output += f"  VLAN {subnet_idx}0:           Subred {subnet_idx}\n"
            output += f"  Tx Ring Limit:        10000\n"
            
            if sw_idx == 0:
                output += f"  Puerto Fa0/1:         TRUNK - Conectado a Router {router_num} (Gig0/{subnet_idx - 1})\n"
            else:
                output += f"  Puerto Fa0/1:         TRUNK - Conectado a Switch {switch_counter}\n"
            
            devices_per_switch = num_devices // num_switches_here
            if sw_idx < num_devices % num_switches_here:
                devices_per_switch += 1
            
            output += f"  Puertos Fa0/2-24:     ACCESS - VLAN {subnet_idx}0 ({devices_per_switch} dispositivos)\n\n"
        
        output += f"DISPOSITIVOS EN SUBRED {subnet_idx}:\n"
        output += f"{'-' * 90}\n"
        
        current_ip = subnet.network_address + 2
        devices_per_switch = num_devices // len(switches_in_subnet)
        extra_devices = num_devices % len(switches_in_subnet)
        
        for sw_idx, sw_num in enumerate(switches_in_subnet):
            devices_here = devices_per_switch + (1 if sw_idx < extra_devices else 0)
            
            for dev_idx in range(devices_here):
                if current_ip >= subnet.broadcast_address:
                    break
                    
                port_num = (dev_idx % 23) + 2
                
                output += f"  PC{device_counter}:\n"
                output += f"    IPv4 Address:       {current_ip}\n"
                output += f"    Subnet Mask:        {subnet_mask}\n"
                output += f"    Default Gateway:    {router_ip}\n"
                output += f"    Conectado a:        Switch {sw_num} - Puerto Fa0/{port_num}\n"
                output += f"    VLAN:               {subnet_idx}0\n\n"
                
                current_ip = ipaddress.IPv4Address(int(current_ip) + 1)
                device_counter += 1
        
        switch_counter += num_switches_here
    
    if num_routers > 1:
        output += f"\n{'=' * 90}\n"
        output += "INTERCONEXION DE ROUTERS\n"
        output += f"{'=' * 90}\n\n"
        output += "NOTA: Conectar los routers entre si usando interfaces seriales o GigabitEthernet\n"
        output += "      adicionales para permitir enrutamiento entre subredes.\n\n"
        
        for r in range(1, num_routers + 1):
            if r < num_routers:
                output += f"  Router {r} Serial0/0/0 <---> Router {r + 1} Serial0/0/1\n"
    
    output += f"\n{'=' * 90}\n"
    output += "CONFIGURACION ADICIONAL RECOMENDADA\n"
    output += f"{'=' * 90}\n\n"
    output += "1. Configurar enrutamiento estatico o dinamico (RIP, OSPF) entre routers\n"
    output += "2. Configurar VLANs en los switches segun se indica\n"
    output += "3. Verificar conectividad con ping entre dispositivos\n"
    output += "4. Configurar nombres de host en todos los dispositivos\n"
    output += "5. Guardar las configuraciones (write memory)\n\n"
    
    cpt_text.insert('1.0', output)


def generate_cpt_schema():
    messagebox.showinfo("Información", "Esta funcionalidad está en desarrollo.\nPor ahora, usa la pestaña 'Cálculo Detallado' para generar subredes.")


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
    
    output = "=" * 90 + "\n"
    output += "CALCULO DE VLSM (Variable Length Subnet Mask)\n"
    output += "=" * 90 + "\n\n"
    
    output += f"RED BASE: {base_network}\n"
    output += f"NUMERO DE SUBREDES: {len(hosts_list)}\n"
    output += f"HOSTS SOLICITADOS: {', '.join(map(str, hosts_list))}\n"
    output += f"HOSTS ORDENADOS (mayor a menor): {', '.join(map(str, hosts_sorted))}\n\n"
    
    output += "METODOLOGIA VLSM:\n"
    output += "-" * 90 + "\n"
    output += "1. Ordenar subredes de MAYOR a MENOR número de hosts\n"
    output += "2. Para cada subred calcular:\n"
    output += "   - Bits de host necesarios: menor n donde 2^n - 2 >= H\n"
    output += "   - Prefijo: 32 - n\n"
    output += "   - Tamaño de bloque: 2^n\n"
    output += "   - Asignar rangos secuencialmente\n\n"
    
    current_base = base_network.network_address
    base_broadcast = base_network.broadcast_address
    
    for idx, num_hosts in enumerate(hosts_sorted, 1):
        output += "=" * 90 + "\n"
        output += f"SUBRED {idx}: {num_hosts} hosts necesarios\n"
        output += "=" * 90 + "\n\n"
        
        # Calcular bits necesarios
        needed_addresses = num_hosts + 2  # +2 por network y broadcast
        n = math.ceil(math.log2(needed_addresses))
        prefix = 32 - n
        block_size = 2 ** n
        
        output += "PASO 1: CALCULAR BITS DE HOST\n"
        output += "-" * 90 + "\n"
        output += f"Hosts necesarios: {num_hosts}\n"
        output += f"Direcciones totales necesarias: {num_hosts} + 2 (network + broadcast) = {needed_addresses}\n"
        output += f"Bits de host (n): menor n donde 2^n >= {needed_addresses}\n"
        output += f"  2^{n} = {2**n} >= {needed_addresses} ✓\n"
        output += f"Bits de host: {n}\n\n"
        
        output += "PASO 2: CALCULAR PREFIJO Y MASCARA\n"
        output += "-" * 90 + "\n"
        output += f"Prefijo: 32 - {n} = /{prefix}\n"
        
        # Calcular máscara
        mask_int = (0xFFFFFFFF << n) & 0xFFFFFFFF
        mask_octets = [(mask_int >> 24) & 0xFF, (mask_int >> 16) & 0xFF,
                       (mask_int >> 8) & 0xFF, mask_int & 0xFF]
        mask_str = '.'.join(map(str, mask_octets))
        output += f"Máscara de subred: {mask_str}\n"
        output += f"Tamaño de bloque: 2^{n} = {block_size} direcciones\n\n"
        
        # Verificar si cabe en la red base
        if int(current_base) + block_size - 1 > int(base_broadcast):
            output += "ERROR: No hay suficiente espacio en la red base para esta subred\n"
            output += f"Se necesitan {block_size} direcciones pero solo quedan {int(base_broadcast) - int(current_base) + 1}\n\n"
            break
        
        # Asignar rangos
        network = current_base
        first_host = ipaddress.IPv4Address(int(network) + 1)
        broadcast = ipaddress.IPv4Address(int(network) + block_size - 1)
        last_host = ipaddress.IPv4Address(int(broadcast) - 1)
        next_base = ipaddress.IPv4Address(int(network) + block_size)
        
        output += "PASO 3: ASIGNACION DE RANGOS\n"
        output += "-" * 90 + "\n"
        output += f"Dirección de red:     {network}/{prefix}\n"
        output += f"Primera IP usable:    {first_host}\n"
        output += f"Última IP usable:     {last_host}\n"
        output += f"Dirección broadcast:  {broadcast}\n"
        output += f"Siguiente red base:   {next_base}\n\n"
        
        output += "CALCULO DETALLADO:\n"
        output += "-" * 90 + "\n"
        output += f"network        = {network} (base actual)\n"
        output += f"first_host     = network + 1 = {network} + 1 = {first_host}\n"
        output += f"last_host      = network + block_size - 2 = {network} + {block_size} - 2 = {last_host}\n"
        output += f"broadcast      = network + block_size - 1 = {network} + {block_size} - 1 = {broadcast}\n"
        output += f"next_base      = network + block_size = {network} + {block_size} = {next_base}\n\n"
        
        output += "RESUMEN:\n"
        output += "-" * 90 + "\n"
        output += f"Hosts disponibles:    {block_size - 2}\n"
        output += f"Hosts solicitados:    {num_hosts}\n"
        output += f"Hosts desperdiciados: {block_size - 2 - num_hosts}\n"
        output += f"Eficiencia:           {(num_hosts / (block_size - 2) * 100):.2f}%\n\n"
        
        current_base = next_base
    
    # Resumen final
    output += "\n" + "=" * 90 + "\n"
    output += "RESUMEN FINAL DE SUBREDES\n"
    output += "=" * 90 + "\n\n"
    
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
        
        output += f"Subred {idx}: {network}/{prefix} - {broadcast} ({num_hosts} hosts)\n"
        current_base = ipaddress.IPv4Address(int(network) + block_size)
    
    vlsm_text.insert('1.0', output)

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

# TAB 3 - CPT
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="CPT - Cisco Packet Tracer")

cpt_main = tk.Frame(tab3, padx=20, pady=20)
cpt_main.pack(fill=tk.BOTH, expand=True)

tk.Label(cpt_main, text="GENERADOR DE ESQUEMAS PARA CISCO PACKET TRACER", 
         font=('Arial', 16, 'bold'), fg='#FF6600').pack(pady=10)
tk.Label(cpt_main, text="Genera configuraciones detalladas listas para implementar", 
         font=('Arial', 10, 'italic')).pack(pady=5)

ttk.Separator(cpt_main, orient='horizontal').pack(fill=tk.X, pady=15)

input_cpt_frame = tk.LabelFrame(cpt_main, text="Parametros de Red", font=('Arial', 11, 'bold'), padx=15, pady=15)
input_cpt_frame.pack(fill=tk.X, pady=10)

tk.Label(input_cpt_frame, text="Direccion IP base (ej: 192.168.1.0/24):", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
entry_cpt_ip = tk.Entry(input_cpt_frame, width=30, font=('Arial', 10))
entry_cpt_ip.grid(row=0, column=1, pady=5, padx=10)
entry_cpt_ip.insert(0, "192.168.1.0/24")

tk.Label(input_cpt_frame, text="Numero de subredes:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
entry_cpt_subnets = tk.Entry(input_cpt_frame, width=30, font=('Arial', 10))
entry_cpt_subnets.grid(row=1, column=1, pady=5, padx=10)
entry_cpt_subnets.insert(0, "4")

tk.Label(input_cpt_frame, text="Numero de routers:", font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
entry_cpt_routers = tk.Entry(input_cpt_frame, width=30, font=('Arial', 10))
entry_cpt_routers.grid(row=2, column=1, pady=5, padx=10)
entry_cpt_routers.insert(0, "2")

tk.Label(input_cpt_frame, text="Numero de switches:", font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=5)
entry_cpt_switches = tk.Entry(input_cpt_frame, width=30, font=('Arial', 10))
entry_cpt_switches.grid(row=3, column=1, pady=5, padx=10)
entry_cpt_switches.insert(0, "4")

tk.Label(input_cpt_frame, text="Dispositivos por subred (separados por coma):", font=('Arial', 10)).grid(row=4, column=0, sticky='w', pady=5)
entry_cpt_devices = tk.Entry(input_cpt_frame, width=30, font=('Arial', 10))
entry_cpt_devices.grid(row=4, column=1, pady=5, padx=10)
entry_cpt_devices.insert(0, "10,15,8,12")

tk.Button(input_cpt_frame, text="Generar Esquema CPT", command=generate_cpt_schema,
          bg='#FF6600', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=10).grid(row=5, column=0, columnspan=2, pady=15)

result_cpt_frame = tk.Frame(cpt_main, padx=10, pady=10)
result_cpt_frame.pack(fill=tk.BOTH, expand=True)

cpt_scrollbar = tk.Scrollbar(result_cpt_frame)
cpt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

cpt_text = tk.Text(result_cpt_frame, height=25, wrap=tk.WORD, font=('Courier New', 9), yscrollcommand=cpt_scrollbar.set)
cpt_text.pack(fill=tk.BOTH, expand=True)
cpt_scrollbar.config(command=cpt_text.yview)

cpt_instructions = """BIENVENIDO AL GENERADOR DE ESQUEMAS CPT

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
cpt_text.insert('1.0', cpt_instructions)


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

vlsm_instructions = """BIENVENIDO A LA CALCULADORA VLSM

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
"""
vlsm_text.insert('1.0', vlsm_instructions)


root.mainloop()