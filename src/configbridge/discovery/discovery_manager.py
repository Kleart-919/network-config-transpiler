"""
Discovery Manager

Coordinates discovery of connected network devices.
"""

from configbridge.discovery.command_executor import CommandExecutor
from configbridge.models.device_inventory import DeviceInventory
from configbridge.plugins.vendor_manifest import VendorManifest


class DiscoveryManager:
    """
    Coordinates discovery of a connected device.
    """

    def __init__(self, session_manager):
        self.executor = CommandExecutor(session_manager)

    def discover(
        self,
        vendor: VendorManifest,
        hostname: str | None = None,
    ) -> DeviceInventory:

        inventory = DeviceInventory(
            hostname=hostname,
            vendor=vendor.name,
        )

        profile = vendor.discovery_profile
        parser = vendor.discovery_parser

        # Iterate over every capability supported by the vendor profile.
        for capability, command in profile.commands.items():

            output = self.executor.execute(command)
            print("\n========== RAW DISCOVERY OUTPUT ==========\n")
            print(output)
            print("\n==========================================\n")
            

            # Dispatch to the appropriate parser method.
            parser_method = getattr(
                parser,
                f"parse_{capability}",
                None,
            )

            if parser_method is None:
                continue

            discovered_inventory = parser_method(
                output,
                hostname=hostname,
            )

            inventory.interfaces.extend(
                discovered_inventory.interfaces
            )

        return inventory