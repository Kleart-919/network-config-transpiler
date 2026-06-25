# Project Proposal

## Project Title

**ConfigBridge – A Discovery-Assisted Multi-Vendor Network Configuration Transpilation and Unified Network Access Platform**

---

## Student Details

**Student Name:** Kleart Sufa

**Student ID:** 001323960

**Programme:** BSc (Hons) Computer Security and Forensics (Sandwich)

**Supervisor:** *To be confirmed*

---

# 1. Introduction

Enterprise networks increasingly operate heterogeneous infrastructures consisting of equipment from multiple vendors, including Cisco, Juniper, Aruba, Hewlett Packard Enterprise (HPE), Arista and Cisco Nexus platforms. These environments arise through phased hardware replacement, mergers, acquisitions, procurement strategies and differing technical requirements.

Although these platforms implement many equivalent networking concepts, they expose those concepts through different command-line interfaces, configuration syntaxes and operational workflows. Consequently, engineers managing heterogeneous environments must either maintain expertise across multiple vendor ecosystems or organisations must invest in specialist recruitment, vendor-specific certification programmes and commercial multi-vendor management platforms.

Configuration migration between vendors is frequently performed manually, requiring engineers to understand both the source and destination operating systems before rewriting configuration. This process is time-consuming, error-prone and difficult to scale as additional vendors are introduced.

ConfigBridge proposes a different architectural approach.

Rather than translating vendor commands directly, the system discovers the connected device, constructs a vendor-neutral representation of network intent and generates equivalent configuration for the target platform using a layered software architecture.

The objective is not to replace experienced network engineers but to reduce migration effort, improve accessibility within heterogeneous environments and support cost avoidance while preserving engineering control and validation.

---

# 2. Problem Statement

Current multi-vendor network administration presents both technical and organisational challenges.

From a technical perspective, equivalent networking concepts are represented using different syntaxes, configuration structures and deployment workflows.

Examples include:

* Layer 2 interface configuration
* VLAN management
* Interface descriptions
* Configuration deployment
* Vendor-specific operational behaviour

From an organisational perspective, heterogeneous environments often require organisations to:

* recruit engineers with expertise across multiple vendor ecosystems;
* invest in vendor-specific training and certification programmes;
* purchase commercial multi-vendor management platforms;
* dedicate significant engineering effort to configuration migration; and
* make infrastructure decisions based upon existing staff familiarity rather than technical suitability.

While several commercial products provide multi-vendor management capabilities, these platforms are often proprietary, costly and primarily focused on orchestration rather than configuration transpilation.

Furthermore, many existing approaches rely upon direct command mappings between vendors. Such approaches become increasingly difficult to maintain as the number of supported vendors increases.

This project investigates whether a discovery-assisted, intent-driven architecture can provide a more scalable foundation for multi-vendor configuration transpilation.

---

# 3. Aim

The aim of this project is to design and implement ConfigBridge, a discovery-assisted multi-vendor network configuration transpilation platform capable of understanding network configurations through a vendor-neutral intermediate representation while supporting interactive network administration through a unified network session manager.

Unlike direct command translation systems, ConfigBridge first discovers the connected device, constructs an operational inventory, resolves relationships between network objects and subsequently generates vendor-specific configuration from a shared vendor-neutral intent model.

This architecture aims to improve extensibility while reducing dependence on vendor-specific implementation throughout the remainder of the system.

---

# 4. Objectives

The project objectives are:

* Design and implement a unified Network Session Manager supporting SSH and Telnet connectivity.
* Develop a Discovery Framework capable of analysing connected network devices.
* Construct a Device Inventory representing operational device characteristics.
* Design a Relationship Engine capable of resolving relationships between network objects.
* Develop a Vendor-Neutral Intent Model representing network behaviour independently of vendor syntax.
* Implement configuration parsers for Cisco IOS and Juniper Junos.
* Implement configuration generators for Cisco IOS and Juniper Junos.
* Demonstrate bidirectional configuration transpilation between Cisco IOS and Juniper Junos.
* Design a plugin architecture supporting future vendor integration.
* Investigate future automated vendor onboarding through vendor documentation and configuration knowledge extraction.
# 5. Proposed Solution

ConfigBridge proposes a layered software architecture that separates communication, discovery, relationship analysis, network intent and configuration generation into independent software components.

The proposed workflow differs significantly from traditional command translation systems.

Instead of translating directly between vendor-specific commands, ConfigBridge performs a sequence of independent operations.

```
Network Session

↓

Device Discovery

↓

Device Inventory

↓

Relationship Analysis

↓

Vendor-Neutral Intent Model

↓

Configuration Generation
```

