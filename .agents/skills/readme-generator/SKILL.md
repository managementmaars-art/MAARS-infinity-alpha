---
name: readme-generator
description: Draft or rewrite GitHub README.md files for repositories, libraries, apps, CLIs, starters, cookbook repos, curated resource lists, and internal tools. Use when Codex needs to inspect a codebase, choose the right README shape for the repo type, answer what the project is and how to use it quickly, avoid duplicated top-of-file descriptions, and use GitHub Markdown features only when they improve comprehension.
---

# README Generator

Write README files that feel edited, not templated. Keep them concise, but front-load the details a reader needs to decide whether the project is worth their time.

## Working Pass

1. Inspect the repository before writing. Read manifests, scripts, entrypoints, tests, existing docs, release metadata, and any current README material. Do not invent commands, features, support status, or maintainership claims.
2. Decide the README shape from the repo type before drafting. A library, app, CLI, starter, cookbook repo, curated list, and internal tool should not get the same structure.
3. Before using advanced formatting or unfamiliar Markdown, read [references/github-readme-patterns.md](references/github-readme-patterns.md) and [references/github-markdown-docs.md](references/github-markdown-docs.md).
4. Build the first screen first. Make the opening answer the reader's main questions before adding lower-priority sections.
5. Expand only where the reader would otherwise be blocked, confused, or unable to trust the project enough to continue.
6. Compress the draft aggressively. Remove repeated summaries, generic feature dumps, padded intros, and sections that only restate nearby text.

## First-Screen Test

Before writing past the first screenful, make sure a reader can answer these questions quickly:

- What is this?
- Does it solve my problem?
- Can I use it right now?
- Can I trust it enough to continue?

For libraries and tools, explicitly optimize the opening around the classic triage questions: does it solve my problem, can I use this code, and can I trust this code.

If the README fails that test, fix the top before adding more depth.

## Default Length

Aim for the shortest README that still lets a new reader understand the project, start using it, and judge whether it is credible. Most repos only need a title, one sharp sentence, one install block, and one usage example.

Expand only when a reader would otherwise be blocked, confused, or likely to misuse the project.

## House Style

Use lowercase for the project title only when it fits the repository's visual identity. Do not force every section heading to lowercase. Use normal Title Case or sentence case for section headings unless the repository already has a clear house style.

Make the tone technical, calm, and approachable. Avoid filler, empty hype, and stiff corporate copy. "Friendly" means easy to read, not sales-heavy.

Center the title and short tagline for many GitHub-facing READMEs, but not by default in every repo. Use HTML only when it improves the layout or keeps the intro shorter.

Prefer prose over bullet spam. Use lists only when the content is genuinely list-shaped.

Use badges, tables, alerts, details blocks, footnotes, diagrams, task lists, images, star-history charts, and inline HTML only when they make the README faster to scan or shorter overall. If a richer element does not improve comprehension, cut it.

## Title Block

Start from this pattern when the repository does not already have a better visual identity:

```markdown
<p align="center">
  <img src="./docs/placeholder-hero.png" alt="project preview" width="1200" />
</p>

<h1 align="center">project name</h1>

<p align="center">one sharp sentence about what the project does.</p>
```

Use one clear short description near the top. Do not write a second "overview" paragraph that merely repeats the same sentence with more words.

Add an overview only when it contributes new information such as:

- who the project is for
- why it exists
- how it works at a high level
- key tradeoffs
- where it fits in a larger ecosystem

If the one-line description already does the job, skip the overview entirely.

If the repository has no real screenshots or diagrams yet, insert a clearly labeled placeholder and tell the user to replace it:

```markdown
<!-- Replace docs/placeholder-hero.png with a real screenshot, UI crop, or architecture diagram. -->
```

Only include an image slot when a visual would materially speed up understanding. Use it for apps, extensions, dashboards, workflows, or architecture diagrams. For invisible tools or tiny libraries, skip the hero instead of forcing a placeholder.

Treat visuals as proof, not as the only explanation. A reader should still understand the project without loading the image.

