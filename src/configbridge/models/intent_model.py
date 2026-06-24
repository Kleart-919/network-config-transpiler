"""
Intent Model

This module defines the vendor-neutral configuration model used by ConfigBridge.

Parsers convert vendor-specific configuration text into this model.
Generators read this model and produce vendor-specific configuration output.

Important:
    This model should not contain Cisco-specific, Juniper-specific, or
    vendor-specific syntax. It should represent network intent.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VLAN:
    """
    Vendor-neutral VLAN representation.
    """

    vlan_id: int
    name: Optional[str] = None


@dataclass
class Interface:
    """
    Vendor-neutral Layer 2 interface representation.

    mode can be:
    - "access"
    - "trunk"
    - None
    """

    name: str
    description: Optional[str] = None
    mode: Optional[str] = None
    access_vlan: Optional[int] = None
    allowed_vlans: list[int] = field(default_factory=list)


@dataclass
class IntentModel:
    """
    Vendor-neutral network configuration model.

    This is version 1 of the model and focuses on basic Layer 2 switching.
    """

    hostname: Optional[str] = None
    vlans: list[VLAN] = field(default_factory=list)
    interfaces: list[Interface] = field(default_factory=list)

    def to_dict(self) -> dict:
        """
        Convert the intent model into a dictionary.

        This is useful for debugging, testing, JSON output, and later GUI display.
        """

        return {
            "hostname": self.hostname,
            "vlans": [
                {
                    "id": vlan.vlan_id,
                    "name": vlan.name,
                }
                for vlan in self.vlans
            ],
            "interfaces": [
                {
                    "name": interface.name,
                    "description": interface.description,
                    "mode": interface.mode,
                    "access_vlan": interface.access_vlan,
                    "allowed_vlans": interface.allowed_vlans,
                }
                for interface in self.interfaces
            ],
        }