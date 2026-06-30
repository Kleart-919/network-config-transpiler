"""
Cisco runtime output generator.
"""

from configbridge.runtime.runtime_output import RuntimeOutput


class CiscoOutputGenerator:

    def generate(self, output: RuntimeOutput) -> str:

        if output.output_type != "interfaces":

            return output.rows[0]["text"]

        lines = []

        for row in output.rows:

            interface = row["interface"]

            interface = interface.replace(
                "ge-",
                "GigabitEthernet",
            )

            lines.append(
                f"{interface:<28}"
                f"{row['admin']:<8}"
                f"{row['oper']}"
            )

        return "\n".join(lines)