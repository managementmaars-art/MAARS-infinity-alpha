---
name: diffity-tour
description: >-
  Create a guided code tour that walks through the codebase to answer a question
  or explain a feature. Opens in the browser with step-by-step navigation and
  highlighted code.
user-invocable: true
---

# Diffity Tour Skill

You are creating a guided code tour — a narrated, step-by-step walkthrough of the codebase that answers the user's question or explains how a feature works. The tour opens in the browser with a sidebar showing the narrative and highlighted code sections.

## Arguments

- `question` (required): The user's question, topic, or concept. Examples:
  - `/diffity-tour how does authentication work?`
  - `/diffity-tour explain the request lifecycle`
  - `/diffity-tour how are comments stored and retrieved?`
  - `/diffity-tour closures`
  - `/diffity-tour async/await patterns`
  - `/diffity-tour React hooks`

## CLI Reference

```
diffity agent tour-start --topic "<text>" [--body "<text>"] --json
diffity agent tour-step --tour <id> --file <path> --line <n> [--end-line <n>] --body "<text>" [--annotation "<text>"] --json
diffity agent tour-done --tour <id> --json
diffity list --json
```

## Prerequisites

1. Check that `diffity` is available: run `which diffity`. If not found, install it with `npm install -g diffity`.
2. Ensure a tree instance is running: run `diffity list --json`.
   - If no instance is running, start one: run `diffity tree --no-open` using the Bash tool with `run_in_background: true`, wait 2 seconds, then run `diffity list --json` to get the port.

## Instructions

### Phase 1: Scope and research

Before creating any tour steps, you must deeply understand the answer to the user's question.

1. **Scope the question.** Not every question is equally focused. Before researching, decide the right scope:
   - **Focused question** (e.g. "how does the login endpoint validate tokens?") → follow one code path end-to-end, 3-6 steps
   - **Feature question** (e.g. "how does authentication work?") → cover the feature's key flows and components, 6-10 steps
   - **System question** (e.g. "how does the app work?") → cover the architecture at a higher level, touching key subsystems without going deep into any one. 8-15 steps. Focus on entry points, data flow, and how pieces connect.
   - **Concept question** (e.g. "closures", "async/await", "React hooks") → find real examples of this concept in the codebase and teach it progressively from simple to complex, 3-8 steps. See the **Concept tours** section below.

   If the question is too broad to answer well in a single tour (e.g. "explain everything"), mentally narrow it to the most interesting or important aspect and note in the intro what you're covering and what you're leaving out.

2. **Identify the audience.** Consider how the question was phrased:
   - "How does X work?" → assume someone **new to this codebase** — explain architectural decisions, not just code mechanics
   - "Why does X do Y?" → assume someone **debugging or reviewing** — focus on the reasoning and edge cases
   - "Walk me through X" → assume someone who wants the **full picture** — be thorough, include context

3. **Research the codebase.** Read the relevant source files thoroughly. Follow the code path from entry point to completion.

4. **Identify the key locations** that tell the story — the files and line ranges that someone needs to see to understand the answer.

5. **Note configuration dependencies.** If the behavior changes based on environment variables, feature flags, config files, or runtime conditions, note these. They must be called out in the tour so the reader understands "this is what happens when X is configured, but if Y were set instead, the flow would differ here."

6. **Plan a logical sequence** of steps that builds understanding progressively. Each step should lead naturally to the next.

**Guidelines for choosing steps:**
- Start where the flow begins (entry point, config, initialization)
- Follow the execution path in the order things actually happen
- Include only locations that are essential to understanding — skip boilerplate
- End at the final outcome (response sent, data persisted, UI rendered)
- Each step should cover a single concept or code section
- Include concrete examples where possible (e.g. "when the user runs `diffity main`, this becomes...")

**Handling cross-module flows:** When the code path crosses into a library, utility module, or deeply nested abstraction, decide whether to follow it:
- **Follow it** if the logic there is essential to understanding the answer (e.g. a custom middleware that transforms the request)
- **Summarize it** if the module does something standard or well-known (e.g. "this calls the Express router, which matches the path and invokes our handler") — mention what it does in the step body without creating a separate step for it
- **Skip it** if it's pure boilerplate or plumbing (e.g. re-exports, type-only files)

### Phase 2: Create the tour

