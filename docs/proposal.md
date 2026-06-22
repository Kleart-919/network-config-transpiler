# ConfigBridge: A Multi-Vendor Network Configuration Transpiler and Unified Access Management Platform

**Student:** Kleart Sufa
**Banner ID:** 001323960
**Programme:** Computer Security and Forensics BSc (Hons) with Sandwich Year
**Supervisor:** [Supervisor Placeholder]
**Repository:** https://github.com/Kleart-919/network-config-transpiler
**Submission date:** [Leave blank]

## Declaration of AI Use

AI has been used to support project planning, outline development, concept explanation, language refinement, and early documentation drafting. All final decisions, implementation work, testing, evaluation, and submitted project artefacts remain the responsibility of the student.

## Synopsis

ConfigBridge is a proposed desktop-based network management platform that combines a Network Session Manager with a Configuration Transpilation Engine. The project investigates whether a unified network access platform can automate the translation and deployment of configurations across heterogeneous network environments. The prototype will initially focus on Cisco IOS and Juniper Junos, while maintaining an extensible architecture for vendors such as Cisco Nexus, Aruba, HP and Arista.

The system will support SSH and Telnet connectivity, configuration retrieval, pasted configuration input, parsing of vendor-specific syntax, generation of an Intermediate Intent Model, and rendering of equivalent configuration for a target vendor. The project will be evaluated through translation accuracy, parsing success rate, configuration generation correctness, deployment success rate, risk detection and expert review from users with networking experience.

**Keywords:** network automation, configuration transpiler, Cisco IOS, Juniper Junos, multi-vendor networks, SSH, Telnet, network management, configuration translation, cybersecurity

# 1. Aim and Objectives

## 1.1 Aim

This project aims to design, implement and evaluate ConfigBridge, a desktop-based multi-vendor network access and configuration transpilation platform that can retrieve, parse, translate, compare and safely deploy network configurations across heterogeneous network environments.

## 1.2 Objectives

### Objective 1: Conduct background research and requirements analysis

Activities:

* Research multi-vendor network configuration challenges. [7 days]
* Review existing network automation and configuration management tools. [7 days]
* Identify functional and non-functional requirements. [5 days]

Deliverables:

* Background research notes
* Requirements specification
* Product comparison table

### Objective 2: Design the ConfigBridge system architecture

Activities:

* Design the Network Session Manager. [5 days]
* Design the Configuration Transpilation Engine. [7 days]
* Design the Intermediate Intent Model. [7 days]
* Design the Vendor Abstraction Framework. [7 days]
* Create architecture and translation pipeline diagrams. [4 days]

Deliverables:

* System architecture document
* Component diagram
* Translation pipeline diagram
* Vendor plugin design

### Objective 3: Implement the Network Session Manager

Activities:

* Build a Python desktop interface using PySide6. [10 days]
* Implement SSH connectivity. [7 days]
* Implement Telnet connectivity. [7 days]
* Add session logging and basic command execution. [5 days]

Deliverables:

* Working desktop session manager
* SSH and Telnet connection support
* Session logs

### Objective 4: Implement the Configuration Transpilation Engine

Activities:

* Build initial Cisco IOS and Juniper Junos parsers. [15 days]
* Generate an Abstract Syntax Tree from parsed configuration. [10 days]
* Convert parsed configuration into an Intermediate Intent Model. [10 days]
* Build Cisco IOS and Juniper Junos configuration generators. [15 days]

Deliverables:

* Cisco IOS parser
* Juniper Junos parser
* AST representation
* Intermediate Intent Model
* Cisco IOS generator
* Juniper Junos generator
* Cisco IOS to Juniper Junos translation
* Juniper Junos to Cisco IOS translation

### Objective 5: Implement vendor-aware safety, comparison and deployment features

Activities:

* Implement risky command detection. [7 days]
* Add confirmation before dangerous commands are executed. [5 days]
* Implement configuration comparison. [10 days]
* Implement controlled deployment workflow. [10 days]

Deliverables:

* Risk Assessment Engine
* Configuration comparison feature
* Controlled deployment workflow

### Objective 6: Test and evaluate the prototype

Activities:

