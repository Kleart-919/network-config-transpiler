from configbridge.plugins.vendor_manifest import VendorManifest
from configbridge.plugins.vendor_registry import VendorRegistry

registry = VendorRegistry()

registry.register(
    VendorManifest(
        name="Cisco IOS",
        discovery_profile=None,
        discovery_parser=None,
        configuration_parser=None,
        configuration_generator=None,
    )
)

registry.register(
    VendorManifest(
        name="Juniper Junos",
        discovery_profile=None,
        discovery_parser=None,
        configuration_parser=None,
        configuration_generator=None,
    )
)

print("Supported vendors:")
print(registry.supported_vendors())

vendor = registry.get_vendor("Cisco IOS")

print("\nRetrieved Vendor:")
print(vendor.name)