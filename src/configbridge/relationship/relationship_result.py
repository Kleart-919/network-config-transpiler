"""
Relationship Result

Represents one inferred relationship between two network objects.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class RelationshipResult:
    """
    One inferred relationship.
    """

    source_object: str

    target_object: str

    confidence: float

    matched_attributes: list[str] = field(default_factory=list)