This separation enables vendor-specific syntax to remain isolated while the remainder of the system operates on vendor-neutral representations.

The proposed architecture also supports future expansion through additional vendor plugins without requiring redesign of the core system.

---

# 6. System Design Overview

The system consists of seven primary architectural components.

### Network Session Manager

Provides interactive communication with network devices through SSH and Telnet.

Responsibilities include:

* session establishment;
* interactive terminal communication;
* session logging;
* connection lifecycle management.

Future versions may support Serial Console, NETCONF and REST APIs.

---

### Discovery Framework

The Discovery Framework analyses connected devices before transpilation begins.

Rather than assuming hardware layouts or interface numbering, ConfigBridge collects operational information from the connected device.

Typical discovery information includes:

* running configuration;
* interface status;
* VLAN information;
* LLDP/CDP neighbours;
* operational interface characteristics.

The Discovery Framework constructs a Device Inventory representing the current state of the connected infrastructure.

---

### Device Inventory

The Device Inventory represents operational knowledge rather than configuration intent.

It stores information such as:

* hostname;
* vendor;
* interface inventory;
* operational status;
* interface descriptions;
* VLAN membership;
* neighbour information.

Multiple inventories may exist simultaneously when migrating configurations between different devices.

---

### Relationship Engine

The Relationship Engine is responsible for determining correspondence between network objects.

Unlike traditional migration tools, ConfigBridge does not assume that similarly numbered interfaces represent equivalent physical connections.

Instead, relationships are inferred from discovered operational information.

Examples include:

* interface descriptions;
* operational status;
* VLAN membership;
* LLDP/CDP neighbours;
* interface speed;
* link aggregation information.

Future implementations may associate confidence values with inferred relationships before presenting them for engineer validation.

---

### Vendor-Neutral Intent Model

The Intent Model represents network behaviour independently of vendor syntax.

It stores networking concepts such as:

* hostnames;
* VLANs;
* Layer 2 interface behaviour;
* access ports;
* trunk ports;
* interface descriptions.

Every parser produces the same Intent Model regardless of vendor.

Every generator consumes the same Intent Model regardless of vendor.

---

### Configuration Parsers

Vendor-specific parsers convert configuration syntax into the Vendor-Neutral Intent Model.

Current implementation includes:

* Cisco IOS Parser
* Juniper Junos Parser

Future versions will extend support to additional vendors including Cisco Nexus, Aruba, HP and Arista EOS.

---

### Configuration Generators

Configuration generators convert the Vendor-Neutral Intent Model into vendor-specific configuration.

Current implementation includes:

* Cisco IOS Generator
* Juniper Junos Generator

Future generators will support additional vendors through the same plugin architecture.

---

# 7. Proposed Methodology

The project follows a hybrid iterative software engineering methodology.

Development is organised into incremental phases, with each phase producing a functional prototype while simultaneously refining the overall architecture.

Rather than attempting to implement complete vendor support immediately, each iteration validates a subset of networking concepts before extending functionality.

The implementation strategy consists of:

**Phase 1**

* Network Session Manager
* SSH support
* Telnet support
* Interactive terminal
* Session logging

**Phase 2**

* Discovery Framework
* Device Inventory
* Relationship Engine
* Vendor-Neutral Intent Model
* Cisco and Juniper parsers
* Cisco and Juniper generators
* Bidirectional transpilation pipeline

**Phase 3**

* Configuration comparison
* Deployment framework
* Validation mechanisms
* Rollback support
* Additional vendor integration

This iterative approach reduces implementation risk while ensuring that architectural decisions are validated before significant feature expansion.

---

# 8. Technology Stack

The current implementation uses Python due to its extensive networking ecosystem and rapid development capabilities.

Primary technologies include:

* Python 3
* PySide6
* Paramiko
* Socket programming
* Git
* GitHub

The application is currently implemented as a desktop application targeting Microsoft Windows.

The architecture has been designed so that future API or web interfaces could be introduced without requiring significant redesign of the underlying transpilation framework.
# 9. Expected Outcomes

The primary outcome of this project is a functional proof-of-concept demonstrating that heterogeneous network configurations can be represented through a vendor-neutral intermediate model and regenerated for multiple network operating systems.

The completed prototype is expected to provide:

* A unified Network Session Manager supporting interactive SSH and Telnet connectivity.
* A Discovery Framework capable of analysing connected network devices.
* A Device Inventory representing the operational characteristics of discovered devices.
* A Relationship Engine capable of resolving relationships between network objects across heterogeneous platforms.
* A Vendor-Neutral Intent Model representing network behaviour independently of vendor syntax.
* Cisco IOS configuration parsing.
* Juniper Junos configuration parsing.
* Cisco IOS configuration generation.
* Juniper Junos configuration generation.
* Bidirectional configuration transpilation between Cisco IOS and Juniper Junos.

