#!/usr/bin/env python3
"""
Schema Drafter - offline, human-triggered LLM-assisted schema authoring tool.

NOT part of the ConfigBridge app: nothing under src/configbridge/ imports
this file, and it is not on any code path the running app can reach. It
exists to help a human draft a new schema/vendors/<vendor>.yaml concept
entry from vendor documentation, not to run the transpiler.

Hard boundary this tool exists to preserve: ConfigBridge's batch and
runtime pipelines never call an LLM and never fetch anything live at
execution time - they only ever run against schema/vendors/*.yaml files a
human has reviewed and committed to the repo. This tool only ever writes
to a staging file under authoring/drafts/; it NEVER writes to the real
schema files, and never runs `git add`/`git commit` itself. A human must
review the draft, merge it into the real schema file by hand, and commit
it themselves before ConfigBridge's SchemaLoader will ever see it - at
which point it is indistinguishable from a hand-written entry.

Usage:
    python tools/schema_drafter.py \
        --vendor juniper_junos \
        --concept interface_native_vlan \
        --doc path/to/vendor_doc_excerpt.txt \
        [--sample path/to/sample_config_snippet.txt] \
        [--model claude-sonnet-5] \
        [--max-retries 2]

Requires an ANTHROPIC_API_KEY environment variable and the `anthropic`
package - deliberately NOT a project dependency (not in requirements.txt);
install it separately: pip install anthropic
"""

import argparse
import copy
import difflib
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_VENDORS_DIR = REPO_ROOT / "src" / "configbridge" / "schema" / "vendors"
INTENT_MODEL_PATH = REPO_ROOT / "src" / "configbridge" / "models" / "intent_model.py"
DRAFTS_DIR = REPO_ROOT / "authoring" / "drafts"

sys.path.insert(0, str(REPO_ROOT / "src"))

from configbridge.schema.loader import SchemaLoader, SchemaError  # noqa: E402
from configbridge.engine.generic_parser import GenericConfigParser  # noqa: E402
from configbridge.engine.generic_generator import GenericConfigGenerator  # noqa: E402


PROMPT_TEMPLATE = """You are drafting one entry for a network vendor configuration schema.

The schema format is YAML. It must match this shape (a "concept" definition, \
one of several under a vendor's top-level `concepts:` key). Here is the \
COMPLETE existing schema for this vendor, so you can match its style, \
tokenizer style, and conventions exactly:

--- BEGIN EXISTING SCHEMA: {vendor_id} ---
{existing_schema_text}
--- END EXISTING SCHEMA ---

Here is the authoritative target data model you must map fields onto. You \
may ONLY set fields that already exist on these dataclasses - never invent \
new Intent Model fields:

--- BEGIN INTENT MODEL ---
{intent_model_text}
--- END INTENT MODEL ---

Here is an excerpt of vendor documentation describing the config syntax you \
need to model:

--- BEGIN VENDOR DOCUMENTATION EXCERPT ---
{doc_excerpt}
--- END VENDOR DOCUMENTATION EXCERPT ---

Draft the schema entry for the concept named "{concept_name}", matching the \
existing schema's tokenizer style ("block" = regex-per-line with block_start \
+ members, or "token" = shlex-tokenized "set ..." lines with positional / \
contains_single / contains_rest members - see the existing schema for which \
one this vendor uses and follow its exact conventions).

Respond with ONLY the YAML for this one concept's body (the mapping that \
would go under `concepts.{concept_name}:` in the vendor file) - do not wrap \
it in a `concepts:` key, do not include the vendor/tokenizer/naming_convention \
sections, and do not add commentary outside a single ```yaml fenced code \
block.
{retry_context}"""

RETRY_TEMPLATE = """

Your previous draft failed validation with this error - fix it and redraft \
the complete concept entry:

{error}

Previous draft:
```yaml
{previous_draft}
```"""


def load_existing_schema_text(vendor_id: str) -> str:
    path = SCHEMA_VENDORS_DIR / f"{vendor_id}.yaml"
    if not path.exists():
        raise SystemExit(f"No existing schema for vendor '{vendor_id}' at {path}")
    return path.read_text()


def build_prompt(vendor_id, concept_name, doc_excerpt, sample_note, previous_error=None, previous_draft=None):
    existing_schema_text = load_existing_schema_text(vendor_id)
    intent_model_text = INTENT_MODEL_PATH.read_text()

    retry_context = ""
    if previous_error:
        retry_context = RETRY_TEMPLATE.format(error=previous_error, previous_draft=previous_draft)

    return PROMPT_TEMPLATE.format(
        vendor_id=vendor_id,
        existing_schema_text=existing_schema_text,
        intent_model_text=intent_model_text,
        doc_excerpt=doc_excerpt,
        concept_name=concept_name,
        retry_context=retry_context,
    )


def call_llm(prompt: str, model: str) -> str:
    try:
        import anthropic
    except ImportError:
        raise SystemExit(
            "The 'anthropic' package is required to draft a schema entry "
            "(pip install anthropic) - it is deliberately not a project "
            "dependency, since only this offline authoring tool needs it."
        )

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return "".join(block.text for block in response.content if block.type == "text")


def extract_yaml_fragment(response_text: str) -> str:
    if "```yaml" in response_text:
        fragment = response_text.split("```yaml", 1)[1].split("```", 1)[0]
    elif "```" in response_text:
        fragment = response_text.split("```", 1)[1].split("```", 1)[0]
    else:
        fragment = response_text

    return fragment.strip()


