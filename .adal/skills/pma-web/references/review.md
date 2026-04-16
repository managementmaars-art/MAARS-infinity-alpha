# PMA-Web Review

## Required Verification

Before merge:

- lint passes
- typecheck passes
- build passes
- tests pass for the affected scope
- accessibility review completed for changed UI
- security review completed for changed trust boundaries

## Accessibility Review

For every UI-affecting change, verify:

- keyboard navigation works
- focus states are visible
- controls have labels or accessible names
- contrast is acceptable
- loading, empty, and error states remain understandable
- dialogs, popovers, and menus trap and restore focus correctly

## Security Review

For frontend changes, verify:

- no unsafe HTML injection
- no accidental secret exposure through client env usage
- auth and permission checks still match the product model
- redirects and route guards cannot be bypassed trivially
- untrusted URL or file input is validated before use

## Testing Guidance

- keep unit and integration tests in Vitest
- use Playwright only for critical flows that need browser coverage
- prefer focused tests around changed behavior over broad snapshot churn

## Generated And Owned Code

- treat shadcn output as owned code
- keep generated route tree files out of manual edits unless regeneration is impossible
- when generated files change, verify the underlying config and source files instead of reviewing generated diff alone