* Test using sample configurations. [7 days]
* Test using real Cisco and Juniper switches where available. [10 days]
* Measure parsing success, translation accuracy and risk detection. [7 days]
* Collect technical review feedback from network engineers or experienced users. [7 days]

Deliverables:

* Test results
* Evaluation report
* Final prototype demonstration

# 2. Background Research and Project Rationale

Enterprise networks often contain devices from multiple vendors. Although these devices support similar networking concepts, such as VLANs, trunk ports, access ports, static routes, management services and access control, the syntax and deployment behaviour can vary significantly between vendors.

For example, Cisco IOS and Juniper Junos use different configuration styles and operational models. Cisco IOS typically applies configuration commands directly to the running configuration, whereas Juniper Junos uses a candidate configuration model that requires commit behaviour. This difference means that configuration migration is not simply a matter of replacing command words. It requires an understanding of configuration intent, vendor syntax, interface naming conventions and deployment behaviour.

Beyond technical differences, multi-vendor environments introduce organisational and financial challenges. Organisations may limit infrastructure decisions based on existing staff expertise, invest in additional vendor-specific training, employ specialist personnel, or purchase commercial management platforms. These approaches can increase operational cost, extend migration timelines and contribute to vendor lock-in. Therefore, a system that improves configuration understanding and translation across vendors may support more flexible infrastructure decisions and reduce operational dependency on a narrow set of skills or platforms.

Existing network automation tools can assist with device access, configuration retrieval and scripted automation. However, many tools do not directly address the problem of translating configuration intent between different vendor command-line environments. Manual translation remains common in migration or mixed-vendor environments, increasing the risk of human error and requiring specialist knowledge of multiple network operating systems.

ConfigBridge does not seek to replace vendor expertise or existing enterprise management platforms. Instead, it aims to improve accessibility, reduce migration friction and lower the operational overhead associated with heterogeneous network environments. By combining a unified access platform with a configuration transpilation engine, the project seeks to assist engineers in understanding, translating, comparing and deploying configurations across different network operating systems while preserving vendor-specific behaviour where necessary.

ConfigBridge addresses this problem by applying a transpiler-style approach. Instead of relying on static one-to-one command mappings, the system will parse vendor-specific configuration into an Abstract Syntax Tree, convert it into an Intermediate Intent Model, and then generate target vendor syntax. This approach is inspired by compiler design principles and applied to the network configuration domain.

The project is relevant to Computer Security and Forensics because secure network infrastructure depends on accurate configuration, controlled administrative access, logging and risk-aware deployment. Incorrect network configuration can weaken segmentation, expose management services, misconfigure access controls or disrupt availability. A tool that helps interpret, compare and safely deploy configurations therefore has practical value in network security and infrastructure management.

# 3. Methodology and Technical Approach

The project will use a hybrid methodology combining Design Science Research and Iterative Prototyping.

Design Science Research is suitable because the project creates and evaluates an artefact intended to address a real technical problem. The artefact is ConfigBridge itself. The research question guiding the artefact is:

**Can a unified network access platform automate the translation and deployment of configurations across heterogeneous network environments?**

Iterative Prototyping is suitable because the project contains technical uncertainty. The parser, Intermediate Intent Model, generators and deployment workflow are likely to evolve as testing is carried out against sample configurations and real network devices. This makes an incremental approach more realistic than a fixed linear development model.

The development will be organised into four major phases:

1. Pre-phase: documentation, planning and GitHub setup.
2. Phase 1: Network Session Manager.
3. Phase 2: Configuration Transpilation Engine.
4. Phase 3: Vendor Framework, safety, comparison and deployment.
5. Phase 4: testing, evaluation and final reporting.

The prototype will be developed in Python. PySide6 will be used for the desktop interface. Netmiko or Scrapli will be investigated for SSH and Telnet communication. Lark will be investigated for grammar-based parsing. SQLite may be used for local storage of device profiles and session history. Python comparison libraries such as difflib will be considered for configuration comparison.

The first implementation will focus on Cisco IOS and Juniper Junos. The intended configuration scope includes hostnames, VLANs, access ports, trunk ports, interface descriptions, allowed VLANs, static routes, default routes, NTP, SNMP and investigation of ACL translation. Cisco Nexus, Aruba, HP and Arista will be considered as future vendor plugins.