def validate_structurally(vendor_id: str, concept_name: str, fragment_yaml: str):
    """
    Merge the draft into a copy of the real schema (in memory / a temp
    file only - never the real file) and load it through the real
    SchemaLoader. Returns (VendorSchema, merged_raw_dict) on success, or
    raises SchemaError/yaml.YAMLError on failure - the same errors a
    hand-written schema mistake would raise.
    """

    fragment_dict = yaml.safe_load(fragment_yaml)
    if not isinstance(fragment_dict, dict):
        raise SchemaError("Drafted fragment is not a YAML mapping")

    existing_path = SCHEMA_VENDORS_DIR / f"{vendor_id}.yaml"
    merged_raw = copy.deepcopy(yaml.safe_load(existing_path.read_text()))
    merged_raw.setdefault("concepts", {})[concept_name] = fragment_dict

    with tempfile.TemporaryDirectory() as tmp:
        tmp_vendors_dir = Path(tmp)
        (tmp_vendors_dir / f"{vendor_id}.yaml").write_text(yaml.safe_dump(merged_raw, sort_keys=False))

        schema = SchemaLoader(vendors_dir=tmp_vendors_dir).load(vendor_id)

    return schema, merged_raw


def behavioral_round_trip(schema, sample_config_text: str) -> str:
    """
    Parse the supplied sample through the merged (draft-included) schema
    and regenerate it, returning a unified diff against the original for a
    human to judge. Not a pass/fail gate on its own - concepts the schema
    doesn't model yet are expected to disappear on regeneration; a human
    reviews whether the diff makes sense for what was actually drafted.
    """

    parser = GenericConfigParser(schema)
    generator = GenericConfigGenerator(schema)

    intent = parser.parse(sample_config_text)
    regenerated = generator.generate(intent)

    diff_lines = list(
        difflib.unified_diff(
            sample_config_text.splitlines(keepends=True),
            regenerated.splitlines(keepends=True),
            fromfile="sample (original)",
            tofile="regenerated (round-trip)",
        )
    )

    return "".join(diff_lines) if diff_lines else "(no differences - exact round trip)"


def draft_schema_entry(vendor_id, concept_name, doc_excerpt, sample_config_text, model, max_retries):
    previous_error = None
    previous_draft = None

    for attempt in range(1, max_retries + 2):
        prompt = build_prompt(
            vendor_id, concept_name, doc_excerpt,
            sample_note=bool(sample_config_text),
            previous_error=previous_error,
            previous_draft=previous_draft,
        )

        print(f"[attempt {attempt}] calling {model}...")
        response_text = call_llm(prompt, model)
        fragment_yaml = extract_yaml_fragment(response_text)

        try:
            schema, merged_raw = validate_structurally(vendor_id, concept_name, fragment_yaml)
        except (SchemaError, yaml.YAMLError) as exc:
            print(f"[attempt {attempt}] structural validation FAILED: {exc}")
            previous_error = str(exc)
            previous_draft = fragment_yaml
            if attempt <= max_retries:
                continue
            return fragment_yaml, "FAIL", f"Structural validation failed after {attempt} attempts: {exc}"

        report_lines = [f"Structural validation: PASS (attempt {attempt})"]

        if sample_config_text:
            round_trip = behavioral_round_trip(schema, sample_config_text)
            report_lines.append("Behavioral round-trip diff (review, not auto pass/fail):")
            report_lines.append(round_trip)
        else:
            report_lines.append("No sample config supplied - behavioral round-trip skipped.")

        return fragment_yaml, "PASS", "\n".join(report_lines)

    return fragment_yaml, "FAIL", "Exhausted retries"


def write_draft_file(vendor_id, concept_name, fragment_yaml, status, report) -> Path:
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = concept_name.replace(" ", "_").lower()
    out_path = DRAFTS_DIR / f"{vendor_id}_{slug}_{timestamp}.yaml"

    header = (
        f"# DRAFT schema entry - NOT committed, NOT used by the app.\n"
        f"# vendor: {vendor_id}   concept: {concept_name}   status: {status}\n"
        f"# Suggested insertion point: schema/vendors/{vendor_id}.yaml, "
        f"under `concepts.{concept_name}:`\n"
        f"#\n"
        f"# Validation report:\n"
        + "\n".join(f"# {line}" for line in report.splitlines())
        + "\n#\n"
        f"# A human must review this, edit as needed, merge it into the real\n"
        f"# schema file, and `git add`/`git commit` it themselves. Nothing\n"
        f"# does this automatically.\n\n"
    )

    out_path.write_text(header + fragment_yaml + "\n")
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vendor", required=True, help="Vendor schema id, e.g. juniper_junos")
    parser.add_argument("--concept", required=True, help="Concept name to draft, e.g. interface_native_vlan")
    parser.add_argument("--doc", required=True, type=Path, help="Path to a vendor documentation excerpt (text)")
    parser.add_argument("--sample", type=Path, help="Optional sample config snippet for a behavioral round-trip check")
    parser.add_argument("--model", default="claude-sonnet-5", help="Anthropic model id")
    parser.add_argument("--max-retries", type=int, default=2)
    args = parser.parse_args()

    doc_excerpt = args.doc.read_text()
    sample_config_text = args.sample.read_text() if args.sample else None

    fragment_yaml, status, report = draft_schema_entry(
        args.vendor, args.concept, doc_excerpt, sample_config_text, args.model, args.max_retries
    )

    out_path = write_draft_file(args.vendor, args.concept, fragment_yaml, status, report)

    print()
    print(f"Status: {status}")
    print(report)
    print()
    print(f"Draft written to: {out_path}")
    print("Review it, then merge it into "
          f"src/configbridge/schema/vendors/{args.vendor}.yaml yourself and commit.")

    sys.exit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
