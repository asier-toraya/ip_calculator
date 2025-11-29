import ipaddress
import tkinter as tk
from tkinter import ttk, messagebox
import math

def ip_to_binary(ip):
    return '.'.join(f'{int(octet):08b}' for octet in ip.split('.'))

def calculate_main():
    ip_input = entry_ip.get()
    try:
        network = ipaddress.IPv4Network(ip_input, strict=False)
    except ValueError:
        messagebox.showerror("Error", "IP or mask invalid.")
        return

    ip_str = str(network.network_address)
    mask_str = str(network.netmask)
    broadcast_str = str(network.broadcast_address)

    binary_ip = ip_to_binary(ip_str)

    label_network.config(text=f"Dirección de red: {ip_str}/{network.prefixlen}")
    label_mask.config(text=f"Máscara: {mask_str}")
    label_broadcast.config(text=f"Broadcast: {broadcast_str}")
    label_binary.config(text=f"IP en binario: {binary_ip}")

def calculate_subnets():
    ip_input = entry_ip.get()
    try:
        network = ipaddress.IPv4Network(ip_input, strict=False)
    except ValueError:
        messagebox.showerror("Error", "IP or mask invalid.")
        return

    try:
        num_subnets = int(entry_subnets.get())
        if num_subnets < 1:
            raise ValueError
    except ValueError:
        label_subnets.config(text="Introduce un número válido de subredes (>=1).")
        subnets_text.delete('1.0', tk.END)
        return

    bits_needed = math.ceil(math.log2(num_subnets))
    new_prefix = network.prefixlen + bits_needed
    if new_prefix > 32:
        label_subnets.config(text="Número de subredes demasiado grande para esta red.")
        subnets_text.delete('1.0', tk.END)
        return

    label_subnets.config(text=f"Subredes (total {num_subnets}):")
    subnets_text.delete('1.0', tk.END)
    subnets = list(network.subnets(new_prefix=new_prefix))
    for i, subnet in enumerate(subnets[:num_subnets], 1):
        net_addr = str(subnet.network_address)
        mask = str(subnet.netmask)
        broadcast = str(subnet.broadcast_address)
        subnets_text.insert(tk.END, f"{i}. Red: {net_addr} | Máscara: {mask} | Broadcast: {broadcast}\n")

def calculate_devices():
    ip_input = entry_ip.get()
    try:
        base_network = ipaddress.IPv4Network(ip_input, strict=False)
    except ValueError:
        messagebox.showerror("Error", "IP or mask invalid.")
        return

    devices_input = entry_devices.get()
    try:
        devices_list = [int(x.strip()) for x in devices_input.split(',') if x.strip()]
        if any(d < 1 for d in devices_list):
            raise ValueError
    except ValueError:
        label_devices.config(text="Introduce números válidos de dispositivos separados por comas (>=1).")
        devices_text.delete('1.0', tk.END)
        return

    devices_list.sort(reverse=True)

    devices_text.delete('1.0', tk.END)
    label_devices.config(text=f"Subredes para dispositivos (ordenadas mayor a menor):")

    next_network_address = base_network.network_address

    for num_devices in devices_list:
        needed_hosts = num_devices + 2
        bits_for_hosts = math.ceil(math.log2(needed_hosts))
        new_prefix = 32 - bits_for_hosts

        if new_prefix < base_network.prefixlen:
            devices_text.insert(tk.END, f"No es posible crear una subred para {num_devices} dispositivos en esta red.\n\n")
            continue

        try:
            subnet = ipaddress.IPv4Network(f"{next_network_address}/{new_prefix}", strict=True)
        except ValueError:
            devices_text.insert(tk.END, f"No se pudo calcular la subred para {num_devices} dispositivos.\n\n")
            continue

        if not subnet.subnet_of(base_network):
            devices_text.insert(tk.END, f"La subred para {num_devices} dispositivos excede la red base.\n\n")
            continue

        net_addr = str(subnet.network_address)
        mask = str(subnet.netmask)
        broadcast = str(subnet.broadcast_address)
        devices_text.insert(tk.END, f"Dispositivos: {num_devices}\nRed: {net_addr}/{new_prefix}\nMáscara: {mask}\nBroadcast: {broadcast}/{new_prefix}\n\n")

        try:
            next_network_address = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)
        except ipaddress.AddressValueError:
            break

