"""
Device Inventory Model

This module represents information discovered from a connected network device.

The purpose of this model is to avoid guessing physical interface mappings based
only on interface names. Different devices, even from the same vendor, can use
different interface layouts.

Future discovery modules will populate this model from live device data such as:
- running configuration
- interface status
- LLDP/CDP neighbours
- VLAN membership
- interface descriptions
"""


from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DiscoveredInterface:
    """
    Represents an interface discovered from a live device.
    """

    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    speed: Optional[str] = None
    mode: Optional[str] = None
    access_vlan: Optional[int] = None
    allowed_vlans: list[int] = field(default_factory=list)
    neighbours: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)


@dataclass
class DeviceInventory:
    """
    Represents discovered information about a network device.
    """

    hostname: Optional[str] = None
    vendor: Optional[str] = None
    interfaces: list[DiscoveredInterface] = field(default_factory=list)

    def find_interface(self, name_or_alias: str) -> Optional[DiscoveredInterface]:
        """
        Find an interface by real name or alias.
        """

        normalized_input = name_or_alias.lower()

        for interface in self.interfaces:
            if interface.name.lower() == normalized_input:
                return interface

            for alias in interface.aliases:
                if alias.lower() == normalized_input:
                    return interface

        return None

    def to_dict(self) -> dict:
        """
        Convert the inventory into a dictionary for debugging and testing.
        """

        return {
            "hostname": self.hostname,
            "vendor": self.vendor,
            "interfaces": [
                {
                    "name": interface.name,
                    "description": interface.description,
                    "status": interface.status,
                    "speed": interface.speed,
                    "mode": interface.mode,
                    "access_vlan": interface.access_vlan,
                    "allowed_vlans": interface.allowed_vlans,
                    "neighbours": interface.neighbours,
                    "aliases": interface.aliases,
                }
                for interface in self.interfaces
            ],
        }