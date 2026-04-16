# Embedding Diagrams in ADRs

## Markdown Format (MANDATORY: Always Include Source)

**CRITICAL**: Every rendered diagram MUST be followed by a collapsible `<details>` block containing the graph-easy source code. This is non-negotiable for:

- **Reproducibility**: Future maintainers can regenerate the diagram
- **Editability**: Source can be modified and re-rendered
- **Auditability**: Changes to diagrams are trackable in git diffs

````markdown
## Architecture

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Before  │ ──> │  After   │ ──> │ Database │
└──────────┘     └──────────┘     └──────────┘
```

<details>
<summary>graph-easy source</summary>

```
graph { flow: east; }
[Before] -> [After] -> [Database]
```

</details>
````

**The `<details>` block is MANDATORY** - never embed a diagram without its source.

## GFM Collapsible Section Syntax

GitHub Flavored Markdown supports HTML `<details>` and `<summary>` tags for collapsible sections. Key syntax rules:

**Structure:**

```html
<details>
  <summary>Click to expand</summary>

  <!-- BLANK LINE REQUIRED HERE -->
  Content goes here (Markdown supported)
  <!-- BLANK LINE REQUIRED HERE -->
</details>
```

**Critical rules:**

1. **Blank lines required** - Must have empty line after `<summary>` and before `</details>` for Markdown to render
2. **No indentation** - `<details>` and `<summary>` must be at column 0 (no leading spaces)
3. **Summary is clickable label** - Text in `<summary>` appears as the collapsed header
4. **Markdown inside works** - Code blocks, headers, lists all render correctly inside

**Optional: Default expanded:**

```html
<details open>
  <summary>Expanded by default</summary>

  Content visible on page load
</details>
```

**Common mistake (Markdown won't render):**

```html
<details>
  <summary>Broken</summary>
  No blank line - this won't render as Markdown!
</details>
```

**References:**

- [GitHub Docs: Collapsed sections](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections)
- [GFM details/summary gist](https://gist.github.com/scmx/eca72d44afee0113ceb0349dd54a84a2)

## File Organization

No separate asset files needed - diagram is inline in the markdown.

## Regeneration

If ADR changes, regenerate by running the source through graph-easy again:

```bash
# Extract source from <details> block, pipe through graph-easy
graph-easy --as=boxart << 'EOF'
# paste source here
EOF
```
