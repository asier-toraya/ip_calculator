"""
Generador de esquemas para Cisco Packet Tracer
"""
import ipaddress
import math


def generate_cpt_topology(base_network, num_subnets, num_routers, num_switches, devices_list):
    """
    Genera un esquema completo de topología para Cisco Packet Tracer usando VLSM
    Soporta switches compartidos y salida resumida.
    Returns: (str output, str error_message or None)
    """
    # Validar que hay suficientes dispositivos especificados
    if len(devices_list) != num_subnets:
        return None, f"Debes especificar {num_subnets} valores de dispositivos. Ingresaste {len(devices_list)}"
    
    # NOTA: Eliminada la restricción de num_switches < num_subnets para permitir switches compartidos

    # --- LOGICA VLSM ---
    devices_sorted_indices = sorted(range(len(devices_list)), key=lambda k: devices_list[k], reverse=True)
    devices_sorted = [devices_list[i] for i in devices_sorted_indices]
    
    # Estructura para guardar la asignación completa
    topology_data = []
    
    current_ip = base_network.network_address
    
    for i, original_idx in enumerate(devices_sorted_indices):
        num_hosts = devices_sorted[i]
        
        # Calcular bits necesarios
        needed = num_hosts + 2
        bits = math.ceil(math.log2(needed))
        prefix = 32 - bits
        
        if prefix < base_network.prefixlen:
            return None, f"El grupo de {num_hosts} dispositivos requiere /{prefix}, que es más grande que la red base"
        
        if prefix > 30:
             return None, f"El grupo de {num_hosts} dispositivos requiere /{prefix}, excede límite práctico (/30)"

        try:
            # Alineación VLSM
            block_size = 2**(32 - prefix)
            ip_int = int(current_ip)
            if ip_int % block_size != 0:
                padding = block_size - (ip_int % block_size)
                current_ip = ipaddress.IPv4Address(ip_int + padding)
            
            subnet = ipaddress.IPv4Network(f"{current_ip}/{prefix}", strict=True)
            
            if not subnet.subnet_of(base_network):
                return None, f"No hay espacio suficiente en la red base para el grupo de {num_hosts} dispositivos."
            
            # Asignar recursos (Router, Switch, VLAN)
            # ID lógico para mostrar al usuario (1, 2, 3...)
            subnet_id = i + 1 
            
            # Asignación Round-Robin de Routers y Switches
            router_id = (i % num_routers) + 1
            switch_id = (i % num_switches) + 1
            vlan_id = subnet_id * 10 # VLAN 10, 20, 30...
            
            topology_data.append({
                'id': subnet_id,
                'num_hosts': num_hosts,
                'subnet': subnet,
                'router_id': router_id,
                'switch_id': switch_id,
                'vlan_id': vlan_id,
                'gateway': subnet.network_address + 1,
                'mask_str': str(subnet.netmask)
            })
            
            current_ip = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)
            
        except Exception as e:
            return None, f"Error al calcular subred: {e}"

    # Generar output estructurado
    output = _generate_header(base_network, num_subnets, num_routers, num_switches)
    output += _generate_router_section(topology_data, num_routers)
    output += _generate_switch_section(topology_data, num_switches)
    output += _generate_devices_section(topology_data)
    output += _generate_recommendations()
    
    return output, None


def _generate_header(base_network, num_subnets, num_routers, num_switches):
    output = "=" * 90 + "\n"
    output += "ESQUEMA DE RED PARA CISCO PACKET TRACER (VLSM)\n"
    output += "=" * 90 + "\n\n"
    output += f"RED BASE: {base_network}\n"
    output += f"SUBREDES: {num_subnets} | ROUTERS: {num_routers} | SWITCHES: {num_switches}\n"
    output += f"METODO: VLSM (Ordenado por tamaño de mayor a menor)\n\n"
    return output


def _generate_router_section(topology_data, num_routers):
    output = "=" * 90 + "\n"
    output += "1. CONFIGURACION DE ROUTERS\n"
    output += "=" * 90 + "\n"
    
    # Agrupar por router
    routers = {r: [] for r in range(1, num_routers + 1)}
    for data in topology_data:
        routers[data['router_id']].append(data)
        
    for r_id in range(1, num_routers + 1):
        output += f"\nROUTER {r_id}\n"
        output += "-" * 90 + "\n"
        
        subnets = routers[r_id]
        if not subnets:
            output += "  (Sin subredes asignadas)\n"
            continue
            
        for i, sub in enumerate(subnets):
            # Usamos interfaces físicas diferentes para cada subred para simplificar
            # En un escenario real avanzado se usarían subinterfaces (RoAS)
            output += f"  Interfaz GigabitEthernet 0/{i}:\n"
            output += f"    Descripcion:  Gateway Subred {sub['id']} (VLAN {sub['vlan_id']})\n"
            output += f"    IP Address:   {sub['gateway']}\n"
            output += f"    Subnet Mask:  {sub['mask_str']}\n"
            output += f"    Conectar a:   Switch {sub['switch_id']}\n\n"
            
    return output


