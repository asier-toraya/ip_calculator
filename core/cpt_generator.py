"""Cisco Packet Tracer topology generator (basic mode)."""

from __future__ import annotations

import ipaddress
import math

from .ip_tools import align_address_to_prefix


def generate_cpt_topology(base_network, num_subnets, num_routers, num_switches, devices_list):
    """Generate a complete CPT topology using VLSM."""
    if num_subnets < 1:
        return None, "El numero de subredes debe ser mayor a 0."
    if num_routers < 1:
        return None, "El numero de routers debe ser mayor a 0."
    if num_switches < 1:
        return None, "El numero de switches debe ser mayor a 0."

    if len(devices_list) != num_subnets:
        return None, (
            f"Debes especificar {num_subnets} valores de dispositivos. "
            f"Ingresaste {len(devices_list)}"
        )

    if any(hosts < 1 for hosts in devices_list):
        return None, "Todos los valores de dispositivos deben ser mayores a 0."

    sorted_indexes = sorted(range(len(devices_list)), key=lambda idx: devices_list[idx], reverse=True)
    sorted_devices = [devices_list[idx] for idx in sorted_indexes]

    topology_data = []
    current_ip = base_network.network_address

    for index, num_hosts in enumerate(sorted_devices, start=1):
        needed = num_hosts + 2
        host_bits = math.ceil(math.log2(needed))
        prefix = 32 - host_bits

        if prefix < base_network.prefixlen:
            return None, (
                f"El grupo de {num_hosts} dispositivos requiere /{prefix}, "
                "mas grande que la red base."
            )
        if prefix > 30:
            return None, (
                f"El grupo de {num_hosts} dispositivos requiere /{prefix}, "
                "excede limite practico (/30)."
            )

        aligned_ip = align_address_to_prefix(current_ip, prefix)

        try:
            subnet = ipaddress.IPv4Network(f"{aligned_ip}/{prefix}", strict=True)
        except ValueError as error:
            return None, f"Error al calcular subred: {error}"

        if not subnet.subnet_of(base_network):
            return None, (
                "No hay espacio suficiente en la red base para el grupo "
                f"de {num_hosts} dispositivos."
            )

        router_id = ((index - 1) % num_routers) + 1
        switch_id = ((index - 1) % num_switches) + 1
        vlan_id = index * 10

        topology_data.append(
            {
                "id": index,
                "num_hosts": num_hosts,
                "subnet": subnet,
                "router_id": router_id,
                "switch_id": switch_id,
                "vlan_id": vlan_id,
                "gateway": subnet.network_address + 1,
                "mask_str": str(subnet.netmask),
            }
        )

        current_ip = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)

    output = _generate_header(base_network, num_subnets, num_routers, num_switches)
    output += _generate_router_section(topology_data, num_routers)
    output += _generate_switch_section(topology_data, num_switches)
    output += _generate_devices_section(topology_data)
    output += _generate_router_interconnection(num_routers)
    output += _generate_recommendations()
    return output, None


def _generate_header(base_network, num_subnets, num_routers, num_switches):
    lines = [
        "=" * 90,
        "ESQUEMA DE RED PARA CISCO PACKET TRACER (VLSM)",
        "=" * 90,
        "",
        f"RED BASE: {base_network}",
        f"SUBREDES: {num_subnets} | ROUTERS: {num_routers} | SWITCHES: {num_switches}",
        "METODO: VLSM (Ordenado por tamano de mayor a menor)",
        "",
    ]
    return "\n".join(lines)


def _generate_router_section(topology_data, num_routers):
    lines = ["=" * 90, "1. CONFIGURACION DE ROUTERS", "=" * 90]

    routers = {router_id: [] for router_id in range(1, num_routers + 1)}
    for subnet_data in topology_data:
        routers[subnet_data["router_id"]].append(subnet_data)

    for router_id in range(1, num_routers + 1):
        lines.extend(["", f"ROUTER {router_id}", "-" * 90])
        assigned = routers[router_id]
        if not assigned:
            lines.append("  (Sin subredes asignadas)")
            continue

        for interface_index, subnet_data in enumerate(assigned):
            lines.extend(
                [
                    f"  Interfaz GigabitEthernet 0/{interface_index}:",
                    (
                        "    Descripcion:  Gateway Subred "
                        f"{subnet_data['id']} (VLAN {subnet_data['vlan_id']})"
                    ),
                    f"    IP Address:   {subnet_data['gateway']}",
                    f"    Subnet Mask:  {subnet_data['mask_str']}",
                    f"    Conectar a:   Switch {subnet_data['switch_id']}",
                    "",
                ]
            )

    return "\n".join(lines)


