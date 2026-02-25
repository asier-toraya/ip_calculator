"""Subnet calculation helpers and reporting."""

from __future__ import annotations

import ipaddress
import math

from .ip_tools import align_address_to_prefix, host_range, usable_hosts_for_prefix


def calculate_subnets(network: ipaddress.IPv4Network, num_subnets: int):
    """Split a network into ``num_subnets`` equal-size subnets."""
    if num_subnets < 1:
        return None, "ERROR: El numero de subredes debe ser mayor a 0"

    bits_needed = 0 if num_subnets == 1 else math.ceil(math.log2(num_subnets))
    new_prefix = network.prefixlen + bits_needed

    if new_prefix > 32:
        return None, f"ERROR: /{new_prefix} excede /32"

    subnets = list(network.subnets(new_prefix=new_prefix))

    return {
        "bits_needed": bits_needed,
        "new_prefix": new_prefix,
        "hosts_per_subnet": usable_hosts_for_prefix(new_prefix),
        "subnets": subnets[:num_subnets],
        "total_possible": 2 ** bits_needed,
    }, None


def calculate_subnets_by_devices(base_network: ipaddress.IPv4Network, devices_list: list[int]):
    """Allocate variable-size subnets based on requested devices."""
    if not devices_list:
        return []

    devices_sorted = sorted(devices_list, reverse=True)
    results = []
    next_addr = base_network.network_address

    for idx, num_devices in enumerate(devices_sorted, start=1):
        if num_devices < 1:
            results.append(
                {
                    "index": idx,
                    "devices": num_devices,
                    "error": "El numero de dispositivos debe ser mayor a 0",
                }
            )
            continue

        needed_addresses = num_devices + 2
        host_bits = math.ceil(math.log2(needed_addresses))
        prefix = 32 - host_bits

        if prefix < base_network.prefixlen:
            results.append(
                {
                    "index": idx,
                    "devices": num_devices,
                    "error": "Subred demasiado grande para la red base",
                }
            )
            continue

        aligned_addr = align_address_to_prefix(next_addr, prefix)

        try:
            subnet = ipaddress.IPv4Network(f"{aligned_addr}/{prefix}", strict=True)
        except ValueError as error:
            results.append(
                {
                    "index": idx,
                    "devices": num_devices,
                    "error": f"No se pudo crear subred: {error}",
                }
            )
            continue

        if not subnet.subnet_of(base_network):
            results.append(
                {
                    "index": idx,
                    "devices": num_devices,
                    "error": "Excede la red base",
                }
            )
            continue

        first_host, last_host = host_range(subnet)
        usable_hosts = usable_hosts_for_prefix(prefix)

        results.append(
            {
                "index": idx,
                "devices": num_devices,
                "subnet": subnet,
                "network_addr": subnet.network_address,
                "broadcast_addr": subnet.broadcast_address,
                "mask_str": str(subnet.netmask),
                "prefix": prefix,
                "first_host": first_host,
                "last_host": last_host,
                "total_hosts": usable_hosts,
                "wasted_hosts": max(usable_hosts - num_devices, 0),
                "host_bits": host_bits,
            }
        )

        next_addr = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)

    return results


def format_subnets_output(base_network, num_subnets, subnet_info):
    """Format subnet split output."""
    lines = [
        "CALCULO DE SUBREDES",
        "=" * 80,
        "",
        f"Red base: {base_network}",
        f"Subredes solicitadas: {num_subnets}",
        "",
        (
            f"Bits necesarios: {subnet_info['bits_needed']} "
            f"(2^{subnet_info['bits_needed']} = {subnet_info['total_possible']})"
        ),
        f"Nueva mascara: /{subnet_info['new_prefix']}",
        f"Hosts usables por subred: {subnet_info['hosts_per_subnet']}",
        "",
    ]

    for index, subnet in enumerate(subnet_info["subnets"], start=1):
        lines.append(
            f"{index}. {subnet.network_address}/{subnet_info['new_prefix']} - {subnet.broadcast_address}"
        )

    return "\n".join(lines)


def format_devices_output(base_network, devices_list, results):
    """Format VLSM-by-devices output."""
    lines = [
        "SUBREDES POR DISPOSITIVOS",
        "=" * 80,
        "",
        f"Red base: {base_network}",
        f"Dispositivos solicitados: {', '.join(map(str, devices_list))}",
        f"Ordenados (mayor a menor): {', '.join(map(str, sorted(devices_list, reverse=True)))}",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"SUBRED {result['index']}: {result['devices']} dispositivos",
                "-" * 80,
            ]
        )

        if "error" in result:
            lines.extend([f"ERROR: {result['error']}", ""])
            continue

        lines.extend(
            [
                f"Direccion de red:     {result['network_addr']}/{result['prefix']}",
                f"Mascara de red:       {result['mask_str']}",
                f"Broadcast:            {result['broadcast_addr']}",
                f"Hosts disponibles:    {result['total_hosts']}",
                (
                    "Primera IP host:      "
                    f"{result['first_host'] if result['first_host'] is not None else 'No aplica'}"
                ),
                (
                    "Ultima IP host:       "
                    f"{result['last_host'] if result['last_host'] is not None else 'No aplica'}"
                ),
                f"Hosts desperdiciados: {result['wasted_hosts']}",
                (
                    f"Calculo: 2^{result['host_bits']} - 2 = "
                    f"{(2 ** result['host_bits']) - 2} hosts"
                ),
                "",
            ]
        )

    return "\n".join(lines)
