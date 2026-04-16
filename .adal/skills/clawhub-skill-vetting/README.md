# Skill Vetting (ClawHub)

Security‑first vetting protocol for OpenClaw/ClawHub skills. The goal is to prevent installing untrusted skills by enforcing code review, scope checks, and a standardized risk report.

## What it does
- Forces **code review** (SKILL.md alone is not enough)
- Detects **red flags** (exfiltration, obfuscation, exec/eval, secrets access)
- Checks **recent activity** to catch supply‑chain risks
- Enforces **permission scope** and explicit domain listing
- Produces a **standard report** with a **confidence score (0–100)**

## Files
- `SKILL.md` — the skill instructions and workflow
- `references/vetting-guide.md` — full checklist, commands, red flags, report template

## How to use (in OpenClaw)
Ask the agent to vet a skill:
```
Vet this ClawHub skill: <link>
```

The output will be a **SKILL VETTING REPORT** with:
- Metrics (downloads, last update, files reviewed)
- Red flags
- Permissions needed
- Confidence score + risk level
- Final verdict

## Hard rules
- **SKILL.md is not enough** — provide the code for a final verdict
- If in doubt → **do not install**

## Confidence score
Weighted rubric (0–100):
- Provenance/author (0–25)
- Code transparency (0–25)
- Permission scope (0–20)
- Network risk (0–15)
- Community signals (0–15)

Thresholds:
- 80–100 → ✅ OK (sandbox still recommended)
- 60–79 → ⚠️ Caution (sandbox + read‑only for non‑sensitive paths)
- <60 → ❌ No‑go

## Notes
This skill is preventive. It reduces risk but does not guarantee safety.
