from configbridge.models.device_inventory import (
    DeviceInventory,
    DiscoveredInterface,
)


inventory = DeviceInventory(
    hostname="EX-SW1",
    vendor="Juniper Junos",
    interfaces=[
        DiscoveredInterface(
            name="ge-0/0/1",
            description="User Access Port",
            status="up",
            speed="1g",
            mode="access",
            access_vlan=10,
            aliases=[
                "GigabitEthernet0/0/1",
                "Gi0/0/1",
            ],
        )
    ],
)

print(inventory.to_dict())

resolved = inventory.find_interface("Gi0/0/1")

if resolved:
    print(f"Resolved alias Gi0/0/1 to real interface {resolved.name}")
else:
    print("Interface not found")