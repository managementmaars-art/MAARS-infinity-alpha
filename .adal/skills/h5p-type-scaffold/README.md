# H5P Type Scaffolder

This skill scaffolds a modern H5P content type using proven boilerplates and vanilla JavaScript. It generates the minimal files needed to build, test, and package a new library.

## Packaging intent

- `library-install` (default): upload a library/content-type package to a platform installer.
- `content-import` (advanced): import a content instance package (`h5p.json` + `content/content.json`).
- The scaffold produced by this skill is for `library-install`.

## What it generates

- `library.json` and `semantics.json`
- `src/entries`, `src/scripts`, `src/styles`
- `README.md` (templates)
- `DEV.md` (templates, dev harness)
- `webpack.config.js`, `.babelrc`
- build scripts in `package.json`

## Quick start

```bash
bash /mnt/skills/user/h5p-type-scaffold/scripts/scaffold.sh \
  --title "My Content Type" \
  --machine "H5P.MyContentType" \
  --kind "content" \
  --version "1.0.0" \
  --description "Short description" \
  --author "Your Name" \
  --license "MIT" \
  --template "snordian" \
  --out /path/to/output
```

Editor widget example:

```bash
bash /mnt/skills/user/h5p-type-scaffold/scripts/scaffold.sh \
  --title "My Editor Widget" \
  --machine "H5PEditor.MyWidget" \
  --kind "editor" \
  --out /path/to/output
```

## Build & package

```bash
npm install
npm run build
h5p core
h5p setup <library>
h5p server
h5p pack <library> [my-library.h5p]
```

Use this package in the platform's library/content-type upload flow.  
For library packages, keep `library.json` and avoid top-level `h5p.json` or `content/`.

### Strict-validator packaging (Drupal 11.x H5P 2.0.0+)

Some platforms (notably Drupal 11.x with the H5P 2.0.0 beta module) reject zip
directory entries such as `dist/` or `language/` because they lack an allowed
file extension. Use `scripts/pack.sh` instead of `h5p pack` to produce a
`.h5p` archive that omits directory entries:

```bash
bash /mnt/skills/user/h5p-type-scaffold/scripts/pack.sh \
  --dir /path/to/built-library \
  --out MyLibrary.h5p
```

Add `--strict` to abort if any packaged file lacks an allowed extension.

Validate an unpacked package before upload:

```bash
bash /mnt/skills/user/h5p-type-scaffold/scripts/validate-package.sh --mode library-install --dir /path/to/unpacked
bash /mnt/skills/user/h5p-type-scaffold/scripts/validate-package.sh --mode content-import --dir /path/to/unpacked
```

## Notes

- Default template is `snordian` (linting + i18n scaffolding).
- Use `vanilla` for the simplest official baseline.
- Use `editor` with `--kind editor` to scaffold H5P editor widgets.
- Other options to consider: `otacke/h5p-editor-boilerplate` (editor widgets) and `tarmoj/h5p-react-boilerplate` (React, but stale).
- For a local dev harness, see `references/DEV-HARNESS.md` or run `scripts/h5p-dev.sh`.
- Validate package layout before upload with `scripts/validate-package.sh`.
- Pack for strict validators (Drupal 11.x) with `scripts/pack.sh` (omits directory entries).
- For xAPI integration guidance, see `references/XAPI.md`.
- See `references/CONCEPTS.md`, `references/CONTENT-TYPE-AUTHORING.md`, and `references/H5P-CLI.md` for deeper guidance.
- If import errors mention `content/ not allowed`, missing `preloadDependencies` in `h5p.json`, or invalid `license` in `h5p.json`, you're importing a content package through a library upload path.
- If Drupal 11.x (H5P 2.0.0 beta) rejects the upload with "File 'dist/' not allowed" or "File 'language/' not allowed", the `.h5p` zip contains directory entries. Repack using `scripts/pack.sh --dir <library-dir>`.
