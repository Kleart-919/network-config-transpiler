"""
Generic runtime parser.
"""

from configbridge.runtime.runtime_command import RuntimeCommand


class RuntimeParser:

    def parse(self, command: str) -> RuntimeCommand | None:

        tokens = command.lower().strip().split()

        if len(tokens) < 2:
            return None

        verb = tokens[0]

        resource = tokens[1]

        qualifier = None

        arguments = []

        if len(tokens) >= 3:
            qualifier = tokens[2]

        if len(tokens) > 3:
            arguments = tokens[3:]

        return RuntimeCommand(
            verb=verb,
            resource=resource,
            qualifier=qualifier,
            arguments=arguments,
        )