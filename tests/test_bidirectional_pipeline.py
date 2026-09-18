from pathlib import Path

from configbridge.schema.loader import SchemaLoader
from configbridge.engine.generic_parser import GenericConfigParser
from configbridge.engine.generic_generator import GenericConfigGenerator

loader = SchemaLoader()
cisco_schema = loader.load("cisco_ios")
juniper_schema = loader.load("juniper_junos")

print("=" * 70)
print("Cisco IOS -> Intent Model -> Juniper Junos")
print("=" * 70)

cisco_config = Path("sample-configs/cisco/basic_l2_config.txt").read_text()

cisco_parser = GenericConfigParser(cisco_schema)
cisco_intent = cisco_parser.parse(cisco_config)

juniper_generator = GenericConfigGenerator(juniper_schema)
juniper_output = juniper_generator.generate(cisco_intent)

print(juniper_output)


print("=" * 70)
print("Juniper Junos -> Intent Model -> Cisco IOS")
print("=" * 70)

juniper_config = Path("sample-configs/juniper/basic_l2_config.txt").read_text()

juniper_parser = GenericConfigParser(juniper_schema)
juniper_intent = juniper_parser.parse(juniper_config)

cisco_generator = GenericConfigGenerator(cisco_schema)
cisco_output = cisco_generator.generate(juniper_intent)

print(cisco_output)