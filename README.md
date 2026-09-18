# ConfigBridge

*A Discovery-Assisted Multi-Vendor Network Configuration Transpilation and Unified Network Access Platform*

---

## Overview

ConfigBridge is a desktop application designed to simplify the management, migration and interoperability of heterogeneous network infrastructures.

Rather than relying on direct command translation between vendors, ConfigBridge separates vendor-specific syntax from vendor-neutral network intent through a layered software architecture.

The system combines:

* A unified network session manager.
* Device discovery.
* Device inventory construction.
* Relationship analysis.
* Vendor-neutral intent modelling.
* Multi-vendor configuration generation.

This architecture enables network configurations to be understood independently of the originating vendor while providing a scalable foundation for future multi-vendor support.

---

# Motivation

Modern enterprise networks rarely consist of equipment from a single vendor.

Cisco IOS, Cisco Nexus, Juniper Junos, ArubaOS, HP Comware and Arista EOS frequently coexist within the same environment due to procurement strategies, phased hardware refreshes, mergers or differing technical requirements.

Managing these environments often requires organisations to:

* recruit engineers with expertise across multiple vendors;
* invest in vendor-specific certification and training;
* purchase commercial multi-vendor management platforms; or
* limit infrastructure decisions based on existing staff familiarity.

ConfigBridge does not attempt to replace experienced network engineers.

Instead, it aims to improve accessibility, reduce migration effort, reduce operational overhead and support cost avoidance by providing a discovery-assisted, vendor-neutral software architecture for heterogeneous network environments.

---

# Current Features

## Network Session Manager

* SSH support
* Telnet support
* Interactive terminal
* Session logging
* Connection status monitoring

---

## Discovery Framework

* Device discovery architecture
* Device inventory model
* Vendor discovery parsers
* Interface discovery prototype

---

## Configuration Transpilation

ConfigBridge uses one shared, schema-driven configuration engine rather than separate hand-written parser and generator implementations for each vendor.

The batch configuration pipeline is driven by:

* `engine/generic_parser.py`
* `engine/generic_generator.py`
* `schema/vendors/cisco_ios.yaml`
* `schema/vendors/juniper_junos.yaml`

The vendor YAML schemas contain the vendor-specific syntax knowledge consumed by the generic engine. They are the source of truth for the currently supported vendor syntax.

The interactive runtime CLI translator uses the same schema data through:

* `engine/generic_runtime_parser.py`
* `engine/generic_runtime_generator.py`

Currently implemented:

* Cisco IOS configuration parsing
* Juniper Junos configuration parsing
* Cisco IOS configuration generation
* Juniper Junos configuration generation
* Vendor-neutral Intent Model
* Bidirectional transpilation pipeline
* Schema-driven batch and interactive runtime translation

---

## Architecture

ConfigBridge currently consists of the following major components.

```text
Network Session Manager
        │
Discovery Framework
        │
Device Inventory
        │
Relationship Engine
        │
Vendor-Neutral Intent Model
        │
Schema-Driven Configuration Engine
        │
Configuration Output
```

Vendor-specific configuration knowledge is kept in the vendor schema layer rather than duplicated across Python parser and generator implementations.

---

# Current Vendor Support

## Configuration Parsing

* Cisco IOS
* Juniper Junos

## Configuration Generation

* Cisco IOS
* Juniper Junos

Both vendors currently use the same generic schema-driven parsing and generation engine.

The corresponding syntax definitions are maintained in:

```text
src/configbridge/schema/vendors/
├── cisco_ios.yaml
└── juniper_junos.yaml
```

These schema files are the source of truth for vendor-specific syntax used by both the batch configuration pipeline and the interactive runtime CLI translator.

## Session Management

* SSH
* Telnet

Future versions will support additional network operating systems and networking concepts as the Intent Model and vendor schemas are extended.

---

# Planned Features

* Discovery-assisted interface relationship resolution
* Configuration comparison
* Deployment framework
* Rollback support
* Additional vendor support
* Automated vendor onboarding
* Layer 3 networking
* ACLs
* NTP
* SNMP
* QoS
* VRFs

The Relationship Engine is already implemented as a v1 alias-based implementation. Future work will extend its relationship signals beyond aliases to include richer discovery evidence such as interface descriptions, VLAN information, LLDP/CDP and other operational characteristics.

---

# Project Structure

```text
src/
│
└── configbridge/
    │
    ├── connections/       # SSH/Telnet session and transport handling
    ├── discovery/         # Device discovery and discovery parsing
    ├── engine/            # Shared schema-driven parsing/generation engines
    ├── gui/               # PySide6 desktop interface
    ├── models/            # Intent and device inventory models
    ├── plugins/           # Vendor registry and plugin integration
    ├── relationship/      # Interface/device relationship resolution
    ├── runtime/           # Interactive runtime CLI translation
    ├── safety/            # Safety-related placeholders
    ├── schema/            # Schema models, loading and vendor syntax definitions
    └── transpiler/        # Transpilation orchestration
        │
        └── ...
           

schema/vendors/
├── cisco_ios.yaml         # Cisco IOS syntax source of truth
└── juniper_junos.yaml     # Juniper Junos syntax source of truth

tools/
└── schema_drafter.py      # Offline schema-authoring and validation tool

tests/
└── parity/
    └── run_parity.py      # Schema/engine regression gate

docs/
├── proposal.md
├── design-document.md
├── architecture.md
└── project-phases.md
```

The vendor schema files under `schema/vendors/` are the source of truth for supported vendor syntax. The generic engines interpret these schemas rather than relying on separate hand-written vendor parser/generator modules.

`tools/schema_drafter.py` is an offline authoring and validation utility for drafting schema fragments. It does not generate parser or generator code and is not part of the runtime application pipeline.

`tests/parity/run_parity.py` provides the regression gate for schema and engine changes. It compares current batch and runtime behaviour against the committed current baseline and must report zero differences before a schema or engine change is considered complete.

---

# Technology Stack

* Python
* PySide6
* Paramiko
* Git
* GitHub

---

# Current Status

Current development stage:

**Phase 2 – Discovery and Intent-Driven Configuration Transpilation**

Implemented:

* Network Session Manager
* Discovery architecture
* Device inventory
* Vendor-neutral Intent Model
* Schema-driven configuration parsing and generation
* Cisco IOS support
* Juniper Junos support
* Bidirectional transpilation
* Interactive runtime CLI translation
* Transpilation orchestration
* Relationship Engine v1

The transpilation orchestration is implemented in:

```text
src/configbridge/transpiler/transpilation_engine.py
```

and is wired through the default vendor registry in:

```text
src/configbridge/plugins/vendor_registry.py
```

using `build_default_registry()`.

The Relationship Engine is also a real v1 implementation. Its current relationship matching is alias-based. Richer evidence such as descriptions, VLANs, LLDP/CDP, speed and other operational signals remains future work.

The safety and comparison areas remain placeholders/stubs rather than completed functionality.

Before schema or engine changes are considered complete, the parity regression gate must report zero differences:

```text
tests/parity/run_parity.py
```

Schema authoring can be assisted offline using:

```text
tools/schema_drafter.py
```

which drafts schema data for human review and validation against the real schema-driven engine.

---

# Long-Term Vision

The long-term objective of ConfigBridge is to become a discovery-assisted, relationship-aware, intent-driven platform for heterogeneous network environments.

Future versions aim to reduce the engineering effort required to support additional vendors by combining device discovery, vendor metadata and automated or semi-automated onboarding while preserving deterministic validation before deployment.

The architecture is intentionally designed to evolve without requiring fundamental redesign as additional networking technologies and vendors are incorporated.
