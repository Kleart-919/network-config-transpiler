from pathlib import Path

from configbridge.parsers.cisco_parser import CiscoParser


sample_dir = Path("sample-configs/cisco")
parser = CiscoParser()

for config_file in sample_dir.glob("*.txt"):
    print("=" * 70)
    print(f"Testing: {config_file}")

    config_text = config_file.read_text()
    intent = parser.parse(config_text)

    print(intent.to_dict())
    print()