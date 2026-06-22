Diagram 1

High-Level System Architecture

User Interface
        ↓
Network Session Manager
        ↓
Vendor Abstraction Layer
        ↓
Parser
        ↓
AST
        ↓
Intent Model
        ↓
Renderer
        ↓
Risk Engine
        ↓
Deployment Manager
Diagram 2

Translation Pipeline

Cisco Config
     ↓
Parser
     ↓
AST
     ↓
Intent Model
     ↓
Juniper Renderer
     ↓
Juniper Config
Diagram 3

Vendor Plugin Architecture

Vendor Plugin
│
├── Parser
├── Renderer
├── Validator
├── Deployment Rules
└── Interface Mapper
Diagram 4

Deployment Workflow

Generated Config
       ↓
Risk Assessment
       ↓
Confirmation
       ↓
Deployment
       ↓
Save / Commit