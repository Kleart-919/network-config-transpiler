"""
Runtime command model.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeCommand:

    action: str

    resource: str

    operation: str | None = None

    arguments: list[str] = field(default_factory=list)