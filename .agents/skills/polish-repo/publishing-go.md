# Publishing Go CLI Tools

Reference guide for setting up automated Go binary releases with GoReleaser and tag-based GitHub Actions.

## Pattern reference

- Config: `agentduty/cli/.goreleaser.yml`
- Workflow: `agentduty/.github/workflows/release.yml`

## Overview

This setup uses:
- **GoReleaser** to build cross-platform binaries and create GitHub releases
- **Tag-based releases** — push a `v*` tag to trigger a release
- **Cross-compilation** for linux/darwin on amd64/arm64
- **Checksums** for verifying binary integrity

## 1. Create .goreleaser.yml

```yaml
version: 2

before:
  hooks:
    - go mod tidy

builds:
  - main: ./cmd/{project-name}
    binary: "{{ .ProjectName }}"
    env:
      - CGO_ENABLED=0
    goos:
      - linux
      - darwin
    goarch:
      - amd64
      - arm64
    ldflags:
      - -s -w
      - -X main.version={{ .Version }}
      - -X main.commit={{ .ShortCommit }}
      - -X main.date={{ .Date }}

archives:
  - format: tar.gz
    name_template: "{{ .ProjectName }}-{{ .Os }}-{{ .Arch }}"

checksum:
  name_template: "checksums.txt"

release:
  github:
    owner: continuedev
    name: "{{ .ProjectName }}"
```

Key details:
- **`CGO_ENABLED=0`** — produces static binaries that work without system C libraries
- **`ldflags`** — injects version, commit, and build date at compile time
- **`-s -w`** — strips debug info to reduce binary size
- **`format: tar.gz`** — standard archive format for CLI distribution
- **`name_template`** — produces binaries like `myproject-linux-amd64`, `myproject-darwin-arm64`

## 2. Version injection

In your main package, declare variables that GoReleaser populates via ldflags:

```go
package main

var (
    version = "dev"
    commit  = "none"
    date    = "unknown"
)
```

Use these in a `version` command:

```go
fmt.Printf("%s version %s (commit %s, built %s)\n", projectName, version, commit, date)
```

## 3. Create the release workflow

`.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version-file: go.mod

      - name: Run GoReleaser
        uses: goreleaser/goreleaser-action@v6
        with:
          version: "~> v2"
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Key details:
- **Triggered on `v*` tags** — not on push to main
- **`fetch-depth: 0`** — GoReleaser needs git history for changelog generation
- **`go-version-file: go.mod`** — uses the Go version specified in the project
- **`--clean`** — removes previous build artifacts before building

## 4. Release process

Releases are triggered by pushing a version tag:

```bash
# Tag the release
git tag v1.0.0

# Push the tag
git push origin v1.0.0
```

GoReleaser will:
1. Build binaries for all platform/arch combinations
2. Create tar.gz archives
3. Generate checksums.txt
4. Create a GitHub release with:
   - Auto-generated changelog from commits since the last tag
   - Binary archives as release assets
   - Checksum file

## 5. Binary naming conventions

Archives are named `{project}-{os}-{arch}.tar.gz`:
- `myproject-linux-amd64.tar.gz`
- `myproject-linux-arm64.tar.gz`
- `myproject-darwin-amd64.tar.gz`
- `myproject-darwin-arm64.tar.gz`

Inside each archive, the binary is just named `{project}` (no platform suffix).

## 6. Installation instructions for users

Include these in the README:

```bash
# Download the latest release for your platform
curl -sL https://github.com/continuedev/{project}/releases/latest/download/{project}-$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m | sed 's/x86_64/amd64/').tar.gz | tar xz

# Move to PATH
sudo mv {project} /usr/local/bin/
```

Or direct users to the [Releases page](https://github.com/continuedev/{project}/releases).

## Troubleshooting

- **"tag not found"** — Ensure the tag is pushed to the remote: `git push origin v1.0.0`
- **"binary not found"** — Check the `main` path in `.goreleaser.yml` matches your project's entry point
- **"CGO required"** — If your project needs CGO (e.g., SQLite), remove `CGO_ENABLED=0` and use `zig` for cross-compilation, or limit to native platform builds
- **"permission denied"** — The `GITHUB_TOKEN` needs `contents: write` to create releases
