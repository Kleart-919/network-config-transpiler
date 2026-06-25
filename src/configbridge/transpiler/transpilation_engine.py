"""
Transpilation Engine

The Transpilation Engine coordinates the complete transpilation workflow.

It does not contain vendor-specific logic.

Instead, it orchestrates:

- Vendor lookup
- Discovery
- Parsing
- Relationship resolution
- Configuration generation
"""
from configbridge.relationship.relationship_engine import (
    RelationshipEngine,
)
from configbridge.discovery.discovery_manager import DiscoveryManager
from configbridge.plugins.vendor_registry import VendorRegistry


class TranspilationEngine:
    """
    Main orchestration component.
    """

    def __init__(
        self,
        registry: VendorRegistry,
        discovery_manager: DiscoveryManager,
    ):

        self.registry = registry

        self.discovery_manager = discovery_manager

        self.relationship_engine = RelationshipEngine()

    def discover(
        self,
        vendor_name: str,
        hostname: str,
    ):
        """
        Build a DeviceInventory for the connected device.
        """

        vendor = self.registry.get_vendor(vendor_name)

        return self.discovery_manager.discover(
            vendor=vendor,
            hostname=hostname,
        )

    def transpile(
        self,
        source_vendor: str,
        target_vendor: str,
        config_text: str,
        source_inventory=None,
        destination_inventory=None,
    ) -> str:
        """
        Execute the complete transpilation workflow.
        """

        source = self.registry.get_vendor(source_vendor)

        target = self.registry.get_vendor(target_vendor)

        intent = source.configuration_parser.parse(
            config_text
        )

        #
        # Relationship Resolution
        #
        if (
            source_inventory is not None
            and destination_inventory is not None
        ):

            relationships = self.relationship_engine.resolve(
                source_inventory,
                destination_inventory,
            )

            print("\n===== RELATIONSHIPS =====")

            for relationship in relationships:

                print(
                    relationship
                )

            print("=========================\n")

        return target.configuration_generator.generate(
            intent
        )