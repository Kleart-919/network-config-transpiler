from pathlib import Path

from configbridge.discovery.discovery_manager import DiscoveryManager
from configbridge.discovery.discovery_profile import DiscoveryProfile
from configbridge.parsers.juniper_discovery_parser import (
    JuniperDiscoveryParser,
)
from configbridge.plugins.vendor_registry import build_default_registry
from configbridge.transpiler.transpilation_engine import (
    TranspilationEngine,
)


def dummy_runner(command: str) -> str:
    return ""


# configuration_parser/configuration_generator come from the schema-driven
# generic engine (see plugins/vendor_registry.build_default_registry).
# Discovery wiring is a separate concern, added here on top.
registry = build_default_registry()

registry.get_vendor("Cisco IOS").discovery_profile = DiscoveryProfile(
    vendor_name="Cisco IOS",
    commands={},
)

juniper = registry.get_vendor("Juniper Junos")
juniper.discovery_profile = DiscoveryProfile(
    vendor_name="Juniper Junos",
    commands={
        "interfaces": "show interfaces terse",
    },
)
juniper.discovery_parser = JuniperDiscoveryParser()

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