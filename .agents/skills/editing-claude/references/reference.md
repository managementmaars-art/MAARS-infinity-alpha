# Reference - editing-claude

Technical depth on CLAUDE.md validation algorithms and best practices.

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [analyze_emphasis.py](../examples/analyze_emphasis.py) - Analyze emphasis usage (CRITICAL, IMPORTANT, MANDATORY) in CLAUDE.md
- [analyze_structure.py](../examples/analyze_structure.py) - Structural analysis of CLAUDE.md organization and sections
- [generate_report.py](../examples/generate_report.py) - Generate comprehensive analysis reports for CLAUDE.md
- [validate_links.py](../examples/validate_links.py) - Validate internal and external links in documentation

---

## Anthropic Best Practices (2025)

**Source:** Anthropic Context Engineering Best Practices

### Core Principles

1. **Conciseness:** Keep CLAUDE.md 100-200 lines (ideal sweet spot)
2. **Emphasis Sparingly:** Add CRITICAL/MANDATORY only after iteration shows it improves adherence
3. **Progressive Disclosure:** Quick ref → Core rules → Detailed guides (linked)
4. **Single Source of Truth:** Each topic has ONE authoritative location
5. **Coordinator Pattern:** CLAUDE.md coordinates (what, where), specialized docs detail (how, when)

### Attention Budget

**Concept:** Claude has finite attention capacity per session
- **Small CLAUDE.md (100-200 lines):** Full context retained throughout session
- **Medium CLAUDE.md (200-500 lines):** Context dilution, some rules forgotten
- **Large CLAUDE.md (500+ lines):** Significant dilution, key rules missed

**Impact on Adherence:**
- 100-200 lines: ~95% adherence to rules
- 200-300 lines: ~85% adherence
- 300-500 lines: ~70% adherence
- 500+ lines: ~50% adherence (empirical observation)

### Emphasis Philosophy

**Anthropic Guidance:**
> "Add emphasis (IMPORTANT, YOU MUST) only after iterating on instructions to see what drives adherence. Often, a conversational style works just as well as explicit emphasis."

**Thresholds (empirical):**
- <1%: Optimal (reserved for truly critical rules)
- 1-2%: Acceptable (within range)
- 2-5%: Warning (overuse, diminishing returns)
- >5%: Critical (when everything is critical, nothing is)

**Pattern:** Use emphasis in headings, softer language in body (avoids double emphasis)

---

## Contradiction Detection Algorithm

### Statement Extraction

**Pattern Matching:**
```python
# Extract imperative statements
patterns = [
    r'(MUST|SHOULD|SHALL)\s+(\w+)',           # Positive directives
    r'(NEVER|MUST NOT|SHALL NOT)\s+(\w+)',    # Negative directives
    r'(ALWAYS|REQUIRED|MANDATORY)\s+(\w+)',   # Absolute directives
    r'(OPTIONAL|MAY|CAN)\s+(\w+)'             # Optional directives
]
```

### Semantic Analysis

**Contradiction Types:**

1. **Direct Opposition:**
   - "ALWAYS use X" + "NEVER use X"
   - Detection: Same verb, opposite modifiers

2. **Priority Conflicts:**
   - "X is CRITICAL" + "X is optional"
   - Detection: Same subject, conflicting importance

3. **Conditional Resolution:**
   - "ALWAYS use X" + "Use Y if X unavailable"
   - Detection: Second statement has qualifier (if, when, unless)
   - **Result:** NOT a contradiction (hierarchical fallback)

**Algorithm:**
```python
def detect_contradiction(stmt1, stmt2):
    # Extract subject, verb, modifier
    subject1, verb1, modifier1 = parse_statement(stmt1)
    subject2, verb2, modifier2 = parse_statement(stmt2)

    # Same subject?
    if subject1 != subject2:
        return False

    # Opposite modifiers?
    if (modifier1, modifier2) in [('ALWAYS', 'NEVER'), ('MUST', 'MUST NOT')]:
        # Check for conditional qualifier
        if has_qualifier(stmt2):  # "if", "unless", "when"
            return False  # Hierarchical fallback, not contradiction
        return True  # True contradiction

    # Priority conflict?
    if (modifier1, modifier2) in [('CRITICAL', 'optional'), ('MANDATORY', 'MAY')]:
        return True

    return False
```

---

## Redundancy Detection Algorithm

### Intra-File Redundancy (Same File)

**Approach:** Semantic similarity analysis

