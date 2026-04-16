# MCP Attack Detection Checks — Design Document

**Date:** 2026-03-04
**Version target:** 3.1.0
**Scope:** 8 new critical checks (#55-#62) for MCP server attack patterns

## Motivation

MCP (Model Context Protocol) adoption is accelerating, and with it a growing attack
surface. Research from Invariant Labs, Trail of Bits, Palo Alto Unit 42, Keysight, and
Snyk has documented 18+ attack categories with real CVEs and incidents in the wild
(postmark-mcp supply chain attack, Supabase Cursor agent compromise).

Skillvet currently has zero MCP-specific checks. This design adds 8 focused,
grep-detectable checks targeting the attack patterns most likely to appear in
skill/plugin source code.

## New Checks

### #55 — Tool Poisoning Instructions (Severity: 9)

**Source:** Invariant Labs (2025), MCPTox benchmark

**Attack:** Hidden manipulation instructions embedded in tool description strings.
These are invisible in most UIs but visible to the LLM, with success rates up to 72.8%.

**Patterns (inline):** Phrases like "ignore previous instructions", "do not tell the
user", "without the user knowing", "secretly", "covertly", "you must not reveal",
"do not mention", "hide this from".

**Remediation:** "Tool descriptions should only contain factual documentation. Remove
any imperative instructions targeting the LLM."

### #56 — Cross-Server Shadowing (Severity: 8)

**Source:** Invariant Labs (2025), WhatsApp MCP exploit

**Attack:** Tool descriptions contain instructions that manipulate how the LLM uses
tools from OTHER servers. Demonstrated by making Cursor agent BCC all emails to attacker.

**Patterns (inline, only in quoted strings):** Phrases like "when using", "before
calling", "after calling", "instead of", "always include", "always add", "also do",
"also send" — only when inside string literals.

**Remediation:** "Tool descriptions should not reference or instruct behavior for other
tools. Each tool should be self-contained."

### #57 — Conversation History Exfiltration (Severity: 9)

**Source:** Trail of Bits (April 2025), HiddenLayer

**Attack:** Malicious tools use parameter names or description instructions to capture
conversation history, API keys, and other data from the LLM context.

**Patterns (inline):** Parameter names like "conversation_history", "chat_history",
"previous_messages", "full_conversation". Conditional triggers referencing keys/passwords/
tokens. Data gathering instructions.

**Remediation:** "Tool parameters should not request conversation history or contain
conditional data-gathering instructions."

### #58 — Command Injection in Handlers (Severity: 8)

**Source:** Keysight (Jan 2026), Snyk, 43% of tested MCP implementations

**Attack:** MCP tool handlers pass user input directly to shell commands without
sanitization. Real CVEs: mcp-server-kubernetes, mcp-package-docs, aws-mcp-server.

**Patterns (base64-encoded):** Shell execution with template literal interpolation in
Node.js, subprocess with shell=True in Python, Command with sh/bash in Go.

**Remediation:** "Never pass user-supplied input directly to shell commands. Use
parameterized APIs (spawn with array args, subprocess with shell=False)."

### #59 — Bulk Environment Exfiltration (Severity: 9)

**Source:** Knostic (2025), McpInject module, Acuvity

**Attack:** Malicious MCP servers read ALL environment variables at startup to steal
API keys, tokens, and credentials.

**Patterns (base64-encoded):** Bulk env access patterns — Object.keys on env in Node.js,
dict/items on environ in Python, printenv piped to network tools in shell.

**Note:** Complements existing check #2 (individual env var theft). This catches bulk
enumeration — a more dangerous pattern.

**Remediation:** "MCP servers should only access specific, documented environment
variables. Never enumerate or serialize all environment variables."

### #60 — Cloud Metadata SSRF (Severity: 9)

**Source:** Multiple CVEs (CVE-2025-65513, CVE-2025-5276), BlueRock MarkItDown exploit

**Attack:** MCP servers fetch URLs without validation, allowing access to cloud instance
metadata endpoints. Can lead to full cloud account takeover.

**Patterns (base64-encoded):** Cloud metadata IPs and hostnames — AWS/GCP link-local
address, GCP/Azure/Alibaba metadata hostnames.

**Remediation:** "Block requests to cloud metadata endpoints. Validate all user-supplied
URLs against an allowlist."

### #61 — DNS Rebinding Exposure (Severity: 6, WARNING)

**Source:** Straiker AI Research (2025), CVE-2025-66414, CVE-2025-66416, CVE-2025-9611

**Attack:** MCP servers on localhost using SSE transport bind to all interfaces without
origin validation, enabling DNS rebinding attacks from malicious websites.

**Patterns (inline):** All-interface binding (0.0.0.0, ::) in listen/bind calls combined
with SSE/HTTP transport keywords.

**Note:** This is a WARNING, not critical. Binding to all interfaces is common in dev.

**Remediation:** "Bind MCP servers to 127.0.0.1 instead of 0.0.0.0. Enable DNS rebinding
protection and validate Origin headers on SSE endpoints."

### #62 — Rug Pull / Dynamic Tool Definitions (Severity: 8)

**Source:** Invariant Labs (2025), postmark-mcp incident (Sep 2025)

**Attack:** MCP servers change tool definitions over time — initially benign, then
malicious. postmark-mcp used this: 15 clean versions, then malicious v1.0.16.

**Patterns (base64-encoded):** Time functions near tool registration, HTTP fetch inside
tools/list handlers, eval/Function on remote data, version-conditional tool defs.

**Remediation:** "Tool definitions should be static and deterministic. Never fetch tool
definitions from remote servers or gate them on time/version conditions."

## Implementation Plan

### Pattern Encoding

| Check | Encoding | Reason |
|-------|----------|--------|
| #55 Tool Poisoning | Inline | English phrases, no AV risk |
| #56 Cross-Server Shadowing | Inline | English phrases, no AV risk |
| #57 Conversation Exfil | Inline | English phrases, no AV risk |
| #58 Command Injection | patterns.b64 | Contains shell command patterns |
| #59 Bulk Env Exfil | patterns.b64 | Contains env access patterns |
| #60 Cloud Metadata SSRF | patterns.b64 | Contains IP addresses |
| #61 DNS Rebinding | Inline | Simple patterns, no AV risk |
| #62 Rug Pull | patterns.b64 | Contains eval/fetch patterns |

### New patterns.b64 Entries

Four new named patterns:
- MCP_CMD_INJECT — regex for shell execution with interpolation
- MCP_BULK_ENV — regex for bulk env var access
- MCP_CLOUD_META — regex for cloud metadata endpoints
- MCP_RUG_PULL — regex for dynamic tool definition patterns

### Test Fixtures (8 new)

Each fixture is a minimal skill directory that triggers exactly one check:

1. trigger-tool-poisoning — SKILL.md with hidden instruction strings
2. trigger-cross-server-shadow — JS file with cross-tool manipulation
3. trigger-conversation-exfil — Python file with suspicious param names
4. trigger-command-injection-handler — Node.js with unsanitized shell exec
5. trigger-bulk-env-exfil — Python reading all env vars
6. trigger-cloud-metadata-ssrf — Shell script accessing cloud metadata
7. trigger-dns-rebinding — Node.js server listening on all interfaces
8. trigger-rug-pull — JS with time-gated tool definitions

### Documentation Updates

- SKILL.md: New "MCP Security Checks (#55-62)" section in check reference
- SKILL.md: Version bump to 3.1.0
- CLAUDE.md: Update check count from 54 to 62

### Files Modified

1. scripts/skill-audit.sh — Add 8 check functions
2. scripts/patterns.b64 — Add 4 new encoded patterns
3. tests/run-tests.sh — Add 8 test cases
4. tests/fixtures.b64 — Add 8 encoded fixtures
5. SKILL.md — Documentation + version bump
6. CLAUDE.md — Update check count

## Research Sources

- Invariant Labs: Tool Poisoning Attacks, WhatsApp MCP Exploit
- Trail of Bits: Jumping the Line, Conversation History Theft, ANSI Codes
- Palo Alto Unit 42: MCP Sampling Attack Vectors
- Keysight: MCP Command Injection (Jan 2026)
- Snyk: Command Injection in MCP Servers
- Knostic: Env File Secret Leakage
- Straiker AI: DNS Rebinding Exposure
- Semgrep: First Malicious MCP on npm (postmark-mcp)
- Multiple CVEs: CVE-2025-6514, CVE-2025-49596, CVE-2025-66414, CVE-2025-5276, CVE-2025-5273
