"""
Runtime generator.

Generates native commands from runtime operations using vendor templates.
"""

from configbridge.models.device_inventory import DeviceInventory
from configbridge.runtime.runtime_command import RuntimeCommand
from configbridge.runtime.runtime_templates import RUNTIME_TEMPLATES


class RuntimeGenerator:

    def __init__(self, vendor="Juniper Junos"):
        self.vendor = vendor
        self.inventory: DeviceInventory | None = None

    def set_inventory(self, inventory):
        self.inventory = inventory
        self.vendor = inventory.vendor

    def generate(self, command: RuntimeCommand):
        templates = RUNTIME_TEMPLATES[self.vendor]

        if command.operation not in templates:
            return ""

        template = templates[command.operation]

        values = {}

        if "{interface}" in template:
            values["interface"] = self.resolve_interface(command.arguments[0])

        if "{value}" in template:
            values["value"] = " ".join(command.arguments)

        if "{vlan}" in template:
            values["vlan"] = command.arguments[0]

        return template.format(**values)

    def resolve_interface(self, interface):
        if self.inventory is None:
            return interface

        discovered = self.inventory.find_interface(interface)

        if discovered is None:
            return interface

        return discovered.name