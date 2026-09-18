"""
Juniper runtime output parser.
"""

import re

from configbridge.runtime.runtime_output import RuntimeOutput


class JuniperOutputParser:
    """
    interface_name_pattern: a regex fragment (no anchors) matching a native
    Juniper interface name, e.g. r"ge-\\d+/\\d+/\\d+". As of Phase 7 this is
    supplied by the caller from the schema data that already defines this
    shape (the pattern Cisco's naming_convention recognizes as a Juniper
    name - see runtime/runtime_engine.py's construction), rather than being
    hardcoded here a second time.
    """

    def __init__(self, interface_name_pattern: str):
        self._interface_regex = re.compile(
            rf"^({interface_name_pattern})\s+(\w+)\s+(\w+)"
        )

    def parse(self, text: str) -> RuntimeOutput:

        output = RuntimeOutput(
            output_type="raw"
        )

        interface_regex = self._interface_regex

        for line in text.splitlines():

            match = interface_regex.match(line)

            if match:

                output.output_type = "interfaces"

                output.rows.append(
                    {
                        "interface": match.group(1),
                        "admin": match.group(2),
                        "oper": match.group(3),
                    }
                )

        if output.rows:
            return output

        output.rows.append(
            {
                "text": text,
            }
        )

        return output