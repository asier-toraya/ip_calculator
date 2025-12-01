"""
Generador Avanzado de Esquemas CPT con configuración detallada por subred
"""
import ipaddress
import math


def generate_advanced_cpt(base_network, subnet_configs, routing_type):
    """
    Genera esquema CPT avanzado con configuración detallada por subred
    
    Args:
        base_network: IPv4Network - Red base
        subnet_configs: list of dict - Configuración de cada subred
            [{
                'routers': int,
                'switches': int, 
                'hosts': int
            }, ...]
        routing_type: str - 'estatico', 'rip', 'ospf'
    
    Returns:
        (str output, str error) - Esquema generado o mensaje de error
    """
    if not subnet_configs:
        return None, "Debes configurar al menos una subred"
    
    # Calcular subredes usando VLSM
    allocated_subnets = []
    current_ip = base_network.network_address
    
    for idx, config in enumerate(subnet_configs):
        # Calcular hosts totales necesarios (routers + switches + hosts + gateway)
        # Cada router necesita 1 IP, cada switch no consume IP, cada host 1 IP
        # + 1 para gateway + 2 para red y broadcast
        total_hosts_needed = config['routers'] + config['hosts'] + 3
        
        # Calcular bits necesarios
        bits = math.ceil(math.log2(total_hosts_needed))
        prefix = 32 - bits
        
        if prefix < base_network.prefixlen:
            return None, f"Subred {idx} necesita /{prefix}, más grande que red base"
        
        if prefix > 30:
            return None, f"Subred {idx} requiere /{prefix}, excede límite /30"
        
        try:
            # Alineación VLSM
            block_size = 2**(32 - prefix)
            ip_int = int(current_ip)
            if ip_int % block_size != 0:
                padding = block_size - (ip_int % block_size)
                current_ip = ipaddress.IPv4Address(ip_int + padding)
            
            subnet = ipaddress.IPv4Network(f"{current_ip}/{prefix}", strict=True)
            
            if not subnet.subnet_of(base_network):
                return None, f"No hay espacio para subred {idx}"
            
            allocated_subnets.append({
                'id': idx,
                'subnet': subnet,
                'config': config,
                'is_main': (idx == 0)
            })
            
            current_ip = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)
            
        except Exception as e:
            return None, f"Error calculando subred {idx}: {e}"
    
    # Generar output
    output = _generate_header(base_network, len(subnet_configs), routing_type)
    output += _generate_subnet_details(allocated_subnets)
    output += _generate_routing_config(allocated_subnets, routing_type)
    output += _generate_final_notes()
    
    return output, None


def _generate_header(base_network, num_subnets, routing_type):
    """Genera encabezado del esquema"""
    output = "=" * 100 + "\n"
    output += "ESQUEMA AVANZADO CPT - CONFIGURACION DETALLADA POR SUBRED\n"
    output += "=" * 100 + "\n\n"
    output += f"RED BASE:           {base_network}\n"
    output += f"SUBREDES:           {num_subnets}\n"
    output += f"ENRUTAMIENTO:       {routing_type.upper()}\n"
    output += f"METODO:             VLSM (Variable Length Subnet Mask)\n\n"
    return output


def _generate_subnet_details(allocated_subnets):
    """Genera detalles de cada subred con VLANs"""
    output = "=" * 100 + "\n"
    output += "CONFIGURACION DETALLADA POR SUBRED\n"
    output += "=" * 100 + "\n"
    
    for subnet_data in allocated_subnets:
        subnet_id = subnet_data['id']
        subnet = subnet_data['subnet']
        config = subnet_data['config']
        is_main = subnet_data['is_main']
        
        vlan_id = 10 if subnet_id == 0 else (subnet_id + 1) * 10
        
        output += f"\n{'#' * 100}\n"
        if is_main:
            output += f"SUBRED {subnet_id} - RED PRINCIPAL (Conexión a Internet)\n"
        else:
            output += f"SUBRED {subnet_id}\n"
        output += f"{'#' * 100}\n\n"
        
        # Información de red
        mask_str = str(subnet.netmask)
        gateway = subnet.network_address + 1
        
        output += f"INFORMACION DE RED:\n"
        output += f"{'-' * 100}\n"
        output += f"  Red:              {subnet.network_address}/{subnet.prefixlen}\n"
        output += f"  Subnet Mask:      {mask_str}\n"
        output += f"  Broadcast:        {subnet.broadcast_address}\n"
        output += f"  Gateway:          {gateway}\n"
        output += f"  VLAN ID:          {vlan_id}\n"
        output += f"  Hosts disponibles: {subnet.num_addresses - 2}\n\n"
        
        # Routers
        if config['routers'] > 0:
            output += _generate_router_details(subnet, config['routers'], gateway, mask_str, 
                                               vlan_id, is_main, subnet_id)
        
        # Switches
        if config['switches'] > 0:
            output += _generate_switch_details(subnet, config['switches'], vlan_id, 
                                               config['routers'], config['hosts'], subnet_id)
        
        # Hosts
        if config['hosts'] > 0:
            output += _generate_host_details(subnet, config['hosts'], gateway, mask_str, 
                                            vlan_id, config['routers'], subnet_id)
    
    return output


