# Object Store & Org Filesystem Reference

Unified storage layer for Eve Horizon: S3-compatible object storage backing org filesystem sync and app object buckets.

## Use When

- You need to set up or troubleshoot org filesystem sync between local machines and Eve.
- You need to share files via share tokens or public paths.
- You need to understand how agents access the org filesystem at runtime.
- You need to declare object store buckets for an app service.
- You need to configure native GCS storage via Workload Identity.
- You need to mount Google Drive (or other cloud storage) into an org's filesystem.

## Load Next

- `references/cli-org-project.md` for org/project setup and docs CLI commands.
- `references/secrets-auth.md` for access groups and scoped bindings (orgfs permissions).
- `references/events.md` for event-driven automation triggered by file changes.

## Ask If Missing

- Confirm target org ID before running any `eve fs` command.
- Confirm sync mode needed (two-way, push-only, pull-only) before initializing.
- Confirm include/exclude patterns if syncing a subset of files.

## Overview

Four storage primitives share a common object store backend:

| Primitive | Scope | Use Case |
|-----------|-------|----------|
| **Object Store** | Platform | Binary file storage via presigned URL transfers |
| **Org Filesystem** | Org | Multi-device file sync with real-time events |
| **Org Docs** | Org | Versioned document store with full-text search |
| **Cloud FS** | Org/Project | Google Drive (and future providers) as mounted cloud filesystems |

The object store is MinIO locally (k3d dev) and S3/GCS/R2/Tigris in cloud. All speak the S3 protocol.

### Storage Backends

The platform supports two native storage backends:

| Backend | Config | Auth | Use Case |
|---------|--------|------|----------|
| **S3-compatible** | `EVE_STORAGE_BACKEND=s3` (default) | Access key + secret key | AWS S3, GCS+HMAC, MinIO, R2, Tigris |
| **Native GCS** | `EVE_STORAGE_BACKEND=gcs` | Workload Identity (ADC) | Google Cloud Storage without API keys |

When `EVE_STORAGE_BACKEND=gcs` and no HMAC keys are set, the platform uses the native GCS client with Application Default Credentials / Workload Identity. No API keys or HMAC configuration needed -- the GKE service account's Workload Identity binding provides auth automatically.

The `ObjectStorageClient` abstraction (`packages/shared/src/storage/`) provides a unified interface:
- `S3StorageClient`: existing path for all S3-compatible backends
- `GcsStorageClient`: native GCS via ADC (dynamic import, only loaded when `backend=gcs`)

All consumers (StorageService, BucketProvisioner, InvokeService, snapshot system) use this abstraction. AWS deployments are completely unaffected.

**CORS**: Org buckets are automatically created with CORS headers (`GET`, `PUT`, `HEAD` from all origins). This means browser JS (`fetch`, `XMLHttpRequest`, PDF.js) can access presigned URLs directly. Simple HTML elements (`<img>`, `<embed>`, `<a>`) work without CORS.

## Org Filesystem

### Sync Protocol

Files transfer via **presigned URLs** -- content never flows through the Eve API:

- **Upload**: CLI detects change -> computes SHA-256 -> gets presigned PUT URL -> uploads direct to S3
- **Download**: SSE event stream delivers presigned GET URL -> CLI downloads direct from S3

### Sync Modes

| Mode | Behavior |
|------|----------|
| `two-way` | Bidirectional sync (default) |
| `push-only` | Local -> remote only |
| `pull-only` | Remote -> local only |

### CLI Commands

```bash
# Initialize sync
eve fs sync init --org <org> --local <path> [--mode two-way|push-only|pull-only] \
  [--remote-path /] [--include "**/*.md"] [--exclude "**/.git/**"]

# Status and monitoring
eve fs sync status --org <org>
eve fs sync logs --org <org> [--follow]
eve fs sync doctor --org <org>

# Link management
eve fs sync pause --org <org>
eve fs sync resume --org <org>
eve fs sync disconnect --org <org>
eve fs sync mode --org <org> --set <mode>

# Conflict resolution
eve fs sync conflicts --org <org>
eve fs sync resolve --org <org> --conflict <id> --strategy <pick-remote|pick-local|manual>
```

### Share Tokens

Time-limited, revocable access to individual files:

```bash
eve fs share <path> --org <org> [--expires 7d] [--label "description"]
eve fs shares --org <org>
eve fs revoke <token> --org <org>
```

### Public Paths

Permanent unauthenticated access to path prefixes:

```bash
eve fs publish <path-prefix> --org <org> [--label "description"]
eve fs public-paths --org <org>
```

Public file resolver (no auth): `GET /orgs/{orgId}/fs/public/{path}`

### Text Indexing

Text files (markdown, YAML, JSON; under 512 KB) synced to the org filesystem are automatically indexed into org documents for full-text search. Indexing is async (poll interval: 2s, batch: 10).

### Events

| Event | Trigger |
|-------|---------|
| `file.created` | New file uploaded |
| `file.updated` | Existing file modified |
| `file.deleted` | File removed |
| `conflict.detected` | Both sides modified same file |

SSE stream: `GET /orgs/{orgId}/fs/events/stream?after_seq=<n>`

### Agent Runtime

Warm pods mount org filesystem as PVC at `/org` (`EVE_ORG_FS_ROOT=/org`). Agents read/write directly -- changes sync to S3 and index into org docs automatically.

