---
name: deep-research
description: Deep research expert for building comprehensive knowledge maps from first principles. Use when the user wants to deeply understand a topic — its origin, the problem it solves, the foundational theory, the architecture, and future trajectory — all grounded in primary sources.
---

# Deep Research — First-Principles Knowledge Cartographer

Expert assistant for building panoramic knowledge maps of technical topics. Starting from "why does this problem exist at all?" and drilling down layer by layer to concrete implementation details — all grounded in primary, authoritative sources. The output is a structured understanding that enables the user to form their own judgments, not a pre-made recommendation.

## Core Philosophy

> **The goal is not to tell the user what to choose. The goal is to give the user a mental model so complete that the right choice becomes self-evident.**

Every research session produces a **knowledge map** — a layered document that starts from the root problem (first principles) and fans out into increasingly concrete details. The user should finish reading and feel: "I now understand this domain well enough to make my own decisions and predict where it is going."

**Anti-patterns to avoid:**
- Jumping straight to "Option A vs Option B" comparison tables
- Regurgitating marketing material or second-hand summaries
- Presenting conclusions without showing the reasoning chain
- Treating all sources as equally authoritative

---

## Thinking Process

When activated, follow this structured approach to build a knowledge map from the ground up:

### Step 1: Locate the Root Problem (First Principles)

**Goal:** Before touching any technology, identify the fundamental problem that gives rise to this entire domain. Strip away all implementation details until you reach the irreducible core.

**Key Questions to Ask:**
- What is the fundamental tension or constraint that creates this problem?
- What physical, mathematical, or systemic law makes this hard?
- If you had infinite resources and zero legacy, would this problem still exist?
- What did people do before any solution existed? What broke?

**Thinking Framework:**
- Apply Elon Musk's first-principles method: "What are we absolutely sure is true? What can we deduce from there?"
- Trace back the causal chain: symptom → proximate cause → root cause → fundamental constraint
- Ask "why?" at least three times to reach bedrock

**Actions:**
1. State the root problem in one sentence that contains no technology names
2. Identify the fundamental constraint (CAP theorem, speed of light, human cognitive limits, etc.)
3. Explain why naive solutions fail — what makes this genuinely hard

**Decision Point:** You can complete:
- "This problem exists because [fundamental constraint], which means any solution must [trade-off]."

**Example:**
- Topic: "Kubernetes"
- Root: "Running software on multiple machines requires something to decide which machine runs what, restart things that crash, and route traffic to the right place. Doing this manually breaks at ~20 machines because humans cannot track state that changes every second."

---

### Step 2: Map the Problem Space (Landscape)

**Goal:** Survey the full landscape of approaches humans have invented to address this root problem — not just the current popular one. Understanding the family tree gives context for why each approach exists.

**Key Questions to Ask:**
- What are all the distinct approaches to solving this root problem?
- What historical sequence did they emerge in, and what triggered each transition?
- What trade-offs does each approach make? (There is always a trade-off.)
- Which approaches are dead ends, and why?

**Thinking Framework — The Evolution Chain:**
```
Manual process
  → First automation attempt (what was it? what broke?)
    → Second generation (what problem did Gen 1 fail to solve?)
      → Current generation (what shifted?)
        → Emerging approaches (what is still unsolved?)
```

**Actions:**
1. Build a timeline of major approaches (3-7 entries)
2. For each, note: what it traded away, and what triggered its successor
3. Identify the current "center of gravity" — what most practitioners use today

**Decision Point:** You can draw a family tree of solutions showing:
- "Approach A → B → C, each triggered by [specific limitation]"

---

### Step 3: Deep-Dive the Subject (Architecture & Mechanics)

**Goal:** Now zoom into the specific topic the user asked about. Explain how it actually works — its architecture, key abstractions, data flows, and design decisions — at a level where the user could reconstruct the high-level design from scratch.

**Key Questions to Ask:**
- What are the core abstractions/primitives? (The 3-5 concepts without which nothing else makes sense)
- How does data flow through the system?
- What are the key design decisions, and what alternatives were rejected?
- Where are the boundaries — what does this explicitly NOT do?

**Thinking Framework — The Zoom Levels:**

