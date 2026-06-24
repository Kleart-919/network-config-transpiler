from pathlib import Path

from configbridge.parsers.cisco_parser import CiscoParser
from configbridge.parsers.juniper_parser import JuniperParser
from configbridge.renderers.cisco_generator import CiscoGenerator
from configbridge.renderers.juniper_generator import JuniperGenerator


print("=" * 70)
print("Cisco IOS -> Intent Model -> Juniper Junos")
print("=" * 70)

cisco_config = Path("sample-configs/cisco/basic_l2_config.txt").read_text()

cisco_parser = CiscoParser()
cisco_intent = cisco_parser.parse(cisco_config)

juniper_generator = JuniperGenerator()
juniper_output = juniper_generator.generate(cisco_intent)

print(juniper_output)


print("=" * 70)
print("Juniper Junos -> Intent Model -> Cisco IOS")
print("=" * 70)

juniper_config = Path("sample-configs/juniper/basic_l2_config.txt").read_text()

juniper_parser = JuniperParser()
juniper_intent = juniper_parser.parse(juniper_config)

cisco_generator = CiscoGenerator()
cisco_output = cisco_generator.generate(juniper_intent)

print(cisco_output)