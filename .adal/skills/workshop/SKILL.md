---
name: workshop
description: "Facilitate structured requirements workshops (JAD-style). Guides through agenda, captures decisions, resolves conflicts, and produces consolidated requirements. Supports multiple workshop formats."
argument-hint: "[--domain <domain-name>] [--format jad|discovery|refinement|prioritization] [--duration short|standard|extended]"
allowed-tools: Task, Read, Write, Glob, Grep, Skill, AskUserQuestion
---

# Workshop Command

Facilitate structured requirements workshops following Joint Application Development (JAD) patterns.

## Interactive Workshop Configuration

Use AskUserQuestion to configure the workshop session:

```yaml
# Question 1: Workshop Format (MCP: JAD methodology patterns)
question: "What type of requirements workshop do you need?"
header: "Format"
options:
  - label: "Discovery (Recommended)"
    description: "Explore and understand the problem space"
  - label: "JAD (Full)"
    description: "Comprehensive requirements definition with all stakeholders"
  - label: "Refinement"
    description: "Clarify and decompose existing requirements"
  - label: "Prioritization"
    description: "Reach consensus on requirement priorities"

# Question 2: Session Duration (MCP: CLI best practices - scope selection)
question: "How long should the workshop session be?"
header: "Duration"
options:
  - label: "Short (Recommended)"
    description: "30 minutes - focused, single objective"
  - label: "Standard"
    description: "2 hours - full workshop with all phases"
  - label: "Extended"
    description: "4+ hours - comprehensive multi-session workshop"
```

Use these responses to tailor workshop format and time allocation.

## Usage

```bash
/requirements-elicitation:workshop
/requirements-elicitation:workshop --domain "inventory"
/requirements-elicitation:workshop --domain "crm" --format discovery
/requirements-elicitation:workshop --domain "billing" --format prioritization --duration short
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| --domain | No | Domain for the workshop (default: current/most recent) |
| --format | No | Workshop format: `jad`, `discovery`, `refinement`, `prioritization` (default: `jad`) |
| --duration | No | Expected duration: `short` (30m), `standard` (2h), `extended` (4h+) (default: `standard`) |

## Workshop Formats

### JAD (Joint Application Development)

Comprehensive requirements workshop format.

```yaml
jad_workshop:
  purpose: "Collaborative requirements definition with all stakeholders"
  participants:
    required:
      - "Executive sponsor"
      - "Business stakeholders"
      - "End users (representatives)"
      - "Technical team"
    optional:
      - "Subject matter experts"
      - "Compliance/legal"

  agenda:
    1_opening:
      duration: "15 min"
      activities:
        - "Welcome and introductions"
        - "Review objectives and ground rules"
        - "Confirm scope boundaries"

    2_context:
      duration: "30 min"
      activities:
        - "Present current state"
        - "Review known requirements"
        - "Identify gaps and pain points"

    3_requirements:
      duration: "60 min"
      activities:
        - "Brainstorm requirements by category"
        - "Clarify and refine each requirement"
        - "Identify dependencies and conflicts"
        - "Capture acceptance criteria"

    4_prioritization:
      duration: "30 min"
      activities:
        - "Apply MoSCoW or other method"
        - "Resolve priority conflicts"
        - "Define MVP scope"

    5_wrap_up:
      duration: "15 min"
      activities:
        - "Summarize decisions"
        - "Identify action items"
        - "Schedule follow-ups"
```

### Discovery Workshop

Focus on exploring and understanding the problem space.

```yaml
discovery_workshop:
  purpose: "Understand the problem before defining solutions"

  agenda:
    1_problem_statement:
      duration: "20 min"
      activities:
        - "What problem are we solving?"
        - "Who experiences this problem?"
        - "What's the impact of not solving it?"

    2_stakeholder_mapping:
      duration: "20 min"
      activities:
        - "Identify all stakeholders"
        - "Map their interests and influence"
        - "Note conflicting perspectives"

    3_current_state:
      duration: "30 min"
      activities:
        - "How is the problem handled today?"
        - "What workarounds exist?"
        - "What works well? What doesn't?"

    4_desired_state:
      duration: "30 min"
      activities:
        - "What does success look like?"
        - "What outcomes matter most?"
        - "What constraints exist?"

    5_gap_analysis:
      duration: "20 min"
      activities:
        - "What's missing to get from current to desired?"
        - "What are the biggest obstacles?"
        - "What questions remain unanswered?"