Prefer a short GIF or live demo link over a static screenshot when motion or interaction is central to understanding the product. Use a screenshot when it communicates the point just as well with less noise.

## Cognitive Funnel

Order the README from broad, high-value triage to deeper detail:

1. Identity: title plus one-sentence description
2. Proof: screenshot, GIF, demo link, or one strong example when it helps
3. Adoption: install, quickstart, usage
4. Trust: compatibility, maintenance, docs, support, license, caveats
5. Depth: API, background, FAQ, contributing, acknowledgements, roadmap

Keep the top optimized for a skim. Push background, contributor notes, acknowledgements, and changelog material lower or out of the README unless a first-time reader truly needs them.

## Shape by Repo Type

- Library or tool: title, one-liner, install, minimal usage, API or docs pointer, requirements and compatibility if needed, license, and trust signals such as maintenance or support paths when they are available.
- App, dashboard, site, or extension: title, one-liner, visual proof when available, quickstart, core user flow, environment notes, demo or docs links.
- CLI: title, one-liner, install, command examples, output or before/after examples, options table only if it is shorter than prose.
- Starter, template, or clone: title, one-liner, screenshot, GIF, or live demo when available, concise quickstart, included stack or features, opinionated choices, references explaining the structure, and FAQ only for recurring setup friction.
- Cookbook or examples repo: title, one-liner, table of contents, reproducible run instructions, dependency and data notes, links to datasets or external inputs when needed, task-specific recipes, and subdirectory READMEs when local context matters.
- Curated list or resources repo: title, one-liner, strong table of contents, well-grouped sections, contribution guidance, clear scope, and a basic code of conduct if the project is active enough to need one.
- Internal tool: keep it shorter; include only what a teammate needs to run it, use it safely, and know where to go next.

## Section Decisions

Include installation or setup only when the repository exposes real commands. Favor one happy-path example over a matrix of package managers unless the project officially supports several.

Include usage when the install or run command is not enough to teach first use. Prefer one to three strong, runnable examples over an API wall.

Include a highlights or features section only when three to five bullets materially speed up evaluation. Do not add highlights that merely paraphrase the one-liner.

Be explicit about requirements, dependencies, and platform support. If the project is Ubuntu-only, Python-version-bound, browser-limited, or depends on external services, say so plainly.

Use a quick-links row only when the repo has meaningful destinations such as docs, demo, website, API reference, examples, Discord, or issue tracker, and the reader benefits from jumping there immediately.

Use trust signals when they help a reader decide whether to adopt the project: compatibility notes, support status, active docs, CI, release status, or contact points. Do not add a ceremonial "trust" section; integrate those signals where they fit naturally.

Include contact details or a support path for public projects when the maintainer wants issues, discussions, email, Discord, or social links to serve as a real trust and feedback channel.

Use tables when they compress commands, options, environments, compatibility notes, or feature differences better than prose.

Use badges when they add real signal near the top of the README, such as CI status, package version, license, coverage, or release channel. Skip vanity badge piles.

Use alerts only when a warning or caveat is important enough to isolate.

Use details blocks when setup is real but optional, or when deeper technical notes would otherwise bloat the default path.

Use task lists for setup checklists or short roadmaps only when checkboxes genuinely improve scanning.

Use footnotes for small caveats or definitions that would otherwise interrupt a sentence.

Use diagrams only when a workflow, architecture, or data flow is harder to explain in one paragraph.

Use a short `Why`, `Why this exists`, or `Why not` section only when the category is crowded, the tradeoffs matter, or the reader would not quickly understand the motivation.

Use a short alternatives or comparison section only when similar projects are relevant and the comparison helps a reader choose. Keep it brief and objective; link out for the deep comparison if needed.

Use a compatibility matrix only when runtime, platform, browser, version, or environment support materially affects adoption.

Use a background section when the project depends on unfamiliar concepts, jargon, or surrounding ecosystems. Linkify unfamiliar terms instead of assuming the reader already knows them.

Use troubleshooting or FAQ only when setup friction is common enough that a short rescue section will save users time.