def calculate_detailed():
    """Calcula y muestra paso a paso los detalles de la red"""
    ip_input = entry_detailed_ip.get().strip()
    
    try:
        if '/' not in ip_input:
            messagebox.showerror("Error", "Formato inválido. Usa el formato IP/CIDR (ej: 192.168.0.11/24)")
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
    mask_octets = [
        (mask_int >> 24) & 0xFF,
        (mask_int >> 16) & 0xFF,
        (mask_int >> 8) & 0xFF,
        mask_int & 0xFF
    ]
    mask_str = '.'.join(map(str, mask_octets))
    
    network_int = int(ip_obj) & mask_int
    network_octets = [
        (network_int >> 24) & 0xFF,
        (network_int >> 16) & 0xFF,
        (network_int >> 8) & 0xFF,
        network_int & 0xFF
    ]
    network_addr = '.'.join(map(str, network_octets))
    
    wildcard_int = 0xFFFFFFFF ^ mask_int
    broadcast_int = network_int | wildcard_int
    broadcast_octets = [
        (broadcast_int >> 24) & 0xFF,
        (broadcast_int >> 16) & 0xFF,
        (broadcast_int >> 8) & 0xFF,
        broadcast_int & 0xFF
    ]
    broadcast_addr = '.'.join(map(str, broadcast_octets))
    
    determining_octet = -1
    for i in range(3, -1, -1):
        if mask_octets[i] != 255:
            determining_octet = i
            break
    
    output = "=" * 80 + "\n"
    output += "CÁLCULO DETALLADO DE RED\n"
    output += "=" * 80 + "\n\n"
    
    output += f"📌 DATOS DE ENTRADA:\n"
    output += f"   IP ingresada: {ip_part}\n"
    output += f"   CIDR (prefijo): /{cidr}\n\n"
    
    output += "=" * 80 + "\n"
    output += "PASO 1: CÁLCULO DE LA MÁSCARA DE RED\n"
    output += "=" * 80 + "\n\n"
    
    output += f"El prefijo /{cidr} significa que los primeros {cidr} bits son 1 y los restantes {32-cidr} bits son 0.\n\n"
    
    mask_binary = format(mask_int, '032b')
    mask_binary_formatted = '.'.join([mask_binary[i:i+8] for i in range(0, 32, 8)])
    output += f"Máscara en binario:\n"
    output += f"   {mask_binary_formatted}\n\n"
    
    output += f"Conversión a decimal por octeto:\n"
    for i, octet in enumerate(mask_octets, 1):
        binary_octet = format(octet, '08b')
        output += f"   Octeto {i}: {binary_octet} = {octet}\n"
    
    output += f"\n✅ MÁSCARA DE RED: {mask_str}\n\n"
    
    output += "=" * 80 + "\n"
    output += "PASO 2: CÁLCULO DE LA DIRECCIÓN DE RED\n"
    output += "=" * 80 + "\n\n"
    
    output += "La dirección de red se obtiene aplicando una operación AND bit a bit\n"
    output += "entre la IP y la máscara de red.\n\n"
    
    ip_binary = format(int(ip_obj), '032b')
    ip_binary_formatted = '.'.join([ip_binary[i:i+8] for i in range(0, 32, 8)])
    
    output += f"IP en binario:\n"
    output += f"   {ip_binary_formatted}\n\n"
    
    output += f"Máscara en binario:\n"
    output += f"   {mask_binary_formatted}\n\n"
    
    output += "Operación AND bit a bit:\n"
    network_binary = format(network_int, '032b')
    network_binary_formatted = '.'.join([network_binary[i:i+8] for i in range(0, 32, 8)])
    output += f"   {network_binary_formatted}\n\n"
    
    output += "Conversión a decimal por octeto:\n"
    for i, octet in enumerate(network_octets, 1):
        binary_octet = format(octet, '08b')
        output += f"   Octeto {i}: {binary_octet} = {octet}\n"
    
    output += f"\n✅ DIRECCIÓN DE RED: {network_addr}/{cidr}\n\n"
    
    output += "=" * 80 + "\n"
    output += "PASO 3: CÁLCULO DEL SALTO DE BLOQUE (BLOCK SIZE)\n"
    output += "=" * 80 + "\n\n"
    
    output += "El salto de bloque se calcula a partir del último octeto de la máscara\n"
    output += "que no sea 255.\n\n"
    
    if determining_octet >= 0:
        output += f"Último octeto de la máscara que no es 255: Octeto {determining_octet + 1} = {mask_octets[determining_octet]}\n\n"
        output += f"Fórmula del salto de bloque:\n"
        output += f"   Salto = 256 - {mask_octets[determining_octet]}\n"
        output += f"   Salto = {256 - mask_octets[determining_octet]}\n\n"
        
        output += f"Esto significa que las redes se incrementan de {256 - mask_octets[determining_octet]} en {256 - mask_octets[determining_octet]}\n"
        output += f"en el octeto {determining_octet + 1}.\n\n"
    else:
        output += "Todos los octetos son 255, por lo que el salto de bloque es 256.\n\n"
    
    output += f"✅ SALTO DE BLOQUE: {256 - mask_octets[determining_octet] if determining_octet >= 0 else 256}\n\n"
    
    output += "=" * 80 + "\n"
    output += "PASO 4: CÁLCULO DE LA DIRECCIÓN DE BROADCAST\n"
    output += "=" * 80 + "\n\n"
    
    output += "La dirección de broadcast se calcula sumando la wildcard mask\n"
    output += "a la dirección de red.\n\n"
    
    output += "Primero calculamos la wildcard mask (inverso de la máscara):\n"
    wildcard_octets = [255 - m for m in mask_octets]
    output += f"   Wildcard = 255.255.255.255 - {mask_str}\n"
    output += f"   Wildcard = {'.'.join(map(str, wildcard_octets))}\n\n"
    
    output += "Luego sumamos la wildcard a la dirección de red:\n"
    output += f"   Broadcast = Dirección de Red + Wildcard\n"
    output += f"   Broadcast = {network_addr} + {'.'.join(map(str, wildcard_octets))}\n\n"
    
    output += "Suma por octetos:\n"
    for i in range(4):
        result = network_octets[i] + wildcard_octets[i]
        output += f"   Octeto {i+1}: {network_octets[i]} + {wildcard_octets[i]} = {result}\n"
    
    output += f"\n✅ DIRECCIÓN DE BROADCAST: {broadcast_addr}\n\n"
    
    output += "=" * 80 + "\n"
    output += "RESUMEN FINAL\n"
    output += "=" * 80 + "\n\n"
    
    output += f"📍 IP ingresada:        {ip_part}/{cidr}\n"
    output += f"📍 Dirección de red:    {network_addr}/{cidr}\n"
    output += f"📍 Máscara de red:      {mask_str}\n"
    output += f"📍 Salto de bloque:     {256 - mask_octets[determining_octet] if determining_octet >= 0 else 256}\n"
    output += f"📍 Broadcast:           {broadcast_addr}\n"
    output += f"📍 Rango de hosts:      {network_octets[0]}.{network_octets[1]}.{network_octets[2]}.{network_octets[3] + 1} - "
    output += f"{broadcast_octets[0]}.{broadcast_octets[1]}.{broadcast_octets[2]}.{broadcast_octets[3] - 1}\n"
    output += f"📍 Total de hosts:      {2**(32-cidr) - 2}\n\n"
    
    detailed_text.insert('1.0', output)

