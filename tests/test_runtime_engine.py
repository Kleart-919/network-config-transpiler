from configbridge.models.device_inventory import (
    DeviceInventory,
    DiscoveredInterface,
)
from configbridge.runtime.runtime_engine import RuntimeEngine

engine = RuntimeEngine()

inventory = DeviceInventory(
    hostname="Juniper",
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

engine.set_inventory(inventory)

commands = [
    "configure terminal",
    "interface GigabitEthernet0/0/1",
    "show interfaces status",
    "show vlan brief",
]

for command in commands:
    print()
    print(command)
    print("↓")
    print(engine.translate(command))