# ClawHub Skill Vetting — Trust but Verify

## Context
ClawHub is OpenClaw’s community skill marketplace. Malicious or unsafe skills exist (exfiltration, prompt injection, hidden instructions). Use this guide before installing any skill.

---

## Hard rule
**SKILL.md is not enough.** Provide the code for a final verdict.

---

## 1) Source check
Questions:
- Where did this skill come from?
- Is the author known/reputable?
- Downloads/stars?
- Last updated?
- Any reviews from other agents?

## 2) Code review (MANDATORY)
Clone first **do not install blindly**:
```bash
git clone https://github.com/author/skill-name
cd skill-name
```
List code files:
```bash
find . -type f -name "*.ts" -o -name "*.js" -o -name "*.py"
```
Search for suspicious patterns:
```bash
grep -r "fetch\|axios\|http\|request" --include="*.ts" --include="*.js"
grep -r "env\|secret\|key\|token\|password" --include="*.ts" --include="*.js"
grep -r "eval\|exec\|spawn\|child_process" --include="*.ts" --include="*.js"
```

### 🚨 Reject immediately if you see
- curl/wget to unknown URLs
- Sends data to external servers
- Requests credentials/tokens/API keys
- Reads `~/.ssh`, `~/.aws`, `~/.config` without clear reason
- Accesses `MEMORY.md`, `USER.md`, `SOUL.md`, `IDENTITY.md` without explicit consent
- Base64 decode of opaque blobs
- `eval()` / `exec()` with external input
- Modifies system files outside workspace
- Installs packages without listing them
- Network calls to **IPs** instead of domains
- Obfuscated/minified code
- Requests elevated/sudo permissions
- Accesses browser cookies/sessions
- Touches credential files

## 3) Permission scope
Evaluate:
- Files it needs to read/write
- Commands it runs
- Network access (to where?)
- Is scope minimal for stated purpose?

## 4) Recent activity (supply‑chain risk)
```bash
git log --oneline -10
git diff HEAD~10..HEAD
```
Red flag: dormant for months then huge update.

## 5) Community check
Search OpenClaw Discord + GitHub Discussions for prior reviews.

---

## Install safely (even after vetting)
```bash
openclaw skill install author/skill-name --sandbox
openclaw skill inspect author/skill-name
```
`--sandbox` runs the skill in isolation: no filesystem, no env vars, no access to other skills.

---

## Risk classification
- 🟢 **LOW**: notes, weather, formatting → basic review OK
- 🟡 **MEDIUM**: file ops, browser, APIs → full review required
- 🔴 **HIGH**: credentials, trading, system access → human approval required
- ⛔ **EXTREME**: security configs/root → do **not** install

---

## Confidence score (0–100)
**How to score** (simple weighted rubric):
- **Provenance/author (0–25)**: known + active = 25; unknown = 5
- **Code transparency (0–25)**: full readable code = 25; partial/obfuscated = 0
- **Permission scope (0–20)**: minimal + coherent = 20; excessive = 0
- **Network risk (0–15)**: known domains listed = 15; unknown/IPs = 0
- **Community signals (0–15)**: positive reviews/benign scan = 15; flagged = 0

**Thresholds**
- **80–100** → ✅ OK (sandbox still recommended)
- **60–79** → ⚠️ caution (sandbox + read‑only for non‑sensitive paths)
- **<60** → ❌ no‑go

---

## Output format
```
SKILL VETTING REPORT
══════════════════════════════════════
Skill: [name]
Source: [ClawHub / GitHub / other]
Author: [username]
Version: [version]
───────────────────────────────────────
METRICS:
• Downloads/Stars: [count]
• Last Updated: [date]
• Files Reviewed: [count]
───────────────────────────────────────
RED FLAGS: [None / List them]
PERMISSIONS NEEDED:
• Files: [list or "None"]
• Network: [list or "None"]
• Commands: [list or "None"]
───────────────────────────────────────
CONFIDENCE SCORE: [0–100]
RISK LEVEL: [🟢 LOW / 🟡 MEDIUM / 🔴 HIGH / ⛔ EXTREME]
VERDICT: [✅ SAFE TO INSTALL / ⚠️ INSTALL WITH CAUTION / ❌ DO NOT INSTALL]
NOTES: [Any observations]
══════════════════════════════════════
```

---

## Quick vet commands (GitHub‑hosted)
```bash
curl -s "https://api.github.com/repos/OWNER/REPO" | jq '{stars: .stargazers_count, forks: .forks_count, updated: .updated_at}'
curl -s "https://api.github.com/repos/OWNER/REPO/contents/skills/SKILL_NAME" | jq '.[].name'
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/skills/SKILL_NAME/SKILL.md"
```

---

## Trust hierarchy
- Official OpenClaw skills → lower scrutiny (still review)
- High‑star repos (1000+) → moderate scrutiny
- Known authors → moderate scrutiny
- New/unknown sources → maximum scrutiny
- Skills requesting credentials → human approval always

---

## Final rule
No skill is worth compromising security. When in doubt, don’t install.

---

## Next hardening steps
- Network security + gateway checklist
- DM policies & pairing
- Sandboxing strategy
- API keys & tool policies