def calculate_detailed_subnets():
    """Calcula subredes con explicación detallada"""
    ip_input = entry_detailed_ip.get().strip()
    
    try:
        if '/' not in ip_input:
            messagebox.showerror("Error", "Primero ingresa una IP con máscara en el campo superior")
            return
        
        network = ipaddress.IPv4Network(ip_input, strict=False)
        num_subnets = int(entry_detailed_subnets.get())
        
        if num_subnets < 1:
            raise ValueError("El número de subredes debe ser mayor a 0")
            
    except ValueError as e:
        messagebox.showerror("Error", f"Error en los datos: {e}")
        return
    
    detailed_text.delete('1.0', tk.END)
    
    output = "=" * 80 + "\n"
    output += "CÁLCULO DETALLADO DE SUBREDES\n"
    output += "=" * 80 + "\n\n"
    
    output += f"📌 DATOS DE ENTRADA:\n"
    output += f"   Red base: {network}\n"
    output += f"   Número de subredes solicitadas: {num_subnets}\n\n"
    
    output += "=" * 80 + "\n"
    output += "PASO 1: CALCULAR BITS NECESARIOS PARA LAS SUBREDES\n"
    output += "=" * 80 + "\n\n"
    
    bits_needed = math.ceil(math.log2(num_subnets))
    output += f"Para crear {num_subnets} subredes, necesitamos calcular cuántos bits adicionales\n"
    output += f"debemos tomar prestados de la parte de host.\n\n"
    
    output += f"Fórmula: 2^n >= {num_subnets}, donde n es el número de bits\n\n"
    
    for i in range(1, bits_needed + 2):
        result = 2**i
        symbol = "✓" if result >= num_subnets else "✗"
        output += f"   2^{i} = {result} {symbol}\n"
    
    output += f"\n✅ BITS NECESARIOS: {bits_needed} bits\n"
    output += f"   Con {bits_needed} bits podemos crear hasta {2**bits_needed} subredes\n\n"
    
    output += "=" * 80 + "\n"
    output += "PASO 2: CALCULAR NUEVA MÁSCARA DE SUBRED\n"
    output += "=" * 80 + "\n\n"
    
    old_prefix = network.prefixlen
    new_prefix = old_prefix + bits_needed
    
    if new_prefix > 32:
        output += f"❌ ERROR: La nueva máscara sería /{new_prefix}, lo cual excede /32\n"
        output += f"No es posible crear {num_subnets} subredes en esta red.\n"
        detailed_text.insert('1.0', output)
        return
    
    output += f"Máscara original: /{old_prefix}\n"
    output += f"Bits tomados prestados: +{bits_needed}\n"
    output += f"Nueva máscara: /{old_prefix} + {bits_needed} = /{new_prefix}\n\n"
    
    output += f"Esto significa que:\n"
    output += f"   - Antes teníamos {32 - old_prefix} bits para hosts\n"
    output += f"   - Ahora tenemos {32 - new_prefix} bits para hosts\n"
    output += f"   - Hosts por subred: 2^{32 - new_prefix} - 2 = {2**(32 - new_prefix) - 2}\n\n"
    
    output += "=" * 80 + "\n"
    output += "PASO 3: GENERAR LAS SUBREDES\n"
    output += "=" * 80 + "\n\n"
    
    subnets = list(network.subnets(new_prefix=new_prefix))
    
    output += f"Dividiendo la red {network} en subredes /{new_prefix}:\n\n"
    
    for i, subnet in enumerate(subnets[:num_subnets], 1):
        output += f"━━━ SUBRED {i} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"   Dirección de red:  {subnet.network_address}/{new_prefix}\n"
        output += f"   Máscara:           {subnet.netmask}\n"
        output += f"   Primer host:       {list(subnet.hosts())[0] if subnet.num_addresses > 2 else 'N/A'}\n"
        output += f"   Último host:       {list(subnet.hosts())[-1] if subnet.num_addresses > 2 else 'N/A'}\n"
        output += f"   Broadcast:         {subnet.broadcast_address}\n"
        output += f"   Total de hosts:    {subnet.num_addresses - 2}\n\n"
    
    output += "=" * 80 + "\n"
    output += "RESUMEN\n"
    output += "=" * 80 + "\n\n"
    
    output += f"✅ Se crearon {num_subnets} subredes /{new_prefix}\n"
    output += f"✅ Cada subred tiene {2**(32 - new_prefix) - 2} hosts disponibles\n"
    output += f"✅ Se utilizaron {bits_needed} bits adicionales para subnetting\n\n"
    
    detailed_text.insert('1.0', output)

