from pathlib import Path

from configbridge.runtime.juniper_output_parser import (
    JuniperOutputParser,
)
from configbridge.runtime.cisco_output_generator import (
    CiscoOutputGenerator,
)

text = Path(
    "sample-configs/juniper/show_interfaces_terse.txt"
).read_text()

parser = JuniperOutputParser()

generator = CiscoOutputGenerator()

runtime = parser.parse(text)

print(generator.generate(runtime))