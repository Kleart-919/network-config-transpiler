"""
Shared value-template mechanics used by both the generic parser and the
generic generator: parsing "{name}" / "{name:transform}" placeholders and
applying the small fixed set of transforms the schema format supports.

This is the one place the two known cross-vendor VLAN-reference semantics
(Cisco: by numeric id: Juniper: by name, resolved via the VLAN list) become
shared, generic code rather than vendor-specific Python - see vlan_name /
vlan_names_space below.
"""

import re

_PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z_]+))?\}")
_WHOLE_PLACEHOLDER_RE = re.compile(r"^\{([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z_]+))?\}$")


def coerce_set_value(transform: str | None, raw: str):
    """Apply a parse-side transform to a captured raw string."""

    if transform is None:
        return raw
    if transform == "int":
        return int(raw)
    if transform == "int_csv":
        return [int(part.strip()) for part in raw.split(",")]
    if transform == "bracket_list":
        return [part for part in raw.split() if part not in ("[", "]")]
    raise ValueError(f"Unknown set transform: {transform}")


def apply_set_template(template: str, captures: dict) -> object:
    """
    Resolve a 'set' value template against captured values.

    A set template is always either a literal constant (no placeholder,
    e.g. "access") or a single whole-string placeholder (e.g. "{value}",
    "{vlan_id:int}") - never a mix of literal text and a placeholder.
    """

    match = _WHOLE_PLACEHOLDER_RE.match(template)
    if match is None:
        return template

    name, transform = match.groups()
    return coerce_set_value(transform, captures[name])


def find_vlan(intent, vlan_id: int):
    for vlan in intent.vlans:
        if vlan.vlan_id == vlan_id:
            return vlan
    return None


def vlan_name(intent, vlan_id: int) -> str:
    """Resolve a numeric VLAN id to its name, synthesizing one if unnamed/unknown."""

    vlan = find_vlan(intent, vlan_id)
    if vlan is not None and vlan.name:
        return vlan.name
    return f"VLAN_{vlan_id}"


def render_value(name: str, transform: str | None, context: dict, intent=None):
    """Resolve one placeholder's value for a render template, applying a render-side transform."""

    value = context.get(name)

    if transform is None:
        return "" if value is None else value
    if transform == "int_csv":
        return ",".join(str(v) for v in value)
    if transform == "vlan_name":
        return vlan_name(intent, value)
    if transform == "vlan_names_space":
        return " ".join(vlan_name(intent, v) for v in value)
    raise ValueError(f"Unknown render transform: {transform}")


def render_template(template: str, context: dict, intent=None) -> str:
    """Substitute every '{name}' / '{name:transform}' placeholder in a render template."""

    def substitute(match: re.Match) -> str:
        name, transform = match.groups()
        return str(render_value(name, transform, context, intent))

    return _PLACEHOLDER_RE.sub(substitute, template)


def when_matches(when, context: dict) -> bool:
    """
    Evaluate a render/resolve 'when' - a single condition or a list of
    conditions ANDed together. Each condition is a bare field name (truthy
    check) or 'field:value' (equality check against str(value)).
    """

    conditions = when if isinstance(when, list) else [when]

    for condition in conditions:
        if condition == "always":
            continue
        if ":" in condition:
            field, expected = condition.split(":", 1)
            if str(context.get(field)) != expected:
                return False
        else:
            if not context.get(condition):
                return False

    return True
