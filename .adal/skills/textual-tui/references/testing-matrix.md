# Testing matrix

Treat tests as part of the deliverable, not optional polish.

## Default minimum

For any non-trivial feature, leave behind:

1. **Smoke test**  
   App launches under `run_test()`.

2. **Behaviour test**  
   The user interaction that changed actually works.

3. **Layout or size test**  
   Use an alternate terminal size when the layout matters.

4. **Snapshot test**  
   Add one when the feature is visually structured and regressions are likely.

## Pilot-first testing

Use `run_test()` and `Pilot` for:
- `press(...)`
- `click(...)`
- filling inputs
- pausing for async work
- asserting widget state

Good behaviour tests:
- typing into a filter updates results
- selecting a row updates a detail pane
- pressing a binding changes mode/screen
- a save action updates status and notifies

## Snapshot tests

Use snapshot tests when:
- TCSS and layout are important
- the app has multiple panes
- narrow vs wide layouts matter
- a refactor might silently change structure

Useful variations:
- alternate terminal sizes
- initial key presses
- a small setup callback before capture

## Layout-sensitive features

Always consider a second size when the app has:
- side panes
- breakpoints
- content switchers
- long forms
- data tables
- browser support

## Test-writing guidance

- give important widgets stable IDs
- avoid selectors based on display text when IDs or classes are better
- test through user actions rather than internal methods when possible
- pause for worker completion in the smallest reliable way
- keep one smoke test even if snapshot coverage exists

## Good output for a skill-driven change

- a passing smoke test
- a focused behaviour test
- a comment or docstring only where behaviour is subtle
- snapshot coverage only where it earns its keep