def _distribute_access_ports(available_ports, num_segments):
    if num_segments <= 0 or available_ports <= 0:
        return [0] * max(num_segments, 0)

    base = available_ports // num_segments
    remainder = available_ports % num_segments
    distribution = [base] * num_segments
    for index in range(remainder):
        distribution[index] += 1
    return distribution


def _generate_switch_section(topology_data, num_switches):
    lines = ["=" * 90, "2. CONFIGURACION DE SWITCHES", "=" * 90]

    switches = {switch_id: [] for switch_id in range(1, num_switches + 1)}
    for subnet_data in topology_data:
        switches[subnet_data["switch_id"]].append(subnet_data)

    for switch_id in range(1, num_switches + 1):
        lines.extend(["", f"SWITCH {switch_id}", "-" * 90])
        assigned = switches[switch_id]
        if not assigned:
            lines.append("  (Sin subredes asignadas)")
            continue

        lines.append("  Base de Datos VLAN:")
        for subnet_data in assigned:
            lines.append(f"    - VLAN {subnet_data['vlan_id']}: Nombre 'Subred_{subnet_data['id']}'")

        lines.append("")
        lines.append("  Puertos Uplink (Hacia Router):")
        for uplink_index, subnet_data in enumerate(assigned, start=1):
            lines.append(
                (
                    f"    - Fa0/{uplink_index}: Modo ACCESS (o TRUNK) -> "
                    f"VLAN {subnet_data['vlan_id']} (Hacia Router {subnet_data['router_id']})"
                )
            )

        uplinks_count = len(assigned)
        lines.append("")
        lines.append("  Puertos de Acceso (Hacia Dispositivos):")

        available_ports = max(24 - uplinks_count, 0)
        port_distribution = _distribute_access_ports(available_ports, len(assigned))

        current_port = uplinks_count + 1
        for subnet_data, ports_for_vlan in zip(assigned, port_distribution):
            if ports_for_vlan <= 0:
                lines.append(
                    (
                        f"    - VLAN {subnet_data['vlan_id']}: "
                        "sin puertos libres en este switch (requiere expansion)."
                    )
                )
                continue

            end_port = current_port + ports_for_vlan - 1
            lines.append(
                (
                    f"    - Fa0/{current_port}-Fa0/{end_port}: "
                    f"Modo ACCESS -> VLAN {subnet_data['vlan_id']} (Subred {subnet_data['id']})"
                )
            )
            current_port = end_port + 1

    return "\n".join(lines)


def _generate_devices_section(topology_data):
    lines = ["=" * 90, "3. CONFIGURACION DE DISPOSITIVOS (Resumen)", "=" * 90]

    for subnet_data in topology_data:
        lines.extend(
            [
                "",
                (
                    f"SUBRED {subnet_data['id']} "
                    f"({subnet_data['num_hosts']} dispositivos) - VLAN {subnet_data['vlan_id']}"
                ),
                "-" * 90,
                f"  Red: {subnet_data['subnet']} | Gateway: {subnet_data['gateway']}",
                "",
            ]
        )

        sample_limit = 3
        current_ip = subnet_data["subnet"].network_address + 2

        shown_hosts = min(subnet_data["num_hosts"], sample_limit)
        for host_index in range(shown_hosts):
            lines.extend(
                [
                    f"  PC_{subnet_data['id']}_{host_index + 1}:",
                    (
                        f"    IP: {current_ip} | Mask: {subnet_data['mask_str']} "
                        f"| Gateway: {subnet_data['gateway']}"
                    ),
                    (
                        f"    Conectar a: Switch {subnet_data['switch_id']} "
                        f"(Puerto de VLAN {subnet_data['vlan_id']})"
                    ),
                ]
            )
            current_ip = ipaddress.IPv4Address(int(current_ip) + 1)

        remaining = subnet_data["num_hosts"] - shown_hosts
        if remaining > 0:
            lines.append(f"\n  ... y {remaining} dispositivos mas configurados secuencialmente.")

    return "\n".join(lines)


def _generate_router_interconnection(num_routers):
    if num_routers <= 1:
        return ""

    lines = ["", "=" * 90, "INTERCONEXION DE ROUTERS", "=" * 90]
    for router_id in range(1, num_routers):
        lines.append(
            f"  Router {router_id} Serial0/0/0 <---> Router {router_id + 1} Serial0/0/1"
        )
    return "\n".join(lines)


def _generate_recommendations():
    lines = [
        "",
        "=" * 90,
        "RECOMENDACIONES",
        "=" * 90,
        "1. Si usas un solo cable por VLAN hacia el router, configura el puerto en modo ACCESS.",
        "2. Si prefieres Router-on-a-Stick, usa un solo TRUNK y subinterfaces (ej: Gi0/0.10).",
        "3. Crea siempre las VLANs en el switch antes de asignar puertos.",
    ]
    return "\n".join(lines)
