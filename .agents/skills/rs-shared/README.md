# rs-shared

Shared scripts and fragments used by RootSpec skills.

## Scripts

Scripts extract structured data from spec files. All output plain text (one item per line) for easy parsing by skills.

| Script | Purpose | Input |
|--------|---------|-------|
| `scan-spec.sh` | Find spec dir, list found/missing files, detect version | project root |
| `scan-project.sh` | Detect framework, source dirs, config files | project root |
| `extract-l1-pillars.sh` | Extract Design Pillar names | spec dir |
| `extract-l2-truths.sh` | Extract Stable Truth section names | spec dir |
| `extract-l3-patterns.sh` | Extract interaction pattern names | spec dir |
| `list-l4-systems.sh` | List system file paths | spec dir |
| `list-l5-stories.sh` | List user story YAML paths | spec dir |
| `list-l5-fine-tuning.sh` | List fine-tuning YAML paths | spec dir |
| `extract-l5-journeys.sh` | Extract unique @journey values | spec dir |

## Fragments

Markdown snippets referenced by skill instructions:

| Fragment | Content |
|----------|---------|
| `framework-rules.md` | Reference hierarchy, placeholder rules, pillar quality |
| `interview-protocol.md` | How to conduct the interview process |
| `cascade-protocol.md` | Downstream cascade check instructions |
| `anti-patterns.md` | Common anti-patterns organized by level |
| `l5-yaml-format.md` | L5 YAML syntax rules, story structure, fine-tuning format, examples |
| `l5-test-dsl.md` | Test DSL step reference, extension patterns, Cypress infrastructure |
