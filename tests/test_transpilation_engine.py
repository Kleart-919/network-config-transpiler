from pathlib import Path

from configbridge.discovery.discovery_manager import DiscoveryManager
from configbridge.discovery.discovery_profile import DiscoveryProfile
from configbridge.parsers.cisco_parser import CiscoParser
from configbridge.parsers.juniper_discovery_parser import (
    JuniperDiscoveryParser,
)
from configbridge.renderers.juniper_generator import (
    JuniperGenerator,
)
from configbridge.plugins.vendor_manifest import VendorManifest
from configbridge.plugins.vendor_registry import VendorRegistry
from configbridge.transpiler.transpilation_engine import (
    TranspilationEngine,
)


def dummy_runner(command: str) -> str:
    return ""


registry = VendorRegistry()

registry.register(
    VendorManifest(
        name="Cisco IOS",
        discovery_profile=DiscoveryProfile(
            vendor_name="Cisco IOS",
            commands={},
        ),
        discovery_parser=None,
        configuration_parser=CiscoParser(),
        configuration_generator=None,
    )
)

registry.register(
    VendorManifest(
        name="Juniper Junos",
        discovery_profile=DiscoveryProfile(
            vendor_name="Juniper Junos",
            commands={
                "interfaces": "show interfaces terse",
            },
        ),
        discovery_parser=JuniperDiscoveryParser(),
        configuration_parser=None,
        configuration_generator=JuniperGenerator(),
    )
)

engine = TranspilationEngine(
    registry=registry,
    discovery_manager=DiscoveryManager(
        dummy_runner,
    ),
)

config = Path(
    "sample-configs/cisco/basic_l2_config.txt"
).read_text()

from configbridge.models.device_inventory import (
    DeviceInventory,
    DiscoveredInterface,
)

source_inventory = DeviceInventory(
    hostname="Cisco",
    vendor="Cisco IOS",
    interfaces=[
        DiscoveredInterface(
            name="GigabitEthernet0/0/1",
        ),
    ],
)

destination_inventory = DeviceInventory(
    hostname="Juniper",
    vendor="Juniper Junos",
    interfaces=[
        DiscoveredInterface(
            name="ge-0/0/1",
            aliases=[
                "GigabitEthernet0/0/1",
            ],
        ),
    ],
)

output = engine.transpile(
    source_vendor="Cisco IOS",
    target_vendor="Juniper Junos",
    config_text=config,
    source_inventory=source_inventory,
    destination_inventory=destination_inventory,
)

print(output)