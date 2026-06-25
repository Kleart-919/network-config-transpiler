# Relationship Engine Design

## Introduction

The Relationship Engine is responsible for determining correspondence between network objects discovered on heterogeneous network devices.

Unlike traditional migration tools, ConfigBridge does not assume that interfaces with similar numbering schemes represent equivalent physical or logical connections.

Instead, relationships are inferred from operational evidence collected during device discovery.

---

# Motivation

Examples of interface naming include:

Cisco Catalyst 2960

```
Gi0/1
```

Cisco Catalyst 3560X

```
Gi1/0/1
```

Cisco Nexus

```
Ethernet1/1
```

Juniper EX

```
ge-0/0/0
```

Although these interfaces may perform identical networking functions, they cannot be matched reliably using numbering conventions alone.

Consequently, interface mapping becomes a relationship inference problem rather than a string translation problem.

---

# Inputs

The Relationship Engine receives:

* Source Device Inventory
* Destination Device Inventory
* Vendor-Neutral Intent Model

---

# Relationship Evidence

Potential evidence includes:

* Interface descriptions
* Operational status
* VLAN membership
* Interface speed
* LLDP neighbours
* CDP neighbours
* Port-channel membership
* MAC learning
* Hardware capabilities
* Future topology information

Each evidence source contributes to an overall relationship confidence.

---

# Output

The Relationship Engine produces a Relationship Graph.

Example:

```
Gi1/0/48

↓

Confidence = 96%

↓

ge-0/0/0
```

The resulting relationship is subsequently used by the Configuration Generator.

---

# Architectural Position

```
Discovery Framework

↓

Device Inventory

↓

Relationship Engine

↓

Vendor-Neutral Intent Model

↓

Configuration Generator
```

---

# Future Development

Future versions may include:

* Graph-based relationship analysis
* Confidence scoring algorithms
* Machine-assisted relationship inference
* Topology-aware migration
* Automatic interface correspondence
* Multi-device relationship analysis

The Relationship Engine is therefore expected to become one of the central architectural components of ConfigBridge as the project evolves.
