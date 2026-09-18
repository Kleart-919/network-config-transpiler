"""
Generic, schema-driven batch config parser.

Replaces parsers/cisco_parser.py and parsers/juniper_parser.py with one
class parameterized by a VendorSchema, dispatching on
schema.tokenizer_style ("block" for Cisco's indented-line style, "token"
for Juniper's flat "set ..." style). See schema/vendors/*.yaml for the
concept data this interprets.

The Intent Model itself (models/intent_model.py) is not schema-driven in
this POC - IntentModel/VLAN/Interface stay fixed dataclasses, per the
project plan's scope boundary. CONCEPT_TARGETS below is the one explicit,
deliberate coupling point between a schema concept name and the Intent
Model class/list it builds; extending the Intent Model with a new concept
means updating both the model and this mapping, consistent with the
architecture CLAUDE.md already documents.
"""

import re
import shlex

from configbridge.models.intent_model import VLAN, Interface, IntentModel
from configbridge.schema.schema_model import VendorSchema
from configbridge.engine.value_templates import apply_set_template, when_matches

CONCEPT_TARGETS = {
    "vlan": (VLAN, "vlans"),
    "interface": (Interface, "interfaces"),
}


class GenericConfigParser:
    def __init__(self, schema: VendorSchema):
        self.schema = schema

    def parse(self, config_text: str) -> IntentModel:
        if self.schema.tokenizer_style == "block":
            return self._parse_block_style(config_text)
        return self._parse_token_style(config_text)

    # ------------------------------------------------------------------
    # Block style (Cisco): regex-per-line, current_vlan/current_interface
    # style block context.
    # ------------------------------------------------------------------

    def _parse_block_style(self, config_text: str) -> IntentModel:
        intent = IntentModel()

        scalar_concepts = self._concepts_of_kind("scalar")
        block_concepts = self._concepts_of_kind("block")

        current_context: dict[str, object] = {name: None for name, _ in block_concepts}

        for raw_line in config_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if self._try_scalar_match(intent, scalar_concepts, line):
                continue

            if self._try_block_start(intent, block_concepts, current_context, line):
                continue

            self._try_member_match(block_concepts, current_context, line)

        return intent

    def _try_scalar_match(self, intent, scalar_concepts, line) -> bool:
        for _, concept in scalar_concepts:
            match = re.match(concept["match"], line)
            if match:
                self._apply_set(intent, concept.get("set", {}), match.groupdict())
                return True
        return False

    def _try_block_start(self, intent, block_concepts, current_context, line) -> bool:
        for name, concept in block_concepts:
            block_start = concept["block_start"]
            match = re.match(block_start["match"], line)
            if not match:
                continue

            resolved = {
                field: apply_set_template(template, match.groupdict())
                for field, template in block_start.get("set", {}).items()
            }
            obj = self._new_block_object(name, resolved)
            getattr(intent, CONCEPT_TARGETS[name][1]).append(obj)

            for other in current_context:
                current_context[other] = None
            current_context[name] = obj

            return True
        return False

    def _try_member_match(self, block_concepts, current_context, line) -> bool:
        for name, concept in block_concepts:
            obj = current_context.get(name)
            if obj is None:
                continue

            for member in concept.get("members", []):
                match = re.match(member["match"], line)
                if match:
                    self._apply_set(obj, member.get("set", {}), match.groupdict())
                    return True
            return False
        return False

    # ------------------------------------------------------------------
    # Token style (Juniper): "set ..." lines, shlex-tokenized, positional
    # and anchor-search matching, with cross-line lookup tables and
    # order-dependent resolve rules.
    # ------------------------------------------------------------------

    def _parse_token_style(self, config_text: str) -> IntentModel:
        intent = IntentModel()

        scalar_concepts = self._concepts_of_kind("scalar")
        block_concepts = self._concepts_of_kind("block")

        single_line_blocks = [(n, c) for n, c in block_concepts if "match" in c]
        multi_line_blocks = [(n, c) for n, c in block_concepts if "match_prefix" in c]

        lookup_tables: dict[str, dict] = {}
        dedup_registry: dict[str, dict[str, object]] = {name: {} for name, _ in multi_line_blocks}

        for raw_line in config_text.splitlines():
            line = raw_line.strip()
            if not line or not line.startswith("set "):
                continue

            try:
                parts = shlex.split(line)
            except ValueError:
                continue

            if len(parts) < 2:
                continue

            if self._try_scalar_tokens(intent, scalar_concepts, parts):
                continue

            if self._try_single_line_block(intent, single_line_blocks, parts, lookup_tables):
                continue

            self._try_multi_line_block(intent, multi_line_blocks, parts, dedup_registry, lookup_tables)

        return intent

    def _try_scalar_tokens(self, intent, scalar_concepts, parts) -> bool:
        for _, concept in scalar_concepts:
            captured = self._match_tokens_at(concept["match"], parts, 0)
            if captured is not None:
                self._apply_set(intent, concept.get("set", {}), captured)
                return True
        return False

    def _try_single_line_block(self, intent, single_line_blocks, parts, lookup_tables) -> bool:
        for name, concept in single_line_blocks:
            captured = self._match_tokens_at(concept["match"], parts, 0)
            if captured is None:
                continue

            resolved = {
                field: apply_set_template(template, captured)
                for field, template in concept.get("set", {}).items()
            }
            obj = self._new_block_object(name, resolved)
            getattr(intent, CONCEPT_TARGETS[name][1]).append(obj)

            lookup = concept.get("register_lookup")
            if lookup:
                table = lookup_tables.setdefault(lookup["table"], {})
                table[resolved[lookup["key"]]] = resolved[lookup["value"]]

            return True
        return False

    def _try_multi_line_block(self, intent, multi_line_blocks, parts, dedup_registry, lookup_tables) -> bool:
        for name, concept in multi_line_blocks:
            prefix_tokens = concept["match_prefix"]
            captured_prefix = self._match_tokens_at(prefix_tokens, parts, 0)
            if captured_prefix is None:
                continue

            key_field = concept["key"]
            key_value = apply_set_template("{" + key_field + "}", captured_prefix)

            registry = dedup_registry[name]
            if key_value in registry:
                obj = registry[key_value]
            else:
                obj = self._new_block_object(name, {key_field: key_value})
                registry[key_value] = obj
                getattr(intent, CONCEPT_TARGETS[name][1]).append(obj)

            offset = len(prefix_tokens)

            for member in concept.get("members", []):
                if self._apply_member(member, parts, offset, obj, lookup_tables):
                    break

            return True
        return False

    def _apply_member(self, member: dict, parts: list[str], offset: int, obj, lookup_tables: dict) -> bool:
        kind = member["kind"]

        if kind == "positional":
            captured = self._match_tokens_at(member["tokens"], parts, offset)
            if captured is None:
                return False
            self._apply_set(obj, member.get("set", {}), captured)
            return True

        if kind == "contains_single":
            anchor = member["anchor"]
            if anchor not in parts:
                return False
            index = parts.index(anchor)
            if index + 1 < len(parts):
                self._apply_set(obj, member.get("set", {}), {"captured": parts[index + 1]})
            return True

        if kind == "contains_rest":
            anchor = member["anchor"]
            require_present = member.get("require_present", [])
            if anchor not in parts or any(token not in parts for token in require_present):
                return False

            index = parts.index(anchor)
            strip_tokens = set(member.get("strip_tokens", []))
            captured_list = [t for t in parts[index + 1:] if t not in strip_tokens]

            self._apply_resolve(member.get("resolve"), obj, captured_list, lookup_tables)
            return True

        raise ValueError(f"Unknown member kind: {kind}")

    def _apply_resolve(self, resolve: dict | None, obj, captured_list: list[str], lookup_tables: dict) -> None:
        if resolve is None:
            return

        depends_on = resolve["depends_on"]
        if not getattr(obj, depends_on, None):
            return  # on_missing_dependency: skip (the only supported strategy)

        context = {depends_on: getattr(obj, depends_on)}

        for branch in resolve["branches"]:
            if not when_matches(branch["when"], context):
                continue

            for target_field, expr in branch["set"].items():
                value = self._apply_lookup_function(expr, captured_list, lookup_tables)
                if value is not _NO_VALUE:
                    setattr(obj, target_field, value)
            return

    def _apply_lookup_function(self, expr: str, captured_list: list[str], lookup_tables: dict):
        match = re.match(r"^(lookup_first|lookup_each)\(captured\)$", expr)
        function = match.group(1)

        table = self._the_only_lookup_table(lookup_tables)

        if function == "lookup_first":
            if not captured_list:
                return _NO_VALUE
            return table.get(captured_list[0])

        return [table[name] for name in captured_list if name in table]

    def _the_only_lookup_table(self, lookup_tables: dict) -> dict:
        if len(lookup_tables) != 1:
            raise ValueError(
                "lookup_first/lookup_each require exactly one registered lookup table in this POC scope "
                f"(found {list(lookup_tables)}); extend the engine if a schema needs more than one."
            )
        return next(iter(lookup_tables.values()))

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _concepts_of_kind(self, kind: str):
        return [
            (name, concept)
            for name, concept in self.schema.concepts.items()
            if concept.get("kind", "scalar") == kind
        ]

    def _new_block_object(self, concept_name: str, initial_fields: dict):
        cls, _ = CONCEPT_TARGETS[concept_name]
        return cls(**initial_fields)

    def _apply_set(self, target, set_block: dict, captures: dict) -> None:
        for field, template in set_block.items():
            setattr(target, field, apply_set_template(template, captures))

    def _match_tokens_at(self, pattern_tokens: list[str], parts: list[str], offset: int) -> dict | None:
        if len(parts) < offset + len(pattern_tokens):
            return None

        captured = {}

        for i, token in enumerate(pattern_tokens):
            actual = parts[offset + i]

            if token.startswith("<") and token.endswith(">"):
                name = token[1:-1].split(":")[0]
                captured[name] = actual
            elif token != actual:
                return None

        return captured


class _NoValue:
    def __repr__(self):
        return "<no value>"


_NO_VALUE = _NoValue()