Beyond demonstrating successful transpilation, the project aims to validate the proposed software architecture as a scalable foundation for future multi-vendor network management.

---

# 10. Success Criteria

The project will be considered successful if it demonstrates the following:

### Network Session Manager

* Successful SSH connectivity.
* Successful Telnet connectivity.
* Interactive terminal sessions.
* Session logging.
* Stable communication with physical network devices.

### Discovery Framework

* Successful collection of operational device information.
* Construction of a Device Inventory representing the connected infrastructure.
* Successful interface discovery from supported vendors.

### Intent-Based Configuration Processing

* Successful parsing of Cisco IOS configuration.
* Successful parsing of Juniper Junos configuration.
* Successful generation of Cisco IOS configuration from the Vendor-Neutral Intent Model.
* Successful generation of Juniper Junos configuration from the Vendor-Neutral Intent Model.
* Successful bidirectional transpilation between Cisco IOS and Juniper Junos.

### Architecture

* Clear separation between communication, discovery, relationship analysis, intent modelling and configuration generation.
* Extensible plugin architecture capable of supporting future vendors.
* Validation that vendor-specific syntax remains isolated from the remainder of the system.

---

# 11. Risks and Limitations

Several technical challenges have been identified during the design process.

### Vendor Diversity

Different vendors implement equivalent networking concepts using significantly different configuration syntaxes and operational workflows.

The current implementation therefore focuses on validating the architecture using a representative subset of Layer 2 networking concepts before extending support to more advanced technologies.

---

### Hardware Differences

Different hardware platforms frequently expose different interface layouts, naming conventions and capabilities.

Consequently, ConfigBridge avoids assuming that similarly numbered interfaces represent equivalent physical connections.

Instead, future development will extend the Relationship Engine to infer relationships from discovered operational characteristics.

---

### Vendor-Specific Features

Certain platform capabilities may not have direct equivalents on other vendors.

In these situations, the project aims to preserve networking intent wherever possible while identifying vendor-specific functionality requiring manual review.

---

### Scope Management

Supporting every networking feature across multiple vendors is beyond the scope of an undergraduate final-year project.

The current implementation therefore focuses on validating the architectural approach rather than providing complete vendor coverage.

---

# 12. Project Timeline

The proposed implementation schedule is:

| Phase            | Activities                                                                                                      |
| ---------------- | --------------------------------------------------------------------------------------------------------------- |
| Phase 1          | Network Session Manager, SSH, Telnet, interactive terminal, logging                                             |
| Phase 2          | Discovery Framework, Device Inventory, Relationship Engine, Intent Model, parsers, generators and transpilation |
| Phase 3          | Configuration comparison, deployment framework, validation, rollback support and additional vendor integration  |
| Final Evaluation | Testing, performance evaluation, documentation and dissertation preparation                                     |

Development will follow an iterative approach, allowing architectural refinement throughout implementation.

---

# 13. Evaluation

The completed prototype will be evaluated using both functional and architectural criteria.

Functional evaluation will include:

* successful communication with physical Cisco and Juniper devices;
* successful parsing of representative configurations;
* successful bidirectional configuration generation;
* successful discovery of connected devices;
* successful relationship resolution using discovered device information.

Architectural evaluation will consider:

* maintainability;
* modularity;
* extensibility;
* scalability;
* separation of concerns.

The evaluation will also consider whether the proposed architecture provides a practical foundation for future vendor integration and automated vendor onboarding.

---

# 14. Ethical and Professional Considerations

ConfigBridge is intended to assist qualified network engineers rather than replace professional judgement.

Configuration transpilation and relationship inference should therefore be treated as engineering assistance rather than authoritative configuration generation.

Future deployment workflows should include validation and approval before configurations are applied to production infrastructure.

This approach supports responsible engineering practice while reducing operational risk.

---

# 15. Conclusion

ConfigBridge proposes a discovery-assisted, intent-driven architecture for multi-vendor network configuration transpilation.

By separating communication, discovery, relationship analysis, vendor-neutral intent and configuration generation into independent software components, the proposed architecture improves maintainability, scalability and future extensibility.

The project aims to demonstrate that heterogeneous network configurations can be understood through a shared internal representation while reducing migration effort, improving accessibility and supporting cost avoidance within multi-vendor environments.

The resulting architecture provides a strong foundation for future research into automated vendor onboarding, relationship inference and scalable heterogeneous network management.
