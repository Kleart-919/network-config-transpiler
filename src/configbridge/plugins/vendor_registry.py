"""
Vendor Registry

The Vendor Registry stores every supported network operating system.

Each vendor registers the components required by ConfigBridge.

Future vendor plugins simply register themselves here.
"""

from dataclasses import dataclass
from typing import Any
from configbridge.plugins.vendor_manifest import VendorManifest

@dataclass
class VendorManifest:
    """
    Represents one supported vendor.
    """

    name: str

    discovery_profile: Any = None
    discovery_parser: Any = None

    configuration_parser: Any = None
    configuration_generator: Any = None

    metadata: dict | None = None


class VendorRegistry:
    """
    Stores all supported vendors.
    """

    def __init__(self):
        self._vendors = {}

    def register(self, vendor: VendorManifest):
        """
        Register a supported vendor.
        """

        self._vendors[vendor.name.lower()] = vendor

    def get_vendor(self, vendor_name: str) -> VendorManifest:
        """
        Return a registered vendor.
        """

        key = vendor_name.lower()

        if key not in self._vendors:
            raise ValueError(f"Vendor '{vendor_name}' is not registered.")

        return self._vendors[key]

    def supported_vendors(self) -> list[str]:
        """
        Return registered vendor names.
        """

        return sorted(self._vendors.keys())