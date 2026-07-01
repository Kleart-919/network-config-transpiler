"""
Runtime command model.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeCommand:

    operation: str

    arguments: list[str] = field(default_factory=list)

    mode_change: str | None = None