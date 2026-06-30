"""
Generic runtime parser.
"""

from configbridge.runtime.runtime_command import RuntimeCommand


class RuntimeParser:

    def parse(self, command: str) -> RuntimeCommand | None:
        command = command.strip()

        if not command:
            return None

        lowered = command.lower()

        if lowered in ("configure terminal", "conf t", "configure"):
            return RuntimeCommand(
                verb="configure",
                resource="terminal",
                configuration_mode=True,
            )

        if lowered.startswith("interface ") or lowered.startswith("int "):
            interface = command.split(maxsplit=1)[1]

            return RuntimeCommand(
                verb="interface",
                resource="interface",
                arguments=[interface],
                configuration_mode=True,
            )

        tokens = lowered.split()

        if len(tokens) < 2:
            return None

        verb = tokens[0]
        resource = tokens[1]
        qualifier = tokens[2] if len(tokens) >= 3 else None
        arguments = tokens[3:] if len(tokens) > 3 else []

        return RuntimeCommand(
            verb=verb,
            resource=resource,
            qualifier=qualifier,
            arguments=arguments,
        )