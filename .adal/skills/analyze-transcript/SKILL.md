---
name: analyze-transcript
description: Analyze meeting transcripts to extract requirements, decisions, and action items. Specialized extraction for conversational content.
argument-hint: <transcript-path> [--domain <domain-name>] [--speakers <speaker-roles>]
allowed-tools: Read, Glob, Grep, Write, Skill
---

# Analyze Transcript Command

Extract requirements and decisions from meeting transcripts and conversational content.

## Usage

```bash
/requirements-elicitation:analyze-transcript ./meetings/kickoff-notes.md
/requirements-elicitation:analyze-transcript ./transcripts/stakeholder-call.txt --domain "checkout"
/requirements-elicitation:analyze-transcript ./notes/*.md --speakers "PM:ProductManager,TL:TechLead,UX:Designer"
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| transcript-path | Yes | Path to transcript file or glob pattern |
| --domain | No | Domain name for organizing output |
| --speakers | No | Speaker role mapping (format: `abbreviation:Role`) |

## What It Extracts

### Requirements

- Explicitly stated requirements
- Implied requirements from discussions
- Feature requests and suggestions

### Decisions

- Agreed-upon approaches
- Technology choices
- Scope decisions

### Action Items

- Commitments made
- Follow-up tasks
- Assignments

### Concerns

- Risks identified
- Issues raised
- Open questions

## Extraction Patterns

### Decision Markers

```text
"We decided that..."
"The conclusion is..."
"Going with [option]..."
"Agreed: ..."
"Decision: ..."
```

### Action Item Markers

```text
"Action: [name] will..."
"TODO: ..."
"[Name] to follow up on..."
"We need to..."
"Next step: ..."
```

### Requirement Discussions

```text
"The system should..."
"Users need to be able to..."
"It must handle..."
"Requirements: ..."
"Feature request: ..."
```

### Concern Markers

```text
"I'm concerned about..."
"Risk: ..."
"Issue: ..."
"What if...?"
"Problem: ..."
```

## Workflow

### Step 1: Load Transcript

Read the transcript file(s) using the Read tool.

### Step 2: Identify Speakers

If --speakers provided, use the mapping.
Otherwise, attempt to identify speakers from patterns like:

- `[Name]:` or `Name:`
- `**Name**:`
- Speaker labels in transcript format

### Step 3: Extract Content

Spawn `document-miner` agent with transcript-specific extraction patterns.

Extract:

1. Requirements (explicit and implicit)
2. Decisions
3. Action items
4. Concerns and risks

### Step 4: Attribute and Weight

For each extraction:

- Note the speaker (if identifiable)
- Apply weighting based on speaker role
- Record surrounding context

### Step 5: Save and Report

Save to `.requirements/{domain}/transcripts/`
Report summary of findings.

## Speaker Weighting

```yaml
speaker_weights:
  product_owner: high    # Business requirements
  technical_lead: high   # Technical constraints
  stakeholder: high      # Domain requirements
  developer: medium      # Implementation insights
  designer: medium       # UX requirements
  unknown: low           # Needs validation
```

## Examples

### Basic Transcript Analysis

```bash
/requirements-elicitation:analyze-transcript ./meetings/sprint-planning.md
```

Output:

```text
Analyzing: sprint-planning.md

Speakers identified:
- PM (ProductManager): 45 statements
- TL (TechLead): 32 statements
- DEV (Developer): 28 statements

Extraction Results:

REQUIREMENTS (8):
- REQ-TR-001: "Users shall receive email notifications for order status" [PM, High]
- REQ-TR-002: "API response time must be under 200ms" [TL, High]
...

DECISIONS (3):
- DEC-001: "Use PostgreSQL for primary database" [TL]
- DEC-002: "Target launch date: Q2 2025" [PM]
...

ACTION ITEMS (5):
- ACT-001: "TL to create database schema document"
- ACT-002: "PM to get stakeholder sign-off"
...

