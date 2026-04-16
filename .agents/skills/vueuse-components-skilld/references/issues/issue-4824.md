---
number: 4824
title: `docs` | Auto-generate `llms.txt`
type: docs
state: open
created: 2025-06-16
url: "https://github.com/vueuse/vueuse/issues/4824"
reactions: 7
comments: 4
labels: "[documentation, good first issue]"
---

# `docs` | Auto-generate `llms.txt`

### Clear and concise description of the problem

As a developer using VueUse, I want to provide LLMs (local or API-based) with structured, easy-to-ingest documentation via a standard `/llms.txt` file, so that I can improve prompt-based tooling, contextual embeddings, and agent access to VueUse APIs.

Happy to contribute a PR if maintainers support this direction.


### Suggested solution

llms.txt


### Alternative

Copy/Paste


### Additional context

llms.txt is designed to be human- and LLM-readable, minimal, and works well with fixed-token contexts.



### Validations

- [x] Follow our Code of Conduct
- [x] Read the Contributing Guidelines.
- [x] Read the docs.
- [x] Check that there isn't already an issue that request the same feature to avoid creating a duplicate.

---

## Top Comments

**@OrbisK** [maintainer] (+5):

I think we can do this with: https://github.com/okineadev/vitepress-plugin-llms

**@ilyaliao** [maintainer] (+1):

I'd love to have this! Though I tried `vitepress-plugin-llms` but couldn't quite get it working 

**@matthall-akkio**:

Would love this! The workflow of "hey <agent> here's my codebase and the VueUse docs, please upgrade to use where appropriate" would work quite well based on my experience doing the same with other libs.