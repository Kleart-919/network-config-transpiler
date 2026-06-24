from pathlib import Path

from configbridge.parsers.cisco_parser import CiscoParser
from configbridge.renderers.juniper_generator import JuniperGenerator


config_path = Path("sample-configs/cisco/basic_l2_config.txt")
config_text = config_path.read_text()

parser = CiscoParser()
intent = parser.parse(config_text)

generator = JuniperGenerator()
juniper_config = generator.generate(intent)

print(juniper_config)