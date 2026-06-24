"""
Cisco Parser

Version 1 parser for Cisco IOS Layer 2 configurations.

Supported:

- hostname
- vlan
- vlan name
- interface
- description
- access mode
- trunk mode
- access vlan
- allowed vlans
"""

from configbridge.models.intent_model import (
    IntentModel,
    VLAN,
    Interface,
)


class CiscoParser:
    """
    Cisco IOS parser.

    Reads configuration text and produces an IntentModel.
    """

    def parse(self, config_text: str) -> IntentModel:
        """
        Parse Cisco configuration text.
        """

        intent = IntentModel()

        current_vlan = None
        current_interface = None

        lines = config_text.splitlines()

        for raw_line in lines:
            line = raw_line.strip()

            if not line:
                continue

            # ------------------------------
            # Hostname
            # ------------------------------
            if line.startswith("hostname "):
                intent.hostname = line.split(maxsplit=1)[1]
                continue

            # ------------------------------
            # VLAN
            # ------------------------------
            if line.startswith("vlan "):
                vlan_id = int(line.split()[1])

                current_vlan = VLAN(vlan_id=vlan_id)
                intent.vlans.append(current_vlan)

                current_interface = None
                continue

            if current_vlan and line.startswith("name "):
                current_vlan.name = line.split(maxsplit=1)[1]
                continue

            # ------------------------------
            # Interface
            # ------------------------------
            if line.startswith("interface "):
                interface_name = line.split(maxsplit=1)[1]

                current_interface = Interface(
                    name=interface_name
                )

                intent.interfaces.append(current_interface)

                current_vlan = None
                continue

            if current_interface is None:
                continue

            # ------------------------------
            # Interface Description
            # ------------------------------
            if line.startswith("description "):
                current_interface.description = line.split(
                    maxsplit=1
                )[1]
                continue

            # ------------------------------
            # Access / Trunk Mode
            # ------------------------------
            if line == "switchport mode access":
                current_interface.mode = "access"
                continue

            if line == "switchport mode trunk":
                current_interface.mode = "trunk"
                continue

            # ------------------------------
            # Access VLAN
            # ------------------------------
            if line.startswith("switchport access vlan "):
                current_interface.access_vlan = int(
                    line.split()[-1]
                )
                continue

            # ------------------------------
            # Allowed VLANs
            # ------------------------------
            if line.startswith(
                "switchport trunk allowed vlan "
            ):
                vlan_string = line.replace(
                    "switchport trunk allowed vlan ",
                    ""
                )

                current_interface.allowed_vlans = [
                    int(vlan.strip())
                    for vlan in vlan_string.split(",")
                ]

        return intent