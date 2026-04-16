# __TITLE__

Scaffolded H5P content type library: __MACHINE__ v__VERSION__.

## Authoring essentials
- Runtime entry: `src/scripts/h5p-__SLUG__.js` implements `attach` to render into a container.
- Editor schema: `semantics.json` defines the data structure, editor fields, and validation.
- Metadata & assets: `library.json` declares metadata and preloaded JS/CSS (built into `dist/`).

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

Commands run relative to the working directory. Use `h5p help` to see supported commands and `h5p help pack` for packaging.

## Packaging

```bash
h5p pack <library> [<library2>...] [my.h5p]
```

For content-type library install, upload a package containing `library.json`-based libraries.
If validation errors mention `content/ not allowed` or invalid `h5p.json`, use the library upload flow instead of content import.
If running from this skill repo, validate package intent first with `scripts/validate-package.sh`.

### Drupal 11.x / strict validators

If upload fails with "File 'dist/' not allowed" or similar, the `.h5p` zip
contains directory entries. Use `scripts/pack.sh` to create a clean archive:

```bash
bash scripts/pack.sh --dir . --out __MACHINE__.h5p
```

Add `--strict` to abort if any file lacks an allowed H5P extension.

## References
- https://h5p.org/library-development
- https://h5p.org/semantics
- https://github.com/h5p/h5p-cli
- https://h5p.org/h5p-cli-guide

## xAPI Integration

H5P content types emit xAPI statements via the built-in event system. Your platform forwards those statements to an LRS.

- Emit statements: `triggerXAPI(...)`, `triggerXAPIScored(...)`
- Listen for statements: `instance.on('xAPI', ...)`

See `references/XAPI.md` in this repo for full guidance.
