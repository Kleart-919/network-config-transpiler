from configbridge.plugins.vendor_registry import (
    VendorPlugin,
    VendorRegistry,
)

registry = VendorRegistry()

registry.register(
    VendorPlugin(
        name="Cisco IOS",
    )
)

registry.register(
    VendorPlugin(
        name="Juniper Junos",
    )
)

print("Supported vendors:")
print(registry.supported_vendors())

vendor = registry.get_vendor("Cisco IOS")

print("\nRetrieved Vendor:")
print(vendor.name)