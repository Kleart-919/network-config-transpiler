"""
Generic, schema-driven runtime command generator.

Replaces runtime/runtime_generator.py + runtime/runtime_templates.py. Looks
up the TARGET vendor's schema.runtime "templates" entry for an operation
and fills its placeholders per the entry's declared "arguments" bindings,
instead of the legacy per-placeholder-name hardcoded Python
(values["interface"] = ..., values["value"] = " ".join(...), etc).

"resolve: device_inventory_alias" tries live DeviceInventory alias lookup
first (resolve_interface()'s original behavior); as of Phase 7, if that
finds no match, it falls back to the schema-driven static naming_convention
mapper (engine/naming.py) - the same one the batch generator uses - instead
of passing the raw typed name through unconverted. Live discovery data
wins whenever it's available and matches; the static mapper is strictly a
fallback for names discovery hasn't seen.
"""

from configbridge.models.device_inventory import DeviceInventory
from configbridge.runtime.runtime_command import RuntimeCommand
from configbridge.schema.schema_model import VendorSchema
from configbridge.engine.naming import InterfaceNameMapper


class GenericRuntimeGenerator:
    def __init__(self, schema: VendorSchema):
        if schema.runtime is None or "templates" not in schema.runtime:
            raise ValueError(f"Vendor schema '{schema.vendor_id}' has no runtime.templates section")

        self.schema = schema
        self.naming = InterfaceNameMapper(schema.naming)
        self.inventory: DeviceInventory | None = None

    def set_inventory(self, inventory: DeviceInventory) -> None:
        self.inventory = inventory

    def generate(self, command: RuntimeCommand) -> str:
        templates = self.schema.runtime["templates"]

        if command.operation not in templates:
            return ""

        entry = templates[command.operation]
        template = entry["template"]
        if isinstance(template, list):
            template = "\n".join(template)

        values = {
            arg_name: self._resolve_argument(spec, command.arguments)
            for arg_name, spec in entry.get("arguments", {}).items()
        }

        return template.format(**values)

    def _resolve_argument(self, spec: dict, arguments: list[str]):
        source = spec["source"]

        if source == "arg0":
            raw = arguments[0]
        elif source == "all_args":
            raw = " ".join(arguments)
        else:
            raise ValueError(f"Unknown argument source: {source}")

        if spec.get("resolve") == "device_inventory_alias":
            return self._resolve_interface_alias(raw)

        return raw

    def _resolve_interface_alias(self, interface: str) -> str:
        if self.inventory is not None:
            discovered = self.inventory.find_interface(interface)
            if discovered is not None:
                return discovered.name

        return self.naming.convert(interface)