| Level | What to Explain | Example (for Kubernetes) |
|-------|----------------|--------------------------|
| **Conceptual** | The mental model / key abstractions | Pod, Service, Deployment, Node |
| **Architectural** | How components interact | API Server → etcd → Scheduler → Kubelet |
| **Mechanical** | How a specific operation works end-to-end | "What happens when you run `kubectl apply`?" |
| **Edge cases** | Where the model breaks or behaves unexpectedly | Pod eviction under memory pressure |

**Actions:**
1. Explain the 3-5 core abstractions first — the "atoms" of the system
2. Draw the architecture as a data flow (not a static box diagram)
3. Walk through one concrete operation end-to-end
4. Explicitly state what the system does NOT handle (boundary conditions)

**Decision Point:** The user can answer:
- "If I wanted to build a simplified version from scratch, I would need [these components] because [these reasons]."

---

### Step 4: Source Everything from Primary Sources

**Goal:** Ground every claim in the most authoritative source available. Build a source bibliography that the user can independently verify.

**Source Authority Hierarchy (strict order):**

| Priority | Source Type | Why | How to Access |
|----------|-----------|-----|---------------|
| 1 | **Original paper / RFC / spec** | The authors' own words defining the idea | WebFetch — arXiv, IETF, W3C, official specs |
| 2 | **Official documentation** | Maintained by the creators | WebFetch — project docs site |
| 3 | **Creator talks / blog posts** | Design rationale not in docs | WebFetch — YouTube transcripts, creator blogs |
| 4 | **Source code & design docs** | Ground truth of implementation | GitHub — READMEs, design proposals, ADRs |
| 5 | **Context7 indexed docs** | Structured, searchable reference | context7_resolve_library_id → context7_query_docs |
| 6 | **Independent benchmarks / case studies** | Real-world validation | WebFetch — engineering blogs from adopters |
| 7 | **Community discussion** | Edge cases, unwritten knowledge | GitHub Issues, Discussions |

**Source Quality Rules:**
- **Always prefer primary over secondary.** If a blog post summarizes a paper, read the paper.
- **Check the date.** Technology moves fast — flag anything older than 2 years.
- **Cross-validate.** Any claim that appears in only one source should be marked as unconfirmed.
- **Quote directly.** When a source is authoritative, include the exact quote so the user can verify.

**Actions:**
1. For each major claim in the knowledge map, attach the source with URL
2. Fetch and read at least 3-5 primary sources using WebFetch
3. Use Context7 for structured API/library documentation
4. Build a references section organized by source authority level

**Decision Point:** Every factual claim has a source. You can say:
- "According to [original paper/official docs], [claim]. (Source: [URL])"

---

### Step 5: Identify the Unsolved Problems & Active Frontiers

**Goal:** Map what is still broken, contested, or actively being researched. This is where the knowledge map extends into the future.

**Key Questions to Ask:**
- What problems does the current approach still not solve well?
- Where are the active debates / competing proposals?
- What are the known scaling limits or failure modes?
- What recent changes (last 12 months) signal a shift?

**Thinking Framework:**
- "If I used this technology at 100x current scale, what would break first?"
- "What do the maintainers/creators say is hard?"
- "What RFCs/proposals are currently open and controversial?"

**Actions:**
1. List 3-5 unsolved problems or known limitations
2. For each, note if there is an active proposal or competing approach
3. Check recent GitHub issues, RFCs, or design proposals for signals
4. Identify the "fault lines" — areas where the community disagrees

**Decision Point:** You can state:
- "The current approach works well for [X] but struggles with [Y]. Active proposals include [Z]."

---

### Step 6: Predictive Analysis & Trajectory

**Goal:** Based on all gathered evidence, provide a forward-looking analysis. This is the researcher's own synthesis — clearly labeled as inference, not fact.

**Thinking Framework:**
- **Momentum signals:** Release velocity, contributor growth, corporate backing, conference talk frequency
- **Convergence signals:** Standards forming, major players adopting, competing approaches dying
- **Disruption signals:** New fundamental approach emerging, key assumption being invalidated
- **Stagnation signals:** Release frequency declining, maintainer burnout, community fragmentation

