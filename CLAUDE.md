# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ConfigBridge is a desktop app (PySide6 GUI) for multi-vendor network config transpilation, built around a compiler-style pipeline: vendor config → parser → vendor-neutral Intent Model → generator → target vendor config. It currently supports Cisco IOS and Juniper Junos. Vendor syntax knowledge (both the batch config pipeline and the interactive runtime CLI pipeline) is declarative data — one YAML schema file per vendor under `schema/vendors/`, interpreted by a shared generic engine under `engine/` — not hand-written per-vendor Python. Adding a vendor or a config feature within the current scope (hostname, VLANs, interface mode/description/VLANs) means writing schema data, not code. See `docs/architecture.md` for the full design rationale (layered architecture, discovery-before-translation, relationship engine, vendor plugin model) — read it before making structural changes.

## Setup

No `setup.py`/`pyproject.toml` exists — the `configbridge` package under `src/` is **not pip-installed**. Everything must be run with `src/` on `PYTHONPATH` (or run from `src/` directly).

```bash
pip install -r requirements.txt
```

## Running the app

```bash
PYTHONPATH=src python -m configbridge.main
```

## Tests

There is no pytest/unittest suite and no test runner config. Files under `tests/` are standalone scripts: they import from `configbridge`, execute pipeline/engine logic against fixtures in `sample-configs/`, and `print()` results for manual inspection rather than asserting outcomes. Run one directly from the repo root:

```bash
PYTHONPATH=src python tests/test_bidirectional_pipeline.py
```

`tests/parity/run_parity.py` is the regression gate for the schema-driven engine: it diffs current batch + runtime pipeline output against a committed baseline (`tests/parity/baseline/current.json`) and must report zero differences before any schema/engine change is considered done. `tests/parity/baseline/legacy.json` is a frozen, un-reproducible historical snapshot of the original hand-written parsers/generators (captured before they were deleted) — never target it, never try to regenerate it.

When adding a new one, follow the existing pattern (script that prints intermediate/final state) rather than introducing a new test framework, unless asked to.

## Architecture

The pipeline is a strict layered pipe: each stage only talks to its immediate neighbor, and the **Intent Model is the only thing that crosses vendor boundaries** — parsers never call generators directly, and generators never know which vendor produced the Intent Model they're rendering.

```
Network Session Manager (connections/)     SSH/Telnet transport, vendor-agnostic
        │
Discovery Framework (discovery/)           runs operational show commands, produces...
        │
Device Inventory (models/device_inventory.py)   actual discovered device state (interfaces, status, neighbours)
        │
Relationship Engine (relationship/)        matches interfaces across two inventories by evidence (aliases, desc, VLANs...), not by name — never assume Gi0/1 on one vendor == Gi0/1 on another
        │
Vendor-Neutral Intent Model (models/intent_model.py)   desired config state: hostname, VLANs, interface mode/VLANs — no vendor syntax allowed here
        │
Configuration Parsers/Generators (engine/generic_parser.py, generic_generator.py)   schema-driven; vendor-specific syntax lives only in schema/vendors/*.yaml
```

Key modules:
- `schema/vendors/cisco_ios.yaml`, `schema/vendors/juniper_junos.yaml` — the single source of truth for each vendor's syntax: batch config recognition/rendering rules, the interactive runtime CLI grammar/templates, and the interface-naming convention, all in one file per vendor. `schema/schema_model.py` defines the shape; `schema/loader.py` (`SchemaLoader`) loads and structurally validates a schema file, raising a clear `SchemaError` on malformed data. Extending an existing concept (hostname/VLAN/interface) or adding a vendor within that scope means editing/adding a YAML file here, not writing a parser/generator class.
- `engine/` — the generic engine that interprets a `VendorSchema`, parameterized by data rather than per-vendor code: `generic_parser.py`/`generic_generator.py` (batch config pipeline), `generic_runtime_parser.py`/`generic_runtime_generator.py` (interactive runtime pipeline), `naming.py` (`InterfaceNameMapper`, the one shared interface-naming-convention implementation both pipelines use), `value_templates.py` (shared placeholder/transform resolution). The Intent Model itself (below) is *not* schema-driven — `CONCEPT_TARGETS` in `generic_parser.py` is the one explicit, deliberate coupling point between a schema concept name and the fixed `IntentModel`/`VLAN`/`Interface` classes it builds.
- `models/intent_model.py` — the central `IntentModel`/`Interface`/`VLAN` dataclasses, built/consumed by the generic engine above. Adding a networking concept (routing, ACLs, etc.) means extending this model first, then extending both vendor schemas and `CONCEPT_TARGETS` to support it.
- `models/device_inventory.py` — `DeviceInventory`/`DiscoveredInterface`, the *actual* discovered device state (separate concept from the Intent Model — discovery vs. desired config).
- `plugins/vendor_registry.py`, `plugins/vendor_manifest.py` — a vendor is registered as a `VendorManifest` bundling its discovery profile/parser + config parser/generator. `vendor_registry.build_default_registry()` is the standard way to get a `VendorRegistry` with both vendors' `configuration_parser`/`configuration_generator` wired to the schema-driven engine — prefer it over constructing manifests by hand.
- `runtime/` — a live/interactive CLI translator used by the terminal GUI (`gui/virtual_cli_widget.py`) to translate individual commands as they're typed, and to reverse-translate device output back (`runtime_engine.py`'s `translate()` vs `virtualize_output()`). As of the schema migration, `RuntimeEngine` is built from `engine/generic_runtime_parser.py`/`generic_runtime_generator.py` reading the same `schema/vendors/*.yaml` files the batch pipeline uses (the `runtime:` section of each) — it is a separate *pipeline* (different algorithm shape: single-line token-tree + interactive mode-transition state machine, vs. the batch pipeline's whole-document block parsing) but no longer separate *vendor knowledge*. It does not use `lark`; command recognition is plain shortest-unambiguous-prefix matching over the schema's `runtime.modes` tree. `runtime/cisco_output_generator.py`/`juniper_output_parser.py` (device-output virtualization) also consume the schema's naming convention rather than hardcoding their own.
- `connections/` — `SSHConnection`/`TelnetConnection` implement `base_connection.py`'s interface; `session_manager.py` is the shared entry point. Discovery, the interactive terminal, and the runtime CLI translator all go through this layer rather than talking to devices directly.
- `gui/main_window.py` — the `QMainWindow` wiring together connection setup, the terminal widget, and discovery; `DiscoveryWorker` runs discovery on a background `QThread` so the GUI doesn't block.
- `relationship/` — interface-matching between two `DeviceInventory` objects (source/destination), producing confidence-scored `RelationshipResult`s rather than a direct name mapping. Currently alias-based only (v1); see `docs/architecture.md` §8/§18 for the intended scoring signals (description, VLANs, LLDP/CDP, speed, port-channel).

`transpiler/transpilation_engine.py` is real, working orchestration (vendor lookup → parse → optional relationship resolution → generate), wired via `build_default_registry()`; `safety/` and `comparison/` are present but effectively stubs/placeholders for future work — check before assuming functionality exists there.

`sample-configs/` holds fixture configs (Cisco/Juniper) used by the test scripts and for manual pipeline verification.
