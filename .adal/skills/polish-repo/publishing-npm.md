# Publishing npm Packages

Reference guide for setting up automated npm publishing with semantic-release and OIDC-based authentication.

## Pattern reference

- Config: `next-geo/release.config.cjs`
- Workflow: `next-geo/.github/workflows/release.yaml`

## Overview

This setup uses:
- **semantic-release** to automate versioning and publishing based on Conventional Commits
- **npm Trusted Publishing (OIDC)** so no `NPM_TOKEN` secret is needed — GitHub Actions authenticates directly with npm via OpenID Connect
- **Provenance** so published packages are cryptographically linked to their source repo and build

## 1. Install dependencies

```bash
npm install -D semantic-release @semantic-release/commit-analyzer @semantic-release/release-notes-generator @semantic-release/npm @semantic-release/github
```

## 2. Create release.config.cjs

```js
module.exports = {
  branches: ["main"],
  plugins: [
    [
      "@semantic-release/commit-analyzer",
      {
        releaseRules: [
          { type: "feat", release: "minor" },
          { type: "fix", release: "patch" },
          { type: "perf", release: "patch" },
          { breaking: true, release: "major" },
        ],
      },
    ],
    "@semantic-release/release-notes-generator",
    "@semantic-release/npm",
    "@semantic-release/github",
  ],
};
```

Plugins run in order:
1. **commit-analyzer** — determines the release type from commit messages
2. **release-notes-generator** — generates changelog from commits
3. **npm** — publishes to npm
4. **github** — creates a GitHub release with notes

## 3. Create the release workflow

`.github/workflows/release.yaml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
      id-token: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
          registry-url: "https://registry.npmjs.org"

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Run tests
        run: npm test

      - name: Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_CONFIG_PROVENANCE: true
        run: npx semantic-release
```

Key details:
- **`fetch-depth: 0`** — semantic-release needs full git history to analyze commits
- **`persist-credentials: false`** — prevents the default GITHUB_TOKEN from interfering with semantic-release's git operations
- **`id-token: write`** — required for OIDC-based npm authentication
- **`NPM_CONFIG_PROVENANCE: true`** — enables npm provenance (links package to source)
- **No `NPM_TOKEN` secret** — Trusted Publishing uses OIDC instead

## 4. Configure npm Trusted Publishing

On npmjs.com:
1. Go to your package's settings → Publishing access
2. Add a new Trusted Publisher
3. Set the repository to `continuedev/{repo-name}`
4. Set the workflow to `release.yaml`
5. Set the environment to empty (no environment required)

This allows the GitHub Actions workflow to publish without an npm token.

## 5. package.json requirements

Ensure these fields are set correctly:

```json
{
  "name": "your-package-name",
  "version": "0.1.0",
  "repository": {
    "type": "git",
    "url": "https://github.com/continuedev/{repo-name}.git"
  },
  "files": [
    "dist",
    "README.md"
  ],
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    }
  }
}
```

- **`version`** — semantic-release manages this; set to `0.1.0` or `1.0.0` initially
- **`repository`** — must match the GitHub repo for provenance to work
- **`files`** — only include what consumers need (dist, README, etc.)
- **`exports`** — use explicit exports map for ESM packages

## 6. How releases work

1. Developer merges a PR to `main` with Conventional Commit messages
2. GitHub Actions triggers the release workflow
3. semantic-release analyzes commits since the last release:
   - `feat:` → minor bump (0.1.0 → 0.2.0)
   - `fix:` / `perf:` → patch bump (0.1.0 → 0.1.1)
   - `BREAKING CHANGE:` → major bump (0.1.0 → 1.0.0)
   - `docs:` / `chore:` / `ci:` → no release
4. If a release is needed, semantic-release:
   - Updates `version` in package.json
   - Publishes to npm with provenance
   - Creates a GitHub release with auto-generated notes
   - Creates a git tag

## Troubleshooting

- **"No npm token"** — Ensure `id-token: write` is in the workflow permissions and Trusted Publishing is configured on npmjs.com
- **"No release published"** — Commits must follow Conventional Commits format. `chore:` and `docs:` commits don't trigger releases.
- **"Permission denied"** — The `GITHUB_TOKEN` needs `contents: write` to create tags and releases
