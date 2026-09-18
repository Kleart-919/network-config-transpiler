"""
Vendor schema data model.

A VendorSchema is the single declarative source of truth for one vendor's
config syntax: how to recognize it (parsing), how to emit it (rendering),
and how its interface-naming convention works. It is consumed by the
generic batch engine (engine/generic_parser.py, generic_generator.py,
built in Phase 2/3) and, once extended with a `runtime` section (Phase 5),
the generic runtime engine.

Concept internals (`VendorSchema.concepts`) are kept as validated plain
dicts rather than a deep dataclass tree: Cisco's block/regex-style syntax
and Juniper's flat/token-style syntax shape their concepts differently
enough that a single rigid dataclass would either force one style onto the
other or duplicate itself per style. The YAML shape itself is the schema of
the schema; SchemaLoader validates structurally against it.
"""

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class NamingRecognizer:
    """
    One rule for recognizing a foreign vendor's interface name and
    re-rendering it in this vendor's own style.

    `pattern` is a regex with named capture groups; `render` is a
    str.format template using those group names. Mirrors today's
    map_interface_name() behavior exactly, quirks included (see
    naming_convention.md notes in the vendor YAML comments) - it is
    deliberately NOT a full bidirectional slot/module/port model.
    """

    pattern: str
    render: str


@dataclass
class NamingConvention:
    """
    A vendor's interface-naming rules. `recognizes` is checked in order;
    the first matching pattern's render template produces the name. A name
    matching none of them passes through unchanged (today's silent no-op
    fallback).
    """

    recognizes: list[NamingRecognizer] = field(default_factory=list)


@dataclass
class VendorSchema:
    """
    One vendor's complete declarative syntax definition.
    """

    vendor_id: str
    display_name: str
    tokenizer_style: Literal["block", "token"]
    naming: NamingConvention
    concepts: dict[str, dict[str, Any]]
    runtime: dict[str, Any] | None = None
