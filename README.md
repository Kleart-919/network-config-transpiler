# ConfigBridge

**ConfigBridge** is a desktop-based multi-vendor network access and configuration transpilation platform designed to simplify the management, migration, and deployment of network configurations across heterogeneous network environments.

The project combines a **Network Session Manager** with a **Configuration Transpilation Engine**, allowing network administrators and engineers to connect to devices, retrieve configurations, translate configuration intent between vendors, compare configurations, and safely deploy changes.

---

## Project Goal

Modern enterprise networks frequently contain equipment from multiple vendors such as Cisco, Juniper, Aruba, HP, Arista, and Cisco Nexus.

Although these platforms implement similar networking concepts, they expose them through different command-line interfaces, configuration models, and deployment workflows.

ConfigBridge aims to reduce the operational complexity of multi-vendor network management by translating vendor-specific configurations through a shared vendor-neutral representation.

Organizations operating heterogeneous network environments often face challenges associated with vendor-specific expertise, training requirements, migration complexity, and platform selection. Existing solutions may involve significant investment in commercial management platforms, specialist personnel, or extensive staff training across multiple vendor ecosystems.

ConfigBridge does not seek to replace vendor expertise or existing enterprise management platforms. Instead, it aims to improve accessibility, reduce migration friction, and lower the operational overhead associated with multi-vendor environments. By providing a unified access platform and a configuration transpilation engine, the project seeks to assist engineers in understanding, translating, comparing, and deploying configurations across different network operating systems while preserving vendor-specific behaviour where necessary.


Instead of relying on one-to-one command mapping, ConfigBridge uses a transpiler-inspired architecture:

```text
Any Supported Vendor Configuration
        ↓
Intermediate Intent Model
        ↓
Any Supported Vendor Configuration
```

This allows the platform to support bidirectional and multi-directional configuration translation between vendors.

---

## Key Features

### Network Session Manager

Supported protocols:

* SSH
* Telnet

Future support:

* Serial Console

Capabilities:

* Device access
* Command execution
* Session logging
* Vendor selection
* Connection history

---

### Configuration Transpilation Engine

Capabilities:

* Parse vendor-specific configuration
* Generate Abstract Syntax Trees (AST)
* Create vendor-neutral network intent
* Generate target vendor configuration
* Validate generated output

---

### Vendor Abstraction Framework

Initial support:

* Cisco IOS
* Juniper Junos

Planned support:

* Cisco Nexus NX-OS
* Aruba
* HP
* Arista EOS

Each vendor plugin contains:

* Parser
* Generator
* Validation rules
* Deployment rules
* Interface mapping rules

---

### Configuration Comparison

Compare configurations across:

* VLANs
* Interfaces
* Routing
* NTP
* SNMP
* ACLs

The comparison engine will attempt to compare configuration meaning rather than simple text differences.

---

### Risk Assessment Engine

Detect and warn about potentially dangerous operations before deployment.

Examples:

* reload
* write erase
* erase startup-config
* delete
* shutdown
* no interface

---

## High-Level Architecture

```text
User Interface
        ↓
Network Session Manager
        ↓
Vendor Abstraction Framework
        ↓
Configuration Parser
        ↓
Abstract Syntax Tree
        ↓
Intermediate Intent Model
        ↓
Configuration Generator
        ↓
Risk Assessment Engine
        ↓
Deployment Manager
```

---

## Translation Workflow

```text
Cisco IOS Configuration
        ↓
Cisco Parser
        ↓
Intermediate Intent Model
        ↓
Juniper Generator
        ↓
Juniper Configuration
```

Reverse translation:

```text
Juniper Configuration
        ↓
Juniper Parser
        ↓
Intermediate Intent Model
        ↓
Cisco Generator
        ↓
Cisco Configuration
```

General architecture:

```text
Any Vendor Parser
        ↓
Intermediate Intent Model
        ↓
Any Vendor Generator
```

---

## Technology Stack

| Component          | Technology        |
| ------------------ | ----------------- |
| Language           | Python            |
| GUI                | PySide6           |
| SSH/Telnet         | Netmiko / Scrapli |
| Parsing            | Lark              |
| Database           | SQLite            |
| Comparison         | difflib           |
| Version Control    | Git               |
| Repository Hosting | GitHub            |

---

## Project Roadmap

### Pre-Phase

* Documentation
* Architecture
* Repository setup

### Phase 1

Network Session Manager

Deliverables:

* Desktop GUI
* SSH support
* Telnet support
* Session logging

### Phase 2

Configuration Transpilation Engine

Deliverables:

* Vendor parsers
* AST generation
* Intermediate Intent Model
* Vendor generators

### Phase 3

Vendor Framework and Safety Layer

Deliverables:

* Plugin architecture
* Validation engine
* Risk assessment engine

### Phase 4

Comparison, Deployment and Evaluation

Deliverables:

* Configuration comparison
* Deployment manager
* Evaluation report

---

## Repository Structure

```text
network-config-transpiler/
├── docs/
├── sample-configs/
├── src/
│   └── configbridge/
│       ├── gui/
│       ├── connections/
│       ├── parsers/
│       ├── models/
│       ├── renderers/
│       ├── plugins/
│       ├── safety/
│       └── comparison/
└── tests/
```

---

## Status

Current Status:

**Pre-Phase – Planning and Architecture**

Next Milestone:

**Phase 1 – Network Session Manager**
