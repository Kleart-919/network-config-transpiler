"""
Cisco runtime output generator.
"""

from configbridge.runtime.runtime_output import RuntimeOutput
from configbridge.schema.schema_model import NamingConvention
from configbridge.engine.naming import InterfaceNameMapper


class CiscoOutputGenerator:

    def __init__(self, naming: NamingConvention):
        self._naming = InterfaceNameMapper(naming)

    def generate(self, output: RuntimeOutput) -> str:

        if output.output_type != "interfaces":

            return output.rows[0]["text"]

        lines = []

        for row in output.rows:

            interface = self._naming.convert(row["interface"])

            lines.append(
                f"{interface:<28}"
                f"{row['admin']:<8}"
                f"{row['oper']}"
            )

        return "\n".join(lines)