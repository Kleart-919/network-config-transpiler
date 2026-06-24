from pathlib import Path

from configbridge.parsers.juniper_parser import JuniperParser
from configbridge.renderers.cisco_generator import CiscoGenerator


config_path = Path("sample-configs/juniper/basic_l2_config.txt")
config_text = config_path.read_text()

parser = JuniperParser()
intent = parser.parse(config_text)

generator = CiscoGenerator()
cisco_config = generator.generate(intent)

print(cisco_config)