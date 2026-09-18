from pathlib import Path

from configbridge.schema.loader import SchemaLoader
from configbridge.engine.naming import unanchored_pattern
from configbridge.runtime.juniper_output_parser import (
    JuniperOutputParser,
)
from configbridge.runtime.cisco_output_generator import (
    CiscoOutputGenerator,
)

text = Path(
    "sample-configs/juniper/show_interfaces_terse.txt"
).read_text()

cisco_schema = SchemaLoader().load("cisco_ios")

parser = JuniperOutputParser(unanchored_pattern(cisco_schema.naming.recognizes[0].pattern))

generator = CiscoOutputGenerator(cisco_schema.naming)

runtime = parser.parse(text)

print(generator.generate(runtime))