---
title: Use CLI for Component Schema Management
impact: MEDIUM
impactDescription: enables version control and multi-environment sync
tags: cli, components, sync, devops, version-control
---

## Use CLI for Component Schema Management

**Impact: MEDIUM (enables version control and multi-environment sync)**

Use the Storyblok CLI to pull, push, and sync component schemas. This enables version control, code review, and consistent schemas across environments.

**Incorrect (manual component management):**

```bash
# Bad: Making changes directly in production UI
# Changes are not tracked, can't be rolled back

# Bad: Copy-pasting between spaces
# Error-prone, inconsistent, no audit trail

# Bad: No schema in version control
# Team members can't review component changes
```

**Correct (CLI v4 workflow):**

> **Note:** CLI v4 uses a new `<domain> <verb>` command structure. The old v3 syntax (`pull-components`, `push-components`) is deprecated.

```bash
# Install Storyblok CLI v4
npm install -g storyblok

# Login to Storyblok
storyblok login

# Pull components from development space (CLI v4 syntax)
storyblok components pull --space 12345

# Components saved to .storyblok/12345/
# ├── components.json
# ├── groups.json
# ├── presets.json
# └── tags.json
```

```bash
# Push components to staging space (CLI v4 syntax)
# Use --from to specify the source space ID
storyblok components push --space 67890 --from 12345

# Sync components between spaces
storyblok sync \
  --type components \
  --source 12345 \
  --target 67890

# Sync multiple resource types
storyblok sync \
  --type components,datasources,roles \
  --source 12345 \
  --target 67890

# Preview changes before applying (CLI v4 syntax)
storyblok components push --space 67890 --from 12345 --preview
```

```json
// .storyblok/components/12345/components.json
{
  "components": [
    {
      "name": "hero",
      "display_name": "Hero Section",
      "is_nestable": true,
      "is_root": false,
      "schema": {
        "title": {
          "type": "text",
          "pos": 0,
          "required": true,
          "translatable": true
        },
        "subtitle": {
          "type": "text",
          "pos": 1,
          "translatable": true
        },
        "image": {
          "type": "asset",
          "pos": 2,
          "filetypes": ["images"]
        }
      }
    }
  ]
}
```

```yaml
# .github/workflows/storyblok-sync.yml
name: Sync Storyblok Components

on:
  push:
    branches: [main]
    paths:
      - '.storyblok/components/**'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Storyblok CLI
        run: npm install -g storyblok

      - name: Login to Storyblok
        run: storyblok login --token ${{ secrets.STORYBLOK_PAT }}

      - name: Push to Staging
        run: |
          storyblok components push \
            --space ${{ secrets.STORYBLOK_STAGING_SPACE }} \
            --from ${{ secrets.STORYBLOK_DEV_SPACE }}

      - name: Push to Production
        if: github.ref == 'refs/heads/main'
        run: |
          storyblok components push \
            --space ${{ secrets.STORYBLOK_PROD_SPACE }} \
            --from ${{ secrets.STORYBLOK_DEV_SPACE }}
```

```bash
# Generate TypeScript types from components (CLI v4 syntax)
# First pull components, then generate types
storyblok components pull --space 12345
storyblok types generate --space 12345

# Or use storyblok-generate-ts package
npx storyblok-generate-ts \
  --sourceFilePaths .storyblok/*/components.json \
  --destinationFilePath ./src/types/storyblok-component-types.d.ts
```

**CLI v4 commands reference:**

| Command (CLI v4) | Description |
|------------------|-------------|
| `components pull` | Download components from space |
| `components push` | Upload components to space |
| `sync` | Sync resources between spaces |
| `components delete` | Remove component from space |
| `types generate` | Generate TypeScript types |

**Development workflow:**

1. Pull from dev space: `storyblok components pull --space DEV_SPACE`
2. Edit `components.json` locally
3. Commit changes to git
4. PR review for component changes
5. CI pushes to staging on merge
6. Promote to production after testing

Reference: [Storyblok CLI](https://www.storyblok.com/docs/packages/storyblok-cli)
