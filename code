"""
Juniper runtime generator.
"""

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
            and command.resource == "interfaces"
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
        """

        if self.inventory is None:
            return name_or_alias

        interface = self.inventory.find_interface(name_or_alias)

        if interface is None:
            return name_or_alias

        return interface.name