def calculate_detailed_devices():
    """Calcula subredes por dispositivos con explicación detallada"""
    ip_input = entry_detailed_ip.get().strip()
    
    try:
        if '/' not in ip_input:
            messagebox.showerror("Error", "Primero ingresa una IP con máscara en el campo superior")
            return
        
        base_network = ipaddress.IPv4Network(ip_input, strict=False)
        devices_input = entry_detailed_devices.get().strip()
        devices_list = [int(x.strip()) for x in devices_input.split(',') if x.strip()]
        
        if not devices_list or any(d < 1 for d in devices_list):
            raise ValueError("Ingresa números válidos de dispositivos separados por comas")
            
    except ValueError as e:
        messagebox.showerror("Error", f"Error en los datos: {e}")
        return
    
    detailed_text.delete('1.0', tk.END)
    
    devices_list_sorted = sorted(devices_list, reverse=True)
    
    output = "=" * 80 + "\n"
    output += "CÁLCULO DETALLADO DE SUBREDES POR DISPOSITIVOS\n"
    output += "=" * 80 + "\n\n"
    
    output += f"📌 DATOS DE ENTRADA:\n"
    output += f"   Red base: {base_network}\n"
    output += f"   Dispositivos solicitados: {', '.join(map(str, devices_list))}\n"
    output += f"   Ordenados (mayor a menor): {', '.join(map(str, devices_list_sorted))}\n\n"
    
    output += "💡 NOTA: Se ordenan de mayor a menor para optimizar el uso del espacio\n"
    output += "   de direcciones y evitar fragmentación.\n\n"
    
    next_network_address = base_network.network_address
    subnet_number = 1
    
    for num_devices in devices_list_sorted:
        output += "=" * 80 + "\n"
        output += f"SUBRED {subnet_number}: {num_devices} DISPOSITIVOS\n"
        output += "=" * 80 + "\n\n"
        
        output += "PASO 1: Calcular hosts necesarios\n"
        output += "─" * 40 + "\n"
        needed_hosts = num_devices + 2
        output += f"   Dispositivos solicitados: {num_devices}\n"
        output += f"   + 1 dirección de red\n"
        output += f"   + 1 dirección de broadcast\n"
        output += f"   ─────────────────────────\n"
        output += f"   Total necesario: {needed_hosts} direcciones\n\n"
        
        output += "PASO 2: Calcular bits necesarios para hosts\n"
        output += "─" * 40 + "\n"
        bits_for_hosts = math.ceil(math.log2(needed_hosts))
        output += f"   Fórmula: 2^n >= {needed_hosts}\n\n"
        
        for i in range(1, bits_for_hosts + 2):
            result = 2**i
            symbol = "✓" if result >= needed_hosts else "✗"
            output += f"   2^{i} = {result} {symbol}\n"
        
        output += f"\n   ✅ Bits para hosts: {bits_for_hosts}\n"
        output += f"   Direcciones disponibles: 2^{bits_for_hosts} = {2**bits_for_hosts}\n\n"
        
        output += "PASO 3: Calcular máscara de subred\n"
        output += "─" * 40 + "\n"
        new_prefix = 32 - bits_for_hosts
        output += f"   Prefijo = 32 - {bits_for_hosts} = /{new_prefix}\n\n"
        
        if new_prefix < base_network.prefixlen:
            output += f"   ❌ ERROR: /{new_prefix} es menor que la red base /{base_network.prefixlen}\n"
            output += f"   No es posible crear una subred para {num_devices} dispositivos\n"
            output += f"   en la red {base_network}\n\n"
            subnet_number += 1
            continue
        
        try:
            subnet = ipaddress.IPv4Network(f"{next_network_address}/{new_prefix}", strict=True)
        except ValueError:
            output += f"   ❌ ERROR: No se pudo calcular la subred\n\n"
            subnet_number += 1
            continue
        
        if not subnet.subnet_of(base_network):
            output += f"   ❌ ERROR: La subred excede la red base\n"
            output += f"   Subred calculada: {subnet}\n"
            output += f"   Red base: {base_network}\n\n"
            subnet_number += 1
            continue
        
        output += "PASO 4: Asignar dirección de red\n"
        output += "─" * 40 + "\n"
        output += f"   Siguiente dirección disponible: {next_network_address}\n"
        output += f"   Máscara aplicada: /{new_prefix}\n"
        output += f"   Subred resultante: {subnet}\n\n"
        
        output += "PASO 5: Calcular broadcast\n"
        output += "─" * 40 + "\n"
        output += f"   Dirección de red: {subnet.network_address}\n"
        output += f"   Wildcard: {2**bits_for_hosts - 1}\n"
        output += f"   Broadcast: {subnet.network_address} + {2**bits_for_hosts - 1} = {subnet.broadcast_address}\n\n"
        
        output += "✅ RESULTADO FINAL:\n"
        output += "─" * 40 + "\n"
        output += f"   📍 Red:              {subnet.network_address}/{new_prefix}\n"
        output += f"   📍 Máscara:          {subnet.netmask}\n"
        output += f"   📍 Primer host:      {subnet.network_address + 1}\n"
        output += f"   📍 Último host:      {subnet.broadcast_address - 1}\n"
        output += f"   📍 Broadcast:        {subnet.broadcast_address}\n"
        output += f"   📍 Hosts disponibles: {subnet.num_addresses - 2} (solicitados: {num_devices})\n"
        output += f"   📍 Hosts desperdiciados: {subnet.num_addresses - 2 - num_devices}\n\n"
        
        try:
            next_network_address = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)
            output += f"   ➡️  Siguiente red comenzará en: {next_network_address}\n\n"
        except ipaddress.AddressValueError:
            output += f"   ⚠️  No hay más direcciones disponibles\n\n"
            break
        
        subnet_number += 1
    
    output += "=" * 80 + "\n"
    output += "RESUMEN FINAL\n"
    output += "=" * 80 + "\n\n"
    output += f"✅ Se calcularon subredes para {len(devices_list)} grupos de dispositivos\n"
    output += f"✅ Red base utilizada: {base_network}\n\n"
    
    detailed_text.insert('1.0', output)

