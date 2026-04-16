# ADF Node Reference Guide

Complete reference for all ADF node types, their attributes, allowed children, and examples.

## Document Structure

### Root Node: `doc`

Every ADF document must start with this node.

**Required Properties:**
- `version` (number): Always `1`
- `type` (string): Always `"doc"`
- `content` (array): Array of block nodes

**Example:**
```json
{
  "version": 1,
  "type": "doc",
  "content": [
    { "type": "paragraph", "content": [...] }
  ]
}
```

**Allowed Children:** Any block-level nodes (paragraph, heading, list, panel, etc.)

---

## Block-Level Nodes

Block nodes form the structural elements at the top level of documents.

### `heading`

Represents headings at various levels (H1-H6).

**Properties:**
- `type`: `"heading"`
- `attrs.level` (number): 1-6, where 1 is H1, 6 is H6
- `content` (array): Inline content (text, emoji, links)

**Example:**
```python
{
  "type": "heading",
  "attrs": {"level": 2},
  "content": [{"type": "text", "text": "Heading Text"}]
}
```

**Builder:**
```python
doc.add_heading("Heading Text", level=2)
```

**Allowed Children:** Inline nodes (text, emoji, mention, etc.)

---

### `paragraph`

Plain paragraph of text with optional inline formatting.

**Properties:**
- `type`: `"paragraph"`
- `content` (array): Inline content

**Example:**
```python
{
  "type": "paragraph",
  "content": [
    {"type": "text", "text": "This is "},
    {"type": "text", "text": "bold", "marks": [{"type": "strong"}]},
    {"type": "text", "text": " text."}
  ]
}
```

**Builder:**
```python
doc.add_paragraph(
    doc.add_text("Normal text "),
    doc.bold("bold text")
)
```

**Allowed Children:** Inline nodes (text, emoji, mention, link, etc.)

---

### `bulletList`

Unordered list (bullet points).

**Properties:**
- `type`: `"bulletList"`
- `content` (array): Array of `listItem` nodes

**Example:**
```python
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": "First item"}]
        }
      ]
    }
  ]
}
```

**Builder:**
```python
doc.add_bullet_list(["Item 1", "Item 2", "Item 3"])
```

**Allowed Children:** `listItem` only

---

### `orderedList`

Numbered/ordered list.

**Properties:**
- `type`: `"orderedList"`
- `attrs.order` (number, optional): Starting number (default: 1)
- `content` (array): Array of `listItem` nodes

**Example:**
```python
{
  "type": "orderedList",
  "attrs": {"order": 1},
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": "First step"}]
        }
      ]
    }
  ]
}
```

**Builder:**
```python
doc.add_ordered_list(["Step 1", "Step 2"], start=1)
```

**Allowed Children:** `listItem` only

---

### `listItem`

Individual item within a bullet or ordered list.

**Properties:**
- `type`: `"listItem"`
- `content` (array): Paragraph nodes (typically one paragraph)

**Note:** Created automatically by `add_bullet_list()` and `add_ordered_list()`

**Allowed Children:** `paragraph` (typically)

---

### `codeBlock`

Block of code with optional syntax highlighting.

**Properties:**
- `type`: `"codeBlock"`
- `attrs.language` (string, optional): Programming language (python, javascript, etc.)
- `content` (array): Text nodes with code content

**Example:**
```python
{
  "type": "codeBlock",
  "attrs": {"language": "python"},
  "content": [
    {"type": "text", "text": "def hello():\n    print('world')"}
  ]
}
```

**Builder:**
```python
doc.add_code_block("def hello():\n    print('world')", language="python")
```

**Allowed Children:** `text` nodes

---

### `panel`

Colored information box. Types: info, note, warning, success, error.

**Properties:**
- `type`: `"panel"`
- `attrs.panelType` (string): One of: info, note, warning, success, error
- `content` (array): Block nodes (paragraphs, lists, etc.)

**Example:**
```python
{
  "type": "panel",
  "attrs": {"panelType": "warning"},
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Important warning!"}]
    }
  ]
}
```

**Builder:**
```python
doc.add_panel("warning",
    {"type": "paragraph", "content": [doc.add_text("Warning message")]}
)
```

**Allowed Children:** Block nodes (paragraph, list, code block, etc.)

---

### `rule`

Horizontal rule / separator line.

**Properties:**
- `type`: `"rule"`
- No `content` or `attrs` required

**Example:**
```python
{"type": "rule"}
```

**Builder:**
```python
doc.add_rule()
```

**Allowed Children:** None

---

### `table`

Table with rows, headers, and cells.

