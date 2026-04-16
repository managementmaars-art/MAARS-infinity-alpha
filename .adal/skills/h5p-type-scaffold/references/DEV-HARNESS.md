# H5P CLI Dev Harness

Use the H5P CLI as a lightweight local editor/server for interactive development.

## Prerequisites

- Install CLI: `npm install -g h5p-cli`
- Work from your scaffolded library directory (contains `library.json`).

## Quick Start (Manual)

From your library root:

```bash
# 1) Create a local workspace for h5p-cli
mkdir -p .h5p-dev

# 2) Initialize H5P core in the workspace
cd .h5p-dev
h5p core

# 3) Link your library into the workspace
mkdir -p libraries
ln -s .. "libraries/<machine>"

# 4) Fetch dependencies (optional but recommended)
h5p setup <machine>

# 5) Run the local editor/server
h5p server
```

Open the local server URL that `h5p server` prints (usually `http://localhost:8080`).

## Helper Script

If you are running this skill locally, you can use the helper:

```bash
bash scripts/h5p-dev.sh
```

This script:

- Creates a `.h5p-dev` workspace
- Runs `h5p core`
- Symlinks your library into `libraries/`
- Runs `h5p setup` (unless you pass `--no-setup`)
- Starts `h5p server`

## Notes

- If `h5p setup` fails for a brand new library, retry with `--no-setup` and add dependencies manually later.
- Keep your build watcher running (`npm run build -- --watch`) while testing.

## References
- https://github.com/h5p/h5p-cli
- https://h5p.org/h5p-cli-guide
