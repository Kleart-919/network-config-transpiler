"""
Runtime CLI engine.
"""

from configbridge.models.device_inventory import DeviceInventory
from configbridge.runtime.runtime_parser import RuntimeParser
from configbridge.runtime.runtime_generator import RuntimeGenerator


class RuntimeEngine:

    def __init__(self):
        self.parser = RuntimeParser()
        self.generator = RuntimeGenerator()

    def set_inventory(self, inventory: DeviceInventory):
        self.generator.set_inventory(inventory)

    def translate(self, command: str) -> str:
        runtime = self.parser.parse(command)

        if runtime is None:
            return command

        return self.generator.generate(runtime)