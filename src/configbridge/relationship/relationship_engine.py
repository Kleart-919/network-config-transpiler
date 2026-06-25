"""
Relationship Engine

Infers relationships between network objects.
"""

from configbridge.models.device_inventory import DeviceInventory
from configbridge.relationship.relationship_result import RelationshipResult
from configbridge.relationship.relationship_weights import (
    RelationshipWeights,
)


class RelationshipEngine:

    def __init__(self):
        self.weights = RelationshipWeights()

    def resolve(
        self,
        source: DeviceInventory,
        destination: DeviceInventory,
    ) -> list[RelationshipResult]:
        """
        Resolve relationships between discovered network objects.

        Version 1:
        Alias matching.

        Future versions:
        Description
        VLANs
        LLDP
        CDP
        Speed
        Topology
        """

        results = []

        for source_object in source.interfaces:

            for destination_object in destination.interfaces:

                score = 0
                matched = []

                if (
                    source_object.name
                    in destination_object.aliases
                ):
                    score += self.weights.maximum
                    matched.append("alias")

                if score == 0:
                    continue

                confidence = (
                    score
                    / self.weights.maximum
                ) * 100

                results.append(
                    RelationshipResult(
                        source_object=source_object.name,
                        target_object=destination_object.name,
                        confidence=confidence,
                        matched_attributes=matched,
                    )
                )

        return sorted(
            results,
            key=lambda relationship: relationship.confidence,
            reverse=True,
        )