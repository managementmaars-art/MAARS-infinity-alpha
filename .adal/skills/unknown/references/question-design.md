# Unknown Question Design Guide

## AskUserQuestion Formatting

- Batch up to 4 questions per call
- Prefer 3-4 options per question
- Use `multiSelect: true` when causes can be combined
- Keep options mutually distinguishable

## Round-Specific Question Types

### R1 (Broad Scan)

1. Certainty stress-test (KK boundary)
2. Weakest link selection (KU focus)
3. Underused asset detection (UK discovery)
4. Biggest fear/risk scenario (UU probe)

### R2 (Weak Link Drilldown)

- Root cause disambiguation
- Constraint ranking
- Owner/capability gap checks

### R3 (Execution Detail)

- First experiment design
- Timebox/deadline selection
- Promotion or kill criteria

## Anti-Patterns

- Open questions without options
- 5+ options with overlapping meaning
- Repeating prepared questions regardless of prior answers