# GUI setup
root = tk.Tk()
root.title("Calculadora de Red IP")
root.geometry("900x900")

# Create notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ============================================================================
# TAB 1: Calculadora Principal
# ============================================================================
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Calculadora Principal")

# Main IP input frame
frame_ip = tk.Frame(tab1, pady=10)
frame_ip.pack(fill=tk.X, padx=20)

tk.Label(frame_ip, text="Introduce la IP con máscara (ejemplo 192.168.1.10/24):").pack(anchor='w')
entry_ip = tk.Entry(frame_ip, width=40)
entry_ip.pack(pady=5, fill=tk.X)

btn_calculate_main = tk.Button(frame_ip, text="Calcular", command=calculate_main)
btn_calculate_main.pack(pady=5)

# Main results frame
frame_main_results = tk.LabelFrame(tab1, text="Resultados principales", padx=10, pady=10)
frame_main_results.pack(fill=tk.X, padx=20, pady=10)

label_network = tk.Label(frame_main_results, text="Dirección de red: ")
label_network.pack(anchor='w', pady=2)
label_mask = tk.Label(frame_main_results, text="Máscara: ")
label_mask.pack(anchor='w', pady=2)
label_broadcast = tk.Label(frame_main_results, text="Broadcast: ")
label_broadcast.pack(anchor='w', pady=2)
label_binary = tk.Label(frame_main_results, text="IP en binario: ")
label_binary.pack(anchor='w', pady=2)

