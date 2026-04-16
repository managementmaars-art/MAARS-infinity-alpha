---
name: write-acceptance
description: Write acceptance criteria in Given-When-Then format for user stories following BDD best practices. Use for creating testable, clear acceptance criteria.
allowed-tools: Read, Write, Glob, Skill
argument-hint: <user-story>
---

# Write Acceptance Criteria Command

Generate clear, testable acceptance criteria in Given-When-Then format for user stories.

## Process

### Step 1: Parse User Story

Accept input as:

- Complete user story text
- User story ID (US-001) - look up in docs
- File path to story specification

Extract the user story format:

```text
As a [role]
I want to [action]
So that [benefit]
```

### Step 2: Load Skills

Invoke the `test-strategy:acceptance-criteria-authoring` skill for BDD patterns.

### Step 3: Identify Scenarios

For the user story, identify:

1. **Happy Path**: Primary success scenario
2. **Alternate Paths**: Valid variations
3. **Error Scenarios**: What can go wrong
4. **Edge Cases**: Boundary conditions
5. **Security Scenarios**: Access control, validation

### Step 4: Write Scenarios

Use Given-When-Then format:

```gherkin
Feature: [Feature name from story]

  Background:
    Given [common precondition]
    And [another common setup]

  @happy-path
  Scenario: Successfully [action] as [role]
    Given [specific context]
    And [additional context]
    When [action taken]
    Then [expected outcome]
    And [additional verification]

  @error-handling
  Scenario: Fail to [action] when [condition]
    Given [error-inducing context]
    When [action taken]
    Then [error handling behavior]
    And [system state preserved]

  @edge-case
  Scenario: [Action] with boundary condition
    Given [edge condition]
    When [action at boundary]
    Then [expected boundary behavior]
```

### Step 5: Apply INVEST Validation

Check scenarios against INVEST:

- **I**ndependent: Can run alone
- **N**egotiable: Details can be discussed
- **V**aluable: Delivers user value
- **E**stimable: Can be sized
- **S**mall: Fits in sprint
- **T**estable: Clear pass/fail

### Step 6: Generate SpecFlow (Optional)

For .NET projects, create step definition stubs:

```csharp
[Binding]
public class [Feature]Steps
{
    [Given(@"I am logged in as a (.*)")]
    public void GivenIAmLoggedInAs(string role)
    {
        // TODO: Implement step
    }

    [When(@"I (.*)")]
    public void WhenI(string action)
    {
        // TODO: Implement step
    }

    [Then(@"I should see (.*)")]
    public void ThenIShouldSee(string expected)
    {
        // TODO: Implement step
    }
}
```

### Step 7: Output

```markdown
## Acceptance Criteria Created

**User Story**: [Story ID/Title]

### Scenarios Generated
| Scenario | Type | Priority |
|----------|------|----------|
| Successfully checkout | Happy Path | P1 |
| Payment declined | Error | P1 |
| Cart expires | Edge Case | P2 |

### Files Created
- `features/[feature].feature` - Gherkin scenarios
- `steps/[Feature]Steps.cs` - Step stubs (if .NET)

### Coverage Checklist
- [x] Happy path covered
- [x] Validation errors covered
- [x] Authorization failures covered
- [x] Boundary conditions covered
- [ ] Concurrency scenarios (if applicable)

### Notes
- [Any assumptions made]
- [Questions for product owner]
```

## Examples

**From story text:**

```bash
/test-strategy:write-acceptance "As a customer, I want to checkout with saved payment so I can complete purchases quickly"
```

**From story ID:**

```bash
/test-strategy:write-acceptance US-042
```

**From file:**

```bash
/test-strategy:write-acceptance docs/stories/checkout.md
```