```

### Refinement Workshop

Deep dive into specific requirements for clarity and completeness.

```yaml
refinement_workshop:
  purpose: "Clarify, decompose, and validate existing requirements"

  agenda:
    1_review:
      duration: "15 min"
      activities:
        - "Review requirements to refine"
        - "Identify ambiguities"
        - "Note questions and concerns"

    2_clarification:
      duration: "45 min"
      per_requirement:
        - "Read requirement aloud"
        - "Identify vague terms"
        - "Define acceptance criteria"
        - "Capture edge cases"

    3_decomposition:
      duration: "30 min"
      activities:
        - "Break large requirements into smaller pieces"
        - "Identify hidden sub-requirements"
        - "Map dependencies"

    4_validation:
      duration: "20 min"
      activities:
        - "Verify with stakeholders"
        - "Check for completeness"
        - "Confirm priority still accurate"

    5_documentation:
      duration: "10 min"
      activities:
        - "Update requirement statements"
        - "Document decisions made"
        - "Note open questions"
```

### Prioritization Workshop

Focused session for requirement prioritization decisions.

```yaml
prioritization_workshop:
  purpose: "Reach consensus on requirement priorities"

  agenda:
    1_context:
      duration: "10 min"
      activities:
        - "Review constraints (time, budget, resources)"
        - "Confirm prioritization criteria"
        - "Select prioritization method"

    2_scoring:
      duration: "40 min"
      activities:
        - "Apply selected method (MoSCoW, WSJF, etc.)"
        - "Capture individual scores"
        - "Identify disagreements"

    3_conflict_resolution:
      duration: "20 min"
      activities:
        - "Discuss divergent scores"
        - "Present different perspectives"
        - "Reach consensus or escalate"

    4_finalization:
      duration: "10 min"
      activities:
        - "Document final priorities"
        - "Define MVP scope"
        - "Plan for deferred items"
```

## Workshop Workflow

### Pre-Workshop

```yaml
pre_workshop:
  1. Identify and invite participants
  2. Distribute pre-read materials
  3. Prepare agenda and templates
  4. Set up collaboration tools
  5. Define ground rules
```

### During Workshop

```yaml
during_workshop:
  facilitator_responsibilities:
    - "Keep discussion on track"
    - "Ensure all voices are heard"
    - "Capture decisions and action items"
    - "Manage time"
    - "Resolve or park conflicts"

  capture_template:
    requirement:
      id: "REQ-xxx"
      statement: "..."
      rationale: "Why is this needed?"
      source: "Who requested this?"
      priority: "must|should|could|wont"
      acceptance_criteria: ["..."]
      questions: ["..."]
      decisions: ["..."]
```

### Post-Workshop

```yaml
post_workshop:
  1. Consolidate notes and decisions
  2. Distribute summary to participants
  3. Update requirements repository
  4. Schedule follow-up sessions
  5. Track action items to completion
```

## Workshop Output

```yaml
workshop_report:
  metadata:
    domain: "{domain}"
    format: "jad"
    date: "{ISO-8601}"
    duration: "2 hours"
    facilitator: "Claude AI"

  participants:
    present:
      - role: "Product Owner"
        name: "Simulated"
      - role: "End User Rep"
        name: "Simulated"
      - role: "Technical Lead"
        name: "Simulated"

  agenda_outcomes:
    opening:
      objectives_confirmed: true
      scope_boundaries: ["...", "..."]

    context:
      current_state_summary: "..."
      known_gaps: ["...", "..."]

    requirements:
      new_requirements: 12
      refined_requirements: 8
      removed_requirements: 2

    prioritization:
      method_used: "MoSCoW"
      must_count: 5
      should_count: 8
      could_count: 4
      wont_count: 3

  requirements_captured:
    - id: "REQ-WS-001"
      statement: "..."
      priority: "must"
      acceptance_criteria: ["..."]
      decided_by: "consensus"

  decisions_made:
    - topic: "Authentication approach"
      decision: "Use OAuth2 with SSO"
      rationale: "Enterprise requirement"
      participants: ["all"]

  action_items:
    - action: "Validate security requirements with InfoSec"
      owner: "Technical Lead"
      due_date: "2025-01-03"
      status: "open"

  parking_lot:
    - item: "Mobile app scope"
      reason: "Out of scope for this release"
      revisit_date: "Q2 planning"

  open_questions:
    - question: "Integration with legacy system?"
      assigned_to: "Technical Lead"
      due_date: "2025-01-05"

  next_steps:
    - "Distribute workshop summary"
    - "Schedule refinement session for top 5 requirements"
    - "Set up stakeholder validation meeting"
```

## Example Session

```text
/requirements-elicitation:workshop --domain "expense-management" --format discovery