## App Object Stores

Declare S3-compatible buckets per service in the manifest. Eve provisions each bucket at deploy time and injects credentials as env vars. See `references/manifest.md` (App Object Store Buckets) for the full schema.

```yaml
services:
  api:
    x-eve:
      object_store:
        buckets:
          - name: uploads
            visibility: private
          - name: avatars
            visibility: public
            cors:
              origins: ["*"]
```

Each bucket is provisioned per environment. Auto-injected env vars (per bucket, uppercased name):

| Variable | Description |
|----------|-------------|
| `STORAGE_ENDPOINT` | S3-compatible endpoint |
| `STORAGE_REGION` | Storage region |
| `STORAGE_ACCESS_KEY_ID` / `STORAGE_SECRET_ACCESS_KEY` | Per-deployment scoped credentials |
| `STORAGE_BUCKET_<NAME>` | Physical bucket name (e.g. `eve-org-myorg-myapp-test-uploads`) |
| `STORAGE_FORCE_PATH_STYLE` | `true` for MinIO, omitted for AWS S3 |

## Cloud FS (Google Drive)

Cloud FS mounts external cloud storage (Google Drive today) into the org's storage topology. Agents and apps interact with cloud files through Eve's Cloud FS APIs and tools instead of provider-specific APIs.

### Architecture

Mounts link an org's OAuth integration to a specific provider folder. The platform handles:
- **Mount registry**: DB table mapping `(org, project?) -> provider folder`
- **Change tracking**: Hybrid push (webhooks) + poll (changes cursor) for detecting external changes
- **Auto-indexing**: Filed documents update org docs for full-text search
- **Agent tools**: File operations exposed to agents at runtime

### CLI Commands

```bash
# Mount a Google Drive folder
eve cloud-fs mount \
  --provider google-drive \
  --folder-id <drive-folder-id> \
  --mode read_write \
  --label "Engineering Shared Drive"

# List / browse / search
eve cloud-fs list
eve cloud-fs ls / --mount <mount-id>
eve cloud-fs ls /subfolder --mount <mount-id>          # alias: browse
eve cloud-fs search <query> [--mount <mount-id>]

# Manage
eve cloud-fs show <mount-id>
eve cloud-fs update <mount-id> --mode read_only
eve cloud-fs unmount <mount-id>                        # aliases: remove, delete
```

### Mount Configuration

| Field | Description |
|-------|-------------|
| `provider` | `google_drive` internally. CLI accepts `google-drive` and normalizes it. |
| `root_folder_id` | Provider-specific folder ID |
| `mode` | `read_only`, `write_only`, `read_write` (default) |
| `auto_index` | Update org docs on file changes (default: `true`) |
| `label` | Human-friendly display name |

Mounts are org-scoped, optionally project-scoped. Each mount requires an active integration connection (`eve integrations connect google-drive`). Per-org OAuth app credentials are required (see `references/manifest.md`, Per-Org OAuth Configs).

### Per-Mount File Operations API

The March 18, 2026 Cloud FS update added direct per-mount file operations in the API for Drive-backed mounts. These routes are useful for app UIs and service-to-service flows that need to browse a mounted folder, fetch metadata, download files, upload content, or create folders without going through provider SDKs.

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/orgs/:org_id/cloud-fs/mounts/:mount_id/browse?path=/subdir` | Browse a specific mount by path or `folder_id` |
| `GET` | `/orgs/:org_id/cloud-fs/mounts/:mount_id/files/:file_id` | Fetch file metadata |
| `GET` | `/orgs/:org_id/cloud-fs/mounts/:mount_id/files/:file_id/download` | Stream file contents |
| `POST` | `/orgs/:org_id/cloud-fs/mounts/:mount_id/upload` | Upload a file to a target path |
| `POST` | `/orgs/:org_id/cloud-fs/mounts/:mount_id/folders` | Create a folder |

Upload details:
- Requires `cloud_fs:admin`.
- Send raw file bytes as the request body.
- Set `X-Cloud-FS-Path: /folder/file.ext` to choose the destination path.
- Set `Content-Type` to the file MIME type.
- Read-only mounts reject uploads and folder creation.

### Events

Cloud FS changes emit system events: `system.cloud_fs.file.created`, `system.cloud_fs.file.modified`, `system.cloud_fs.file.deleted`. These can trigger workflows (e.g., a filing agent that auto-organizes uploaded documents).

## Access Control

| Permission | Allows |
|------------|--------|
| `orgfs:read` | List, download, view shares and public paths |
| `orgfs:write` | Upload, create links, resolve conflicts |
| `orgfs:admin` | Manage share tokens, publish/unpublish public paths |

Links support path-scoped ACLs via `scope_json.allow_prefixes`.

## Org Docs (Versioned Document Store)

Covered in detail in the `storage-primitives.md` reference (Section 5). Key points relevant to the storage layer:

- Org docs is Postgres-native -- content stored in rows, not the object store
- Full-text search via `tsvector` with weighted path (A) and content (B)
- Async indexer bridges org filesystem -> org docs for text files
- Search modes: `text` (default), `semantic`, `hybrid` (semantic/hybrid degrade to text when embeddings absent)
- Lifecycle: `--review-in`, `--expires-in`, `eve docs stale`, `eve docs review`
