"""
Cisco Generator

This module converts the vendor-neutral IntentModel into Cisco IOS
configuration commands.
"""

from configbridge.models.intent_model import IntentModel


class CiscoGenerator:
    """
    Generates Cisco IOS configuration from the IntentModel.
    """

    def generate(self, intent: IntentModel) -> str:
        lines = []

        if intent.hostname:
            lines.append(f"hostname {intent.hostname}")
            lines.append("")

        for vlan in intent.vlans:
            lines.append(f"vlan {vlan.vlan_id}")

            if vlan.name:
                lines.append(f" name {vlan.name}")

        if intent.vlans:
            lines.append("")

        for interface in intent.interfaces:
            cisco_interface = self.map_interface_name(interface.name)

            lines.append(f"interface {cisco_interface}")

            if interface.description:
                lines.append(f" description {interface.description}")

            if interface.mode == "access":
                lines.append(" switchport mode access")

                if interface.access_vlan is not None:
                    lines.append(f" switchport access vlan {interface.access_vlan}")

            if interface.mode == "trunk":
                lines.append(" switchport mode trunk")

                if interface.allowed_vlans:
                    vlan_text = ",".join(
                        str(vlan_id) for vlan_id in interface.allowed_vlans
                    )
                    lines.append(f" switchport trunk allowed vlan {vlan_text}")

            lines.append("")

        return "\n".join(lines).strip() + "\n"

    def map_interface_name(self, interface_name: str) -> str:
        """
        Convert a Juniper-style interface name into a basic Cisco-style name.

        This is a temporary demonstration mapping for Phase 2.

        Example:
            ge-0/0/1 -> GigabitEthernet1/0/1

        Future versions should use an interface mapping layer.
        """

        if interface_name.startswith("ge-"):
            numbers = interface_name.replace("ge-", "")
            parts = numbers.split("/")

            if len(parts) == 3:
                return f"GigabitEthernet{parts[1]}/0/{parts[2]}"

        return interface_name