**Properties:**
- `type`: `"table"`
- `attrs.isNumberColumnEnabled` (boolean): Show row numbers
- `attrs.layout` (string): `"default"` or `"wide"`
- `content` (array): Array of `tableRow` nodes

**Example:**
```python
{
  "type": "table",
  "attrs": {"isNumberColumnEnabled": false, "layout": "default"},
  "content": [
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableHeader",
          "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "Header"}]}
          ]
        }
      ]
    }
  ]
}
```

**Allowed Children:** `tableRow` only

---

### `tableRow`

Row in a table.

**Properties:**
- `type`: `"tableRow"`
- `content` (array): Array of `tableHeader` or `tableCell` nodes

**Allowed Children:** `tableHeader`, `tableCell`

---

### `tableHeader`

Header cell in a table row.

**Properties:**
- `type`: `"tableHeader"`
- `content` (array): Block nodes (typically paragraph)

**Allowed Children:** Block nodes (usually `paragraph`)

---

### `tableCell`

Data cell in a table row.

**Properties:**
- `type`: `"tableCell"`
- `content` (array): Block nodes (typically paragraph)

**Allowed Children:** Block nodes (usually `paragraph`)

---

### `blockquote`

Block quotation for highlighting quoted text or content.

**Properties:**
- `type`: `"blockquote"`
- `content` (array): Block nodes (paragraphs, lists, etc.)

**Example:**
```json
{
  "type": "blockquote",
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "This is a quoted passage."}]
    }
  ]
}
```

**Allowed Children:** Block nodes (paragraph, heading, list, etc.)

---

### `expand`

Expandable/collapsible section (also called "expansion").

**Properties:**
- `type`: `"expand"`
- `attrs.title` (string): Title shown when collapsed
- `content` (array): Block nodes displayed when expanded

**Example:**
```json
{
  "type": "expand",
  "attrs": {"title": "Click to expand"},
  "content": [
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Hidden content here"}]
    }
  ]
}
```

**Allowed Children:** Block nodes

---

### `taskList`

List of tasks with checkboxes (todo list).

**Properties:**
- `type`: `"taskList"`
- `attrs.localId` (string): Unique identifier for the task list
- `content` (array): Array of `taskItem` nodes

**Example:**
```json
{
  "type": "taskList",
  "attrs": {"localId": "task-list-1"},
  "content": [
    {
      "type": "taskItem",
      "attrs": {"localId": "task-1", "state": "TODO"},
      "content": [
        {
          "type": "text",
          "text": "Complete this task"
        }
      ]
    }
  ]
}
```

**Allowed Children:** `taskItem` only

---

### `taskItem`

Individual task in a task list.

**Properties:**
- `type`: `"taskItem"`
- `attrs.localId` (string): Unique identifier
- `attrs.state` (string): "TODO" or "DONE"
- `content` (array): Inline content

**Allowed Children:** Inline nodes

---

### `decisionList`

List of decisions with status indicators.

**Properties:**
- `type`: `"decisionList"`
- `attrs.localId` (string): Unique identifier
- `content` (array): Array of `decisionItem` nodes

**Allowed Children:** `decisionItem` only

---

### `decisionItem`

Individual decision in a decision list.

**Properties:**
- `type`: `"decisionItem"`
- `attrs.localId` (string): Unique identifier
- `attrs.state` (string): "DECIDED", etc.
- `content` (array): Inline content

**Allowed Children:** Inline nodes

---

## Inline Nodes

Inline nodes appear within block content (paragraphs, headings, etc.).

### `text`

Text content with optional formatting marks.

**Properties:**
- `type`: `"text"`
- `text` (string): The actual text content
- `marks` (array, optional): Formatting marks

**Example:**
```python
{
  "type": "text",
  "text": "Bold text",
  "marks": [{"type": "strong"}]
}
```

**Builder:**
```python
doc.add_text("Text content")
doc.bold("Bold text")
doc.italic("Italic text")
doc.code("inline_code")
doc.strikethrough("Strikethrough")
```

**Allowed Children:** None

---

### `emoji`

Emoji character.

**Properties:**
- `type`: `"emoji"`
- `attrs.shortName` (string): Emoji shortcode (e.g., `:rocket:`)
- `attrs.text` (string, optional): Unicode character for display

**Example:**
```python
{
  "type": "emoji",
  "attrs": {
    "shortName": ":rocket:",
    "text": "🚀"
  }
}
```

**Builder:**
```python
doc.add_emoji(":rocket:", "🚀")
```

**Allowed Children:** None

---

### `mention`

User or team mention (@mention).

**Properties:**
- `type`: `"mention"`
- `attrs.id` (string): User or team ID
- `attrs.text` (string): Display name

