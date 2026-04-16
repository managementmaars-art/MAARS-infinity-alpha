# GitHub README Patterns

Use this file as a palette, not a checklist. Start plain and stay short.

Most repos need a title, one sharp sentence, one install block, and one usage example. Stop there unless a reader would be blocked without more.

Use lowercase only for the project title when it fits. Keep section headings in normal Title Case or sentence case unless the repo already uses a different system.

Use an image only when the project is meaningfully visual. If the real asset does not exist yet, leave a placeholder comment and tell the user to replace it.

Use one clear short description at the top. Do not add an overview that merely repeats it. Add a follow-up paragraph only if it adds audience, motivation, tradeoffs, or background.

Make the opening answer four questions fast:

- What is this?
- Does it solve my problem?
- Can I use it?
- Can I trust it?

Use a cognitive funnel: identity first, proof second, install and usage next, deeper details later.

For libraries and tools, the README should work as an abstraction layer: a reader should not need to inspect the source to understand whether and how to use it.

Use the smallest Markdown feature that improves scan speed:

| Pattern | Use it when |
| --- | --- |
| Badge | CI, version, license, coverage, or release status adds real signal near the top |
| Table | You need to compare commands, options, environments, support, or feature differences quickly |
| Alert | A warning, note, or caveat is important enough to isolate |
| Details block | Setup is optional or too long for the default path |
| Task list | A setup checklist or short roadmap benefits from visible completion state |
| Footnote | A caveat is real but too small to deserve its own sentence or alert |
| Mermaid | A tiny diagram is clearer than a paragraph |
| Star-history chart | A public repo benefits from showing long-term community growth near the bottom |
| Inline HTML | Centering or image layout improves the intro without taking over the file |

Keep the first screen useful. Prefer one strong example over several shallow ones. Drop developer-only sections unless they are required for setup, contribution, or safe use.

Shape the README to the repo:

- Library/tool: install plus usage first, plus requirements, license, and trust signals when they matter
- App/site/extension: visual proof plus quickstart
- CLI: commands plus output
- Starter/template: preview, quickstart, features, and references
- Cookbook/examples: TOC, reproducible run instructions, and local READMEs where needed
- Curated list: TOC, contribution guidance, and clear scope

Prefer a GIF or demo link over a static screenshot when motion explains the product materially better.

Avoid ASCII repo trees and directory maps for most READMEs. They usually duplicate what the repository view already shows. Use them only when structure is the product, the project is unusually navigation-heavy, or the user asked for that format.

Cut repeated information between the summary, overview, table, and usage. If a section only proves that the repo has files, delete it.

Use the common big-repo sections only when they clearly earn their place:

| Section | Add it when |
| --- | --- |
| Quick links | The repo has docs, demo, API, examples, community, or issue destinations worth jumping to immediately |
| Why / Why not | The reader needs a sharper value proposition or tradeoff framing |
| Compatibility matrix | Platform, runtime, browser, or version support changes adoption decisions |
| Examples | The product is not obvious from install alone |
| Troubleshooting / FAQ | Setup friction is common enough to justify a short rescue section |
| Contributing / Security / Support / License | Public users need those links in the README, even if full policy lives elsewhere |
| Benchmarks | Performance is a real differentiator and there is measured data |
| Ecosystem / Integrations | Adapters, plugins, frameworks, or companion packages matter |
| Docs split | The README is getting too heavy and deeper material should move elsewhere |

Badges should earn their space. A short, relevant row is useful. A decorative pile is not.

If a project has meaningful platform or dependency limits, say them plainly near setup or compatibility instead of forcing users to discover them the hard way.

Star-history charts belong near the bottom, not the hero area.

If a visual is present, it should accelerate understanding, not carry the README by itself.

If you need support details beyond this guide, read [github-markdown-docs.md](github-markdown-docs.md).
