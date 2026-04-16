# Browser and delivery

Textual can run in the terminal and can also be served to a browser. Design export and handoff flows accordingly.

## Dev loop

### `textual run --dev`
Use for day-to-day iteration:
- live CSS updates
- faster feedback while shaping layouts
- easier debugging during development

### `textual console`
Use when:
- event flow is unclear
- style or layout behaviour is confusing
- you need extra introspection while the app runs

### `textual serve`
Use when:
- the app should run in a browser
- download/export behaviour matters
- layout parity between terminal and browser matters

## Delivery APIs

Prefer delivery APIs over assuming local filesystem access when the app may run in a browser.

### `deliver_text(...)`
Use for:
- CSV
- JSON
- markdown exports
- generated reports

### `deliver_binary(...)`
Use for:
- images
- zip files
- binary artefacts
- generated documents

### `deliver_screenshot(...)`
Use when you want to hand the user an image of the current app state.

Listen for delivery completion/failure if the flow needs confirmation or fallback messaging.

## `open_url(...)`
Use when the app should hand off to a browser or external page:
- documentation
- issue tracker
- help site
- user-facing links

## Browser-friendly design rules

- avoid flows that only make sense with a local working directory
- provide explicit download/export actions
- make narrow layouts work well
- do not bury key actions in hover-only affordances
- test both terminal and browser scenarios for apps that promise both

## Export checklist

Before you ship an export flow, ask:
1. does this need to work in a browser?
2. should the user download a file instead of writing to a local path?
3. do I need success/failure notifications?
4. do I need a screenshot or text artefact for bug reports?
