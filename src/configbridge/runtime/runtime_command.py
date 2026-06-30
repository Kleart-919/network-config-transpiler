"""
Runtime command model.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeCommand:

    verb: str

    resource: str

    qualifier: str | None = None

    arguments: list[str] = field(default_factory=list)

    configuration_mode: bool = False