from configbridge.models.device_inventory import (
    DeviceInventory,
    DiscoveredInterface,
)
from configbridge.models.interface_resolver import InterfaceResolver


inventory = DeviceInventory(
    hostname="EX-SW1",
    vendor="Juniper Junos",
    interfaces=[
        DiscoveredInterface(
            name="ge-0/0/1",
            aliases=[
                "GigabitEthernet0/0/1",
                "Gi0/0/1",
            ],
        )
    ],
)

resolver = InterfaceResolver(inventory)

print(resolver.resolve("Gi0/0/1"))
print(resolver.resolve("GigabitEthernet0/0/1"))
print(resolver.resolve("UnknownInterface1"))