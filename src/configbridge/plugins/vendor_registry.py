"""
Vendor Registry

The Vendor Registry stores every supported network operating system.

Each vendor registers the components required by ConfigBridge.

Future vendor plugins simply register themselves here.
"""

from configbridge.plugins.vendor_manifest import VendorManifest
from configbridge.schema.loader import SchemaLoader
from configbridge.engine.generic_parser import GenericConfigParser
from configbridge.engine.generic_generator import GenericConfigGenerator

# vendor schema id -> display name, as registered elsewhere in the app
# (VendorManifest.name / VendorRegistry keys, e.g. discovery profiles,
# DeviceInventory.vendor).
_SCHEMA_VENDORS = {
    "cisco_ios": "Cisco IOS",
    "juniper_junos": "Juniper Junos",
}


class VendorRegistry:
    """
    Stores all supported vendors.
    """

    def __init__(self):
        self._vendors = {}

    def register(self, vendor: VendorManifest):
        """
        Register a supported vendor.
        """

        self._vendors[vendor.name.lower()] = vendor

    def get_vendor(self, vendor_name: str) -> VendorManifest:
        """
        Return a registered vendor.
        """

        key = vendor_name.lower()

        if key not in self._vendors:
            raise ValueError(f"Vendor '{vendor_name}' is not registered.")

        return self._vendors[key]

    def supported_vendors(self) -> list[str]:
        """
        Return registered vendor names.
        """

        return sorted(self._vendors.keys())


def build_default_registry() -> VendorRegistry:
    """
    Build the standard VendorRegistry with every vendor's
    configuration_parser/configuration_generator wired to the schema-driven
    generic engine (schema/vendors/*.yaml via SchemaLoader) instead of the
    legacy hand-written per-vendor parser/generator classes.

    discovery_profile/discovery_parser are left unset (None) here -
    discovery is a separate subsystem (discovery/) with its own vendor
    wiring, out of scope for this schema migration. Callers that need
    discovery too should set those fields on the returned manifests.
    """

    loader = SchemaLoader()
    registry = VendorRegistry()

    for vendor_id, display_name in _SCHEMA_VENDORS.items():
        schema = loader.load(vendor_id)

        registry.register(
            VendorManifest(
                name=display_name,
                discovery_profile=None,
                discovery_parser=None,
                configuration_parser=GenericConfigParser(schema),
                configuration_generator=GenericConfigGenerator(schema),
            )
        )

    return registry