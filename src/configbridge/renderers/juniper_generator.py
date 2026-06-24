"""
Juniper Generator

This module converts the vendor-neutral IntentModel into Juniper Junos
set-style configuration commands.
"""

from configbridge.models.intent_model import IntentModel


class JuniperGenerator:
    """
    Generates Juniper Junos set commands from the IntentModel.
    """

    def generate(self, intent: IntentModel) -> str:
        """
        Convert the intent model into Junos set-style configuration.
        """

        lines = []

        if intent.hostname:
            lines.append(f"set system host-name {intent.hostname}")
            lines.append("")

        for vlan in intent.vlans:
            vlan_name = vlan.name or f"VLAN_{vlan.vlan_id}"
            lines.append(f"set vlans {vlan_name} vlan-id {vlan.vlan_id}")

        if intent.vlans:
            lines.append("")

        for interface in intent.interfaces:
            juniper_interface = self.map_interface_name(interface.name)

            if interface.description:
                lines.append(
                    f'set interfaces {juniper_interface} description "{interface.description}"'
                )

            if interface.mode == "access":
                lines.append(
                    f"set interfaces {juniper_interface} unit 0 family ethernet-switching interface-mode access"
                )

                if interface.access_vlan is not None:
                    vlan_name = self.find_vlan_name(intent, interface.access_vlan)
                    lines.append(
                        f"set interfaces {juniper_interface} unit 0 family ethernet-switching vlan members {vlan_name}"
                    )

            if interface.mode == "trunk":
                lines.append(
                    f"set interfaces {juniper_interface} unit 0 family ethernet-switching interface-mode trunk"
                )

                if interface.allowed_vlans:
                    vlan_members = [
                        self.find_vlan_name(intent, vlan_id)
                        for vlan_id in interface.allowed_vlans
                    ]
                    vlan_text = " ".join(vlan_members)
                    lines.append(
                        f"set interfaces {juniper_interface} unit 0 family ethernet-switching vlan members [ {vlan_text} ]"
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

        Example:
            GigabitEthernet1/0/1 -> ge-0/0/1

        Future versions should use an interface mapping layer rather than a
        hardcoded conversion.
        """

        if interface_name.startswith("GigabitEthernet"):
            numbers = interface_name.replace("GigabitEthernet", "")
            parts = numbers.split("/")

            if len(parts) == 3:
                return f"ge-{parts[1]}/0/{parts[2]}"

        return interface_name