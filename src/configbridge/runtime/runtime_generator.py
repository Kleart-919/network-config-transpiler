"""
Juniper runtime generator.
"""

from configbridge.runtime.runtime_command import RuntimeCommand


class RuntimeGenerator:

    def generate(self, command: RuntimeCommand) -> str:

        #
        # show version
        #

        if (
            command.action == "show"
            and command.resource == "system"
            and command.operation == "version"
        ):
            return "show version"

        #
        # show interfaces status
        #

        if (
            command.action == "show"
            and command.resource == "interfaces"
            and command.operation == "status"
        ):
            return "show interfaces terse"

        #
        # show vlan brief
        #

        if (
            command.action == "show"
            and command.resource == "vlans"
            and command.operation == "brief"
        ):
            return "show vlans"

        return ""