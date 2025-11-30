"""
Cálculos de subredes
"""
import ipaddress
import math


def calculate_subnets(network, num_subnets):
    """
    Calcula división en subredes
    Returns: dict con información de subredes
    """
    bits_needed = math.ceil(math.log2(num_subnets))
    new_prefix = network.prefixlen + bits_needed
    
    if new_prefix > 32:
        return None, f"ERROR: /{new_prefix} excede /32"
    
    subnets = list(network.subnets(new_prefix=new_prefix))
    
    return {
        'bits_needed': bits_needed,
        'new_prefix': new_prefix,
        'hosts_per_subnet': 2**(32 - new_prefix) - 2,
        'subnets': subnets[:num_subnets],
        'total_possible': 2**bits_needed
    }, None


def calculate_subnets_by_devices(base_network, devices_list):
    """
    Calcula subredes optimizadas por número de dispositivos
    Returns: list de dict con información de cada subred
    """
    devices_sorted = sorted(devices_list, reverse=True)
    results = []
    next_addr = base_network.network_address
    
    for idx, num_dev in enumerate(devices_sorted, 1):
        needed = num_dev + 2
        bits = math.ceil(math.log2(needed))
        prefix = 32 - bits
        
        if prefix < base_network.prefixlen:
            results.append({
                'index': idx,
                'devices': num_dev,
                'error': 'Subred muy grande para la red base'
            })
            continue
        
        try:
            subnet = ipaddress.IPv4Network(f"{next_addr}/{prefix}", strict=True)
            if subnet.subnet_of(base_network):
                # Calcular máscara
                mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
                mask_octets = [(mask_int >> 24) & 0xFF, (mask_int >> 16) & 0xFF, 
                               (mask_int >> 8) & 0xFF, mask_int & 0xFF]
                mask_str = '.'.join(map(str, mask_octets))
                
                results.append({
                    'index': idx,
                    'devices': num_dev,
                    'subnet': subnet,
                    'network_addr': subnet.network_address,
                    'broadcast_addr': subnet.broadcast_address,
                    'mask_str': mask_str,
                    'prefix': prefix,
                    'first_host': subnet.network_address + 1,
                    'last_host': subnet.broadcast_address - 1,
                    'total_hosts': subnet.num_addresses - 2,
                    'wasted_hosts': subnet.num_addresses - 2 - num_dev,
                    'bits': bits
                })
                
                next_addr = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)
            else:
                results.append({
                    'index': idx,
                    'devices': num_dev,
                    'error': 'Excede la red base'
                })
        except Exception as e:
            results.append({
                'index': idx,
                'devices': num_dev,
                'error': str(e)
            })
    
    return results


def format_subnets_output(base_network, num_subnets, subnet_info):
    """
    Formatea la salida de cálculo de subredes
    """
    output = "CALCULO DE SUBREDES\n" + "=" * 80 + "\n\n"
    output += f"Red base: {base_network}\nSubredes: {num_subnets}\n\n"
    output += f"Bits necesarios: {subnet_info['bits_needed']} (2^{subnet_info['bits_needed']} = {subnet_info['total_possible']})\n"
    output += f"Nueva mascara: /{subnet_info['new_prefix']}\n"
    output += f"Hosts/subred: {subnet_info['hosts_per_subnet']}\n\n"
    
    for i, subnet in enumerate(subnet_info['subnets'], 1):
        output += f"{i}. {subnet.network_address}/{subnet_info['new_prefix']} - {subnet.broadcast_address}\n"
    
    return output


def format_devices_output(base_network, devices_list, results):
    """
    Formatea la salida de subredes por dispositivos
    """
    output = "SUBREDES POR DISPOSITIVOS\n" + "=" * 80 + "\n\n"
    output += f"Red base: {base_network}\n"
    output += f"Dispositivos solicitados: {', '.join(map(str, devices_list))}\n"
    output += f"Ordenados (mayor a menor): {', '.join(map(str, sorted(devices_list, reverse=True)))}\n\n"
    
    for result in results:
        output += f"SUBRED {result['index']}: {result['devices']} dispositivos\n"
        output += "-" * 80 + "\n"
        
        if 'error' in result:
            output += f"ERROR: {result['error']}\n\n"
        else:
            output += f"Direccion de red:     {result['network_addr']}/{result['prefix']}\n"
            output += f"Mascara de red:       {result['mask_str']}\n"
            output += f"Broadcast:            {result['broadcast_addr']}\n"
            output += f"Hosts disponibles:    {result['total_hosts']}\n"
            output += f"Primera IP host:      {result['first_host']}\n"
            output += f"Ultima IP host:       {result['last_host']}\n"
            output += f"Hosts desperdiciados: {result['wasted_hosts']}\n"
            output += f"Calculo: 2^{result['bits']} - 2 = {2**result['bits']} - 2 = {2**result['bits'] - 2} hosts\n\n"
    
    return output
