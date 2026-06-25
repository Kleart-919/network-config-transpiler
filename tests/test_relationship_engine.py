from configbridge.models.device_inventory import (
    DeviceInventory,
    DiscoveredInterface,
)
from configbridge.relationship.relationship_engine import (
    RelationshipEngine,
)

source = DeviceInventory(
    hostname="Cisco",
    vendor="Cisco IOS",
    interfaces=[
        DiscoveredInterface(
            name="GigabitEthernet0/0/1",
        ),
        DiscoveredInterface(
            name="GigabitEthernet0/0/2",
        ),
    ],
)

destination = DeviceInventory(
    hostname="Juniper",
    vendor="Juniper Junos",
    interfaces=[
        DiscoveredInterface(
            name="ge-0/0/1",
            aliases=[
                "GigabitEthernet0/0/1",
                "Gi0/0/1",
            ],
        ),
        DiscoveredInterface(
            name="ge-0/0/2",
            aliases=[
                "GigabitEthernet0/0/2",
                "Gi0/0/2",
            ],
        ),
    ],
)

engine = RelationshipEngine()

relationships = engine.resolve(
    source,
    destination,
)

for relationship in relationships:

    print()

    print("Source:", relationship.source_object)

    print("Target:", relationship.target_object)

    print("Confidence:", relationship.confidence)

    print("Matched:", relationship.matched_attributes)