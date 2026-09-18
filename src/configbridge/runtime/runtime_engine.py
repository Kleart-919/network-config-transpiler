"""
Runtime CLI engine.
"""

from configbridge.models.device_inventory import DeviceInventory
from configbridge.schema.loader import SchemaLoader
from configbridge.engine.generic_runtime_parser import GenericRuntimeParser
from configbridge.engine.naming import unanchored_pattern
from configbridge.runtime.runtime_registry import RuntimeRegistry
from configbridge.runtime.juniper_output_parser import JuniperOutputParser
from configbridge.runtime.cisco_output_generator import CiscoOutputGenerator

# The vendor grammar a user types commands AGAINST. Matches the legacy
# RuntimeParser's hardcoded "Cisco IOS" load - not yet a configurable
# choice (out of scope for this schema migration; see runtime section
# comments in schema/vendors/cisco_ios.yaml). RuntimeRegistry separately
# wires the device/target side (Juniper Junos) from its own schema.
_TYPED_VENDOR_SCHEMA_ID = "cisco_ios"


class RuntimeEngine:

    def __init__(self):
        typed_schema = SchemaLoader().load(_TYPED_VENDOR_SCHEMA_ID)

        self.parser = GenericRuntimeParser(typed_schema)
        self.registry = RuntimeRegistry()
        self.inventory = None

        # The device's native interface-name shape is defined by whichever
        # vendor recognizes it as foreign - here, the typed (Cisco) schema's
        # own recognizer for Juniper-style names - so both output-side
        # pieces below share the same schema-declared pattern/conversion
        # instead of re-hardcoding it.
        device_naming_pattern = unanchored_pattern(typed_schema.naming.recognizes[0].pattern)
        self.output_parser = JuniperOutputParser(device_naming_pattern)
        self.output_generator = CiscoOutputGenerator(typed_schema.naming)

    def set_inventory(self, inventory: DeviceInventory):
        self.inventory = inventory

    def translate(self, command: str) -> str:
        runtime = self.parser.parse(command)

        if runtime is None:
            return command

        generator = self.registry.get_generator(self.inventory.vendor)
        generator.set_inventory(self.inventory)

        generated = generator.generate(runtime)

        if runtime.mode_change:
            self.parser.set_mode(runtime.mode_change)

        return generated

    def virtualize_output(self, text: str) -> str:
        runtime = self.output_parser.parse(text)
        return self.output_generator.generate(runtime)