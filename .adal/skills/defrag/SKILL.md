---
name: defrag
description: Analyze code for refactoring opportunities and suggest the top 10 highest-value improvements. Use this whenever the user says `/defrag`, asks to refactor, clean up code, improve code quality, identify code smells, or wants a ranked list of code improvements. This skill is for analysis only unless the user explicitly asks to apply a specific suggestion.
---

# Defrag

## Purpose

Use this skill to inspect one or more files, identify the highest-value refactoring opportunities, and present a ranked top 10 list with concrete code-level suggestions.

This skill is analysis-first. Do not apply edits unless the user explicitly switches from analysis to implementation.

## Default Behavior

1. Determine the target scope.
2. Read the relevant files or the user's current selection.
3. Inspect the code for the refactoring types listed below.
4. If git history is available, inspect the last 30 days to find change hotspots. Prefer `scripts/git_hotspots.py` for consistent counts.
5. Score each candidate refactor with the provided weighting model.
6. Return the top 10 opportunities sorted by value score.
7. End by asking whether the user wants any suggestion applied.

If the user did not specify files, use the most relevant local context you can discover from the conversation or repo state. If the scope is still ambiguous and a wrong guess would be misleading, ask for the file or directory to analyze.

## Hard Rules

- Do not apply changes during the analysis pass.
- Do not suggest speculative architecture work that is not justified by the current code.
- Follow YAGNI. Prefer targeted, local refactors over framework churn.
- Keep constants close to usage. Do not suggest dumping values into a global constants file.
- Be specific about file path, line range, and the concrete benefit.
- Show short before/after snippets for every recommendation.
- Sort strictly by value score from highest to lowest.

## Refactoring Types To Look For

Check for these opportunity types:

1. `shorten_file`: files over 300 lines that should be split into coherent units
2. `shorten_function`: functions over 50 lines that should be decomposed
3. `reduce_nesting`: nested conditionals that should become guard clauses or early returns
4. `extract_function`: repeated or complex logic that should move into a named helper
5. `rename_for_clarity`: unclear names, overloaded names, or names that hide intent
6. `simplify_conditionals`: brittle or verbose branching that can be simplified
7. `extract_constants`: magic strings, numbers, selectors, or thresholds that should become local constants
8. `consolidate_duplicates`: duplicate logic that should be merged
9. `modernize_syntax`: safe use of modern syntax such as destructuring or optional chaining
10. `avoid_globality`: move global items closer to where they are used
11. `optimize_imports`: remove unused imports and tighten import organization
12. `remove_dead_code`: identify unused code paths, stale helpers, or unreachable branches
13. `add_tests`: call out risky logic with weak or missing coverage
14. `break_up_hotspots`: inspect the last 30 days of git history and flag files changed more than 30 times

## Hotspot Analysis

When git history is available:

1. Inspect the last 30 days of changes.
2. Find the 5 files with the highest change counts.
3. For any file changed more than 30 times, suggest decomposition or responsibility splits.

If git history is unavailable, say so briefly and continue with static code analysis.

To collect hotspot data, you can run:

```bash
python skills/defrag/scripts/git_hotspots.py --repo . --days 30 --limit 5
```

## Scoring Model

Score each refactoring from `0` to `100` using this weighted model:

- Readability improvement: `35%`
- Maintainability improvement: `30%`
- Bug risk reduction: `25%`
- Performance impact: `5%`
- Scope size: `5%`

Use judgment, but keep scores internally consistent. High scores should correspond to changes that are both important and realistically actionable.

## Analysis Workflow

Follow this order:

1. Confirm the target files, folder, or code selection.
2. Read enough surrounding context to avoid shallow suggestions.
3. Check file size, function length, nesting, duplication, naming, imports, and dead code.
4. If applicable, inspect tests near the target code and note important gaps.
5. If applicable, inspect recent git history for churn hotspots.
6. Produce more than 10 candidate opportunities if needed, then sort and keep the best 10.

## Bundled Resources

- `scripts/git_hotspots.py`: counts per-file churn from recent git history and returns a JSON summary for hotspot analysis
- `evals/evals.json`: starter prompts for validating trigger behavior and output structure
- `agents/openai.yaml`: UI-facing metadata and default invocation prompt

## Output Format

Use this exact structure for each ranked item:

### {rank}. **{type}** (Value: {score}/100)
- **File:** `{filepath}:{start_line}-{end_line}`
- **Description:** {one-line description}
- **Rationale:** {why this helps}

**Before:**
```{language}
{current code snippet}
```

**After:**
```{language}
{refactored code snippet}
```

---

After the ranked list, end with:

`Found {N} refactoring opportunities. Top 10 shown with average score: {avg}`

Then ask:

`Would you like me to apply any of these? Say "apply #1" or "apply all".`

## Snippet Guidance

- Keep before/after snippets focused on the exact issue.
- Show enough context to make the refactor understandable.
- Prefer realistic after examples that fit the current code style.
- Do not fabricate unrelated helper layers or abstractions.

## Review Mindset

Optimize for the highest-value improvements, not the largest number of comments.

A strong result:

- catches structural issues before cosmetic ones
- points to the exact lines that matter
- proposes changes that reduce future editing cost
- avoids vague advice such as "clean this up" or "improve readability"

## Failure Modes To Avoid

Do not:

- recommend massive rewrites without evidence
- flood the list with trivial rename suggestions when there are larger structural problems
- suggest moving everything into shared utils or managers
- present style-only changes as high-value refactors
- apply code edits unless the user explicitly asks for implementation