# 4. Evaluation Plan

The project will be evaluated using both quantitative and qualitative measures.

The quantitative evaluation will include:

* Parsing success rate: percentage of supported configuration blocks parsed successfully.
* Translation accuracy: percentage of generated target configuration lines judged correct.
* Configuration generation correctness: whether rendered output follows target vendor syntax.
* Deployment success rate: percentage of generated configurations successfully applied in a controlled test environment.
* Risk detection success: percentage of dangerous commands correctly flagged before execution.
* Multi-directional translation correctness: whether Cisco IOS to Juniper Junos and Juniper Junos to Cisco IOS workflows both produce valid output.

The qualitative evaluation will include expert or user review where possible. Network engineers or users with practical switching experience may be asked to review generated configurations and comment on correctness, usefulness, usability and limitations.

Testing will use both sample configuration files and real Cisco and Juniper switches where available. The evaluation will acknowledge limitations, especially where certain commands or features are not fully supported in the first prototype.

# 5. Legal, Social, Ethical and Professional Issues

ConfigBridge interacts with network infrastructure and therefore must be designed responsibly. The tool should only be used on devices where the user has permission to connect, retrieve configuration and deploy changes.

Credential handling is an important consideration. The prototype should avoid storing plaintext credentials where possible. If credentials are stored during development, this should be limited to local testing and documented clearly.

Session logs may contain sensitive information such as IP addresses, hostnames, usernames, configuration details and network topology. Therefore, logs should be treated as confidential data and excluded from public GitHub commits. The `.gitignore` file should prevent accidental upload of logs, secrets and environment files.

The project should comply with professional expectations for safe network administration. High-risk commands such as reload, erase, delete, write erase, shutdown and no interface should be detected before execution. The system should require explicit confirmation before such commands are sent to a device.

If user testing is conducted, participant consent and university ethics requirements should be followed. No unnecessary personal data should be collected.

# 6. Risk Assessment

| Risk                                                   | Likelihood | Impact | Mitigation                                         |
| ------------------------------------------------------ | ---------: | -----: | -------------------------------------------------- |
| Vendor syntax is more complex than expected            |       High |   High | Limit prototype scope to selected command families |
| ACL translation becomes too large                      |     Medium | Medium | Treat ACLs as investigatory or partial support     |
| Real hardware availability changes                     |     Medium |   High | Maintain sample config files and simulated tests   |
| SSH/Telnet libraries behave differently across devices |     Medium | Medium | Test early with Cisco and Juniper devices          |
| Time constraints affect implementation                 |     Medium |   High | Use phased delivery and prioritise core features   |
| Incorrect generated config could disrupt devices       |     Medium |   High | Use lab devices only and add risk confirmation     |
| Credentials or logs are accidentally committed         |     Medium |   High | Use `.gitignore` and avoid real secrets in files   |
| GUI development takes too long                         |     Medium | Medium | Keep the first interface simple and functional     |

# 7. Project Plan and Timeline

The planned project period is September 2026 to March 2027, with approximately 10 hours of work per week. This timeline may be adjusted when the final year schedule is confirmed.

| Period         | Activity                                          | Deliverable                                       |
| -------------- | ------------------------------------------------- | ------------------------------------------------- |
| September 2026 | Background research, requirements, product review | Research notes and requirements                   |
| October 2026   | Architecture and design                           | Architecture diagrams and design document         |
| November 2026  | Network Session Manager implementation            | SSH/Telnet prototype                              |
| December 2026  | Parser and Intermediate Intent Model              | Cisco and Juniper parsers with internal model     |
| January 2027   | Vendor generators and translation testing         | Cisco IOS and Juniper Junos translation prototype |
| February 2027  | Safety, comparison and deployment workflow        | Risk engine and config comparison                 |
| March 2027     | Evaluation, testing, final write-up               | Final prototype and report                        |

# References

References will be developed during the research phase using Harvard style. Initial sources will include academic and technical literature on network automation, compiler design, configuration management, secure network administration and vendor documentation.
