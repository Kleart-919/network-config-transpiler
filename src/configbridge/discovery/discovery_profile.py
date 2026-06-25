"""
Discovery Profile

A Discovery Profile defines how a specific vendor exposes operational
information required by ConfigBridge.

The Discovery Manager does not know vendor commands. It asks the vendor's
Discovery Profile which commands to execute.
"""

from dataclasses import dataclass, field


@dataclass
class DiscoveryProfile:
    """
    Vendor discovery definition.

    Each supported vendor provides one DiscoveryProfile.
    """

    vendor_name: str

    commands: dict[str, str] = field(default_factory=dict)

    def get_command(self, capability: str) -> str | None:
        """
        Return the command required to discover a capability.

        Example:

        capability = "interfaces"

        Cisco -> show interfaces status

        Juniper -> show interfaces terse
        """

        return self.commands.get(capability)