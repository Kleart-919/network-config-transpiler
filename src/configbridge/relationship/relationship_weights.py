"""
Relationship Weights

Defines how much evidence contributes towards relationship confidence.

The weights are intentionally separated from the algorithm so they can be
adjusted later without changing the Relationship Engine.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class RelationshipWeights:

    description: int = 40

    vlan_membership: int = 20

    mode: int = 20

    status: int = 10

    speed: int = 10

    @property
    def maximum(self) -> int:
        return (
            self.description
            + self.vlan_membership
            + self.mode
            + self.status
            + self.speed
        )