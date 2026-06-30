"""
Output virtualizer.

Rewrites connected-device output into the selected CLI style.
"""

import re


class OutputVirtualizer:
    """
    Converts vendor-native output into preferred CLI output.
    """

    def virtualize(
        self,
        text: str,
        cli_mode: str,
        connected_vendor: str,
    ) -> str:
        if cli_mode == "Cisco IOS" and connected_vendor == "Juniper Junos":
            return self._juniper_to_cisco_interfaces(text)

        return text

    def _juniper_to_cisco_interfaces(self, text: str) -> str:
        """
        Convert Juniper ge-x/y/z names to Cisco-style GigabitEthernetx/y/z.
        """

        return re.sub(
            r"\bge-(\d+)/(\d+)/(\d+)\b",
            r"GigabitEthernet\1/\2/\3",
            text,
        )