---
name: name-project
description: Run an interactive naming session for a project. Use when the user wants to name a project, app, package, tool, or repo. Presents names in rounds, tracks preferences, and refines suggestions based on selections.
---

# Patrick's Naming System

Instructions for running an interactive naming session.

---

## What This Is

Instructions, seed data, and an evaluation formula for helping name projects through interactive, multi-round sessions. The agent gets progressively better at suggesting names based on your reactions. Everything happens in conversation.

The agent can use external tools (name generators, word-relationship APIs, web searches) opportunistically when they'd help break a creative rut. No fixed list — use whatever's available.

---

## Three Layers of Data

The system has three layers. Each builds on the one below it.

**Layer 1 — Base Seed (this document)**
General developer context, values, aesthetic preferences, and the evaluation formula. Ships with this file. Updated manually when general preferences change.

**Layer 2 — Persisted Taste Profile**
Learned across naming sessions. What patterns, sounds, vibes, and word types you're consistently drawn to or repelled by. Survives between sessions. Can be refined or cleared on request. Stored by the agent however it persists data (memory edits, a companion file, etc.).

**Layer 3 — Session Data**
The current naming session: project context, carried-forward selections, round history, per-session taste refinements. Cleared when the session ends (name locked or session explicitly closed).

When scoring or generating names, the agent applies all three layers: base seed as foundation, persisted taste as a lens, session data as the sharpest signal.

---

## Starting a Session

### Context Discovery

Before asking any questions, the agent should build its own understanding of the project by scanning what's available: README, package.json (description, keywords, tags), doc files, config files with descriptive metadata. Don't load code — look for descriptive signals.

The agent should also draw on its memory of past conversations and anything it already knows about the project.

### What the Agent Needs to Know

The agent needs enough context to generate good names in Round 1. The goal is to understand:

- What the project does and who it's for
- What it's LIKE — the core metaphor or feeling
- What emotional register it should hit
- What it must work as (package name, domain, repo, etc.)
- What sibling names exist in the ecosystem
- What themes, references, or imagery resonate
- What names or patterns to avoid

For concrete data points (what it does, what it must work as, sibling names), ask directly if unknown. For subjective dimensions (metaphor, feeling, themes), describe what you're trying to understand and prompt adaptively based on what you've already learned from project files and memory.

