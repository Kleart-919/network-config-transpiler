"""
Runtime registry.

Provides runtime generators for connected vendors.
"""

from configbridge.runtime.runtime_generator import RuntimeGenerator


class RuntimeRegistry:

    def __init__(self):

        self.generators = {

            "Juniper Junos": RuntimeGenerator(),

        }

    def get_generator(self, vendor):

        if vendor not in self.generators:
            raise ValueError(
                f"No runtime generator for {vendor}"
            )

        return self.generators[vendor]