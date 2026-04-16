# Zachman Framework Code Extraction Limitations

## Overview

This document details what can and cannot be extracted from code analysis for each Zachman Framework row.

## Row-by-Row Analysis

### Row 1: Planner/Executive (Scope)

**Code Extraction Capability:** Cannot Extract

**Why:**

- Strategic context exists outside codebase
- Executive vision requires stakeholder input
- Business context not captured in code
- Market and competitive considerations absent

**What's Needed Instead:**

- Stakeholder interviews
- Strategic planning documents
- Board presentations
- Business cases

**Column-Specific Gaps:**

| Column | Cannot Extract | Requires |
| --- | --- | --- |
| What | Business entity identification | Business glossary, domain experts |
| How | Core process definition | Process documentation |
| Where | Business geography | Location strategy documents |
| Who | Organizational mission | Org strategy |
| When | Business cycles | Business calendar, planning docs |
| Why | Strategic goals | Mission/vision statements |

---

### Row 2: Owner/Business (Model)

**Code Extraction Capability:** Cannot Extract

**Why:**

- Business models are conceptual
- Domain knowledge implicit, not explicit
- Business logic intent vs. implementation differs
- Organizational workflow not in code

**What's Needed Instead:**

- Business analysts
- Domain experts
- Process owners
- Business documentation

**Column-Specific Gaps:**

| Column | Cannot Extract | Requires |
| --- | --- | --- |
| What | Business semantics | Domain-driven design sessions |
| How | Business process intent | BPMN diagrams, interviews |
| Where | Logistics rationale | Supply chain documentation |
| Who | Work organization logic | Org design documents |
| When | Business timing rules | SLA documents, contracts |
| Why | Business strategy | Strategic plans |

---

### Row 3: Designer/Architect (Logical)

**Code Extraction Capability:** Partial

**Can Extract:**

- Code structure patterns
- Module organization
- Interface definitions
- Data relationships (from schema)

**Cannot Extract:**

- Design rationale (unless ADRs exist)
- Alternative approaches considered
- Future evolution plans
- Trade-off decisions

**Column-Specific Capabilities:**

| Column | Can Extract | Cannot Extract |
| --- | --- | --- |
| What | Entity relationships | Model intent, domain meaning |
| How | Component interactions | Design alternatives |
| Where | Deployment architecture | Distribution rationale |
| Who | User interface patterns | UX research insights |
| When | Event flow patterns | Timing rationale |
| Why | Coded constraints | Business rule origins |

---

### Row 4: Builder/Engineer (Physical)

**Code Extraction Capability:** Strong

**Can Extract:**

- Database schemas
- API specifications
- Infrastructure as code
- Build configurations
- Technology choices

**Limitations:**

- "Why this technology" requires ADRs
- Evolution history needs git archaeology
- Integration complexity may be obscured

**Column-Specific Capabilities:**

| Column | Strong Extraction | Partial Extraction |
| --- | --- | --- |
| What | Schemas, types, models | Data lineage |
| How | APIs, functions, services | Algorithm intent |
| Where | Deployment configs | Scaling rationale |
| Who | Auth code, RBAC | UX rationale |
| When | Schedulers, triggers | Timing trade-offs |
| Why | Validation rules, ADRs | Business origins |

---

### Row 5: Subcontractor/Technician (Detail)

**Code Extraction Capability:** Strong

**Can Extract:**

- Detailed code implementation
- Configuration files
- Network configurations
- Security settings
- Build scripts

**Column-Specific Capabilities:**

| Column | Can Extract |
| --- | --- |
| What | Column definitions, data types |
| How | Method implementations |
| Where | Network configs, firewall rules |
| Who | Permission definitions |
| When | Cron expressions, timing configs |
| Why | Constraint definitions |

---

### Row 6: User/Operations (Runtime)

**Code Extraction Capability:** Limited

**Can Extract:**

- Deployment manifests
- Runtime configurations
- Default operational parameters

**Cannot Extract (Requires Runtime Access):**

- Actual data volumes
- Performance metrics
- User behavior patterns
- Operational incidents

**What's Needed:**

- Monitoring systems (APM, logs)
- Database queries (production access)
- User analytics
- Operations documentation

## Summary Matrix

| Row | Extraction Level | Primary Source |
| --- | --- | --- |
| 1 Planner | None | Stakeholders, strategy docs |
| 2 Owner | None | Business analysts, domain experts |
| 3 Designer | Partial | Code + ADRs + architects |
| 4 Builder | Strong | Code + configs |
| 5 Subcontractor | Strong | Code + detailed configs |
| 6 User | Limited | Runtime systems + operators |

## Implications for Automation

### Fully Automatable

- Row 4-5 data extraction
- Schema analysis
- Dependency mapping
- Configuration discovery

### Partially Automatable

- Row 3 structure inference
- Pattern detection
- Consistency checking

### Requires Human Input

- Rows 1-2 content
- Design rationale
- Business context
- Strategic alignment
