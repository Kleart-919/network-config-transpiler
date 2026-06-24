"""
Juniper Generator

This module converts the vendor-neutral IntentModel into Juniper Junos
set-style configuration commands.

Vendor syntax templates are loaded from the vendor template metadata layer.
"""

from configbridge.models.intent_model import IntentModel
from configbridge.plugins.vendor_templates import VENDOR_TEMPLATES


class JuniperGenerator:
    """
    Generates Juniper Junos set commands from the IntentModel.
    """

    def __init__(self):
        self.templates = VENDOR_TEMPLATES["juniper_junos"]

    def generate(self, intent: IntentModel) -> str:
        """
        Convert the intent model into Junos set-style configuration.
        """

        lines = []

        if intent.hostname:
            lines.append(
                self.templates["hostname"].format(hostname=intent.hostname)
            )
            lines.append("")

        for vlan in intent.vlans:
            vlan_name = vlan.name or f"VLAN_{vlan.vlan_id}"
            lines.append(
                self.templates["vlan"].format(
                    vlan_name=vlan_name,
                    vlan_id=vlan.vlan_id,
                )
            )

        if intent.vlans:
            lines.append("")

        for interface in intent.interfaces:
            juniper_interface = self.map_interface_name(interface.name)

            if interface.description:
                lines.append(
                    self.templates["interface_description"].format(
                        interface_name=juniper_interface,
                        description=interface.description,
                    )
                )

            if interface.mode == "access":
                lines.append(
                    self.templates["access_mode"].format(
                        interface_name=juniper_interface
                    )
                )

                if interface.access_vlan is not None:
                    vlan_name = self.find_vlan_name(intent, interface.access_vlan)
                    lines.append(
                        self.templates["access_vlan"].format(
                            interface_name=juniper_interface,
                            vlan_name=vlan_name,
                        )
                    )

            if interface.mode == "trunk":
                lines.append(
                    self.templates["trunk_mode"].format(
                        interface_name=juniper_interface
                    )
                )

                if interface.allowed_vlans:
                    vlan_members = [
                        self.find_vlan_name(intent, vlan_id)
                        for vlan_id in interface.allowed_vlans
                    ]
                    vlan_text = " ".join(vlan_members)
                    lines.append(
                        self.templates["allowed_vlans"].format(
                            interface_name=juniper_interface,
                            vlans=vlan_text,
                        )
                    )

            lines.append("")

        return "\n".join(lines).strip() + "\n"

    def find_vlan_name(self, intent: IntentModel, vlan_id: int) -> str:
        """
        Find the VLAN name for a VLAN ID.

        If no name exists, generate a fallback VLAN name.
        """

        for vlan in intent.vlans:
            if vlan.vlan_id == vlan_id:
                return vlan.name or f"VLAN_{vlan_id}"

        return f"VLAN_{vlan_id}"

    def map_interface_name(self, interface_name: str) -> str:
        """
        Convert a Cisco-style interface name into a basic Juniper-style name.

        This is a temporary demonstration mapping for Phase 2.
        Future versions should use an interface mapping layer.
        """

        if interface_name.startswith("GigabitEthernet"):
            numbers = interface_name.replace("GigabitEthernet", "")
            parts = numbers.split("/")

            if len(parts) == 3:
                return f"ge-{parts[1]}/0/{parts[2]}"

        return interface_name