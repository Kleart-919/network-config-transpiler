"""
Schema loader.

Loads a vendor schema YAML file, validates its structure, and returns a
VendorSchema. Validation failures raise SchemaError with a message
identifying exactly what's wrong and where - this same loader is meant to
be reused, unchanged, by the LLM-assisted authoring tool's self-validation
step (see the project plan's Part 3/4), so error messages should be
readable by a human reviewing a draft, not just by a developer.

This module has no knowledge of *how* a schema is executed - it only knows
the schema's shape. Interpreting it belongs to engine/generic_parser.py and
engine/generic_generator.py (Phase 2/3).
"""

import re
from pathlib import Path
from typing import Any

import yaml

from configbridge.schema.schema_model import NamingConvention, NamingRecognizer, VendorSchema

VENDORS_DIR = Path(__file__).parent / "vendors"

VALID_TOKENIZER_STYLES = {"block", "token"}
VALID_MEMBER_KINDS = {"positional", "contains_single", "contains_rest"}
VALID_SET_TRANSFORMS = {"int", "int_csv", "bracket_list"}
VALID_RENDER_TRANSFORMS = {"int_csv", "vlan_name", "vlan_names_space"}
VALID_RUNTIME_MODES = {"exec", "config", "interface"}
VALID_ARGUMENT_SOURCES = {"arg0", "all_args"}
VALID_ARGUMENT_RESOLVERS = {"device_inventory_alias"}

_PLACEHOLDER_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z_]+))?\}")
_TOKEN_PLACEHOLDER_RE = re.compile(r"^<([A-Za-z_][A-Za-z0-9_]*)(?::([A-Za-z_]+))?>$")


class SchemaError(ValueError):
    """Raised when a vendor schema file is structurally invalid."""


