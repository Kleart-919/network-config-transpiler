"""
Generic, schema-driven runtime command parser.

Replaces runtime/runtime_parser.py. Walks the TYPED vendor's schema.runtime
"modes" tree (schema/vendors/cisco_ios.yaml today - the vendor a user types
commands against) doing the same shortest-unambiguous-prefix matching as
the legacy RuntimeParser, but reading "op"/"mode_change" from schema data
instead of a hardcoded grammar module + if/elif ladder.
"""

from configbridge.runtime.runtime_command import RuntimeCommand
from configbridge.schema.schema_model import VendorSchema


class GenericRuntimeParser:
    def __init__(self, schema: VendorSchema):
        if schema.runtime is None or "modes" not in schema.runtime:
            raise ValueError(f"Vendor schema '{schema.vendor_id}' has no runtime.modes section")

        self.schema = schema
        self.mode = "exec"

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def parse(self, command: str) -> RuntimeCommand | None:
        tokens = command.strip().split()

        if not tokens:
            return None

        node = self.schema.runtime["modes"][self.mode]["commands"]
        operation = None
        mode_change = None
        consumed_count = 0

        for token in tokens:
            key = self._expand_token(token, node)

            if key is None:
                break

            consumed_count += 1
            node = node[key]

            if "op" in node:
                operation = node["op"]
                mode_change = node.get("mode_change")

            if "children" in node:
                node = node["children"]
            else:
                break

        if operation is None:
            return None

        return RuntimeCommand(
            operation=operation,
            arguments=tokens[consumed_count:],
            mode_change=mode_change,
        )

    def _expand_token(self, token: str, node: dict) -> str | None:
        token = token.lower()
        matches = []

        for command in node:
            command_text = str(command)
            minimum = str(node[command]["minimum"])

            if command_text.startswith(token) and len(token) >= len(minimum):
                matches.append(command_text)

        if len(matches) != 1:
            return None

        return matches[0]
