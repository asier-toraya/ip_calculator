"""
Cálculos de red IP - Funciones core para cálculos de redes
"""
import ipaddress


def calculate_network_details(ip_input):
    """
    Calcula detalles completos de una red
    Returns: dict con toda la información de la red
    """
    ip_part, cidr_part = ip_input.split('/')
    cidr = int(cidr_part)
    ip_obj = ipaddress.IPv4Address(ip_part)
    network = ipaddress.IPv4Network(ip_input, strict=False)
    
    # Calcular máscara
    mask_int = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    mask_octets = [(mask_int >> 24) & 0xFF, (mask_int >> 16) & 0xFF, 
                   (mask_int >> 8) & 0xFF, mask_int & 0xFF]
    mask_str = '.'.join(map(str, mask_octets))
    
    # Calcular dirección de red
    network_int = int(ip_obj) & mask_int
    network_octets = [(network_int >> 24) & 0xFF, (network_int >> 16) & 0xFF, 
                      (network_int >> 8) & 0xFF, network_int & 0xFF]
    network_addr = '.'.join(map(str, network_octets))
    
    # Calcular broadcast
    wildcard_int = 0xFFFFFFFF ^ mask_int
    broadcast_int = network_int | wildcard_int
    broadcast_octets = [(broadcast_int >> 24) & 0xFF, (broadcast_int >> 16) & 0xFF, 
                        (broadcast_int >> 8) & 0xFF, broadcast_int & 0xFF]
    broadcast_addr = '.'.join(map(str, broadcast_octets))
    
    # Calcular octeto determinante para salto de bloque
    determining_octet = next((i for i in range(3, -1, -1) if mask_octets[i] != 255), -1)
    block_size = 256 - mask_octets[determining_octet] if determining_octet >= 0 else 256
    
    # Máscara binaria
    mask_binary = '.'.join([format(mask_int >> (24-i*8) & 0xFF, '08b') for i in range(4)])
    
    # Wildcard
    wildcard_octets = [255 - m for m in mask_octets]
    wildcard_str = '.'.join(map(str, wildcard_octets))
    
    return {
        'ip': ip_part,
        'cidr': cidr,
        'mask_str': mask_str,
        'mask_binary': mask_binary,
        'mask_octets': mask_octets,
        'network_addr': network_addr,
        'broadcast_addr': broadcast_addr,
        'wildcard_str': wildcard_str,
        'block_size': block_size,
        'determining_octet': determining_octet,
        'total_hosts': 2**(32-cidr) - 2,
        'network_obj': network
    }


def format_detailed_output(details):
    """
    Formatea la salida detallada de cálculos de red
    """
    output = "=" * 80 + "\nCALCULO DETALLADO DE RED\n" + "=" * 80 + "\n\n"
    output += f"IP: {details['ip']}/{details['cidr']}\n\n"
    
    output += "PASO 1: MASCARA DE RED\n" + "-" * 40 + "\n"
    output += f"/{details['cidr']} = {details['cidr']} bits en 1\n"
    output += f"Binario: {details['mask_binary']}\n"
    output += f"Decimal: {details['mask_str']}\n\n"
    
    output += "PASO 2: DIRECCION DE RED\n" + "-" * 40 + "\n"
    output += "AND entre IP y Mascara\n"
    output += f"Resultado: {details['network_addr']}/{details['cidr']}\n\n"
    
    output += "PASO 3: SALTO DE BLOQUE\n" + "-" * 40 + "\n"
    if details['determining_octet'] >= 0:
        output += f"256 - {details['mask_octets'][details['determining_octet']]} = {details['block_size']}\n\n"
    
    output += "PASO 4: BROADCAST\n" + "-" * 40 + "\n"
    output += f"Wildcard: {details['wildcard_str']}\n"
    output += f"Broadcast: {details['broadcast_addr']}\n\n"
    
    output += "RESUMEN\n" + "=" * 80 + "\n"
    output += f"Red: {details['network_addr']}/{details['cidr']}\n"
    output += f"Mascara: {details['mask_str']}\n"
    output += f"Broadcast: {details['broadcast_addr']}\n"
    output += f"Hosts: {details['total_hosts']}\n"
    
    return output