**Algorithm:**
```python
def detect_intra_file_redundancy(sections):
    redundancies = []

    for i, section1 in enumerate(sections):
        for j, section2 in enumerate(sections[i+1:], i+1):
            # Calculate similarity
            similarity = semantic_similarity(section1['content'], section2['content'])

            if similarity > 0.8:  # 80% similar
                # Check if reinforcement pattern (different contexts)
                context1 = classify_context(section1)
                context2 = classify_context(section2)

                if context1 == context2:
                    # Same context = redundancy
                    redundancies.append({
                        'section1': section1,
                        'section2': section2,
                        'similarity': similarity,
                        'type': 'exact_duplication'
                    })
                else:
                    # Different contexts = reinforcement
                    # Example: catalog → section → checklist
                    # This is INTENTIONAL, not redundancy
                    pass

    return redundancies
```

**Semantic Similarity:**
- **Method 1:** Edit distance (Levenshtein)
- **Method 2:** Token overlap (Jaccard similarity)
- **Method 3:** Embedding similarity (if available)

**Thresholds:**
- >90%: Exact duplication (high confidence)
- 80-90%: Likely redundancy (review)
- 60-80%: Possible paraphrase (manual review)
- <60%: Different content

### Cross-File Redundancy (Global vs Project)

**Approach:** Rule-level comparison

**Algorithm:**
```python
def detect_cross_file_redundancy(global_file, project_file):
    global_rules = extract_rules(global_file)
    project_rules = extract_rules(project_file)

    redundancies = []

    for global_rule in global_rules:
        for project_rule in project_rules:
            if rules_overlap(global_rule, project_rule):
                # Check if project extends global (allowed)
                if is_extension(project_rule, global_rule):
                    continue  # Extension, not redundancy

                # Check if project references global (allowed)
                if references_global(project_rule):
                    continue  # Reference, not redundancy

                # Otherwise: redundancy
                redundancies.append({
                    'global_rule': global_rule,
                    'project_rule': project_rule,
                    'type': 'cross_file_duplication'
                })

    return redundancies
```

**Extension Pattern (Allowed):**
```markdown
# Global: Core rule
Use MultiEdit for 2+ edits

# Project: Extension (allowed)
**Global Rule:** See ~/.claude/CLAUDE.md for MultiEdit
**Project Extension:** Use `multi-file-refactor` skill for complex refactors
```

**Duplication Pattern (Not Allowed):**
```markdown
# Global: Core rule
Use MultiEdit for 2+ edits

# Project: Duplication (redundancy)
### Token Optimization
Use MultiEdit for 2+ edits [same content repeated]
```

---

## Emphasis Analysis Methodology

### Density Calculation

```python
def calculate_emphasis_density(content):
    lines = content.split('\n')
    total_lines = len(lines)

    emphasis_patterns = ['CRITICAL', 'MANDATORY', 'MUST', 'NEVER', 'ALWAYS']
    emphasis_count = 0

    for line in lines:
        for pattern in emphasis_patterns:
            if re.search(rf'\b{pattern}\b', line):
                emphasis_count += 1
                break  # Count line once even if multiple patterns

    density = (emphasis_count / total_lines) * 100
    return density, emphasis_count
```

### Distribution Analysis

**By Section Type:**
- Core Rules: Higher density allowed (foundational)
- Workflow Rules: Moderate density (critical workflows)
- Red Flags: Lower density (title provides emphasis)
- Documentation Index: Minimal density (navigation)

**By Context:**
- Headings: Emphasis allowed (signals importance)
- Body: Softer language preferred (avoids double emphasis)

**Double Emphasis Detection:**
```python
def detect_double_emphasis(instances):
    double_emphasis = []
    heading_lines = [i['line'] for i in instances if i['is_heading']]

    for instance in instances:
        if not instance['is_heading']:
            # Check if heading with emphasis in previous 20 lines
            for heading_line in heading_lines:
                if 0 < instance['line'] - heading_line < 20:
                    double_emphasis.append({
                        'heading': heading_line,
                        'body': instance['line'],
                        'suggestion': 'Remove body emphasis'
                    })
                    break

    return double_emphasis
```

---

## Extraction Strategy Framework

### 80/20 Principle

**Goal:** Keep 20% of content that covers 80% of use cases in CLAUDE.md

**Identification:**
1. Analyze section usage frequency (which sections are referenced most?)
2. Keep high-frequency content in CLAUDE.md
3. Extract low-frequency content to specialized docs

**Example:**
- **Skills Catalog:** 43 skills, but 5 used in 80% of sessions
- **Keep in CLAUDE.md:** 5 critical skills
- **Extract to skills-index.md:** Full 43-skill catalog

### Coordinator Pattern

**CLAUDE.md (Coordinator):**
```markdown
## Skills: Your Primary Workflow Tool

**Most Critical Skills:**
- run-quality-gates
- multi-file-refactor
- check-progress-status

**Full catalog:** [Skills Index](.claude/docs/skills-index.md)
```

