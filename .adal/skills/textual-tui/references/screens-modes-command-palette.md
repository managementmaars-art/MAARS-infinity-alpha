# Screens, modes, and command palette

These three features solve different navigation problems.

## Screens

Use `Screen` when the user changes working context.

Examples:
- dashboard -> job detail
- repository browser -> file editor
- home -> settings
- list -> edit form

Use screens when:
- back-navigation matters
- focus should restore naturally
- the layout meaningfully changes
- a section has its own state and event handling

## Modal screens

Use `ModalScreen` for short interruptions:
- confirmation prompts
- delete dialogs
- small pickers
- quick forms

Do not use a modal to replace a full screen just because it is faster to code.

## Modes

Modes are named screen stacks for durable top-level areas.

Use modes when:
- the app has persistent product areas
- each area may drill down internally
- users need to switch between major sections without losing where they were

Good examples:
- dashboard / jobs / settings / logs
- inbox / projects / account

Bad example:
- a simple two-step wizard

## Command palette

Add command palette support when:
- bindings are numerous
- actions need discoverability
- the app has screens or modes
- power users benefit from searchable commands

Use app-level providers for global actions and screen-level providers for local actions.

Typical palette commands:
- switch mode
- open help
- focus search
- export/download
- toggle theme
- jump to important screens

## Practical defaults

### One-screen app
- no modes
- command palette optional
- `ContentSwitcher` only for local step flows

### Multi-screen workflow
- screens yes
- modes maybe
- command palette usually worthwhile

### Admin shell
- modes yes
- screens inside modes often yes
- command palette strongly recommended

## Common mistakes

- using modes when plain screens would do
- hiding all major actions behind key bindings with no palette support
- creating ad-hoc screen stacks by manually swapping many widgets
- keeping giant screen-specific methods inside the `App` instead of extracting a `Screen`
