# L5 YAML Format Reference

## User Story Structure

```yaml
# =============================================================================
# USER STORY: [Title]
# =============================================================================
# @spec_version: 1.0.0
# @phase: <user-defined> (e.g., MVP, v1, sprint-1)
# @journey: JOURNEY_NAME
# @systems: [SYSTEM_A, SYSTEM_B]
# @last_updated: 2025-01-01T00:00:00Z

id: US-101
title: Short description of user goal
requirement_id: R-101

acceptance_criteria:
  - id: AC-101-1
    title: Specific testable outcome
    narrative: |
      Given I am a logged-in member viewing the main screen
      When I click the add task button and enter a task name
      Then I should see the task appear in my current list
    given:
      - loginAs: member
      - visit: '/dashboard'
    when:
      - click: { selector: '[data-test=add-task]' }
      - fill: { selector: '[data-test=task-input]', value: 'Buy groceries' }
      - click: { selector: '[data-test=save-task]' }
    then:
      - shouldExist: { selector: '[data-test=task-item]' }
      - shouldContain: { selector: '[data-test=task-item]', text: 'Buy groceries' }
```

## Cross-System Example

```yaml
# @systems: [TASK_SYSTEM, REWARD_SYSTEM, VIEW_SYSTEM]
id: US-102
title: See points awarded immediately on task completion

acceptance_criteria:
  - id: AC-102-1
    title: Points update on completion
    narrative: |
      Given I have an active task with base points value
      When I mark the task as complete
      Then I should see my points total increase
    given:
      - loginAs: member
      - seedItem: { slug: 'my-task', status: 'active', points: 10 }
      - visit: '/tasks/my-task'
    when:
      - click: { selector: '[data-test=complete-task]' }
    then:
      - shouldContain: { selector: '[data-test=points-total]', text: '10' }
      - shouldExist: { selector: '[data-test=feedback-animation]' }
```

## Core DSL Steps (use ONLY these)

The `given`/`when`/`then` arrays in acceptance criteria use a fixed DSL. Only use these steps — anything else will fail Zod validation at test time and be stripped by tooling.

**Setup steps (given / when):**
- `visit: '/path'` — navigate to a page
- `click: { selector: '[data-test=btn]' }` — click an element
- `fill: { selector: '[data-test=input]', value: 'text' }` — type into an input
- `loginAs: 'role'` — authenticate as a user role (requires Cypress task)
- `seedItem: { slug: 'id', status: 'active' }` — create test data (requires Cypress task)

**Assertion steps (then):**
- `shouldContain: { selector: '[data-test=el]', text: 'expected' }` — verify text content
- `shouldExist: { selector: '[data-test=el]' }` — verify element exists

**Do NOT use:** `scrollTo`, `shouldNavigateToUrl`, `shouldHaveAttribute`, `wait`, `reload`, `hover`, `dragTo`, or any other step name. These do not exist in the schema. If a behavior can't be tested with the core steps above, simplify the acceptance criterion to use `shouldExist` or `shouldContain` on the observable result.

## YAML Syntax Rules

**Multi-line text** — use pipe operator (`|`):
```yaml
narrative: |
  Given I am a logged-in member
  When I click the button
  Then I should see results
```

**Text with colons** — use pipe or quotes:
```yaml
# Correct
notes: |
  Context: this has colons safely
# Also correct
notes: "Context: this has colons safely"
# WRONG (will fail)
notes: Context: this breaks parsing
```

**Apostrophes** — use double quotes:
```yaml
# Correct
message: "hasn't arrived"
# Also correct (doubled single quotes)
message: 'hasn''t arrived'
# WRONG
message: 'hasn\'t arrived'
```

## Common Pitfalls

1. **Unquoted colons** — text with `:` needs block scalar or quotes
2. **Invalid escaping** — can't use `\'` in single quotes; use double quotes
3. **Bad indentation** — use 2 spaces consistently, never tabs
4. **Empty array elements** — extra `-` with no content creates null values
5. **Misaligned dashes** — sibling array items must align at same column

## Test Control Modifiers

```yaml
id: US-103
skip: true  # Skip entire story (add comment explaining why)
# only: true  # Run ONLY this story (for local dev, never commit)

acceptance_criteria:
  - id: AC-103-1
    # skip: true   # Skip individual AC
    # only: true   # Focus individual AC
```

**Precedence**: Story-level `skip` overrides all AC modifiers. AC-level `only` within a focused story runs only that AC.

## Fine-Tuning Format

```yaml
# =============================================================================
# FINE-TUNING: System Name
# =============================================================================
# @spec_version: 1.0.0
# @spec_source: 04.SYSTEMS/SYSTEM_NAME.md
# @last_updated: 2025-01-01T00:00:00Z

parameter_name:
  value: 100
  # @unit: milliseconds
  # @rationale: Fast enough to feel instant, slow enough to animate
  # @constraint: min=50, max=500
  # @ab_test: test-id-123

nested_group:
  sub_param:
    value: 0.8
    # @unit: ratio
    # @rationale: Balances reward vs. effort
```

**Required annotations**: `@rationale` (why this value), `@spec_source` (which system doc).
**Common annotations**: `@unit`, `@constraint`, `@ab_test`, `@ethical_review`, `@inviolable`.
