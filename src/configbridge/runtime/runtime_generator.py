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
            command.verb == "show"
            and command.resource == "version"
        ):
            return "show version"

        #
        # show interfaces status
        #

        if (
            command.verb == "show"
            and command.resource == "interfaces"
            and command.qualifier == "status"
        ):
            return "show interfaces terse"

        #
        # show vlan brief
        #

        if (
            command.verb == "show"
            and command.resource == "vlan"
            and command.qualifier == "brief"
        ):
            return "show vlans"

        return " ".join(
            filter(
                None,
                [
                    command.verb,
                    command.resource,
                    command.qualifier,
                    *command.arguments,
                ],
            )
        )