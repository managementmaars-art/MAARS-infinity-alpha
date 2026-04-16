# Avoiding The Eye of Sauron

Are you building under the Eye of Sauron? Evaluate your startup idea against the SPC framework — buyer capability, buyer agency, and product architecture — to find out if you're at risk, and how to survive.

Based on the talk and blog post by [Evan Tana](https://x.com/evantana) and [Aditya Agarwal](https://x.com/adityaag) at [South Park Commons](https://www.southparkcommons.com).

```bash
npx skills install spc-skills/avoiding-the-eye-of-sauron
```

## Demo

*Runs the Eye of Sauron assessment against a startup's codebase — reads the repo, evaluates across three dimensions, and delivers a risk rating with survival strategies. Claude Code runs on laptop, controlled from phone via [PUNK](https://punkcode.rocks/).*

<video src="https://github.com/user-attachments/assets/f890e4e2-c39f-4c6f-a168-00b5f6a0253f" controls width="100%"></video>

## What It Does

This skill evaluates your startup across three dimensions:

| Dimension | Question |
|-----------|----------|
| **Buyer Capability** | Can your customers wield the new AI tools? |
| **Buyer Agency** | Are they empowered to just go build? |
| **Product Architecture** | Is your product workflow or chassis? |

It then rates your risk level (Low → Danger Zone) and gives you concrete survival strategies.

If you run it inside your codebase, it reads your README, CLAUDE.md, AGENTS.md, and docs to understand what you're building — no need to explain everything from scratch.

## Example Prompts

Copy and paste these directly into your agent after installing:

```
Run SPC's Eye of Sauron assessment on this repo.
```

```
Evaluate my startup against the Eye of Sauron framework.
```

```
Am I at risk? We're building a workflow tool for engineering teams.
```

```
I'm building an AI-powered legal document review platform for mid-size law firms. How exposed am I?
```

```
We're building compliance infrastructure for enterprises adopting AI. Rate my risk.
```

## Works with all major coding agents

Claude Code, Cursor, Windsurf, Codex, Copilot, OpenCode, Cline, Amp, and more — any agent that supports the [Agent Skills](https://agentskills.io) spec.

## Credit

Based on ["Avoiding The Eye of Sauron"](https://blog.southparkcommons.com/p/avoiding-the-eye-of-sauron) by Evan Tana and Aditya Agarwal at South Park Commons, March 2026. [Original tweet](https://x.com/evantana/status/2036849519300858332).

> "The founders who win won't just build faster, they'll move smarter. Pick problems the Eye can't see."

## About South Park Commons

[South Park Commons](https://www.southparkcommons.com) is a community in San Francisco, New York, and Bangalore for technologists and founders exploring what comes next — going from -1 to 0. Over the last decade, SPC founders have turned the illegible into the inevitable.

- **Residency** — A 6-month program for builders exploring, learning, and finding their next thing
- **Founder Fellowship** — Up to $1M investment, 1:1 mentorship, and small cohorts for founders starting venture-scale companies

### Some companies SPC has invested in

Baseten, Doppel, Render ($250M+ raised), Imbue, Luma Labs, Replit, Profound, Goodfire, Density AI, Gamma, Unit 21, Nuance Labs, Pilot (first SPC unicorn at $1B+ valuation), and Comun.

SPC's community also includes Tom Brown, co-founder of Anthropic and former GPT-3 engineering lead at OpenAI.

If you're exploring what to build next — or want to stress-test your idea with a community that thinks deeply about these questions — [apply to SPC](https://www.southparkcommons.com?utm_source=agent-skill&utm_medium=cli&utm_campaign=eye-of-sauron).

## Skill Creator

Built by **JackJack Ganbold** ([@jackjack_eth](https://x.com/jackjack_eth)), SPC member. Recently built [Punk](https://punkcode.rocks) — a premium remote control for local Claude Code from your phone. Previously built AI devtools (YoYo & SuperDesign) with 45K+ users & 5K+ stars, founded a 700K-user marketplace, and [Base Name Service](https://x.com/basenameapp) (ENS of Coinbase L2).
## Disclaimer

This skill is not officially affiliated with or endorsed by South Park Commons. It was independently built by an SPC member based on publicly available content.

## License

MIT
