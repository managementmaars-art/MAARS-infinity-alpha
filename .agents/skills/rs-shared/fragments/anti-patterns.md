# Anti-Patterns by Level

## Level 1: Foundational Philosophy

- **Feature-as-pillar**: Pillar describes a feature ("Fast Search") instead of a feeling ("Empowered Discovery")
- **Technology in philosophy**: Mentioning specific tech ("Use GraphQL") — belongs in L4
- **Vague mission**: "Build a great product" — needs specific problem and audience
- **Too many pillars**: More than 5 dilutes focus — push to consolidate
- **Numeric values**: Any numbers in L1 — use placeholders
- **Missing North Star**: No description of the ideal user experience

## Level 2: Stable Truths

- **Implementation details**: Describing code architecture — belongs in L4
- **Downward references**: Referencing L3/L4/L5 concepts by name
- **Vague strategies**: "We'll handle errors" — needs specific philosophy
- **Missing trade-offs**: No explicit "we choose X over Y" statements
- **Numeric values**: Specific numbers — use placeholders

## Level 3: Interaction Architecture

- **System references**: Naming specific L4 systems (e.g., "TASK_SYSTEM")
- **Code-level details**: Describing API endpoints or data schemas
- **Missing scales**: Not addressing immediate/session/extended/lifetime interaction scales
- **No failure modes**: Missing edge cases and error states
- **Numeric values**: Specific timings — use placeholders like [brief delay]

## Level 4: Systems

- **Downward references**: Referencing L5 user stories or fine-tuning values
- **Code implementation**: Actual code rather than system descriptions
- **Missing boundaries**: System responsibilities not clearly scoped
- **No interactions**: Systems described in isolation without showing connections
- **Numeric values**: Specific thresholds — use placeholders

## Level 5: Implementation

- **Missing @spec_source**: User stories without traceability to higher levels
- **Missing @phase**: No phase assignment (e.g., MVP, v1, sprint-1)
- **Vague acceptance criteria**: "It should work" instead of specific observable behaviors
- **Untestable stories**: Criteria that can't be verified with Cypress DSL
- **Missing screen coverage**: L3 screens with no corresponding user stories
