"""Core network calculations and formatted educational output."""

from __future__ import annotations

import ipaddress

from .ip_tools import format_octets, host_range, netmask_octets, usable_hosts_for_prefix


def calculate_network_details(ip_input: str):
    """Calculate complete IPv4 details for an ``IP/CIDR`` input."""
    ip_part, cidr_part = ip_input.split("/", 1)
    cidr = int(cidr_part)

    ip_obj = ipaddress.IPv4Address(ip_part)
    network = ipaddress.IPv4Network(ip_input, strict=False)

    mask_octets = netmask_octets(cidr)
    mask_str = format_octets(mask_octets)

    mask_int = int(network.netmask)
    network_int = int(ip_obj) & mask_int
    broadcast_int = network_int | int(network.hostmask)

    network_addr = str(ipaddress.IPv4Address(network_int))
    broadcast_addr = str(ipaddress.IPv4Address(broadcast_int))

    determining_octet = next((idx for idx in range(3, -1, -1) if mask_octets[idx] != 255), -1)
    block_size = 256 - mask_octets[determining_octet] if determining_octet >= 0 else 256

    mask_binary = ".".join(format((mask_int >> (24 - idx * 8)) & 0xFF, "08b") for idx in range(4))
    wildcard_octets = [255 - octet for octet in mask_octets]

    first_host, last_host = host_range(network)

    return {
        "ip": ip_part,
        "cidr": cidr,
        "mask_str": mask_str,
        "mask_binary": mask_binary,
        "mask_octets": mask_octets,
        "network_addr": network_addr,
        "broadcast_addr": broadcast_addr,
        "wildcard_str": format_octets(wildcard_octets),
        "block_size": block_size,
        "determining_octet": determining_octet,
        "total_hosts": usable_hosts_for_prefix(cidr),
        "first_host": first_host,
        "last_host": last_host,
        "network_obj": network,
    }


def format_detailed_output(details):
    """Format network details into a readable report."""
    lines = [
        "=" * 80,
        "CALCULO DETALLADO DE RED",
        "=" * 80,
        "",
        f"IP: {details['ip']}/{details['cidr']}",
        "",
        "PASO 1: MASCARA DE RED",
        "-" * 40,
        f"/{details['cidr']} = {details['cidr']} bits en 1",
        f"Binario: {details['mask_binary']}",
        f"Decimal: {details['mask_str']}",
        "",
        "PASO 2: DIRECCION DE RED",
        "-" * 40,
        "AND entre IP y Mascara",
        f"Resultado: {details['network_addr']}/{details['cidr']}",
        "",
        "PASO 3: SALTO DE BLOQUE",
        "-" * 40,
    ]

    if details["determining_octet"] >= 0:
        mask_value = details["mask_octets"][details["determining_octet"]]
        lines.append(f"256 - {mask_value} = {details['block_size']}")
        lines.append("")

    lines.extend(
        [
            "PASO 4: BROADCAST",
            "-" * 40,
            f"Wildcard: {details['wildcard_str']}",
            f"Broadcast: {details['broadcast_addr']}",
            "",
            "RESUMEN",
            "=" * 80,
            f"Red: {details['network_addr']}/{details['cidr']}",
            f"Mascara: {details['mask_str']}",
            f"Broadcast: {details['broadcast_addr']}",
            f"Hosts usables: {details['total_hosts']}",
        ]
    )

    if details["first_host"] is None:
        lines.append("Rango de hosts: no aplica para /31 o /32")
    else:
        lines.append(f"Primer host: {details['first_host']}")
        lines.append(f"Ultimo host: {details['last_host']}")

    return "\n".join(lines)