**Example:**
```json
{
  "type": "mention",
  "attrs": {
    "id": "557058:12345678-1234-1234-1234-123456789012",
    "text": "@John Doe"
  }
}
```

**Allowed Children:** None

---

### `date`

Date stamp with timestamp.

**Properties:**
- `type`: `"date"`
- `attrs.timestamp` (string): ISO 8601 timestamp

**Example:**
```json
{
  "type": "date",
  "attrs": {
    "timestamp": "1698796800000"
  }
}
```

**Allowed Children:** None

---

### `status`

Status badge/lozenge with color.

**Properties:**
- `type`: `"status"`
- `attrs.text` (string): Status text
- `attrs.color` (string): Color (neutral, purple, blue, red, yellow, green)
- `attrs.localId` (string, optional): Unique identifier

**Example:**
```json
{
  "type": "status",
  "attrs": {
    "text": "In Progress",
    "color": "blue",
    "localId": "status-1"
  }
}
```

**Allowed Children:** None

---

### `hardBreak`

Line break within text.

**Properties:**
- `type`: `"hardBreak"`

**Example:**
```json
{"type": "hardBreak"}
```

**Allowed Children:** None

---

## Text Marks (Formatting)

Marks are applied to text nodes to add formatting.

### `strong`

Make text bold.

**Example:**
```python
{"type": "text", "text": "Bold", "marks": [{"type": "strong"}]}
```

---

### `em`

Make text italic.

**Example:**
```python
{"type": "text", "text": "Italic", "marks": [{"type": "em"}]}
```

---

### `code`

Format as inline code.

**Example:**
```python
{"type": "text", "text": "variable_name", "marks": [{"type": "code"}]}
```

---

### `underline`

Underline text.

**Example:**
```python
{"type": "text", "text": "Underlined", "marks": [{"type": "underline"}]}
```

---

### `strike`

Strikethrough text.

**Example:**
```python
{"type": "text", "text": "Strikethrough", "marks": [{"type": "strike"}]}
```

---

### `link`

Hyperlink with URL.

**Properties:**
- `type`: `"link"`
- `attrs.href` (string): URL target

**Example:**
```python
{
  "type": "text",
  "text": "Click here",
  "marks": [{"type": "link", "attrs": {"href": "https://example.com"}}]
}
```

**Builder:**
```python
doc.link("Click here", "https://example.com")
```

---

### `subsup`

Subscript or superscript text.

**Properties:**
- `type`: `"subsup"`
- `attrs.type` (string): "sub" or "sup"

**Example:**
```json
{
  "type": "text",
  "text": "x2",
  "marks": [{"type": "subsup", "attrs": {"type": "sup"}}]
}
```

---

### `textColor`

Text color formatting.

**Properties:**
- `type`: `"textColor"`
- `attrs.color` (string): Hex color code

**Example:**
```json
{
  "type": "text",
  "text": "Red text",
  "marks": [{"type": "textColor", "attrs": {"color": "#ff0000"}}]
}
```

---

### `backgroundColor`

Background color for text.

**Properties:**
- `type`: `"backgroundColor"`
- `attrs.color` (string): Hex color code

**Example:**
```json
{
  "type": "text",
  "text": "Highlighted",
  "marks": [{"type": "backgroundColor", "attrs": {"color": "#ffff00"}}]
}
```

---

### `border`

Border around text.

**Properties:**
- `type`: `"border"`
- `attrs.color` (string, optional): Border color
- `attrs.size` (number, optional): Border width

**Example:**
```json
{
  "type": "text",
  "text": "Bordered",
  "marks": [{"type": "border"}]
}
```

---

### `alignment`

Text alignment mark.

**Properties:**
- `type`: `"alignment"`
- `attrs.align` (string): "start", "end", "center"

**Example:**
```json
{
  "type": "paragraph",
  "marks": [{"type": "alignment", "attrs": {"align": "center"}}],
  "content": [{"type": "text", "text": "Centered text"}]
}
```

---

### `indentation`

Text indentation level.

**Properties:**
- `type`: `"indentation"`
- `attrs.level` (number): Indentation level (1-6)

**Example:**
```json
{
  "type": "paragraph",
  "marks": [{"type": "indentation", "attrs": {"level": 2}}],
  "content": [{"type": "text", "text": "Indented text"}]
}
```

---

### `annotation`

Inline comment or annotation.

**Properties:**
- `type`: `"annotation"`
- `attrs.id` (string): Annotation ID
- `attrs.annotationType` (string): Type of annotation

