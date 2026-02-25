"""Shared IPv4 utilities for core modules."""

from __future__ import annotations

import ipaddress


def netmask_octets(prefix: int) -> list[int]:
    """Return decimal octets for a CIDR prefix."""
    mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF if prefix > 0 else 0
    return [
        (mask_int >> 24) & 0xFF,
        (mask_int >> 16) & 0xFF,
        (mask_int >> 8) & 0xFF,
        mask_int & 0xFF,
    ]


def format_octets(octets: list[int]) -> str:
    """Convert octets to dotted-decimal text."""
    return ".".join(str(octet) for octet in octets)


def usable_hosts_for_prefix(prefix: int) -> int:
    """Return RFC-agnostic usable host count for a prefix."""
    if prefix >= 31:
        return 0
    return (2 ** (32 - prefix)) - 2


def host_range(network: ipaddress.IPv4Network):
    """Return first/last usable host addresses, or ``None`` if not available."""
    if network.prefixlen >= 31:
        return None, None
    return network.network_address + 1, network.broadcast_address - 1


def align_address_to_prefix(address: ipaddress.IPv4Address, prefix: int) -> ipaddress.IPv4Address:
    """Align an address to the next valid network boundary for ``prefix``."""
    block_size = 2 ** (32 - prefix)
    address_int = int(address)
    remainder = address_int % block_size
    if remainder == 0:
        return address
    return ipaddress.IPv4Address(address_int + (block_size - remainder))