CONCERNS (2):
- CONCERN-001: "Third-party API reliability" [TL]
- CONCERN-002: "Training timeline for new features" [PM]

Saved to: .requirements/sprint-planning/transcripts/TR-sprint-planning.yaml
```

### With Speaker Mapping

```bash
/requirements-elicitation:analyze-transcript ./calls/client-call.txt \
  --speakers "JD:ClientCEO,SM:SalesManager,PM:ProductManager" \
  --domain "enterprise-deal"
```

Output:

```text
Analyzing: client-call.txt

Speaker Mapping Applied:
- JD → ClientCEO (weight: high)
- SM → SalesManager (weight: medium)
- PM → ProductManager (weight: high)

REQUIREMENTS from ClientCEO (5):
- REQ-TR-001: "Must integrate with SAP" [JD, High confidence]
- REQ-TR-002: "Support 50,000 concurrent users" [JD, High confidence]
...

REQUIREMENTS from ProductManager (3):
- REQ-TR-006: "Dashboard customization needed" [PM, High confidence]
...

Saved to: .requirements/enterprise-deal/transcripts/TR-client-call.yaml
```

### Multiple Transcripts

```bash
/requirements-elicitation:analyze-transcript ./meetings/*.md --domain "q1-planning"
```

Output:

```text
Found 4 transcripts matching pattern

Processing:
1. kickoff-meeting.md ........ 12 requirements, 4 decisions
2. technical-review.md ....... 8 requirements, 6 decisions
3. stakeholder-feedback.md ... 15 requirements, 2 decisions
4. sprint-planning.md ........ 5 requirements, 3 decisions

Cross-Transcript Analysis:
- Total requirements: 40
- Duplicates detected: 6 (consolidated to 34)
- Conflicting statements: 2 (flagged for review)

Summary saved to: .requirements/q1-planning/transcripts/summary.yaml
```

## Output Format

### Saved YAML Structure

```yaml
transcript_analysis:
  file: "sprint-planning.md"
  analyzed_date: "2025-12-25T14:30:00Z"
  domain: "{domain}"

speakers:
  - abbreviation: PM
    role: ProductManager
    statement_count: 45
    weight: high
  - abbreviation: TL
    role: TechLead
    statement_count: 32
    weight: high

requirements:
  - id: REQ-TR-001
    text: "System shall send email notifications for order status changes"
    speaker: PM
    speaker_role: ProductManager
    context: "Discussion about customer communication"
    original_quote: "We need email notifications when orders change status"
    confidence: high
    type: functional

decisions:
  - id: DEC-001
    text: "Use PostgreSQL for primary database"
    speaker: TL
    context: "Database technology selection"
    rationale: "Team expertise and scalability needs"

action_items:
  - id: ACT-001
    text: "Create database schema document"
    assignee: TL
    due_date: null  # If not specified
    context: "Follow-up from database decision"

concerns:
  - id: CONCERN-001
    text: "Third-party API reliability during peak hours"
    raised_by: TL
    context: "Integration discussion"
    severity: medium

conflicts:
  - items: [REQ-TR-003, REQ-TR-015]
    description: "Conflicting performance targets"
    resolution_needed: true
```

## Integration

### Follow-Up Commands

```bash
# Check for gaps after transcript analysis
/requirements-elicitation:gaps

# Interview stakeholders about concerns raised
/requirements-elicitation:interview "Technical Lead" --context "API reliability concerns"

# Consolidate with other sources
/requirements-elicitation:discover "{domain}" --sources transcripts,documents
```

## Best Practices

### Transcript Preparation

For best results, transcripts should:

- Clearly identify speakers
- Use consistent formatting
- Include timestamps (optional but helpful)
- Separate topics with headers

### Review Recommendations

After analysis:

1. Review all flagged conflicts
2. Validate low-confidence extractions
3. Follow up on open concerns
4. Assign action items if not already done