def _generate_router_details(subnet, num_routers, gateway, mask_str, vlan_id, is_main, subnet_id):
    """Genera configuración detallada de routers"""
    output = f"ROUTERS ({num_routers}):\n"
    output += f"{'-' * 100}\n"
    
    current_ip = gateway
    
    for i in range(num_routers):
        router_name = f"Router{subnet_id}_{i}" if not is_main else f"RouterPrincipal_{i}"
        
        output += f"\n  {router_name}:\n"
        output += f"    Hostname:         {router_name}\n"
        output += f"    Interfaz:         GigabitEthernet 0/{i}\n"
        output += f"    IP Address:       {current_ip}\n"
        output += f"    Subnet Mask:      {mask_str}\n"
        output += f"    Descripcion:      {'Gateway principal - Conexion a Internet' if is_main and i == 0 else f'Router Subred {subnet_id}'}\n"
        
        if is_main and i == 0:
            output += f"    Interfaz WAN:     GigabitEthernet 0/1 (Conectar a ISP/Internet)\n"
            output += f"    NAT:              Configurar NAT overload en Gi0/1\n"
        
        output += f"    VLAN:             {vlan_id}\n"
        output += f"    Conectar a:       Switch{subnet_id}_0 (Puerto Trunk)\n"
        
        current_ip = ipaddress.IPv4Address(int(current_ip) + 1)
    
    output += "\n"
    return output


def _generate_switch_details(subnet, num_switches, vlan_id, num_routers, num_hosts, subnet_id):
    """Genera configuración detallada de switches"""
    output = f"SWITCHES ({num_switches}):\n"
    output += f"{'-' * 100}\n"
    
    for i in range(num_switches):
        switch_name = f"Switch{subnet_id}_{i}"
        
        output += f"\n  {switch_name}:\n"
        output += f"    Hostname:         {switch_name}\n"
        output += f"    Modelo:           Catalyst 2960\n"
        output += f"    VLAN Database:\n"
        output += f"      - VLAN 1:       Default (Nativa)\n"
        output += f"      - VLAN {vlan_id}:      Subred_{subnet_id}\n\n"
        
        # Puertos Trunk (hacia routers u otros switches)
        output += f"    Puertos TRUNK:\n"
        if i == 0 and num_routers > 0:
            for r in range(min(num_routers, 2)):  # Max 2 routers por switch principal
                output += f"      - Fa0/{r+1}:      Modo TRUNK -> Router{subnet_id}_{r}\n"
                output += f"                        Allowed VLANs: {vlan_id}\n"
        
        if i > 0:
            output += f"      - Fa0/1:          Modo TRUNK -> Switch{subnet_id}_0\n"
            output += f"                        Allowed VLANs: {vlan_id}\n"
        
        # Puertos Access (hacia hosts)
        output += f"\n    Puertos ACCESS:\n"
        
        # Calcular cuántos hosts van a este switch
        hosts_per_switch = num_hosts // num_switches
        if i < num_hosts % num_switches:
            hosts_per_switch += 1
        
        start_port = 3 if i == 0 else 2
        end_port = min(start_port + hosts_per_switch - 1, 24)
        
        if hosts_per_switch > 0:
            output += f"      - Fa0/{start_port}-{end_port}:  Modo ACCESS -> VLAN {vlan_id}\n"
            output += f"                        Conectar {hosts_per_switch} hosts\n"
        else:
            output += f"      - (Sin hosts asignados)\n"
    
    output += "\n"
    return output


def _generate_host_details(subnet, num_hosts, gateway, mask_str, vlan_id, num_routers, subnet_id):
    """Genera configuración de hosts (primeros 4)"""
    output = f"HOSTS/DISPOSITIVOS ({num_hosts}):\n"
    output += f"{'-' * 100}\n"
    
    # IP inicial para hosts (después de gateway y routers)
    current_ip = subnet.network_address + 1 + num_routers + 1
    
    # Mostrar solo los primeros 4
    limit = min(4, num_hosts)
    
    for i in range(limit):
        pc_name = f"PC{subnet_id}_{i+1}"
        
        output += f"\n  {pc_name}:\n"
        output += f"    IP Address:       {current_ip}\n"
        output += f"    Subnet Mask:      {mask_str}\n"
        output += f"    Default Gateway:  {gateway}\n"
        output += f"    DNS:              {gateway} (opcional)\n"
        output += f"    VLAN:             {vlan_id}\n"
        output += f"    Conectar a:       Switch{subnet_id}_0 - Puerto Fa0/{i+3}\n"
        
        current_ip = ipaddress.IPv4Address(int(current_ip) + 1)
    
    remaining = num_hosts - limit
    if remaining > 0:
        output += f"\n  ... y {remaining} hosts más configurados secuencialmente desde {current_ip}\n"
        output += f"      (Mismo Gateway, Subnet Mask y VLAN {vlan_id})\n"
    
    output += "\n"
    return output


