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

Currently implemented:

* Cisco IOS parser
* Juniper Junos parser
* Cisco IOS generator
* Juniper Junos generator
* Vendor-neutral Intent Model
* Bidirectional transpilation pipeline

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
Configuration Generators
```

---

# Current Vendor Support

### Configuration Parsing

* Cisco IOS
* Juniper Junos

### Configuration Generation

* Cisco IOS
* Juniper Junos

### Session Management

* SSH
* Telnet

Future versions will support:

* Cisco Nexus
* Aruba
* HP
* Arista EOS

---

# Planned Features

* Discovery-assisted interface relationship resolution
* Configuration comparison
* Deployment framework
* Rollback support
* Vendor plugin architecture
* Automated vendor onboarding
* Additional vendor support
* Layer 3 networking
* ACLs
* NTP
* SNMP
* QoS
* VRFs

---

# Project Structure

```text
src/
│
├── connections/
├── gui/
├── models/
├── parsers/
├── renderers/
├── plugins/
├── safety/
└── transpiler/ (planned)

docs/
│
├── proposal.md
├── design-document.md
├── architecture.md
└── project-phases.md
```

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
* Cisco and Juniper parsers
* Cisco and Juniper generators
* Bidirectional transpilation

Currently under development:

* Relationship Engine
* Discovery integration
* Transpilation framework

---

# Long-Term Vision

The long-term objective of ConfigBridge is to become a discovery-assisted, relationship-aware, intent-driven platform for heterogeneous network environments.

Future versions aim to reduce the engineering effort required to support additional vendors by combining device discovery, vendor metadata and automated onboarding while preserving deterministic validation before deployment.

The architecture is intentionally designed to evolve without requiring fundamental redesign as additional networking technologies and vendors are incorporated.