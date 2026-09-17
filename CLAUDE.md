# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ConfigBridge is a desktop app (PySide6 GUI) for multi-vendor network config transpilation, built around a compiler-style pipeline: vendor config → parser → vendor-neutral Intent Model → generator → target vendor config. It currently supports Cisco IOS and Juniper Junos. See `docs/architecture.md` for the full design rationale (layered architecture, discovery-before-translation, relationship engine, vendor plugin model) — read it before making structural changes.

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
PYTHONPATH=src python tests/test_cisco_parser.py
```

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
Configuration Parsers/Generators (parsers/, renderers/)   vendor-specific syntax only lives here
```

Key modules:
- `models/intent_model.py` — the central `IntentModel`/`Interface`/`VLAN` dataclasses. Parsers (`parsers/cisco_parser.py`, `parsers/juniper_parser.py`) build these from raw config text; generators (`renderers/cisco_generator.py`, `renderers/juniper_generator.py`) consume them to emit vendor config. Adding a networking concept (routing, ACLs, etc.) means extending this model first, then updating every parser/generator that should support it.
- `models/device_inventory.py` — `DeviceInventory`/`DiscoveredInterface`, the *actual* discovered device state (separate concept from the Intent Model — discovery vs. desired config).
- `plugins/vendor_registry.py`, `plugins/vendor_manifest.py` — a vendor is registered as a `VendorManifest` bundling its discovery profile/parser + config parser/generator. This is the extension point for adding a new vendor.
- `runtime/` — a **separate** pipeline from the batch parser/generator one above: it's a live/interactive CLI translator used by the terminal GUI (`gui/virtual_cli_widget.py`) to translate individual commands as they're typed, and to reverse-translate device output back (`runtime_engine.py`'s `translate()` vs `virtualize_output()`). Vendor CLI grammars are YAML files loaded by `runtime/grammar/grammar_loader.py` (`runtime/grammar/cisco_ios.yaml`, `juniper_junos.yaml`) using `lark`. Don't confuse this with the config-file parsers/generators above — they solve different problems (one-shot config transpilation vs. interactive command translation) and don't share code.
- `connections/` — `SSHConnection`/`TelnetConnection` implement `base_connection.py`'s interface; `session_manager.py` is the shared entry point. Discovery, the interactive terminal, and the runtime CLI translator all go through this layer rather than talking to devices directly.
- `gui/main_window.py` — the `QMainWindow` wiring together connection setup, the terminal widget, and discovery; `DiscoveryWorker` runs discovery on a background `QThread` so the GUI doesn't block.
- `relationship/` — interface-matching between two `DeviceInventory` objects (source/destination), producing confidence-scored `RelationshipResult`s rather than a direct name mapping. Currently alias-based only (v1); see `docs/architecture.md` §8/§18 for the intended scoring signals (description, VLANs, LLDP/CDP, speed, port-channel).

`transpiler/transpilation_engine.py` and `safety/` are present but effectively stubs/placeholders for future work — check before assuming functionality exists there.

`sample-configs/` holds fixture configs (Cisco/Juniper) used by the test scripts and for manual pipeline verification.