═══════════════════════════════════════════════
REQUIREMENTS WORKSHOP: expense-management
Format: Discovery Workshop
═══════════════════════════════════════════════

📋 AGENDA
1. Problem Statement (20 min)
2. Stakeholder Mapping (20 min)
3. Current State Analysis (30 min)
4. Desired State Vision (30 min)
5. Gap Analysis (20 min)

─────────────────────────────────────────────
PHASE 1: PROBLEM STATEMENT
─────────────────────────────────────────────

Facilitator: "What problem are we solving?"

Captured problem statement:
"Employees spend excessive time on expense reporting,
finance struggles with policy compliance, and managers
lack visibility into team spending."

Impact of not solving:
• 4+ hours/month per employee on expense admin
• 15% of expense reports require rework
• Late reimbursements affect employee satisfaction
• Limited spend visibility for budgeting

─────────────────────────────────────────────
PHASE 2: STAKEHOLDER MAPPING
─────────────────────────────────────────────

Stakeholders identified:
┌─────────────────────────────────────────┐
│ HIGH INFLUENCE                          │
│   CFO - Budget control, policy owner    │
│   Finance Team - Processing, compliance │
├─────────────────────────────────────────┤
│ HIGH INTEREST                           │
│   Employees - Submit expenses           │
│   Managers - Approve, budget visibility │
└─────────────────────────────────────────┘

Conflicting interests noted:
• Finance wants stricter controls
• Employees want faster approval
• Managers want flexibility within budget

─────────────────────────────────────────────
PHASE 3: CURRENT STATE
─────────────────────────────────────────────

Current process:
1. Employee collects paper receipts
2. Fills Excel template
3. Emails to manager
4. Manager reviews, forwards to finance
5. Finance validates against policy
6. Finance processes reimbursement

Pain points:
❌ Paper receipts get lost (35% of claims)
❌ No mobile capture option
❌ Manual policy checking (error-prone)
❌ No real-time spending visibility
❌ Reimbursement takes 2-3 weeks

What works:
✓ Familiar Excel format
✓ Manager approval chain

─────────────────────────────────────────────
PHASE 4: DESIRED STATE
─────────────────────────────────────────────

Success vision:
"One-tap expense capture from mobile, automatic
policy validation, real-time approval workflow,
and same-week reimbursement."

Key outcomes:
• <5 min per expense report
• 0% policy violations at submission
• <3 days to reimbursement
• Real-time budget visibility

─────────────────────────────────────────────
PHASE 5: GAP ANALYSIS
─────────────────────────────────────────────

Critical gaps:
1. No mobile capture → Need mobile app
2. Manual validation → Need policy engine
3. Email workflow → Need approval system
4. No visibility → Need dashboard

Requirements emerging:
• Mobile receipt capture with OCR
• Automated policy validation
• Multi-level approval workflow
• Real-time budget dashboard
• Integration with payroll

═══════════════════════════════════════════════
WORKSHOP COMPLETE
═══════════════════════════════════════════════

Summary:
• Problem clearly defined ✓
• 6 stakeholders mapped ✓
• 8 pain points identified ✓
• 5 desired outcomes defined ✓
• 12 requirement candidates generated ✓

Saved to: .requirements/expense-management/workshop/WS-20251226-170000.yaml

Next steps:
1. Run /simulate to validate from stakeholder perspectives
2. Run /brainstorm for additional feature ideas
3. Run /discover to formalize requirements
```

## Output Locations

```yaml
output_locations:
  report: ".requirements/{domain}/workshop/WS-{timestamp}.yaml"
  requirements: ".requirements/{domain}/workshop/requirements-{timestamp}.yaml"
  decisions: ".requirements/{domain}/workshop/decisions-{timestamp}.yaml"
```

## Integration with Other Commands

### Before Workshop

```bash
# Gather context
/requirements-elicitation:research --domain "expenses"

# Review existing requirements
/requirements-elicitation:gaps --domain "expenses"
```

### After Workshop

```bash
# Validate with stakeholder simulation
/requirements-elicitation:simulate --domain "expenses"

# Prioritize captured requirements
/requirements-elicitation:prioritize --domain "expenses" --method moscow

# Export to formal format
/requirements-elicitation:export --domain "expenses" --format ears
```

## Error Handling

```yaml
error_handling:
  insufficient_context:
    message: "Not enough context for workshop"
    action: "Run /research or /discover first"

  no_stakeholders:
    message: "No stakeholder perspectives available"
    action: "Run /simulate to create personas first"
```