Use contributing, security, support, and license sections briefly for public repos when the reader needs those links in the README. If the full policy lives elsewhere, keep the README version short.

Use benchmarks only when performance is a real selling point and the repo has measured data worth showing.

Use ecosystem or integrations only when the project has adapters, plugins, supported frameworks, or companion packages that materially change adoption decisions.

Do not add repository tree diagrams, directory maps, or ASCII file-structure blocks by default. Use them only when the repository is navigation-heavy enough that the structure itself is part of how the project is understood, when the README already uses that pattern, or when the user explicitly asks for it.

Use a docs split rule when the README starts carrying too much detail. If the repo already has dedicated docs, keep the README closer to an elevator pitch plus jump links.

Include development or contribution notes only if the repository has a credible contributor flow and a reader needs that information in the README. If there is no tested workflow, or if the material belongs in separate docs, leave it out.

Add optional sections only when leaving them out would make the README unclear, unsafe, or incomplete for first use. If neither is true, leave the section out.

When deciding whether to add a section, ask: does this help a reader understand, adopt, trust, or evaluate the project faster? If not, leave it out.

When several formatting options could work, choose the smallest one that improves comprehension. A short table is better than four repetitive bullets. A collapsed details block is better than forcing optional setup into the default path.

When the repository already has a README, keep the strongest material and rewrite around it instead of flattening everything into a new template.

## GitHub Markdown Rules

GitHub Markdown supports more than most READMEs need. Use the platform deliberately:

- GitHub already shows an outline when a Markdown file has two or more headings. Do not add a manual table of contents unless the README is long, list-heavy, or a curated resource index.
- Use relative links for local files and images. This keeps links working for both GitHub readers and cloned repositories.
- Use a blank line before a Markdown table or it will not render correctly.
- Use `<details>` plus `<summary>` for optional setup or deep notes, not for core instructions.
- Use alerts sparingly. One or two high-value callouts are enough; do not stack them.
- Use Mermaid only when a small diagram is clearer than prose. Keep diagrams simple and verify the syntax GitHub supports.
- Use workflow badges only when the repository has a real workflow worth surfacing. Point to the actual workflow file and remember that private-repo badges do not embed externally.
- Use footnotes for small caveats, not as a dumping ground for critical instructions.
- Use `<picture>` only when responsive image behavior matters enough to justify inline HTML.

## Final Checks

Confirm that every command exists, every linked path is real, every local image path is real, and every section earns its place.

Confirm that the opening does not duplicate itself. If the one-line description already explains the project, do not follow it with an overview that says the same thing again.

Confirm that a reader can understand the project without opening the source code and without depending on an image alone.

Confirm that a first-time reader can tell whether the project solves their problem, whether they can use it, and whether it looks maintained enough to trust.

Leave explicit placeholders only for facts the repository cannot reveal on its own. If a placeholder is visual, tell the user to replace it with a real image after generation.

If the README uses advanced formatting, make sure each element earns its place. Rich Markdown should reduce clutter, not create it.

If badges or a star-history chart are included, verify that the links resolve and reflect real project state rather than decorative filler.

If the README includes usage code, make sure it is runnable or clearly maps to a real file or command in the repository.

## Avoid

- Do not turn the README into a Markdown feature demo.
- Do not write a mini-docs site when a short README would do the job.
- Do not write both a one-line description and a second summary paragraph that says the same thing in slower prose.
- Do not open with a giant feature checklist.
- Do not stack a wall of low-signal badges across the top.
- Do not mirror generic SaaS landing-page language.
- Do not repeat the same information in the summary, overview, table, and usage example.
- Do not rely on screenshots or GIFs to communicate critical setup or usage steps.
- Do not hide important requirements, platform limits, or external dependencies.
- Do not add ASCII repo trees or directory structure diagrams unless the repo genuinely needs them or the user asks for them.
- Do not add `Why`, compatibility, FAQ, benchmarks, ecosystem, or security sections just because large repos often have them.
- Do not keep sections for development, roadmap, contributing, acknowledgments, or license unless the repository actually benefits from them.
- Do not put changelog material in the README unless there is a very unusual reason.
