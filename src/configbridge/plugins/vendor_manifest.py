"""
Vendor Manifest

A VendorManifest describes everything ConfigBridge needs to know about a
supported network operating system.

It contains references to the vendor's discovery profile, discovery parser,
configuration parser and configuration generator.

The manifest itself contains no logic.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class VendorManifest:
    """
    Describes one supported vendor.
    """

    name: str

    discovery_profile: Any
    discovery_parser: Any

    configuration_parser: Any
    configuration_generator: Any

    metadata: dict[str, Any] | None = None