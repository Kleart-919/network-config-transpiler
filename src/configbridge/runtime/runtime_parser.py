"""
Cisco runtime parser.

Parses user CLI into RuntimeCommand.
"""

from configbridge.runtime.runtime_command import RuntimeCommand


class RuntimeParser:

    def parse(self, command: str) -> RuntimeCommand | None:

        tokens = command.strip().split()

        if not tokens:
            return None

        #
        # show version
        #

        if tokens == ["show", "version"]:

            return RuntimeCommand(

                action="show",

                resource="system",

                operation="version",

            )

        #
        # show interfaces status
        #

        if tokens == ["show", "interfaces", "status"]:

            return RuntimeCommand(

                action="show",

                resource="interfaces",

                operation="status",

            )

        #
        # show vlan brief
        #

        if tokens == ["show", "vlan", "brief"]:

            return RuntimeCommand(

                action="show",

                resource="vlans",

                operation="brief",

            )

        return None