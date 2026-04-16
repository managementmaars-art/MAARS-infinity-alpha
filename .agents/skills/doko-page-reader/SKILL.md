---
name: doko-page-reader
description: Read and extract content from web pages through a locally connected Chrome browser using Dokobot local bridge only. Use when an agent needs JavaScript-rendered pages, logged-in browser content, or pages that block headless scrapers and should be handled entirely through the user's local browser.
---

# Dokobot Local

Use Dokobot only through the local bridge and the user's Chrome session.

## Prerequisites

- Ensure `dokobot` CLI is installed.
- Ensure Chrome is open with the Dokobot extension enabled.
- Ensure the local bridge is installed with `dokobot install-bridge`.
- Prefer local browser reading when the page needs JavaScript, an authenticated browser session, or a real browser to bypass bot friction.

## Core workflow

1. Read the page in local mode:

```bash
dokobot doko read '<URL>' --local
```

2. If the read fails because no local browser is available, tell the user to open Chrome, enable the Dokobot extension, and verify the local bridge is installed.

3. For long pages, collect more screens or extend timeout:

```bash
dokobot doko read '<URL>' --local --screens 5 --timeout 120
```

4. When the response includes a `sessionId` and more scrolling is needed, continue the same session:

```bash
dokobot doko read '<URL>' --local --session-id <SESSION_ID> --screens 5
```

5. Close the session when finished:

```bash
dokobot doko close-session <SESSION_ID> --local
```

## Commands

### Read a page

Use:

```bash
dokobot doko read '<URL>' --local [--screens N] [--timeout S] [--format text|chunks] [--reuse-tab]
```

Notes:

- Always include `--local`.
- Use `--screens N` to scroll and capture more content.
- Use `--timeout S` for slow pages.
- Use `--format chunks` only when segmented content is needed.
- Use `--reuse-tab` to avoid opening a new tab for the same URL.

Default text response shape:

```typescript
{
  text?: string
  sessionId: string
  canContinue: unknown
}
```

Chunked response shape:

```typescript
{
  text?: string
  chunks: Array<{
    id: string
    sourceIds: Array<string>
    text: string
    bounds: [number, number, number, number]
    zIndex?: number
    containerId?: string
  }>
  sessionId: string
  canContinue: unknown
}
```

## Operating rules

- Treat this skill as local-only.
- Keep the command surface minimal: use only `read --local` and `close-session --local`.
- Analyze and summarize content after receiving the raw page text; keep Dokobot focused on extraction.
- Close sessions explicitly when you are done.
- Keep concurrent reads modest; up to 5 parallel reads is a reasonable ceiling.

## Troubleshooting

- `No registered devices.` or similar local-connection failures: Ask the user to open Chrome, enable the Dokobot extension, and confirm the local bridge is installed.
- `503`: Treat it as no local extension/device available and check the local setup.
- `504`: Retry with a larger timeout or fewer screens.
- `422`: Treat it as a cancelled or failed local read and retry if appropriate.

## Security

- Keep usage local to the user's browser session.
- Treat `read` as read-only extraction.
