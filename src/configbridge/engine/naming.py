"""
Static interface-name conversion driven by a vendor's naming_convention
schema data.

Replaces CiscoGenerator.map_interface_name / JuniperGenerator.map_interface_name
(both hardcoded, single-direction, and buggy - see the vendor YAML comments
for the specific bug being deliberately preserved here for Phase 1-3
parity). This is purely a static/algorithmic fallback with no live device
knowledge; where a DeviceInventory with discovered aliases is available
(the runtime pipeline, from Phase 7 onward), alias lookup takes precedence
over this.
"""

import re

from configbridge.schema.schema_model import NamingConvention


_NAMED_GROUP_RE = re.compile(r"\(\?P<\w+>")


def unanchored_pattern(pattern: str) -> str:
    """
    Prepare a naming_convention regex for embedding inside a larger
    pattern: strip the leading '^'/trailing '$' anchors, and turn its named
    capture groups into non-capturing groups so they don't shift the
    numbered group indices the embedding caller relies on
    (match.group(2)/group(3) etc for its own captures).
    """

    unanchored = pattern.removeprefix("^").removesuffix("$")
    return _NAMED_GROUP_RE.sub("(?:", unanchored)


class InterfaceNameMapper:
    def __init__(self, naming: NamingConvention):
        self._compiled = [(re.compile(r.pattern), r.render) for r in naming.recognizes]

    def convert(self, interface_name: str) -> str:
        for pattern, render in self._compiled:
            match = pattern.match(interface_name)
            if match:
                return render.format(**match.groupdict())

        return interface_name
