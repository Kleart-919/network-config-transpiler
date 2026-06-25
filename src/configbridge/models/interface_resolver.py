"""
Interface Resolver

Resolves user-facing or source-vendor interface names into the real interface
name used by the target connected device.

Example:
    Cisco CLI mode input: Gi0/0/1
    Real Juniper interface: ge-0/0/1
"""

from typing import Optional

from configbridge.models.device_inventory import DeviceInventory


class InterfaceResolver:
    """
    Resolves interface names using discovered device inventory data.
    """

    def __init__(self, inventory: Optional[DeviceInventory] = None):
        self.inventory = inventory

    def resolve(self, interface_name: str) -> str:
        """
        Return the real target-device interface name.

        If inventory exists and the interface or alias is found, return the
        discovered real interface name.

        If no match is found, return the original interface name.
        """

        if self.inventory is None:
            return interface_name

        discovered_interface = self.inventory.find_interface(interface_name)

        if discovered_interface is None:
            return interface_name

        return discovered_interface.name