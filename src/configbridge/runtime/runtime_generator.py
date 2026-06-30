"""
Juniper runtime generator.
"""

import re

from configbridge.models.device_inventory import DeviceInventory
from configbridge.runtime.runtime_command import RuntimeCommand


class RuntimeGenerator:

    def __init__(self, inventory: DeviceInventory | None = None):
        self.inventory = inventory

    def set_inventory(self, inventory: DeviceInventory):
        self.inventory = inventory

    def generate(self, command: RuntimeCommand) -> str:

        if command.verb == "configure" and command.resource == "terminal":
            return "configure"

        if command.verb == "interface" and command.arguments:
            interface = self.resolve_interface(command.arguments[0])
            return f"edit interfaces {interface}"

        if command.verb == "show" and command.resource == "version":
            return "show version"

        if (
            command.verb == "show"
            and command.resource in ("interfaces", "interface")
            and command.qualifier == "status"
        ):
            return "show interfaces terse"

        if (
            command.verb == "show"
            and command.resource == "vlan"
            and command.qualifier == "brief"
        ):
            return "show vlans"

        return " ".join(
            filter(
                None,
                [
                    command.verb,
                    command.resource,
                    command.qualifier,
                    *command.arguments,
                ],
            )
        )

    def resolve_interface(self, name_or_alias: str) -> str:
        """
        Resolve preferred CLI interface name to real device interface name.
        Inventory lookup is preferred. Fallback supports common Cisco syntax.
        """

        if self.inventory is not None:
            interface = self.inventory.find_interface(name_or_alias)

            if interface is not None:
                return interface.name

        return self._fallback_cisco_to_juniper(name_or_alias)

    def _fallback_cisco_to_juniper(self, interface: str) -> str:
        """
        Fallback only when inventory has not resolved the interface.
        """

        value = interface.strip()

        match = re.match(
            r"^(gigabitethernet|gi)(\d+)/(\d+)/(\d+)$",
            value,
            re.IGNORECASE,
        )

        if match:
            return f"ge-{match.group(2)}/{match.group(3)}/{match.group(4)}"

        return value