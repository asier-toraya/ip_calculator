"""Advanced Cisco Packet Tracer topology generator."""

from __future__ import annotations

import ipaddress
import math

from .ip_tools import align_address_to_prefix

VALID_ROUTING_TYPES = {"estatico", "rip", "ospf"}


def generate_advanced_cpt(base_network, subnet_configs, routing_type):
    """Generate a detailed CPT scheme with per-subnet configuration."""
    if not subnet_configs:
        return None, "Debes configurar al menos una subred."

    routing = (routing_type or "").lower().strip()
    if routing not in VALID_ROUTING_TYPES:
        return None, "Tipo de enrutamiento invalido. Usa: estatico, rip u ospf."

    allocated_subnets = []
    current_ip = base_network.network_address

    for index, config in enumerate(subnet_configs):
        routers = int(config.get("routers", 0))
        switches = int(config.get("switches", 0))
        hosts = int(config.get("hosts", 0))

        if routers < 0 or switches < 0 or hosts < 0:
            return None, f"Subred {index}: routers/switches/hosts deben ser >= 0."

        total_hosts_needed = routers + hosts + 3
        bits = math.ceil(math.log2(total_hosts_needed))
        prefix = 32 - bits

        if prefix < base_network.prefixlen:
            return None, f"Subred {index} necesita /{prefix}, mas grande que red base."
        if prefix > 30:
            return None, f"Subred {index} requiere /{prefix}, excede limite /30."

        aligned_ip = align_address_to_prefix(current_ip, prefix)

        try:
            subnet = ipaddress.IPv4Network(f"{aligned_ip}/{prefix}", strict=True)
        except ValueError as error:
            return None, f"Error calculando subred {index}: {error}"

        if not subnet.subnet_of(base_network):
            return None, f"No hay espacio para subred {index}."

        allocated_subnets.append(
            {
                "id": index,
                "subnet": subnet,
                "config": {"routers": routers, "switches": switches, "hosts": hosts},
                "is_main": index == 0,
            }
        )

        current_ip = ipaddress.IPv4Address(int(subnet.broadcast_address) + 1)

    output = _generate_header(base_network, len(subnet_configs), routing)
    output += _generate_subnet_details(allocated_subnets)
    output += _generate_routing_config(allocated_subnets, routing)
    output += _generate_final_notes()
    return output, None


def _generate_header(base_network, num_subnets, routing_type):
    lines = [
        "=" * 100,
        "ESQUEMA AVANZADO CPT - CONFIGURACION DETALLADA POR SUBRED",
        "=" * 100,
        "",
        f"RED BASE:           {base_network}",
        f"SUBREDES:           {num_subnets}",
        f"ENRUTAMIENTO:       {routing_type.upper()}",
        "METODO:             VLSM (Variable Length Subnet Mask)",
        "",
    ]
    return "\n".join(lines)


def _generate_subnet_details(allocated_subnets):
    lines = ["=" * 100, "CONFIGURACION DETALLADA POR SUBRED", "=" * 100]

    for subnet_data in allocated_subnets:
        subnet_id = subnet_data["id"]
        subnet = subnet_data["subnet"]
        config = subnet_data["config"]
        is_main = subnet_data["is_main"]

        vlan_id = 10 if subnet_id == 0 else (subnet_id + 1) * 10
        gateway = subnet.network_address + 1
        mask_str = str(subnet.netmask)

        lines.extend(
            [
                "",
                "#" * 100,
                (
                    f"SUBRED {subnet_id} - RED PRINCIPAL (Conexion a Internet)"
                    if is_main
                    else f"SUBRED {subnet_id}"
                ),
                "#" * 100,
                "",
                "INFORMACION DE RED:",
                "-" * 100,
                f"  Red:               {subnet.network_address}/{subnet.prefixlen}",
                f"  Subnet Mask:       {mask_str}",
                f"  Broadcast:         {subnet.broadcast_address}",
                f"  Gateway:           {gateway}",
                f"  VLAN ID:           {vlan_id}",
                f"  Hosts disponibles: {subnet.num_addresses - 2}",
                "",
            ]
        )

        if config["routers"] > 0:
            lines.append(
                _generate_router_details(
                    subnet,
                    config["routers"],
                    gateway,
                    mask_str,
                    vlan_id,
                    is_main,
                    subnet_id,
                )
            )

        if config["switches"] > 0:
            lines.append(
                _generate_switch_details(
                    config["switches"], vlan_id, config["routers"], config["hosts"], subnet_id
                )
            )

        if config["hosts"] > 0:
            lines.append(
                _generate_host_details(
                    subnet,
                    config["hosts"],
                    gateway,
                    mask_str,
                    vlan_id,
                    config["routers"],
                    subnet_id,
                )
            )

    return "\n".join(lines)