If the agent is confident about an answer from its own research, skip the question silently. If it inferred a subjective answer (like the project's emotional register), confirm it before proceeding.

After the initial scan and any questions, the agent should ask itself: "Do I have any follow-up questions that would meaningfully improve Round 1?" If yes, ask them. If not, move to research.

### Research Step

After context discovery and before generating Round 1, the agent does a silent research pass. Search for naming inspiration related to the project's domain, metaphors, themes, and cultural references. Look for how similar projects are named, what words and imagery exist in the space, and what unexpected connections might spark ideas. This enriches Round 1 without slowing the user down.

---

## Round Structure

Each round contains two kinds of names: **carried selections** (names you liked in previous rounds) and **fresh names** (new candidates). You should select fewer names each round, narrowing toward a decision.

**Round 1 — DIVERGE (6-8 fresh names)**
Maximum diversity. No default strategy bias — the agent evaluates the project context and chooses strategies accordingly. You select which names you like.

**Round 2 — CONVERGE (your selections + 4-6 fresh names)**
Carried selections appear alongside new names informed by taste patterns the agent detected. You select from the full list.

**Round 3 — REFINE (your selections + 2-4 fresh names)**
Tighter batch. NAME Scores shown for all candidates. You should be narrowing to 2-3.

**Round 4+ — POLISH (your selections + 1-2 fresh names)**
Final candidates. Full validation. The agent offers remix suggestions. You LOCK a name or choose RESET or REFINE.

### Carry-Forward

Names you select in any round appear in every subsequent round until you deselect them or reset. They're clearly marked as carried selections vs. fresh names. The list contracts as you select fewer each round.

### Interactive Prompts

Every round ends with an interactive multi-select prompt. The options are:

- Each name (carried selections clearly marked)
- "Regenerate new names" (always available)

The agent does NOT ask you to explain your choices unless it can't infer why from the pattern of selections. Figuring out your taste is primarily the agent's job.

After you select, the agent presents its analysis of what taste patterns emerged or shifted, then generates the next round.

### Regenerate

Available at every step. Throws away the current fresh names and generates a new batch. Carried selections and taste profile stay intact. No questions asked — just a fresh roll.

### Stall Detection

If you select the exact same set of names two rounds in a row, the fresh names aren't landing. The agent pauses and offers:

**RESET** — Wipe all selections and all taste/preference learnings from this session. Start completely fresh with new context discovery.

**REFINE** — Preserve your current selections. The agent does a fresh research pass based on current context and your taste profile, then asks interactive reflective questions to sharpen its understanding. After your answers, it replaces only the fresh names and you continue from where you were.

**Regenerate** — Just try new fresh names without questions.

**Lock [name]** — One option per carried selection, in case you're ready to commit.

### When You're Stuck

If few choices remain and you can't decide between finalists:

- Generate an ASCII comparison chart scored on the formula
- Ask grounding questions: "Which would you type in a terminal every day?" with each finalist as an option
- Offer remix moves: swap a syllable, translate a word, try a synonym with better mouth-feel

If you reject all fresh names repeatedly and have no carried selections:

- Ask what word you'd WANT to type every day, even if it's not a name yet
- Ask you to name a project whose name you love, and what you love about it
- Pivot the context: new metaphors, new cultural touchstones, different emotional register
- This is essentially an automatic REFINE trigger

---

## Session History

The agent maintains a running history for the duration of the session:

- Every name ever presented, with round number and whether selected, deselected, or ignored
- Current carried-forward selections
- Evolving taste profile with per-round deltas
- All NAME Scores computed
- Context data, restart count, refine count

Queryable at any time: "show me everything I've ever liked", "what patterns have you found", "compare my current selections", "what did I drop and why do you think I dropped it".

History clears when the session ends. Taste profile insights that seem persistent (not project-specific) get promoted to Layer 2.

---

## The NAME Score

An evaluation formula for scoring name candidates. Grounded in peer-reviewed research on brand naming, phonetic symbolism, and memorability.

### The Formula

```
NAME = (P × Wp) + (E × We) + (D × Wd) + (M × Wm) + (S × Ws) + (F × Wf) + (H × Wh) + (C × Wc)
```

All weights are context-adaptive. The agent sets them at session start based on the project's nature, audience, and use context. No factor is hardcoded as #1. Default weight range: 1.0–3.0. Each criterion scored 0–5.

### The 8 Criteria

**P — Phonetic Quality**
How it feels to say and type. 2-3 syllables optimal. Plosive starts (b,d,g,k,p,t) aid recall. Liquid consonants (l,r) convey warmth. Predictable spelling from hearing. No consonant clusters that force a pause. Phonetic-equivalent spelling variants are allowed (dropped vowels, swapped letters) as long as the name sounds the same spoken aloud.

Research: Lowrey & Shrum (2007), Yorkston & Menon (2004), Luna et al. (2013).

**E — Evocative Power**
Does it create imagery, emotion, or narrative? Does it paint a scene rather than describe a function?

Research: Igor Naming Guide, Giese et al. (2014).

**D — Depth / Layers**
Does it reveal more meaning over time? Hidden etymology, double meaning, cultural reference that rewards curiosity?

Research: Danescu-Niculescu-Mizil et al., Igor engagement taxonomy.

**M — Memorability**
Hear it once, recall it tomorrow. Shorter is better. Sound repetition helps.

Research: Vanden Bergh et al. (1987), Argo et al. (2010).

**S — Semantic Fit**
Does the name metaphorically encode what the project IS? Not literal description — metaphorical truth.

Research: Klink (2000), Shrum et al. (2012).

**F — Functional Fit**
Works as npm package, GitHub repo, domain, Slack channel, directory name, monorepo @scope.

**H — Ecosystem Harmony**
Fits alongside sibling project names without being matchy-matchy.

**C — Collision Clearance**
Is the name already in use? Check npm, GitHub, and domains. If a well-known project already uses it, reject. If only an obscure or abandoned project uses it and yours is personal, it's fine.

### Score Thresholds

Thresholds scale with the maximum possible score (which varies by weight configuration). As a percentage of max:

```
85-100%  EXCEPTIONAL  — Ship it.
67-84%   STRONG       — Solid candidate, minor refinement may help.
50-66%   PROMISING    — Potential, needs work on weak dimensions.
33-49%   MEDIOCRE     — Probably a Happy Idiot or has a fatal flaw.
 0-32%   REJECT       — Not worth polishing.
```

Scores shown from Round 3 onward. Computed internally before that.

### ASCII Comparison

When stuck between finalists, the agent can render a bar chart comparing all 8 dimensions side by side in a code block. Only generated during the session when it would help decide.

---

## Taste Profile (Layer 2)

The agent builds this across sessions. Updated after each session with insights that seem persistent (not project-specific).

```
Attracted to:
  Patterns    — e.g., single evocative words, foreign roots, metaphor
  Sounds      — e.g., soft consonants, two syllables, ends in vowel
  Vibes       — e.g., warm, intimate, slightly mysterious
  Word types  — e.g., nature, craft, movement

Repelled by:
  Patterns    — e.g., compound action words, backronyms, -ify suffixes
  Sounds      — e.g., harsh consonants, four+ syllables
  Vibes       — e.g., corporate, clinical, SaaS-y
  Word types  — e.g., tech jargon, generic positive adjectives

Insights:
  Natural language observations that persist across sessions.
```

Can be refined (agent asks questions to sharpen it) or cleared (back to base seed only) on request.

---

## Naming Strategies

A palette for the agent, not a checklist. The agent picks strategies based on project context.

**Evocative Metaphor** — Captures essence without describing function. Apple, Kindle, Slack.

**Foreign Root / Mythology** — Borrowed meaning. Kubernetes (Greek: helmsman), Ubuntu (Zulu: humanity to others).

**Portmanteau** — Two words fused. Debian (Debra + Ian), Pinterest (Pin + Interest).

**Single Evocative Word** — One word, enormous weight. Figma (figment), Notion, Prisma.

**Anti-Pattern Subversion** — Breaks the space's naming conventions. Apple in computing, Discord in communication.

**Wordplay / Pun** — Makes you smirk. Snort (IDS sniffs packets), Flask (small container for experiments).

**Backronym** — Acronym spells something. GNU (GNU's Not Unix), WINE (Wine Is Not an Emulator).

**Compound Image** — Two words creating a vivid scene. Tailwind, Terraform.

---

## Base Seed Data (Layer 1)

```
Developer profile:
  - Solo indie developer, personal brand / portfolio
  - Core stack: TypeScript, React, Turborepo monorepo, pnpm, Vercel, GitHub Actions
  - Has a shared npm scope
  - Mix of open source and private projects
  - Values simplicity, semantic correctness, industry-standard conventions
  - Rejects over-engineering and custom abstractions where standards exist

Project types (not exhaustive):
  - React web apps
  - API / webhook servers
  - Developer tools
  - Bots
  - Mobile apps (planned)
  - Platforms
  - Small QoL utilities
  - Immersive 3D web experiences (procedural assets, no external files)

Naming preferences:
  - Vibe depends on the project — no single default
  - Word count depends on the project
  - Names should feel timeless unless referencing pop culture the developer personally loves
  - English only
  - Projects should feel loosely related — same vibe, not same theme
  - Small utility projects deserve good names too
  - Names need to work as: npm package, GitHub repo, domain, app/brand identity
  - Whether a name hints at function depends on project type
  - Pop culture references drawn from a mix of movies, TV, games, music, books

Known project: "My Story v3" (working title, acknowledged as a bad name)
  - 3D immersive web experience, clay avatar walks a life timeline
  - Paired content editor ships first
  - Deeply personal, eventually shareable
  - 4 release stages planned
```

---

## Rules for the Agent

### Session Flow
- Scan project files and memory before asking questions. Only ask what can't be confidently determined. Confirm subjective inferences. Add follow-ups only if they'd improve Round 1.
- Do a silent research pass after context discovery and before generating Round 1. Also research during REFINE before generating replacement names.
- Start at 6-8 fresh names in Round 1. Step down progressively. Carry forward all selections, clearly marked vs. fresh names.

### Interaction
- Use interactive multi-select for name selection. Always include "Regenerate new names" as an option.
- After each selection, explain taste patterns before generating the next round. Don't ask why the user likes a name unless you can't infer it.
- Trigger stall detection after 2 identical rounds. Offer RESET, REFINE, Regenerate, or Lock.

### Scoring & Quality
- Set NAME Score weights based on project context. No hardcoded #1 factor. Show scores from Round 3 onward.
- Never suggest Happy Idiot names (two generic positive words) or names that sound like a SaaS product from 2018.
- Phonetic-equivalent spelling variants are allowed. If a name can't be spelled from hearing it (and isn't a phonetic variant), reject it internally.
- Collision: reject if a well-known project uses the name. Accept if only obscure/abandoned projects use it and yours is personal.

### Data Lifecycle
- Session data clears when the session ends. Promote persistent taste insights to Layer 2.
- Keep session history queryable throughout. Use external tools silently — the user sees results, not process.