The tour UI has a dedicated explanation panel. The intro (from `tour-start --body`) is displayed as **step 0** — the first thing the reader sees, filling the full panel. Each subsequent step shows its narrative in the same panel alongside the highlighted code. Since the panel has generous space, write rich, detailed explanations.

1. **Start the tour** with a short topic title and introductory body:
   ```
   diffity agent tour-start --topic "<short title>" --body "<intro>" --json
   ```

   The `--topic` is displayed in the tour panel header — keep it to **3–6 words** (e.g. "Authentication Flow", "How Routing Works", "Comment System Architecture"). Do NOT use the user's full question as the topic.

   **Writing the intro body (step 0):**
   This is the first thing the reader sees and it fills the entire explanation panel. Use this space for a thorough architectural overview that sets up everything the reader needs before diving into code. Include:
   - The key components/packages/modules involved and their responsibilities
   - How they connect — data flow, call chains, or dependency relationships
   - Key abstractions or patterns the reader should know about
   - A summary flow diagram using bold text (e.g. **CLI args → git diff → parser → JSON API → React render**)
   - **Configuration context** — if the feature's behavior depends on config, environment variables, or feature flags, mention them here so the reader knows what mode/state the tour assumes

   If you scoped down a broad question, state what you're covering: "This tour focuses on the OAuth login flow. Token refresh and session management are related but covered separately."

   Use rich markdown formatting — paragraphs, bold, `code`, tables, code blocks. This is not a table of contents of what the tour will cover; it's a standalone overview that orients the reader.

   Extract the tour ID from the JSON output.

2. **Add steps** in order. For each step:
   ```
   diffity agent tour-step --tour <id> --file <path> --line <start> --end-line <end> --body "<narrative>" --annotation "<short label>" --json
   ```

   **Writing step content:**

   - `--file`: Path relative to repo root (e.g. `src/server.ts`)
   - `--line` / `--end-line`: The exact line range to highlight. Keep it focused on the relevant section.
   - `--annotation`: A short label (3-6 words) shown as the step title. Think of it as a chapter heading.
   - `--body`: The narrative shown in the explanation panel. This has generous space — use it to write thorough explanations using markdown:

   **Step transitions — connecting the narrative:**
   Each step should feel like a natural continuation of the previous one. Start each step body with a **transition sentence** that connects it to what came before:
   - "Now that we've seen how the request is parsed, let's look at where it gets validated..."
   - "The handler we just saw delegates to this service, which is where the actual business logic lives..."
   - "At this point the data has been transformed and is ready to be persisted — here's how that happens..."

   Never start a step as if the reader arrived out of context. The tour is a story — each step is a chapter, not an isolated paragraph.

   **Do:**
   - Write in prose paragraphs, supplemented by structured content where it helps
   - Use `code` for function names, variables, refs, commands. When referencing a function, class, or code symbol that lives in a **known file and line**, make it a **goto link** so the reader can click to jump there. Syntax: `` [`symbolName`](goto:path/to/file.ts:startLine-endLine) `` or `` [`symbolName`](goto:path/to/file.ts:line) `` for a single line. These render as clickable inline code that navigates to the file and highlights the target lines. Example: `` [`handleDragEnd`](goto:src/KanbanContent.jsx:42-58) ``. Use plain backtick code for generic terms, CLI commands, or symbols you haven't located in the codebase.
   - Use **bold** for key concepts being introduced
   - Explain *why* the code exists and the design decisions behind it, not just what it does
   - Use concrete examples: "When you run `diffity main`, this line calls `normalizeRef('main')` which computes `git merge-base main HEAD`"
   - Use tables for mappings (input → output, ref → git command)
   - Use code blocks for data structures or command outputs
   - Connect each step to the bigger picture from the intro
   - **Call out edge cases and gotchas** — if there's a non-obvious behavior, a known limitation, or a "this looks wrong but it's intentional" moment, flag it. These are the things that trip people up when they work on this code later.
   - For large highlighted ranges, use **sub-highlight links** to focus on specific sub-sections within the step. Syntax: `[label](focus:startLine-endLine)`. These render as clickable chips that shift the highlight to the specified lines. Example:

     ```markdown
     First, the function validates its parameters:
     [Parameter validation](focus:15-22)

     Then the core transform processes each entry:
     [Core transform](focus:25-40)

     Finally, results are cached before returning:
     [Result caching](focus:42-48)
     ```

     Use sub-highlights when a step covers 30+ lines and the narrative naturally breaks into distinct sections. The line ranges must be within the step's `--line` / `--end-line` range.

   **Mermaid diagrams:**
   When a concept is easier to understand visually — architecture relationships, data flows, state machines, sequence diagrams — include a mermaid code block. Don't force diagrams into every step; use them where they genuinely clarify the explanation. Good candidates:
   - The intro (step 0) overview: a flow showing how components connect
   - Steps involving multi-component interactions or request flows
   - State machines or lifecycle transitions

   Choose the most appropriate diagram type:
   - `graph TD/LR` for architecture, module dependencies, data flow
   - `sequenceDiagram` for call chains, request/response flows
   - `stateDiagram-v2` for state machines, lifecycle transitions
   - `classDiagram` for type hierarchies, struct relationships
   - `flowchart` for algorithms, decision trees, control flow

   Keep diagrams concise (under ~12 nodes). They render inline in the tour panel.

   **Don't:**
   - Write a wall of bullet points — use prose paragraphs with formatting
   - Just describe the syntax — explain the design decisions
   - Repeat information visible in the highlighted code
   - Use headers in step bodies (the annotation serves as the title)
   - Force a diagram into every step — only add one when it genuinely helps
   - Start a step without connecting it to the previous one

