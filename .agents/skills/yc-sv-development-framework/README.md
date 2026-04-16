# YC/SV Development Framework

> A Claude Code Skill based on Y Combinator and Silicon Valley principles for development decisions.

## What is this?

A skill for Claude Code that helps you make development decisions based on real principles from:

- **Paul Graham** - YC Co-founder
- **Sam Altman** - ex-YC President, OpenAI CEO
- **Michael Seibel** - YC Partner Emeritus, Former CEO
- **Patrick Collison** - Stripe CEO
- **Brian Chesky** - Airbnb CEO

## The Central Question

Before any technical decision:

> "Will this help the next customer pay?"

If the answer isn't clearly YES, you probably shouldn't do it.

## Core Principles

| Principle | Source | Implication |
|-----------|--------|-------------|
| Ship > Perfect | Michael Seibel | "If you walk away with one thing, launch something bad quickly" |
| Validation > Architecture | Patrick Collison | Stripe was built with Ruby + MongoDB |
| Do Things That Don't Scale | Paul Graham | Manual first, automate when it hurts |
| Default Alive | Paul Graham | "Default alive or default dead?" |
| Founder Mode | Brian Chesky | Being in the details is NOT micromanagement |

## Installation

```bash
# Copy SKILL.md to your Claude skills directory
cp SKILL.md ~/.claude/skills/yc-sv-development-framework/
```

## Usage

The skill activates automatically when you work on:
- Feature development
- Architecture decisions
- Work prioritization
- Technical debt evaluation

## Decision Framework

### Question 1: Is it currently working?
```
YES it works → DON'T TOUCH IT
```

### Question 2: Are users/customers complaining?
```
NO complaints → Not a priority
YES complaints → Evaluate revenue impact
```

### Question 3: Does it block revenue?
```
YES blocks revenue → P0 (do it TODAY)
NO doesn't block → P1 or P2
```

### Question 4: How many users does it affect?
```
10 users who LOVE the product > 1000 who "kinda like it"
```

## Priorities

| Level | When | Examples |
|-------|------|----------|
| **P0** | TODAY | Bug losing money, system down, vulnerability |
| **P1** | This week | Paying customer bug, requested feature |
| **P2** | When there's time | Refactoring, tests, documentation |
| **NEVER** | Don't do | Rewriting what works, unrequested features |

## Original Sources

- [Do Things That Don't Scale](https://paulgraham.com/ds.html) - Paul Graham
- [Startup Advice](https://blog.samaltman.com/startup-advice) - Sam Altman
- [YC's Essential Startup Advice](https://www.michaelseibel.com/blog/yc-s-essential-startup-advice) - Michael Seibel
- [Founder Mode](https://paulgraham.com/foundermode.html) - Paul Graham (about Brian Chesky)
- [Stripe Engineering Culture](https://newsletter.pragmaticengineer.com/p/stripe-part-2) - Gergely Orosz

## Contributing

PRs welcome. The skill should remain:
- **Concise** - Don't add for the sake of adding
- **Based on real sources** - Always cite
- **Actionable** - No abstract theory

## License

MIT - Use it, modify it, share it.

---

**Built with [Claude Code](https://github.com/anthropics/claude-code)** | Built in public
