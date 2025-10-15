import ipaddress
import tkinter as tk
from tkinter import messagebox

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

    import math
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
        # Removed subtraction of 1 from broadcast
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

    import math
    devices_text.delete('1.0', tk.END)
    label_devices.config(text=f"Subredes para dispositivos (ordenadas mayor a menor):")

    next_network_address = base_network.network_address

    for num_devices in devices_list:
        needed_hosts = num_devices + 2
        bits_for_hosts = math.ceil(math.log2(needed_hosts))
        new_prefix = 32 - bits_for_hosts

        # Check if new_prefix is smaller (larger network) than base network prefix
        if new_prefix < base_network.prefixlen:
            devices_text.insert(tk.END, f"No es posible crear una subred para {num_devices} dispositivos en esta red.\n\n")
            continue

        # Create subnet with the calculated prefix starting at next_network_address
        try:
            subnet = ipaddress.IPv4Network(f"{next_network_address}/{new_prefix}", strict=True)
        except ValueError:
            devices_text.insert(tk.END, f"No se pudo calcular la subred para {num_devices} dispositivos.\n\n")
            continue

        # Check if subnet is inside base network
        if not subnet.subnet_of(base_network):
            devices_text.insert(tk.END, f"La subred para {num_devices} dispositivos excede la red base.\n\n")
            continue

        net_addr = str(subnet.network_address)
        mask = str(subnet.netmask)
        broadcast = str(subnet.broadcast_address)
        # Removed subtraction of 1 from broadcast
        devices_text.insert(tk.END, f"Dispositivos: {num_devices}\nRed: {net_addr}/{new_prefix}\nMáscara: {mask}\nBroadcast: {broadcast}/{new_prefix}\n\n")

        # Calculate next network address: broadcast + 1
        try:
            next_network_address = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)
        except ipaddress.AddressValueError:
            # No more addresses available
            break

# GUI setup
root = tk.Tk()
root.title("Calculadora de Red IP")
root.geometry("600x800")  # Set a reasonable window size

# Main IP input frame
frame_ip = tk.Frame(root, pady=10)
frame_ip.pack(fill=tk.X, padx=20)

tk.Label(frame_ip, text="Introduce la IP con máscara (ejemplo 192.168.1.10/24):").pack(anchor='w')
entry_ip = tk.Entry(frame_ip, width=40)
entry_ip.pack(pady=5, fill=tk.X)

btn_calculate_main = tk.Button(frame_ip, text="Calcular", command=calculate_main)
btn_calculate_main.pack(pady=5)

# Main results frame
frame_main_results = tk.LabelFrame(root, text="Resultados principales", padx=10, pady=10)
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
frame_subnets = tk.LabelFrame(root, text="Crear subredes", padx=10, pady=10)
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
frame_devices = tk.LabelFrame(root, text="Subredes para dispositivos", padx=10, pady=10)
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

# Add extra space at the bottom
tk.Frame(root, height=20).pack()

root.mainloop()