# Subnets input frame
frame_subnets = tk.LabelFrame(tab1, text="Crear subredes", padx=10, pady=10)
frame_subnets.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

frame_subnets_input = tk.Frame(frame_subnets)
frame_subnets_input.pack(fill=tk.X, pady=5)

tk.Label(frame_subnets_input, text="Número de subredes a crear:").pack(side=tk.LEFT)
entry_subnets = tk.Entry(frame_subnets_input, width=10)
entry_subnets.pack(side=tk.LEFT, padx=10)
btn_calculate_subnets = tk.Button(frame_subnets_input, text="Calcular", command=calculate_subnets)
btn_calculate_subnets.pack(side=tk.LEFT)

label_subnets = tk.Label(frame_subnets, text="")
label_subnets.pack(anchor='w', pady=5)

subnets_text = tk.Text(frame_subnets, height=8)
subnets_text.pack(fill=tk.BOTH, expand=True)

# Devices input frame
frame_devices = tk.LabelFrame(tab1, text="Subredes para dispositivos", padx=10, pady=10)
frame_devices.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

frame_devices_input = tk.Frame(frame_devices)
frame_devices_input.pack(fill=tk.X, pady=5)

tk.Label(frame_devices_input, text="Número de dispositivos en la subred (separados por coma):").pack(side=tk.LEFT)
entry_devices = tk.Entry(frame_devices_input, width=20)
entry_devices.pack(side=tk.LEFT, padx=10)
btn_calculate_devices = tk.Button(frame_devices_input, text="Calcular", command=calculate_devices)
btn_calculate_devices.pack(side=tk.LEFT)

label_devices = tk.Label(frame_devices, text="")
label_devices.pack(anchor='w', pady=5)

devices_text = tk.Text(frame_devices, height=8)
devices_text.pack(fill=tk.BOTH, expand=True)

# ============================================================================
# TAB 2: Cálculo Detallado
# ============================================================================
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Cálculo Detallado Paso a Paso")

# Input frame for detailed calculation
frame_detailed_input = tk.Frame(tab2, pady=10)
frame_detailed_input.pack(fill=tk.X, padx=20)

