"""
Juniper Discovery Parser

Parses Juniper operational command output into a DeviceInventory.
"""

from configbridge.models.device_inventory import (
    DeviceInventory,
    DiscoveredInterface,
)


class JuniperDiscoveryParser:
    """
    Parses Juniper discovery command output.
    """

    def parse_interfaces(
        self,
        output_text: str,
        hostname: str | None = None,
    ) -> DeviceInventory:
        """
        Parse 'show interfaces terse'.
        """

        inventory = DeviceInventory(
            hostname=hostname,
            vendor="Juniper Junos",
        )

        lines = output_text.splitlines()

        for raw_line in lines:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("Interface"):
                continue

            parts = line.split()

            if len(parts) < 3:
                continue

            interface_name = parts[0]
            admin_status = parts[1]
            link_status = parts[2]

            if not interface_name.startswith(("ge-", "xe-", "et-")):
                continue

            discovered_interface = DiscoveredInterface(
                name=interface_name,
                status=link_status,
                aliases=self.generate_cisco_style_aliases(interface_name),
            )

            inventory.interfaces.append(discovered_interface)

        return inventory

    def generate_cisco_style_aliases(
        self,
        juniper_interface: str,
    ) -> list[str]:

        if not juniper_interface.startswith("ge-"):
            return []

        numbers = juniper_interface.replace("ge-", "")
        parts = numbers.split("/")

        if len(parts) != 3:
            return []

        fpc, pic, port = parts

        return [
            f"GigabitEthernet{fpc}/{pic}/{port}",
            f"Gi{fpc}/{pic}/{port}",
        ]