3. **Add a conclusion step.** The final step of the tour should wrap things up. Reuse the file/line range from the last meaningful step and write a body that:

   - **Summarizes the full flow** in 2-3 sentences — now that the reader has seen every piece, give them the zoomed-out mental model they can carry forward
   - **Highlights the key design decisions** — what are the 2-3 most important architectural choices in this code, and why were they made?
   - **Points out extension points** — if someone wanted to modify or extend this feature, where would they start? What files would they touch?
   - **Notes related areas** — mention 1-2 related features or flows that connect to this one, so the reader knows where to explore next

   Use the annotation `"Putting It Together"` for this step.

4. **Finish the tour:**
   ```
   diffity agent tour-done --tour <id> --json
   ```

### Phase 3: Open in browser

1. Get the running instance port from `diffity list --json`.
2. Open the tour: `open "http://localhost:<port>/tour/<tour-id>"` (or the appropriate command for the user's OS).
3. Tell the user the tour is ready:

   > Your tour is ready — check your browser.

## Concept tours

When the user asks about a **programming concept** rather than a feature or flow (e.g. "closures", "generics", "error handling patterns"), the tour becomes a teaching tool.

**How concept tours differ from feature tours:**
- **Research phase**: Instead of following an execution path, search the codebase for real instances of the concept. Use grep, glob, and file reads to find patterns. Look broadly — closures might appear as callbacks, factory functions, or event handlers.
- **Example selection**: Pick 3-8 examples that cover different facets, progressing from simple to complex. Don't show 5 examples of the same usage.
- **Intro body**: Write it for someone who may have never encountered this concept. Include: a jargon-free definition, why it exists (what problem it solves), a mental model or analogy, and what syntactic clues to look for.
- **Step bodies**: Each step teaches one facet through a real example. Structure as: orient the reader in the code → point out the concept in action → explain why it's used here → key takeaway. Define jargon inline the first time it appears.
- **Progression**: First example should make the reader think "oh, that's all it is?" Last example should be the most sophisticated usage.
- **Summary step**: Recap 3-5 key rules, list 2-3 common mistakes, suggest related concepts to learn next.
- **Sparse codebases**: If fewer than 3 real examples exist, create temporary teaching snippet files, use them as tour steps (clearly labeled as standalone examples), and delete them after the tour is created.

All other tour guidelines (transitions, goto links, sub-highlights, mermaid diagrams, conclusion) still apply.

## Quality Checklist

Before finishing, verify:

- [ ] Intro (step 0) gives a thorough architectural overview, not a table of contents
- [ ] If the question was scoped down, the intro states what is and isn't covered
- [ ] Configuration dependencies (env vars, feature flags, config) are called out where relevant
- [ ] Steps follow the actual execution/data flow, not alphabetical file order
- [ ] Each step starts with a transition that connects it to the previous step
- [ ] Design decisions and "why" are explained, not just "what the code does"
- [ ] Edge cases and gotchas are flagged where they exist
- [ ] No two consecutive steps highlight the same lines in the same file
- [ ] Cross-module jumps are either followed, summarized, or skipped — not left unexplained
- [ ] A conclusion step ties everything together with a mental model, design decisions, and extension points
- [ ] Every function, class, or symbol reference with a known file location uses a goto link
