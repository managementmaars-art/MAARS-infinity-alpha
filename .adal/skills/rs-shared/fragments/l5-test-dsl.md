# L5 Test DSL Reference

**Ownership boundary:** The Cypress files (`steps.ts`, `schema.ts`, `cypress.config.ts`, `e2e.ts`) are scaffolding — once in the user's project, they own them. Users extend these files heavily with custom DSL steps, auth logic, and seed tasks. NEVER overwrite or regenerate these files. When updating, only add what's missing and preserve all existing customizations.

## Core Setup Steps (given / when)

| Step | Syntax | Purpose |
|------|--------|---------|
| `visit` | `visit: '/path'` | Navigate to a page |
| `click` | `click: { selector: '[data-test=btn]' }` | Click an element |
| `fill` | `fill: { selector: '[data-test=input]', value: 'text' }` | Fill an input |
| `loginAs` | `loginAs: 'member'` | Authenticate as a user role |
| `seedItem` | `seedItem: { slug: 'id', status: 'active' }` | Create test data |

## Core Assertion Steps (then)

| Step | Syntax | Purpose |
|------|--------|---------|
| `shouldContain` | `shouldContain: { selector: '[data-test=el]', text: 'expected' }` | Verify text content |
| `shouldExist` | `shouldExist: { selector: '[data-test=el]' }` | Verify element exists |

## Extending the DSL

Add domain-specific steps in `cypress/support/steps.ts`:

```typescript
// 1. Add to Step union type
export type Step =
  | { visit: string }
  | { click: { selector: string } }
  | { fill: { selector: string; value: string } }
  | { loginAs: string }
  | { seedItem: Record<string, unknown> }
  | { shouldContain: { selector: string; text: string } }
  | { shouldExist: { selector: string } }
  // Custom steps:
  | { createProject: { name: string } }
  | { inviteUser: { email: string; role: string } }

// 2. Implement in runSetupSteps
export function runSetupSteps(steps: Step[]) {
  for (const s of steps ?? []) {
    if ('visit' in s) cy.visit(s.visit);
    else if ('click' in s) cy.get(s.click.selector).click();
    else if ('fill' in s) cy.get(s.fill.selector).type(s.fill.value);
    else if ('loginAs' in s) cy.task('loginAs', s.loginAs);
    else if ('seedItem' in s) cy.task('seedItem', s.seedItem);
    // Custom steps:
    else if ('createProject' in s) cy.task('createProject', s.createProject);
    else if ('inviteUser' in s) cy.task('inviteUser', s.inviteUser);
  }
}

// 3. Implement assertions in runAssertionSteps
export function runAssertionSteps(steps: Step[]) {
  for (const s of steps ?? []) {
    if ('shouldContain' in s) {
      cy.get(s.shouldContain.selector).should('contain', s.shouldContain.text);
    }
    else if ('shouldExist' in s) {
      cy.get(s.shouldExist.selector).should('exist');
    }
  }
}
```

Also register custom steps in `cypress/support/schema.ts`:

```typescript
const StepSchema = z.union([
  z.object({ visit: z.string() }),
  z.object({ click: z.object({ selector: z.string() }) }),
  z.object({ fill: z.object({ selector: z.string(), value: z.string() }) }),
  z.object({ loginAs: z.string() }),
  z.object({ seedItem: z.record(z.unknown()) }),
  z.object({ shouldContain: z.object({ selector: z.string(), text: z.string() }) }),
  z.object({ shouldExist: z.object({ selector: z.string() }) }),
  // Custom:
  z.object({ createProject: z.object({ name: z.string() }) }),
  z.object({ inviteUser: z.object({ email: z.string(), role: z.string() }) }),
]);
```

## Decision Tree: What to Implement

When a test fails, follow this decision tree:

1. **Does the DSL step exist in `steps.ts`?**
   - NO → Extend DSL (add step type + implementation + schema)
   - YES → continue

2. **Does the application feature exist?**
   - NO → Implement the app feature
   - YES → continue

3. **Does the test data exist?**
   - NO → Create fixture or seed data
   - YES → Debug the test or application logic

## Cypress Infrastructure

| File | Purpose |
|------|---------|
| `cypress.config.ts` | Tasks: `loginAs`, `seedItem`, `resetDatabase` |
| `cypress/support/e2e.ts` | Global setup: `beforeEach` with DB reset |
| `cypress/support/steps.ts` | DSL step implementations |
| `cypress/support/schema.ts` | DSL validation schema (Zod) |
| `cypress/e2e/*.cy.ts` | Test suite files that load YAML and run tests |