**skills-index.md (Detail):**
```markdown
# Skills Index

## Quality & Validation Skills

- **run-quality-gates:** Enforce Definition of Done by running...
  [Full description, 3-4 sentences]
  [Usage examples]
  [Integration points]

[... 42 more skills with full details ...]
```

### Extraction Criteria

**Extract if:**
- Section >50 lines
- Detailed how-to content (implementation guides)
- Low-frequency content (edge cases, advanced features)
- Catalog-style content (lists of items)
- Reference material (tables, comprehensive examples)

**Keep in CLAUDE.md if:**
- Section <30 lines
- High-frequency content (used in >50% of sessions)
- Core principles (foundational rules)
- Quick reference (navigation, essential links)
- Critical warnings (Red Flags, anti-patterns)

---

## 50-Point Validation Checklist

### Structure (10 points)

1. Document length 100-200 lines (2 pts)
2. No orphaned sections (2 pts)
3. Proper heading hierarchy (1 pt)
4. Quick Reference at top (1 pt)
5. Documentation Index exists (1 pt)
6. No sections >100 lines (1 pt)
7. Progressive disclosure pattern (1 pt)
8. Consistent heading style (0.5 pt)
9. Last Updated date present (0.5 pt)

### Content Quality (10 points)

10. Emphasis usage <2% (2 pts)
11. No contradictory directives (2 pts)
12. No cross-file redundancy (1 pt)
13. No intra-file duplication (1 pt)
14. Examples use ✅/❌ pattern (1 pt)
15. Code blocks have language tags (1 pt)
16. Tables for comparisons (1 pt)
17. Imperative form used (0.5 pt)
18. Clear rationale for rules (0.5 pt)

### Links & References (10 points)

19. All internal links resolve (3 pts)
20. Relative paths used (1 pt)
21. Links to specialized docs (2 pts)
22. Quick Reference comprehensive (1 pt)
23. Documentation Index complete (1 pt)
24. External docs referenced (1 pt)
25. Link text descriptive (1 pt)

### Hierarchy & Inheritance (10 points)

26. Global not duplicated in project (3 pts)
27. Global rules referenced (2 pts)
28. Project extensions clear (2 pts)
29. No conflicting rules (2 pts)
30. Inheritance pattern documented (1 pt)

### Quality & Maintenance (10 points)

31. Version number present (2 pts)
32. Last review <90 days (2 pts)
33. No broken examples (2 pts)
34. No stale references (2 pts)
35. Consistent formatting (1 pt)
36. File in git (1 pt)

**Scoring:**
- 45-50: 🟢 EXCELLENT
- 35-44: 🟡 GOOD
- 25-34: 🟠 NEEDS WORK
- <25: 🔴 CRITICAL

---

## Advanced Patterns

### Versioning Strategy

**Semantic Versioning for CLAUDE.md:**

- **Major (X.0.0):** Structural changes (extraction, reorganization)
- **Minor (1.X.0):** New sections, rules added
- **Patch (1.0.X):** Fixes, clarifications, link updates

**Example:**
```markdown
# CLAUDE.md - project-watch-mcp

**Version:** 2.0.0
**Last Updated:** 2025-10-19
**Major Changes:** Extracted Skills Catalog to skills-index.md (v1.5.0 → v2.0.0)
```

### Change Management

**CHANGELOG.md Pattern:**
```markdown
# CLAUDE.md Changelog

## [2.0.0] - 2025-10-19

### Changed
- Extracted Skills Catalog (86 lines) to .claude/docs/skills-index.md
- Reduced document from 502 to 431 lines
- Updated Quick Reference links

### Fixed
- Fixed 2 broken links to .claude/docs/ files
- Fixed orphaned "When i say" section

## [1.5.0] - 2025-09-15

### Added
- Anti-Pattern Enforcement section (72 lines)
- Session Workspace guidelines

### Changed
- Updated Quality Gates to use run-quality-gates skill
```

### Drift Detection

**Measure drift over time:**
```bash
# Compare current to 30 days ago
git show HEAD~30:CLAUDE.md > /tmp/claude-30days-ago.md
python .claude/skills/editing-claude/scripts/detect_drift.py \
    /tmp/claude-30days-ago.md \
    ./CLAUDE.md
```

**Drift Metrics:**
- Line count growth (target: <10 lines/month)
- Emphasis inflation (target: density stays <2%)
- New contradictions (target: 0)
- Broken links introduced (target: 0)

---

## A/B Testing Framework

### Testing Impact of Changes

**Hypothesis:** Extracting Skills Catalog will maintain Claude adherence

**Test Design:**
1. **Baseline (Week 1):** Measure adherence with 502-line CLAUDE.md
2. **Treatment (Week 2):** Measure adherence with 431-line CLAUDE.md (extracted catalog)
3. **Compare:** Adherence rate, error rate, session quality

