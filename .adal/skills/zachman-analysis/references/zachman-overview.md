# Zachman Framework 3.0 Complete Matrix

## Full 6x6 Matrix

```text
             │  WHAT (Data)  │  HOW (Function) │ WHERE (Network) │ WHO (People) │ WHEN (Time)  │ WHY (Motivation)│
─────────────┼───────────────┼─────────────────┼─────────────────┼──────────────┼──────────────┼─────────────────┤
 ROW 1       │ Things        │ Processes       │ Locations       │ People       │ Events       │ Ends/Means      │
 PLANNER     │ Important to  │ Performed       │ Where Business  │ Organizat.   │ Business     │ Business        │
 (Executive) │ Business      │ by Business     │ Operates        │ Structure    │ Events       │ Goals           │
─────────────┼───────────────┼─────────────────┼─────────────────┼──────────────┼──────────────┼─────────────────┤
 ROW 2       │ Business      │ Business        │ Business        │ Business     │ Business     │ Business        │
 OWNER       │ Entity        │ Process         │ Logistics       │ Workflow     │ Cycle        │ Plan            │
 (Business)  │ Model         │ Model           │ Model           │ Model        │ Model        │ Model           │
─────────────┼───────────────┼─────────────────┼─────────────────┼──────────────┼──────────────┼─────────────────┤
 ROW 3       │ Logical       │ Application     │ Distributed     │ Human        │ Event        │ Business        │
 DESIGNER    │ Data          │ Architecture    │ System          │ Interface    │ Processing   │ Rule            │
 (Architect) │ Model         │                 │ Architecture    │ Architecture │ Architecture │ Model           │
─────────────┼───────────────┼─────────────────┼─────────────────┼──────────────┼──────────────┼─────────────────┤
 ROW 4       │ Physical      │ System          │ Technology      │ Presentation │ Control      │ Rule            │
 BUILDER     │ Data          │ Design          │ Architecture    │ Architecture │ Flow         │ Specification   │
 (Engineer)  │ Model         │                 │                 │              │              │                 │
─────────────┼───────────────┼─────────────────┼─────────────────┼──────────────┼──────────────┼─────────────────┤
 ROW 5       │ Data          │ Detailed        │ Network         │ Security     │ Timing       │ Rule            │
 SUBCONTR.   │ Definition    │ Program         │ Architecture    │ Architecture │ Definition   │ Definition      │
 (Technician)│               │ Definition      │                 │              │              │                 │
─────────────┼───────────────┼─────────────────┼─────────────────┼──────────────┼──────────────┼─────────────────┤
 ROW 6       │ Operational   │ Working         │ Deployed        │ Trained      │ Operating    │ Enforced        │
 USER        │ Data          │ Application     │ Network         │ Operators    │ Events       │ Rules           │
 (Operator)  │               │                 │                 │              │              │                 │
─────────────┴───────────────┴─────────────────┴─────────────────┴──────────────┴──────────────┴─────────────────┘
```

## Cell Descriptions by Column

### Column 1: WHAT (Data/Inventory)

| Row | Cell Name | Description | Artifacts |
| --- | --- | --- | --- |
| 1 | Scope/Things | Things important to the business | Thing lists, glossary |
| 2 | Business Entities | Semantic/conceptual data model | Entity-relationship diagram |
| 3 | Logical Data | System data model | Normalized data model |
| 4 | Physical Data | Technology data model | Database schemas, DDL |
| 5 | Data Definition | Detailed specifications | Column definitions, types |
| 6 | Operational Data | Actual data instances | Production databases |

### Column 2: HOW (Function/Process)

| Row | Cell Name | Description | Artifacts |
| --- | --- | --- | --- |
| 1 | Scope/Processes | Business processes list | Process inventory |
| 2 | Business Process | Business process model | BPMN diagrams, value chains |
| 3 | Application Arch | Application architecture | Application components |
| 4 | System Design | Detailed system design | Class diagrams, APIs |
| 5 | Program Definition | Implementation specs | Code modules, methods |
| 6 | Working App | Running applications | Deployed software |

### Column 3: WHERE (Network/Distribution)

| Row | Cell Name | Description | Artifacts |
| --- | --- | --- | --- |
| 1 | Scope/Locations | Business locations | Location list, geography |
| 2 | Business Logistics | Business distribution | Logistics network |
| 3 | Distributed System | System distribution | Deployment architecture |
| 4 | Technology Arch | Infrastructure design | Network diagrams |
| 5 | Network Arch | Detailed network | IP schemes, VLANs |
| 6 | Deployed Network | Actual infrastructure | Running infrastructure |

### Column 4: WHO (People/Organization)

| Row | Cell Name | Description | Artifacts |
| --- | --- | --- | --- |
| 1 | Scope/People | Organization types | Org types, roles list |
| 2 | Business Workflow | Work organization | Org chart, workflow |
| 3 | Human Interface | User experience design | UX architecture |
| 4 | Presentation Arch | UI specifications | Screen designs |
| 5 | Security Arch | Access control design | RBAC, permissions |
| 6 | Trained Operators | Actual users | User accounts |

### Column 5: WHEN (Time/Schedule)

| Row | Cell Name | Description | Artifacts |
| --- | --- | --- | --- |
| 1 | Scope/Events | Business events | Event catalog |
| 2 | Business Cycle | Business schedule | Business calendar |
| 3 | Event Processing | Event architecture | Event flows |
| 4 | Control Flow | Process timing | State machines |
| 5 | Timing Definition | Detailed scheduling | Cron, triggers |
| 6 | Operating Events | Actual events | Runtime events |

### Column 6: WHY (Motivation/Rules)

| Row | Cell Name | Description | Artifacts |
| --- | --- | --- | --- |
| 1 | Scope/Ends | Business goals | Goal hierarchy |
| 2 | Business Plan | Strategy model | Balanced scorecard |
| 3 | Business Rules | Rule architecture | Rule engine design |
| 4 | Rule Specification | Technical rules | Validation rules |
| 5 | Rule Definition | Coded rules | Business logic code |
| 6 | Enforced Rules | Active constraints | Running validations |

## Using the Matrix Effectively

### Start with High-Impact Cells

Focus on cells that provide the most value for your context:

1. **Row 3-4, Column 1-2** - Core system design
2. **Row 4, Column 6** - Technical rules (ADRs)
3. **Row 2-3, Column 4** - User workflow

### Traceability

Each row should trace to the row above it:

- Row 6 implements Row 5
- Row 5 details Row 4
- Row 4 realizes Row 3
- Row 3 formalizes Row 2
- Row 2 interprets Row 1

## Reference

Based on Zachman Framework Standard, Version 3.0 by ZIFA.
