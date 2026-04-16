# __TITLE__

Scaffolded H5P editor widget library: __MACHINE__ v__VERSION__.

## Editor widget essentials
- Entry: `src/scripts/h5peditor-__SLUG__.js` implements editor lifecycle methods like `appendTo`, `validate`, and `remove`.
- Styles: `src/styles/h5peditor-__SLUG__.scss` (built into `dist/`).
- Metadata: `library.json` declares the editor library and preloaded assets (`runnable: 0`).

## Build

```bash
npm install
npm run build
```

## Local dev (h5p-cli)

```bash
h5p core
h5p setup <library>
h5p server
```

The widget is available in the H5P editor when installed and referenced by a content type.

## Packaging

```bash
h5p pack <library> [<library2>...] [my.h5p]
```

For editor-library install, upload a package containing `library.json`-based libraries.
If validation errors mention `content/ not allowed` or invalid `h5p.json`, use the library upload flow instead of content import.
If running from this skill repo, validate package intent first with `scripts/validate-package.sh`.

### Drupal 11.x / strict validators

If upload fails with "File 'dist/' not allowed" or similar, the `.h5p` zip
contains directory entries. Use `scripts/pack.sh` to create a clean archive:

```bash
bash scripts/pack.sh --dir . --out __EDITOR_MACHINE__.h5p
```

Add `--strict` to abort if any file lacks an allowed H5P extension.

## References
- https://h5p.org/creating-editor-widgets
- https://h5p.org/technical-overview
- https://github.com/h5p/h5p-cli
- https://h5p.org/h5p-cli-guide

## xAPI Integration

H5P content types emit xAPI statements via the built-in event system. Your platform forwards those statements to an LRS.

- Emit statements: `triggerXAPI(...)`, `triggerXAPIScored(...)`
- Listen for statements: `instance.on('xAPI', ...)`

See `references/XAPI.md` in this repo for full guidance.
