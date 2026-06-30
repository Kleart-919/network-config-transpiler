"""
Runtime CLI engine.
"""

from configbridge.models.device_inventory import DeviceInventory
from configbridge.runtime.runtime_parser import RuntimeParser
from configbridge.runtime.runtime_registry import RuntimeRegistry


class RuntimeEngine:

    def __init__(self):

        self.parser = RuntimeParser()

        self.registry = RuntimeRegistry()

        self.inventory = None

    def set_inventory(
        self,
        inventory: DeviceInventory,
    ):

        self.inventory = inventory

    def translate(
        self,
        command: str,
    ) -> str:

        runtime = self.parser.parse(command)

        if runtime is None:
            return command

        generator = self.registry.get_generator(
            self.inventory.vendor
        )

        generator.set_inventory(
            self.inventory
        )

        return generator.generate(runtime)