def _generate_routing_config(allocated_subnets, routing_type):
    """Genera configuración de enrutamiento"""
    output = "=" * 100 + "\n"
    output += f"CONFIGURACION DE ENRUTAMIENTO - {routing_type.upper()}\n"
    output += "=" * 100 + "\n\n"
    
    if routing_type.lower() == 'estatico':
        output += _generate_static_routing(allocated_subnets)
    elif routing_type.lower() == 'rip':
        output += _generate_rip_routing(allocated_subnets)
    elif routing_type.lower() == 'ospf':
        output += _generate_ospf_routing(allocated_subnets)
    
    return output


def _generate_static_routing(allocated_subnets):
    """Genera comandos para enrutamiento estático"""
    output = "ENRUTAMIENTO ESTATICO:\n"
    output += "-" * 100 + "\n\n"
    
    output += "En cada router, configurar rutas estáticas hacia las demás subredes:\n\n"
    
    for subnet_data in allocated_subnets:
        if subnet_data['config']['routers'] > 0:
            subnet_id = subnet_data['id']
            output += f"Router{subnet_id}_0:\n"
            output += f"  Router(config)# ip route [red_destino] [mascara_destino] [next_hop_ip]\n"
            output += f"  (Configurar una ruta por cada subred remota)\n\n"
    
    output += "NOTA: El next_hop_ip es la IP del router vecino en la red de tránsito.\n\n"
    return output


def _generate_rip_routing(allocated_subnets):
    """Genera comandos para RIP"""
    output = "ENRUTAMIENTO RIP (Routing Information Protocol):\n"
    output += "-" * 100 + "\n\n"
    
    output += "En CADA router, ejecutar:\n\n"
    output += "Router(config)# router rip\n"
    output += "Router(config-router)# version 2\n"
    output += "Router(config-router)# no auto-summary\n"
    
    for subnet_data in allocated_subnets:
        subnet = subnet_data['subnet']
        # Usar la red principal (sin host bits)
        network_addr = subnet.network_address
        output += f"Router(config-router)# network {network_addr}\n"
    
    output += "\nNOTA: RIP propaga automáticamente las rutas entre routers.\n\n"
    return output


def _generate_ospf_routing(allocated_subnets):
    """Genera comandos para OSPF"""
    output = "ENRUTAMIENTO OSPF (Open Shortest Path First):\n"
    output += "-" * 100 + "\n\n"
    
    output += "En CADA router, ejecutar:\n\n"
    output += "Router(config)# router ospf 1\n"
    
    for subnet_data in allocated_subnets:
        subnet = subnet_data['subnet']
        # Calcular wildcard mask
        wildcard_int = int(subnet.hostmask)
        wildcard_octets = [(wildcard_int >> 24) & 0xFF, (wildcard_int >> 16) & 0xFF,
                          (wildcard_int >> 8) & 0xFF, wildcard_int & 0xFF]
        wildcard = '.'.join(map(str, wildcard_octets))
        
        output += f"Router(config-router)# network {subnet.network_address} {wildcard} area 0\n"
    
    output += "\nNOTA: OSPF usa áreas. Area 0 es el backbone.\n\n"
    return output


def _generate_final_notes():
    """Genera notas finales"""
    output = "=" * 100 + "\n"
    output += "PASOS ADICIONALES\n"
    output += "=" * 100 + "\n\n"
    
    output += "1. CONFIGURAR VLANs:\n"
    output += "   - Crear VLANs en cada switch: vlan [id]\n"
    output += "   - Asignar nombre: name [nombre]\n\n"
    
    output += "2. CONFIGURAR PUERTOS:\n"
    output += "   - Trunk: switchport mode trunk\n"
    output += "   - Access: switchport mode access + switchport access vlan [id]\n\n"
    
    output += "3. VERIFICAR CONECTIVIDAD:\n"
    output += "   - Ping entre dispositivos de la misma subred\n"
    output += "   - Ping entre dispositivos de diferentes subredes\n"
    output += "   - Verificar tablas de enrutamiento: show ip route\n\n"
    
    output += "4. GUARDAR CONFIGURACIONES:\n"
    output += "   - Router/Switch# copy running-config startup-config\n"
    output += "   - O simplemente: write memory\n\n"
    
    return output
