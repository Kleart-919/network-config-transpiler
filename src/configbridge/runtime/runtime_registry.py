"""
Runtime registry.

Provides runtime generators for connected vendors, wired to the
schema-driven generic runtime engine (schema/vendors/*.yaml via
SchemaLoader) instead of the legacy hardcoded runtime_generator.py /
runtime_templates.py.
"""

from configbridge.schema.loader import SchemaLoader
from configbridge.engine.generic_runtime_generator import GenericRuntimeGenerator

# vendor schema id -> display name (matches DeviceInventory.vendor /
# VendorManifest.name elsewhere in the app). Only vendors whose schema
# declares a runtime.templates section are targets a command can be
# generated FOR - see schema/vendors/juniper_junos.yaml's runtime section.
_RUNTIME_TARGET_VENDORS = {
    "juniper_junos": "Juniper Junos",
}


class RuntimeRegistry:

    def __init__(self):
        loader = SchemaLoader()

        self.generators = {
            display_name: GenericRuntimeGenerator(loader.load(vendor_id))
            for vendor_id, display_name in _RUNTIME_TARGET_VENDORS.items()
        }

    def get_generator(self, vendor):

        if vendor not in self.generators:
            raise ValueError(
                f"No runtime generator for {vendor}"
            )

        return self.generators[vendor]