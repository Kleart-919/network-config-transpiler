from pathlib import Path

from configbridge.parsers.juniper_parser import JuniperParser


config_path = Path("sample-configs/juniper/basic_l2_config.txt")
config_text = config_path.read_text()

parser = JuniperParser()
intent = parser.parse(config_text)

print(intent.to_dict())