**Example:**
```json
{
  "type": "text",
  "text": "Commented text",
  "marks": [{"type": "annotation", "attrs": {"id": "comment-1", "annotationType": "inlineComment"}}]
}
```

---

## Common Attribute Patterns

### Panel Types

```python
panel_types = ["info", "note", "tip", "warning", "error", "success", "custom"]
doc.add_panel("warning", content_node)
```

### Status Colors

```python
status_colors = ["neutral", "purple", "blue", "red", "yellow", "green"]
# Example in raw ADF:
{
  "type": "status",
  "attrs": {"text": "In Progress", "color": "blue"}
}
```

### Heading Levels

```python
# 1 = largest, 6 = smallest
doc.add_heading("H1", level=1)
doc.add_heading("H2", level=2)
doc.add_heading("H3", level=3)
doc.add_heading("H4", level=4)
doc.add_heading("H5", level=5)
doc.add_heading("H6", level=6)
```

### Code Languages

Common language identifiers for syntax highlighting:

```python
languages = [
    "text",      # No highlighting
    "python",    # Python
    "javascript",# JavaScript/Node.js
    "typescript",# TypeScript
    "java",      # Java
    "kotlin",    # Kotlin
    "go",        # Go
    "rust",      # Rust
    "sql",       # SQL
    "bash",      # Bash/Shell
    "json",      # JSON
    "yaml",      # YAML
    "xml",       # XML
    "html",      # HTML
    "css",       # CSS
]
```

---

## Node Hierarchy Reference

### Valid Block Node Children of `doc`:

```
doc
├── heading
├── paragraph
├── bulletList
├── orderedList
├── taskList
├── decisionList
├── codeBlock
├── panel
├── blockquote
├── expand
├── rule
└── table
```

### Valid Children of `paragraph`:

```
paragraph
├── text
├── emoji
├── mention
├── date
├── status
├── inlineCard
└── hardBreak
```

### Valid Children of `bulletList` / `orderedList`:

```
list
└── listItem
    └── paragraph
        ├── text
        ├── emoji
        └── ...
```

### Valid Children of `table`:

```
table
└── tableRow
    ├── tableHeader
    │   └── paragraph
    │       ├── text
    │       └── ...
    └── tableCell
        └── paragraph
            ├── text
            └── ...
```

### Valid Children of `codeBlock`:

```
codeBlock
└── text (with code content)
```

---

## Validation Checklist

When creating ADF, verify:

- [ ] Root node has `version: 1`, `type: "doc"`, and `content` array
- [ ] All block nodes have `content` array (even if empty)
- [ ] All block nodes requiring `attrs` have them (e.g., heading level, panel type)
- [ ] Block nodes only contain valid children
- [ ] Inline nodes are only used within block `content`
- [ ] Text nodes have `text` property with string value
- [ ] Marks are applied only to text nodes
- [ ] No circular references in node structure
- [ ] All required properties present (type, content where needed)

---

## Example: Complete Document

Here's a complete ADF document showing proper structure:

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": { "level": 1 },
      "content": [
        { "type": "text", "text": "Complete ADF Example" }
      ]
    },
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "This document demonstrates " },
        {
          "type": "text",
          "text": "various ADF nodes",
          "marks": [{ "type": "strong" }]
        },
        { "type": "text", "text": "." }
      ]
    },
    {
      "type": "heading",
      "attrs": { "level": 2 },
      "content": [
        { "type": "text", "text": "Lists" }
      ]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "text": "First item" }
              ]
            }
          ]
        },
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [
                { "type": "text", "text": "Second item" }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "codeBlock",
      "attrs": { "language": "python" },
      "content": [
        {
          "type": "text",
          "text": "def hello():\n    return 'world'"
        }
      ]
    },
    {
      "type": "panel",
      "attrs": { "panelType": "info" },
      "content": [
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "This is an info panel." }
          ]
        }
      ]
    }
  ]
}
```

---

## Debugging Tips

**Issue:** "content is required"
- **Cause:** Block node missing content array
- **Fix:** Add `"content": []` or populate with valid children

**Issue:** "Invalid node type for child position"
- **Cause:** Wrong node type in wrong context
- **Fix:** Check node hierarchy above - ensure correct parent-child relationships

**Issue:** "attrs is required"
- **Cause:** Node needs attributes but they're missing
- **Fix:** Add required `attrs` object (e.g., level for heading, panelType for panel)

**Issue:** Text not appearing in Jira
- **Cause:** Text node missing `text` property
- **Fix:** Verify all text nodes have `"text": "..."` property

**Issue:** Formatting not applied
- **Cause:** Marks not properly attached to text node
- **Fix:** Ensure marks are in `marks` array on text node, not separate