class SchemaLoader:
    def __init__(self, vendors_dir: Path | None = None):
        self.vendors_dir = vendors_dir or VENDORS_DIR

    def load(self, vendor_id: str) -> VendorSchema:
        path = self.vendors_dir / f"{vendor_id}.yaml"

        if not path.exists():
            raise SchemaError(f"No schema file found for vendor '{vendor_id}' at {path}")

        with open(path, "r", encoding="utf-8") as file:
            raw = yaml.safe_load(file)

        return self._validate(raw, source=path.name)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self, raw: dict, source: str) -> VendorSchema:
        if not isinstance(raw, dict):
            raise SchemaError(f"[{source}] schema file must contain a YAML mapping at the top level")

        vendor = self._require(raw, "vendor", dict, source)
        vendor_id = self._require(vendor, "id", str, f"{source}:vendor")
        display_name = self._require(vendor, "display_name", str, f"{source}:vendor")

        tokenizer = self._require(raw, "tokenizer", dict, source)
        style = self._require(tokenizer, "style", str, f"{source}:tokenizer")

        if style not in VALID_TOKENIZER_STYLES:
            raise SchemaError(
                f"[{source}] tokenizer.style must be one of {sorted(VALID_TOKENIZER_STYLES)}, got '{style}'"
            )

        naming = self._validate_naming(raw.get("naming_convention", {}), source)

        concepts_raw = self._require(raw, "concepts", dict, source)
        if not concepts_raw:
            raise SchemaError(f"[{source}] concepts must define at least one concept")

        concepts = {
            name: self._validate_concept(name, concept, style, source)
            for name, concept in concepts_raw.items()
        }

        runtime = raw.get("runtime")
        if runtime is not None:
            self._validate_runtime(runtime, source)

        return VendorSchema(
            vendor_id=vendor_id,
            display_name=display_name,
            tokenizer_style=style,
            naming=naming,
            concepts=concepts,
            runtime=runtime,
        )

    def _validate_naming(self, raw: dict, source: str) -> NamingConvention:
        recognizers = []

        for index, entry in enumerate(raw.get("recognizes", [])):
            context = f"{source}:naming_convention.recognizes[{index}]"
            pattern = self._require(entry, "pattern", str, context)
            render = self._require(entry, "render", str, context)

            compiled = self._compile_regex(pattern, context)
            group_names = set(compiled.groupindex)
            self._check_placeholders(render, group_names, context, "render")

            recognizers.append(NamingRecognizer(pattern=pattern, render=render))

        return NamingConvention(recognizes=recognizers)

    # -- runtime section (interactive CLI pipeline, Phase 5+) --------------

    def _validate_runtime(self, runtime: dict, source: str) -> None:
        context = f"{source}:runtime"

        if not isinstance(runtime, dict):
            raise SchemaError(f"[{context}] must be a mapping")

        has_modes = "modes" in runtime
        has_templates = "templates" in runtime

        if has_modes == has_templates:
            raise SchemaError(
                f"[{context}] must define exactly one of 'modes' (typed/recognized-command vendor) "
                f"or 'templates' (generated-command vendor), not both or neither"
            )

        if has_modes:
            modes = self._require(runtime, "modes", dict, context)
            for mode_name, mode in modes.items():
                if mode_name not in VALID_RUNTIME_MODES:
                    raise SchemaError(
                        f"[{context}.modes] unknown mode '{mode_name}' "
                        f"(known: {sorted(VALID_RUNTIME_MODES)})"
                    )
                commands = self._require(mode, "commands", dict, f"{context}.modes.{mode_name}")
                self._validate_command_tree(commands, f"{context}.modes.{mode_name}.commands")
        else:
            templates = self._require(runtime, "templates", dict, context)
            for op, entry in templates.items():
                self._validate_runtime_template(op, entry, f"{context}.templates.{op}")

    def _validate_command_tree(self, commands: dict, context: str) -> None:
        for word, node in commands.items():
            node_context = f"{context}.{word}"

            if not isinstance(node, dict):
                raise SchemaError(f"[{node_context}] must be a mapping")

            self._require(node, "minimum", str, node_context)

            has_op = "op" in node
            has_children = "children" in node

            if not has_op and not has_children:
                raise SchemaError(f"[{node_context}] must define 'op' (leaf) or 'children' (non-leaf)")

            if "mode_change" in node and node["mode_change"] not in VALID_RUNTIME_MODES:
                raise SchemaError(
                    f"[{node_context}] mode_change must be one of {sorted(VALID_RUNTIME_MODES)}, "
                    f"got '{node['mode_change']}'"
                )

            if has_children:
                self._validate_command_tree(node["children"], node_context)

    def _validate_runtime_template(self, op: str, entry: dict, context: str) -> None:
        if not isinstance(entry, dict):
            raise SchemaError(f"[{context}] must be a mapping")

        template = self._require(entry, "template", (str, list), context)
        if isinstance(template, list) and not all(isinstance(t, str) for t in template):
            raise SchemaError(f"[{context}.template] list entries must all be strings")

        if "mode_change" in entry and entry["mode_change"] not in VALID_RUNTIME_MODES:
            raise SchemaError(
                f"[{context}] mode_change must be one of {sorted(VALID_RUNTIME_MODES)}, "
                f"got '{entry['mode_change']}'"
            )

        template_text = "\n".join(template) if isinstance(template, list) else template
        referenced = set(_PLACEHOLDER_RE.findall(template_text))
        referenced_names = {name for name, _ in referenced}

        arguments = entry.get("arguments", {})
        if not isinstance(arguments, dict):
            raise SchemaError(f"[{context}.arguments] must be a mapping")

        for arg_name, spec in arguments.items():
            arg_context = f"{context}.arguments.{arg_name}"
            source_kind = self._require(spec, "source", str, arg_context)
            if source_kind not in VALID_ARGUMENT_SOURCES:
                raise SchemaError(
                    f"[{arg_context}] source must be one of {sorted(VALID_ARGUMENT_SOURCES)}, "
                    f"got '{source_kind}'"
                )
            if "resolve" in spec and spec["resolve"] not in VALID_ARGUMENT_RESOLVERS:
                raise SchemaError(
                    f"[{arg_context}] resolve must be one of {sorted(VALID_ARGUMENT_RESOLVERS)}, "
                    f"got '{spec['resolve']}'"
                )

        for name in referenced_names:
            if name not in arguments:
                raise SchemaError(
                    f"[{context}] template references '{{{name}}}' with no matching entry in 'arguments'"
                )

    def _validate_concept(self, name: str, concept: dict, style: str, source: str) -> dict:
        context = f"{source}:concepts.{name}"

        if not isinstance(concept, dict):
            raise SchemaError(f"[{context}] concept must be a mapping")

        kind = concept.get("kind", "scalar")

        if kind not in ("scalar", "block"):
            raise SchemaError(f"[{context}] kind must be 'scalar' or 'block', got '{kind}'")

        if style == "block":
            self._validate_block_style_concept(concept, kind, context)
        else:
            self._validate_token_style_concept(concept, kind, context)

        target_fields = self._collect_target_fields(concept, kind)
        self._validate_render(concept.get("render"), kind, target_fields, context)

        return concept

    def _collect_target_fields(self, concept: dict, kind: str) -> set[str]:
        """
        Every Intent Model field name this concept can set, gathered from its
        own 'set' block(s) plus any resolve branches - i.e. the field names
        legitimately available to reference in a render template.
        """

        fields: set[str] = set()

        if "key" in concept:
            fields.add(concept["key"])

        fields.update(concept.get("set", {}).keys())

        if kind == "scalar":
            return fields

        block_start = concept.get("block_start", {})
        fields.update(block_start.get("set", {}).keys())

        for member in concept.get("members", []):
            fields.update(member.get("set", {}).keys())
            resolve = member.get("resolve")
            if resolve:
                for branch in resolve.get("branches", []):
                    fields.update(branch.get("set", {}).keys())

        return fields

    # -- block-style (regex-per-line) validation --------------------------

    def _validate_block_style_concept(self, concept: dict, kind: str, context: str) -> None:
        if kind == "scalar":
            match = self._require(concept, "match", str, context)
            fields = self._compile_regex(match, context).groupindex.keys()
            self._validate_set_block(concept.get("set", {}), fields, context)
            return

        block_start = self._require(concept, "block_start", dict, context)
        match = self._require(block_start, "match", str, f"{context}.block_start")
        fields = self._compile_regex(match, f"{context}.block_start").groupindex.keys()
        self._validate_set_block(block_start.get("set", {}), fields, f"{context}.block_start")

        for index, member in enumerate(concept.get("members", [])):
            member_context = f"{context}.members[{index}]"
            member_match = self._require(member, "match", str, member_context)
            member_fields = self._compile_regex(member_match, member_context).groupindex.keys()
            self._validate_set_block(member.get("set", {}), member_fields, member_context)

    # -- token-style (positional/shlex) validation -------------------------

    def _validate_token_style_concept(self, concept: dict, kind: str, context: str) -> None:
        prefix_captures: set[str] = set()

        if "match" in concept:
            self._validate_token_pattern(concept["match"], context)
            captures = self._extract_token_captures(concept["match"])
            self._validate_set_block(concept.get("set", {}), captures, context)

            if "register_lookup" in concept:
                lookup = concept["register_lookup"]
                self._require(lookup, "table", str, f"{context}.register_lookup")
                lookup_key = self._require(lookup, "key", str, f"{context}.register_lookup")
                lookup_value = self._require(lookup, "value", str, f"{context}.register_lookup")
                for name in (lookup_key, lookup_value):
                    if name not in captures:
                        raise SchemaError(
                            f"[{context}.register_lookup] references unknown capture '{name}'"
                        )

        if kind == "block":
            if "match_prefix" in concept:
                self._validate_token_pattern(concept["match_prefix"], f"{context}.match_prefix")
                prefix_captures = self._extract_token_captures(concept["match_prefix"])

            for index, member in enumerate(concept.get("members", [])):
                member_context = f"{context}.members[{index}]"
                member_kind = self._require(member, "kind", str, member_context)

                if member_kind not in VALID_MEMBER_KINDS:
                    raise SchemaError(
                        f"[{member_context}] kind must be one of {sorted(VALID_MEMBER_KINDS)}, got '{member_kind}'"
                    )

                if member_kind == "positional":
                    tokens = self._require(member, "tokens", list, member_context)
                    self._validate_token_pattern(tokens, member_context)
                    captures = prefix_captures | self._extract_token_captures(tokens)
                else:
                    self._require(member, "anchor", str, member_context)
                    captures = prefix_captures | {"captured"}

                self._validate_set_block(member.get("set", {}), captures, member_context)

                if "resolve" in member:
                    self._validate_resolve(member["resolve"], captures, member_context)

    def _extract_token_captures(self, tokens: list[str]) -> set[str]:
        names = set()
        for token in tokens:
            if token.startswith("<"):
                m = _TOKEN_PLACEHOLDER_RE.match(token)
                if m:
                    names.add(m.group(1))
        return names

    def _validate_token_pattern(self, tokens: Any, context: str) -> None:
        if not isinstance(tokens, list) or not all(isinstance(t, str) for t in tokens):
            raise SchemaError(f"[{context}] must be a list of strings (literals or <name>/<name:transform>)")

        for token in tokens:
            if token.startswith("<"):
                m = _TOKEN_PLACEHOLDER_RE.match(token)
                if not m:
                    raise SchemaError(f"[{context}] malformed token placeholder: '{token}'")
                _, transform = m.groups()
                if transform and transform not in VALID_SET_TRANSFORMS:
                    raise SchemaError(
                        f"[{context}] unknown transform ':{transform}' in '{token}' "
                        f"(known: {sorted(VALID_SET_TRANSFORMS)})"
                    )

    _RESOLVE_FUNCTION_RE = re.compile(r"^(lookup_first|lookup_each)\(([A-Za-z_][A-Za-z0-9_]*)\)$")

    def _validate_resolve(self, resolve: dict, captures: set[str], context: str) -> None:
        context = f"{context}.resolve"
        self._require(resolve, "depends_on", str, context)
        on_missing = self._require(resolve, "on_missing_dependency", str, context)

        if on_missing != "skip":
            raise SchemaError(f"[{context}] on_missing_dependency must be 'skip' (only supported strategy)")

        branches = self._require(resolve, "branches", list, context)
        if not branches:
            raise SchemaError(f"[{context}] must define at least one branch")

        for index, branch in enumerate(branches):
            branch_context = f"{context}.branches[{index}]"
            self._require(branch, "when", str, branch_context)
            branch_set = self._require(branch, "set", dict, branch_context)

            for target_field, expr in branch_set.items():
                m = self._RESOLVE_FUNCTION_RE.match(expr) if isinstance(expr, str) else None
                if not m:
                    raise SchemaError(
                        f"[{branch_context}.set.{target_field}] must be 'lookup_first(<capture>)' "
                        f"or 'lookup_each(<capture>)', got '{expr}'"
                    )
                if m.group(2) not in captures:
                    raise SchemaError(
                        f"[{branch_context}.set.{target_field}] references unknown capture '{m.group(2)}' "
                        f"in '{expr}'"
                    )

    # -- shared -------------------------------------------------------------

    def _validate_set_block(self, set_block: dict, known_fields, context: str) -> None:
        if not isinstance(set_block, dict):
            raise SchemaError(f"[{context}] 'set' must be a mapping")

        for target_field, value_template in set_block.items():
            if not isinstance(value_template, str):
                continue
            self._check_placeholders(value_template, set(known_fields), f"{context}.set.{target_field}", "set")

    def _validate_render(self, render: Any, kind: str, target_fields: set[str], context: str) -> None:
        if render is None:
            return

        if kind == "scalar":
            if not isinstance(render, str):
                raise SchemaError(f"[{context}.render] scalar concept's render must be a plain template string")
            self._check_placeholders(render, target_fields, f"{context}.render", "render")
            return

        if not isinstance(render, dict):
            raise SchemaError(f"[{context}.render] must be a mapping with an optional 'block_start' and 'lines'")

        block_start = render.get("block_start")
        if block_start is not None:
            if not isinstance(block_start, str):
                raise SchemaError(f"[{context}.render.block_start] must be a template string")
            self._check_placeholders(block_start, target_fields, f"{context}.render.block_start", "render")

        for target_field, default_template in render.get("defaults", {}).items():
            self._check_placeholders(
                default_template, target_fields, f"{context}.render.defaults.{target_field}", "render"
            )

        lines = render.get("lines", [])
        if not isinstance(lines, list):
            raise SchemaError(f"[{context}.render.lines] must be a list")

        for index, line in enumerate(lines):
            line_context = f"{context}.render.lines[{index}]"
            self._validate_when(line.get("when"), line_context)
            template = self._require(line, "template", str, line_context)
            self._check_placeholders(template, target_fields, line_context, "render")

    def _validate_when(self, when: Any, context: str) -> None:
        """
        `when` selects whether a render line is emitted: a single condition,
        or a list of conditions ANDed together. Each condition is either a
        bare field name (truthy check) or 'field:value' (equality check).
        """

        if when is None:
            raise SchemaError(f"[{context}] missing required key 'when'")

        conditions = when if isinstance(when, list) else [when]

        if not conditions or not all(isinstance(c, str) for c in conditions):
            raise SchemaError(f"[{context}] 'when' must be a string or a list of strings")

    def _check_placeholders(self, template: str, known_names: set[str], context: str, kind: str) -> None:
        valid_transforms = VALID_SET_TRANSFORMS if kind == "set" else VALID_RENDER_TRANSFORMS

        for name, transform in _PLACEHOLDER_RE.findall(template):
            if name not in known_names:
                noun = "capture group" if kind == "set" else "field"
                raise SchemaError(f"[{context}] references unknown {noun} '{{{name}}}' in '{template}'")
            if transform and transform not in valid_transforms:
                raise SchemaError(
                    f"[{context}] unknown transform ':{transform}' on '{{{name}}}' in '{template}' "
                    f"(known: {sorted(valid_transforms)})"
                )

    def _compile_regex(self, pattern: str, context: str) -> re.Pattern:
        try:
            return re.compile(pattern)
        except re.error as exc:
            raise SchemaError(f"[{context}] invalid regex '{pattern}': {exc}") from exc

    def _require(self, obj: dict, key: str, expected_type: type, context: str):
        if key not in obj:
            raise SchemaError(f"[{context}] missing required key '{key}'")

        value = obj[key]
        if not isinstance(value, expected_type):
            raise SchemaError(
                f"[{context}] key '{key}' must be of type {expected_type.__name__}, got {type(value).__name__}"
            )

        return value
