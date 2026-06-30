"""
Runtime output model.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeOutput:

    output_type: str

    rows: list[dict] = field(default_factory=list)