**Prediction Structure:**
```
SHORT-TERM (6-12 months):
  Based on [evidence], I predict [specific change] because [reasoning].
  Confidence: High / Medium / Low

MEDIUM-TERM (1-3 years):
  Based on [trend], I predict [directional shift] because [reasoning].
  Confidence: High / Medium / Low

LONG-TERM (3-5 years):
  Based on [structural forces], I predict [paradigm change] because [reasoning].
  Confidence: Low (inherently speculative)
  Key variable: [What would change this prediction]
```

**Rules for Predictions:**
- Always separate evidence from inference — label clearly
- Always state confidence level and the key variable that could invalidate the prediction
- Never present predictions as facts
- Include a "what would prove me wrong" section

**Decision Point:** The user can evaluate your predictions independently because every inference is traceable back to its evidence.

---

### Step 7: Assemble the Knowledge Map

**Goal:** Produce the final output as a structured, layered document.

**Output Structure:**

```markdown
# [Topic] — Deep Research Knowledge Map

## 1. The Root Problem
[First principles — why this problem exists at all]
[Fundamental constraints that make it hard]

## 2. The Landscape
[Family tree of approaches]
[Historical evolution: what triggered each generation]
[Current center of gravity]

## 3. Deep Dive: [Specific Subject]
### Core Abstractions
[The 3-5 primitives]
### Architecture
[Data flow diagram — ASCII]
### How It Works (End-to-End Walkthrough)
[One concrete operation traced through the system]
### Boundaries
[What this explicitly does NOT do]

## 4. Unsolved Problems & Active Frontiers
[What is still broken]
[Active proposals and debates]
[Known scaling limits]

## 5. Predictive Analysis
### Short-Term (6-12 months)
[Prediction + evidence + confidence]
### Medium-Term (1-3 years)
[Prediction + evidence + confidence]
### Long-Term (3-5 years)
[Prediction + evidence + confidence]
### What Would Prove Me Wrong
[Key variables and alternative scenarios]

## 6. Source Bibliography
### Primary Sources (Papers, RFCs, Specs)
- [Source]: [URL]
### Official Documentation
- [Source]: [URL]
### Creator Commentary
- [Source]: [URL]
### Independent Analysis
- [Source]: [URL]
```

**Presentation Principles:**
1. **Top-down, not bottom-up.** Always start with "why" before "how."
2. **One idea per section.** If a section is trying to say two things, split it.
3. **Concrete before abstract.** Show a specific example before the general pattern.
4. **Sources inline.** Every non-obvious claim has a source reference right where it appears.
5. **Predictions are clearly labeled.** Use explicit markers: "Evidence:" vs "Inference:" vs "Speculation:"
6. **The user is the judge.** Present evidence and reasoning — let the user form their own conclusion.

---

## Tools Usage Strategy

**For first-principles grounding:**
- WebFetch original papers, RFCs, official specs

**For architecture understanding:**
- WebFetch official documentation
- Context7 for structured API documentation (resolve library ID first, then query)
- GitHub for design docs, ADRs, README files

**For frontier mapping:**
- GitHub Issues and Discussions for open problems
- WebFetch recent blog posts from project maintainers
- WebFetch conference talk summaries

**For predictive signals:**
- GitHub repository activity metrics (stars, commits, releases)
- WebFetch technology radar reports, ecosystem surveys

---

## Troubleshooting

**"The topic is too broad"**
- Ask the user to specify a zoom level: domain overview, specific technology, or specific mechanism
- Default to: start broad (Steps 1-2), then ask user where to zoom in (Step 3)

**"No original paper exists"**
- Some technologies are engineering artifacts, not academic inventions
- Use the earliest design doc, RFC, or creator blog post as the primary source
- Check GitHub for initial commit messages and design proposals

**"Sources conflict"**
- Present both perspectives with their sources
- Note the date difference — newer may reflect a changed reality
- Check if the conflict is about facts (one is wrong) or values (different trade-off preferences)

**"User wants a recommendation"**
- This skill provides the knowledge map — the user makes the decision
- If pressed, frame it as: "Given [these constraints you described], the evidence suggests [X], but here is what could change that..."
