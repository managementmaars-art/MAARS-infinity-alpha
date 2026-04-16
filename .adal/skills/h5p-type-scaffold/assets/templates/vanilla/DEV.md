# Interactive Development (h5p-cli)

Use `h5p-cli` as a local editor/server while you build the content type.

## Prerequisites

```bash
npm install -g h5p-cli
```

## Harness Setup

From this library root:

```bash
mkdir -p .h5p-dev
cd .h5p-dev
h5p core
mkdir -p libraries
ln -s .. "libraries/<machine>"
h5p setup <machine>
h5p server
```

Open the local server URL that `h5p server` prints (usually `http://localhost:8080`).

## Notes

- If `h5p setup` fails for a brand new library, retry without it and add dependencies later.
- Keep your build watcher running: `npm run build -- --watch`.

## Packaging

After building, pack for upload:

```bash
h5p pack <machine> [my-library.h5p]
```

If your target platform uses strict file validation (e.g. Drupal 11.x H5P 2.0.0+)
and rejects entries like `dist/` or `language/`, use `scripts/pack.sh` instead:

```bash
bash scripts/pack.sh --dir . --out <machine>.h5p
```
