"""
Juniper runtime output parser.
"""

import re

from configbridge.runtime.runtime_output import RuntimeOutput


class JuniperOutputParser:

    def parse(self, text: str) -> RuntimeOutput:

        output = RuntimeOutput(
            output_type="raw"
        )

        interface_regex = re.compile(
            r"^(ge-\d+/\d+/\d+)\s+(\w+)\s+(\w+)"
        )

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