def _generate_router_details(subnet, num_routers, gateway, mask_str, vlan_id, is_main, subnet_id):
    lines = [f"ROUTERS ({num_routers}):", "-" * 100]
    current_ip = gateway

    for index in range(num_routers):
        router_name = f"Router{subnet_id}_{index}" if not is_main else f"RouterPrincipal_{index}"
        lines.extend(
            [
                "",
                f"  {router_name}:",
                f"    Hostname:         {router_name}",
                f"    Interfaz:         GigabitEthernet 0/{index}",
                f"    IP Address:       {current_ip}",
                f"    Subnet Mask:      {mask_str}",
                (
                    "    Descripcion:      Gateway principal - Conexion a Internet"
                    if is_main and index == 0
                    else f"    Descripcion:      Router Subred {subnet_id}"
                ),
            ]
        )

        if is_main and index == 0:
            lines.extend(
                [
                    "    Interfaz WAN:     GigabitEthernet 0/1 (Conectar a ISP/Internet)",
                    "    NAT:              Configurar NAT overload en Gi0/1",
                ]
            )

        lines.extend(
            [
                f"    VLAN:             {vlan_id}",
                f"    Conectar a:       Switch{subnet_id}_0 (Puerto Trunk)",
            ]
        )

        current_ip = ipaddress.IPv4Address(int(current_ip) + 1)

    return "\n".join(lines)


def _generate_switch_details(num_switches, vlan_id, num_routers, num_hosts, subnet_id):
    lines = [f"SWITCHES ({num_switches}):", "-" * 100]

    for index in range(num_switches):
        switch_name = f"Switch{subnet_id}_{index}"
        lines.extend(
            [
                "",
                f"  {switch_name}:",
                f"    Hostname:         {switch_name}",
                "    Modelo:           Catalyst 2960",
                "    VLAN Database:",
                "      - VLAN 1:       Default (Nativa)",
                f"      - VLAN {vlan_id}:      Subred_{subnet_id}",
                "",
                "    Puertos TRUNK:",
            ]
        )

        if index == 0 and num_routers > 0:
            for router_index in range(min(num_routers, 2)):
                lines.extend(
                    [
                        f"      - Fa0/{router_index + 1}:      Modo TRUNK -> Router{subnet_id}_{router_index}",
                        f"                        Allowed VLANs: {vlan_id}",
                    ]
                )
        elif index > 0:
            lines.extend(
                [
                    "      - Fa0/1:          Modo TRUNK -> Switch{subnet_id}_0",
                    f"                        Allowed VLANs: {vlan_id}",
                ]
            )
        else:
            lines.append("      - (Sin routers conectados)")

        lines.append("")
        lines.append("    Puertos ACCESS:")

        hosts_per_switch = num_hosts // num_switches
        if index < num_hosts % num_switches:
            hosts_per_switch += 1

        start_port = 3 if index == 0 else 2
        end_port = min(start_port + hosts_per_switch - 1, 24)

        if hosts_per_switch > 0:
            lines.extend(
                [
                    f"      - Fa0/{start_port}-Fa0/{end_port}: Modo ACCESS -> VLAN {vlan_id}",
                    f"                        Conectar {hosts_per_switch} hosts",
                ]
            )
        else:
            lines.append("      - (Sin hosts asignados)")

    return "\n".join(lines)


