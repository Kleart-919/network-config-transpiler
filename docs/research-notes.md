# Architectural Decisions

## Purpose

This document records the major architectural decisions made during the development of ConfigBridge together with the engineering rationale behind each decision.

The purpose of this document is to capture the evolution of the system architecture and explain why specific design decisions were made throughout implementation.

---

# Decision 1 – Vendor-Neutral Intent Model

## Problem

Direct command translation requires vendor-to-vendor mappings.

As the number of supported vendors increases, the number of translation paths increases rapidly.

## Decision

Represent network behaviour using a Vendor-Neutral Intent Model rather than direct command mappings.

## Rationale

Every parser converts vendor syntax into the same internal representation.

Every generator consumes the same internal representation.

This significantly improves scalability and simplifies future vendor integration.

---

# Decision 2 – Discovery Before Transpilation

## Problem

Configuration alone does not describe the physical characteristics of a network device.

Successful migration requires knowledge of the destination device.

## Decision

Introduce a Discovery Framework before transpilation.

## Rationale

The Discovery Framework analyses the connected device and constructs a Device Inventory before any configuration generation occurs.

This reduces assumptions regarding heterogeneous hardware platforms.

---

# Decision 3 – Device Inventory

## Problem

Operational information and configuration intent represent different types of knowledge.

Mixing both concepts reduces maintainability.

## Decision

Create a dedicated Device Inventory model.

## Rationale

The Device Inventory stores operational device characteristics independently from configuration intent.

This separation improves architectural clarity while supporting future discovery capabilities.

---

# Decision 4 – Relationship Engine

## Problem

Interface names cannot reliably identify corresponding physical interfaces across different vendors or even different hardware models from the same vendor.

## Decision

Introduce a Relationship Engine.

## Rationale

Rather than assuming direct interface equivalence, relationships are inferred from operational evidence obtained during device discovery.

Future implementations may assign confidence values to inferred relationships before deployment.

---

# Decision 5 – Plugin-Based Vendor Support

## Problem

Embedding vendor-specific logic throughout the application reduces maintainability.

## Decision

Implement independent vendor plugins.

## Rationale

Each vendor contributes:

* Discovery Parser
* Configuration Parser
* Configuration Generator
* Vendor Metadata

The remainder of the architecture remains vendor-neutral.

---

# Decision 6 – Unified Network Session Manager

## Problem

Communication protocols should not influence higher architectural layers.

## Decision

Separate communication into an independent Network Session Manager.

## Rationale

SSH, Telnet and future communication protocols become interchangeable without affecting discovery or transpilation.

---

# Decision 7 – Vendor Templates

## Problem

Hardcoding generator syntax reduces maintainability.

## Decision

Move vendor syntax into reusable metadata templates.

## Rationale

Future generators can become increasingly data-driven rather than relying on hardcoded implementation.

---

# Decision 8 – Cost and Accessibility

## Problem

Multi-vendor environments frequently require additional investment in training, specialist recruitment or commercial management platforms.

## Decision

Design ConfigBridge to improve accessibility rather than replace professional network engineers.

## Rationale

The objective is to reduce migration effort, improve operational accessibility and support cost avoidance while preserving engineering validation and decision making.

---

# Future Architectural Decisions

The following decisions remain under investigation.

* Automated vendor onboarding.
* Relationship confidence scoring.
* Knowledge-assisted vendor integration.
* Topology-aware relationship inference.
* Automated parser and generator generation.