def _generate_switch_section(topology_data, num_switches):
    output = "=" * 90 + "\n"
    output += "2. CONFIGURACION DE SWITCHES\n"
    output += "=" * 90 + "\n"
    
    # Agrupar por switch
    switches = {s: [] for s in range(1, num_switches + 1)}
    for data in topology_data:
        switches[data['switch_id']].append(data)
        
    for s_id in range(1, num_switches + 1):
        output += f"\nSWITCH {s_id}\n"
        output += "-" * 90 + "\n"
        
        subnets = switches[s_id]
        if not subnets:
            output += "  (Sin subredes asignadas)\n"
            continue
            
        # VLANs
        output += "  Base de Datos VLAN:\n"
        for sub in subnets:
            output += f"    - VLAN {sub['vlan_id']}: Nombre 'Subred_{sub['id']}'\n"
        output += "\n"
        
        # Puertos Uplink (hacia Routers)
        output += "  Puertos Uplink (Hacia Router):\n"
        for i, sub in enumerate(subnets):
            # Asumimos un cable por subred hacia el router (modelo simple)
            output += f"    - Fa0/{i+1}: Modo ACCESS (o TRUNK) -> VLAN {sub['vlan_id']} (Hacia Router {sub['router_id']})\n"
        output += "\n"
        
        # Puertos Access (hacia PCs)
        output += "  Puertos de Acceso (Hacia Dispositivos):\n"
        # Distribuir puertos restantes (24 - uplinks) entre las VLANs
        uplinks_count = len(subnets)
        available_ports = 24 - uplinks_count
        ports_per_vlan = available_ports // len(subnets)
        
        current_port = uplinks_count + 1
        for sub in subnets:
            end_port = current_port + ports_per_vlan - 1
            if end_port > 24: end_port = 24
            
            output += f"    - Fa0/{current_port}-{end_port}: Modo ACCESS -> VLAN {sub['vlan_id']} (Subred {sub['id']})\n"
            current_port = end_port + 1
            
    return output


def _generate_devices_section(topology_data):
    output = "=" * 90 + "\n"
    output += "3. CONFIGURACION DE DISPOSITIVOS (Resumen)\n"
    output += "=" * 90 + "\n"
    
    for data in topology_data:
        output += f"\nSUBRED {data['id']} ({data['num_hosts']} dispositivos) - VLAN {data['vlan_id']}\n"
        output += "-" * 90 + "\n"
        output += f"  Red: {data['subnet']} | Gateway: {data['gateway']}\n\n"
        
        # Generar solo los primeros 3 dispositivos
        limit = 3
        count = 0
        current_ip = data['subnet'].network_address + 2
        
        # Iterar para mostrar ejemplos
        for i in range(data['num_hosts']):
            if count < limit:
                output += f"  PC_{data['id']}_{i+1}:\n"
                output += f"    IP: {current_ip}  |  Mask: {data['mask_str']}  |  Gateway: {data['gateway']}\n"
                output += f"    Conectar a: Switch {data['switch_id']} (Puerto de VLAN {data['vlan_id']})\n"
                count += 1
            
            current_ip = ipaddress.IPv4Address(int(current_ip) + 1)
            
            if current_ip >= data['subnet'].broadcast_address:
                break
        
        remaining = data['num_hosts'] - count
        if remaining > 0:
            output += f"\n  ... y {remaining} dispositivos más configurados secuencialmente.\n"
            
    return output


def _generate_router_interconnection(num_routers):
    if num_routers <= 1: return ""
    output = f"\n{'=' * 90}\nINTERCONEXION DE ROUTERS\n{'=' * 90}\n"
    for r in range(1, num_routers):
        output += f"  Router {r} Serial0/0/0 <---> Router {r + 1} Serial0/0/1\n"
    return output


def _generate_recommendations():
    output = f"\n{'=' * 90}\nRECOMENDACIONES\n{'=' * 90}\n"
    output += "1. Si usas un solo cable por VLAN hacia el router, configura los puertos del switch en modo ACCESS para esa VLAN.\n"
    output += "2. Si prefieres 'Router-on-a-Stick', configura un solo TRUNK en el switch y subinterfaces en el router (ej: Gi0/0.10).\n"
    output += "3. Asegúrate de crear las VLANs en la base de datos del switch (vlan database).\n"
    return output