def _generate_host_details(subnet, num_hosts, gateway, mask_str, vlan_id, num_routers, subnet_id):
    lines = [f"HOSTS/DISPOSITIVOS ({num_hosts}):", "-" * 100]

    current_ip = subnet.network_address + 1 + num_routers + 1
    sample_limit = min(4, num_hosts)

    for index in range(sample_limit):
        pc_name = f"PC{subnet_id}_{index + 1}"
        lines.extend(
            [
                "",
                f"  {pc_name}:",
                f"    IP Address:       {current_ip}",
                f"    Subnet Mask:      {mask_str}",
                f"    Default Gateway:  {gateway}",
                f"    DNS:              {gateway} (opcional)",
                f"    VLAN:             {vlan_id}",
                f"    Conectar a:       Switch{subnet_id}_0 - Puerto Fa0/{index + 3}",
            ]
        )
        current_ip = ipaddress.IPv4Address(int(current_ip) + 1)

    remaining = num_hosts - sample_limit
    if remaining > 0:
        lines.extend(
            [
                "",
                (
                    f"  ... y {remaining} hosts mas configurados secuencialmente "
                    f"desde {current_ip}"
                ),
                f"      (Mismo Gateway, Subnet Mask y VLAN {vlan_id})",
            ]
        )

    return "\n".join(lines)


def _generate_routing_config(allocated_subnets, routing_type):
    lines = ["=" * 100, f"CONFIGURACION DE ENRUTAMIENTO - {routing_type.upper()}", "=" * 100, ""]

    if routing_type == "estatico":
        lines.append(_generate_static_routing(allocated_subnets))
    elif routing_type == "rip":
        lines.append(_generate_rip_routing(allocated_subnets))
    else:
        lines.append(_generate_ospf_routing(allocated_subnets))

    return "\n".join(lines)


def _generate_static_routing(allocated_subnets):
    lines = [
        "ENRUTAMIENTO ESTATICO:",
        "-" * 100,
        "",
        "En cada router, configurar rutas estaticas hacia las demas subredes:",
        "",
    ]

    for subnet_data in allocated_subnets:
        if subnet_data["config"]["routers"] > 0:
            subnet_id = subnet_data["id"]
            lines.extend(
                [
                    f"Router{subnet_id}_0:",
                    "  Router(config)# ip route [red_destino] [mascara_destino] [next_hop_ip]",
                    "  (Configurar una ruta por cada subred remota)",
                    "",
                ]
            )

    lines.append("NOTA: El next_hop_ip es la IP del router vecino en la red de transito.")
    return "\n".join(lines)


def _generate_rip_routing(allocated_subnets):
    lines = [
        "ENRUTAMIENTO RIP (Routing Information Protocol):",
        "-" * 100,
        "",
        "En CADA router, ejecutar:",
        "",
        "Router(config)# router rip",
        "Router(config-router)# version 2",
        "Router(config-router)# no auto-summary",
    ]

    for subnet_data in allocated_subnets:
        network_addr = subnet_data["subnet"].network_address
        lines.append(f"Router(config-router)# network {network_addr}")

    lines.append("\nNOTA: RIP propaga automaticamente las rutas entre routers.")
    return "\n".join(lines)


def _generate_ospf_routing(allocated_subnets):
    lines = [
        "ENRUTAMIENTO OSPF (Open Shortest Path First):",
        "-" * 100,
        "",
        "En CADA router, ejecutar:",
        "",
        "Router(config)# router ospf 1",
    ]

    for subnet_data in allocated_subnets:
        subnet = subnet_data["subnet"]
        lines.append(
            f"Router(config-router)# network {subnet.network_address} {subnet.hostmask} area 0"
        )

    lines.append("\nNOTA: OSPF usa areas. Area 0 es el backbone.")
    return "\n".join(lines)


def _generate_final_notes():
    lines = [
        "=" * 100,
        "PASOS ADICIONALES",
        "=" * 100,
        "",
        "1. CONFIGURAR VLANs:",
        "   - Crear VLANs en cada switch: vlan [id]",
        "   - Asignar nombre: name [nombre]",
        "",
        "2. CONFIGURAR PUERTOS:",
        "   - Trunk: switchport mode trunk",
        "   - Access: switchport mode access + switchport access vlan [id]",
        "",
        "3. VERIFICAR CONECTIVIDAD:",
        "   - Ping entre dispositivos de la misma subred",
        "   - Ping entre dispositivos de diferentes subredes",
        "   - Verificar tablas de enrutamiento: show ip route",
        "",
        "4. GUARDAR CONFIGURACIONES:",
        "   - Router/Switch# copy running-config startup-config",
        "   - O simplemente: write memory",
        "",
    ]
    return "\n".join(lines)