tk.Label(frame_detailed_input, text="Introduce la IP con máscara en formato CIDR (ejemplo: 192.168.0.11/24):", 
         font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)

entry_detailed_ip = tk.Entry(frame_detailed_input, width=40, font=('Arial', 12))
entry_detailed_ip.pack(pady=5, fill=tk.X)

btn_calculate_detailed = tk.Button(frame_detailed_input, text="Calcular Detallado", 
                                   command=calculate_detailed, bg='#4CAF50', fg='white',
                                   font=('Arial', 10, 'bold'), padx=20, pady=5)
btn_calculate_detailed.pack(pady=10)

# Separator
ttk.Separator(tab2, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)

# Subnets calculation section
frame_detailed_subnets = tk.LabelFrame(tab2, text="Cálculo de Subredes", padx=10, pady=10, font=('Arial', 10, 'bold'))
frame_detailed_subnets.pack(fill=tk.X, padx=20, pady=10)

tk.Label(frame_detailed_subnets, text="Número de subredes a crear:").pack(side=tk.LEFT, padx=5)
entry_detailed_subnets = tk.Entry(frame_detailed_subnets, width=10, font=('Arial', 11))
entry_detailed_subnets.pack(side=tk.LEFT, padx=5)

btn_calculate_detailed_subnets = tk.Button(frame_detailed_subnets, text="Calcular Subredes", 
                                           command=calculate_detailed_subnets, 
                                           bg='#2196F3', fg='white',
                                           font=('Arial', 9, 'bold'), padx=15, pady=3)
btn_calculate_detailed_subnets.pack(side=tk.LEFT, padx=10)

# Separator
ttk.Separator(tab2, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)

# Devices calculation section
frame_detailed_devices = tk.LabelFrame(tab2, text="Cálculo de Subredes por Dispositivos", padx=10, pady=10, font=('Arial', 10, 'bold'))
frame_detailed_devices.pack(fill=tk.X, padx=20, pady=10)

tk.Label(frame_detailed_devices, text="Número de dispositivos (separados por coma):").pack(side=tk.LEFT, padx=5)
entry_detailed_devices = tk.Entry(frame_detailed_devices, width=25, font=('Arial', 11))
entry_detailed_devices.pack(side=tk.LEFT, padx=5)

btn_calculate_detailed_devices = tk.Button(frame_detailed_devices, text="Calcular por Dispositivos", 
                                           command=calculate_detailed_devices, 
                                           bg='#FF9800', fg='white',
                                           font=('Arial', 9, 'bold'), padx=15, pady=3)
btn_calculate_detailed_devices.pack(side=tk.LEFT, padx=10)

# Results frame with scrollbar
frame_detailed_results = tk.Frame(tab2, padx=10, pady=10)
frame_detailed_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

scrollbar_detailed = tk.Scrollbar(frame_detailed_results)
scrollbar_detailed.pack(side=tk.RIGHT, fill=tk.Y)

detailed_text = tk.Text(frame_detailed_results, height=30, wrap=tk.WORD, 
                       font=('Courier New', 9), yscrollcommand=scrollbar_detailed.set)
detailed_text.pack(fill=tk.BOTH, expand=True)
scrollbar_detailed.config(command=detailed_text.yview)

# Add instructions
instructions = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    CALCULADORA DE RED - MODO DETALLADO                     ║
╚════════════════════════════════════════════════════════════════════════════╝

Esta herramienta te mostrará paso a paso cómo se calculan:

  🔹 CÁLCULO BÁSICO:
     1️⃣  La MÁSCARA DE RED a partir del prefijo CIDR
     2️⃣  La DIRECCIÓN DE RED usando operación AND
     3️⃣  El SALTO DE BLOQUE (block size) de la máscara
     4️⃣  La DIRECCIÓN DE BROADCAST sumando la wildcard

  🔹 CÁLCULO DE SUBREDES:
     Divide una red en N subredes iguales mostrando el proceso completo
     Ejemplo: Ingresa "192.168.1.0/24" arriba y "5" subredes

  🔹 CÁLCULO POR DISPOSITIVOS:
     Crea subredes optimizadas para diferentes cantidades de dispositivos
     Ejemplo: Ingresa "192.168.1.0/24" arriba y "100,200,30,50" dispositivos

Ingresa los datos correspondientes y presiona el botón para ver el procedimiento.

"""
detailed_text.insert('1.0', instructions)

root.mainloop()