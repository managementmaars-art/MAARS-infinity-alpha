# cloudflare-workers-publish Evolution Log

Reverse-chronological log of skill improvements.

---

## 2026-02-18: Initial skill creation

**Source**: Empirical discovery during rangebar-patterns static hosting setup for Bokeh equity charts (10-15MB HTML files too large for GitHub).

**Reference implementation**: `rangebar-patterns` repository

- `results/published/wrangler.toml` — minimal Workers Static Assets config
- `scripts/publish_findings.sh` — 3-phase deploy (1Password creds, index gen, wrangler deploy)
- `.mise/tasks/publish.toml` — mise task wrapper

**Gotchas documented**: 15 anti-patterns (CFW-01 through CFW-15) covering:

- Cloudflare Pages deprecation (April 2025)
- 1Password service account limitations (read-only, no create)
- CONCEALED field `--reveal` requirement
- macOS bash 3 portability
- workers.dev subdomain discovery
- SSL/TLS handshake failure with macOS curl
- Git LFS pointer vs actual file content
- Tera template conflicts in mise TOML

**Validation**: Deployed 13MB Bokeh HTML chart to `https://rangebar-findings.terry-301.workers.dev/` successfully.
