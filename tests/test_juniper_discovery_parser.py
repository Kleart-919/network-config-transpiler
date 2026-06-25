from pathlib import Path

from configbridge.parsers.juniper_discovery_parser import JuniperDiscoveryParser
from configbridge.models.interface_resolver import InterfaceResolver


output_path = Path("sample-configs/juniper/show_interfaces_terse.txt")
output_text = output_path.read_text()

parser = JuniperDiscoveryParser()
inventory = parser.parse_interfaces(
    output_text,
    hostname="EX-SW1",
)

print(inventory.to_dict())

resolver = InterfaceResolver(inventory)

print("Gi0/0/1 resolves to:", resolver.resolve("Gi0/0/1"))
print("GigabitEthernet0/0/2 resolves to:", resolver.resolve("GigabitEthernet0/0/2"))