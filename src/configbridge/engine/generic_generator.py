"""
Generic, schema-driven batch config generator.

Replaces renderers/cisco_generator.py and renderers/juniper_generator.py
with one class parameterized by a VendorSchema. The overall structural
skeleton (hostname, then all VLAN blocks, then each interface block with a
trailing blank line) is intentionally NOT schema data - research on the
current hand-written generators showed this shape is identical between
Cisco and Juniper (Juniper's generator already proves it by running
entirely off plugins/vendor_templates.py with the same control flow as
Cisco's inline f-strings), so it's kept as shared engine code rather than
duplicated per-vendor data.
"""

from configbridge.models.intent_model import IntentModel
from configbridge.schema.schema_model import VendorSchema
from configbridge.engine.naming import InterfaceNameMapper
from configbridge.engine.value_templates import render_template, when_matches


class GenericConfigGenerator:
    def __init__(self, schema: VendorSchema):
        self.schema = schema
        self.naming = InterfaceNameMapper(schema.naming)

    def generate(self, intent: IntentModel) -> str:
        lines: list[str] = []

        self._render_hostname(intent, lines)
        self._render_vlans(intent, lines)
        self._render_interfaces(intent, lines)

        return "\n".join(lines).strip() + "\n"

    def _render_hostname(self, intent: IntentModel, lines: list[str]) -> None:
        concept = self.schema.concepts.get("hostname")
        if not concept or not intent.hostname:
            return

        lines.append(render_template(concept["render"], {"hostname": intent.hostname}))
        lines.append("")

    def _render_vlans(self, intent: IntentModel, lines: list[str]) -> None:
        concept = self.schema.concepts.get("vlan")
        if not concept:
            return

        for vlan in intent.vlans:
            context = {"vlan_id": vlan.vlan_id, "name": vlan.name}
            self._apply_render_defaults(concept, context)
            self._render_block(concept, context, lines, intent)

        if intent.vlans:
            lines.append("")

    def _render_interfaces(self, intent: IntentModel, lines: list[str]) -> None:
        concept = self.schema.concepts.get("interface")
        if not concept:
            return

        for interface in intent.interfaces:
            context = {
                "name": self.naming.convert(interface.name),
                "description": interface.description,
                "mode": interface.mode,
                "access_vlan": interface.access_vlan,
                "allowed_vlans": interface.allowed_vlans,
            }
            self._render_block(concept, context, lines, intent)
            lines.append("")

    def _render_block(self, concept: dict, context: dict, lines: list[str], intent: IntentModel) -> None:
        render = concept.get("render", {})

        block_start = render.get("block_start")
        if block_start:
            lines.append(render_template(block_start, context, intent))

        for line in render.get("lines", []):
            if when_matches(line["when"], context):
                lines.append(render_template(line["template"], context, intent))

    def _apply_render_defaults(self, concept: dict, context: dict) -> None:
        defaults = concept.get("render", {}).get("defaults", {})
        for field, template in defaults.items():
            if not context.get(field):
                context[field] = render_template(template, context)
