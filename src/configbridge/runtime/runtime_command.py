"""
Runtime command model.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeCommand:
    """
    Represents a runtime CLI command.
    """

    verb: str

    resource: str

    qualifier: str | None = None

    arguments: list[str] = field(default_factory=list)