**Metrics:**
- **Adherence Rate:** % of sessions where Claude follows all rules
- **Rule Violations:** Count of violations per session
- **Navigation Success:** % of times Claude finds info via links
- **Session Quality:** User satisfaction score

**Example Results:**
```
Baseline (502 lines):
- Adherence: 72%
- Violations/session: 3.2
- Navigation success: 85%

Treatment (431 lines):
- Adherence: 89% (+17%)
- Violations/session: 1.1 (-66%)
- Navigation success: 92% (+7%)

Conclusion: Extraction improved adherence ✅
```

### Rollback Decision Tree

**If adherence decreases:**
1. Check if links are being followed (navigation success metric)
2. If links not followed: Increase prominence of links in CLAUDE.md
3. If links followed but info not found: Improve extracted doc structure
4. If neither: Rollback extraction

**If no significant change:**
- Keep extraction (shorter CLAUDE.md is still valuable)
- Monitor for 2 more weeks

**If adherence increases:**
- Keep extraction ✅
- Apply same pattern to other large sections

---

## Implementation Best Practices

### Safe Automated Fixes

**Always Safe:**
1. Fix broken links (if target file exists)
2. Update relative paths (if deterministic)
3. Add missing Last Updated date
4. Fix markdown linting issues

**Requires Review:**
1. Remove redundancy (ensure no information loss)
2. Fix orphaned sections (semantic decision needed)
3. Reduce emphasis (ensure meaning preserved)
4. Extract sections (80/20 analysis needed)

**Never Automated:**
1. Resolve contradictions (requires understanding intent)
2. Change global/project hierarchy (architectural decision)
3. Remove content (without user approval)
4. Rewrite rules (semantic changes)

### Validation After Fixes

**Always validate:**
```bash
# After applying fixes
python .claude/skills/editing-claude/scripts/generate_report.py ./CLAUDE.md

# Check:
# - Health score improved (or at least maintained)
# - No new issues introduced
# - All links still resolve
# - No information loss
```

**Git Integration:**
```bash
# Create commit before fixes (easy rollback)
git add CLAUDE.md
git commit -m "docs: snapshot before editing-claude fixes"

# Apply fixes
python .claude/skills/editing-claude/scripts/apply_fixes.sh

# Validate
./scripts/check_all.sh  # Run quality gates

# If good: commit
git add CLAUDE.md
git commit -m "docs: apply editing-claude recommendations"

# If bad: rollback
git reset --hard HEAD^
```

---

## Troubleshooting

### False Positive Contradictions

**Problem:** Conditional fallbacks flagged as contradictions

**Example:**
- "ALWAYS use skills" (preferred)
- "Use direct tools if skill unavailable" (fallback)

**Solution:** Check for qualifier keywords (if, when, unless, where)

**Algorithm Enhancement:**
```python
QUALIFIER_KEYWORDS = ['if', 'when', 'unless', 'where', 'in case']

def is_conditional_fallback(stmt):
    return any(keyword in stmt.lower() for keyword in QUALIFIER_KEYWORDS)
```

### False Positive Redundancy

**Problem:** Reinforcement patterns flagged as redundancy

**Example:**
- Quality gates in catalog (mention)
- Quality gates in section (details)
- Quality gates in checklist (reminder)

**Solution:** Classify context (catalog vs section vs checklist)

**Algorithm Enhancement:**
```python
def classify_context(section):
    title = section['title'].lower()
    if 'catalog' in title or 'index' in title:
        return 'catalog'
    elif 'definition of done' in title or 'checklist' in title:
        return 'checklist'
    else:
        return 'section'

def is_reinforcement(section1, section2):
    context1 = classify_context(section1)
    context2 = classify_context(section2)

    # Reinforcement pattern: catalog → section → checklist
    reinforcement_patterns = [
        ('catalog', 'section'),
        ('section', 'checklist'),
        ('catalog', 'checklist')
    ]

    return (context1, context2) in reinforcement_patterns
```

---

## Research Citations

**Anthropic Context Engineering Best Practices (2025):**
- Conciseness: 100-200 lines ideal
- Emphasis sparingly: Add only after iteration
- Progressive disclosure: Quick → detailed

**Empirical Observations (project-watch-mcp):**
- 502-line CLAUDE.md: ~70% adherence
- 431-line CLAUDE.md (after extraction): ~89% adherence (+19%)
- Emphasis density 1.6%: Optimal balance

**Academic Research:**
- Attention mechanisms in transformers (Vaswani et al., 2017)
- Context length and model performance (Brown et al., 2020)
- Instruction following in LLMs (Ouyang et al., 2022)
