---
name: google-docs-skill
description: Create, read, update, share, and export Google Docs. Use when the user asks to create documents, write content to Google Docs, share docs, export to PDF/DOCX, or convert markdown files to Google Docs.
allowed-tools: Bash, Read
---

# Google Docs Skill

Create, read, update, share, and export Google Docs with markdown formatting support.

## Setup

Uses same Google OAuth as gmail-skill. If configured, this works automatically.

Otherwise:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth client (Desktop app)
3. Enable **Google Docs API** and **Google Drive API**
4. Download JSON to `~/.claude/skills/google-docs-skill/credentials.json`
5. Run: `python3 ~/.claude/skills/google-docs-skill/docs_skill.py login`

## Commands

### List Documents

```bash
python3 ~/.claude/skills/google-docs-skill/docs_skill.py list [--limit N] [--account EMAIL]
```

### Create Document

```bash
# Empty document
python3 ~/.claude/skills/google-docs-skill/docs_skill.py create --title "My Document"

# With markdown body
python3 ~/.claude/skills/google-docs-skill/docs_skill.py create --title "My Document" --body "# Heading\n\nSome **bold** text"

# From file
python3 ~/.claude/skills/google-docs-skill/docs_skill.py create --title "My Document" --file ~/path/to/content.md

# Create and share immediately
python3 ~/.claude/skills/google-docs-skill/docs_skill.py create --title "My Document" --body "Content" --share user@example.com

# Plain text content (backward compat)
python3 ~/.claude/skills/google-docs-skill/docs_skill.py create --title "My Document" --content "Plain text"
```

### Read Document Content

```bash
python3 ~/.claude/skills/google-docs-skill/docs_skill.py read DOC_ID [--account EMAIL]
```

Returns plain text content of the document.

### Get Document Info

```bash
python3 ~/.claude/skills/google-docs-skill/docs_skill.py get DOC_ID [--account EMAIL]
```

### Update Document (Replace All Content)

```bash
# Replace content with markdown body
python3 ~/.claude/skills/google-docs-skill/docs_skill.py update DOC_ID --body "# New Content\n\nReplaces everything"

# Replace content from file
python3 ~/.claude/skills/google-docs-skill/docs_skill.py update DOC_ID --file ~/path/to/new-content.md
```

### Append Text

```bash
python3 ~/.claude/skills/google-docs-skill/docs_skill.py append DOC_ID --text "New content at the end"
```

### Insert Text at Position

```bash
python3 ~/.claude/skills/google-docs-skill/docs_skill.py insert DOC_ID --text "Inserted text" --index 1
```

Note: Google Docs uses 1-based indexing. Index 1 is the start of the document.

### Find and Replace

```bash
python3 ~/.claude/skills/google-docs-skill/docs_skill.py replace DOC_ID --find "old text" --replace "new text"
```

### Share Document

```bash
# Share as writer (default)
python3 ~/.claude/skills/google-docs-skill/docs_skill.py share DOC_ID --email user@example.com

# Share as reader
python3 ~/.claude/skills/google-docs-skill/docs_skill.py share DOC_ID --email user@example.com --role reader

# Share with multiple people
python3 ~/.claude/skills/google-docs-skill/docs_skill.py share DOC_ID --email user1@example.com user2@example.com

# Roles: reader, writer, commenter
```

### Export Document

```bash
# Export to PDF
python3 ~/.claude/skills/google-docs-skill/docs_skill.py export DOC_ID --format pdf

# Export to DOCX with custom path
python3 ~/.claude/skills/google-docs-skill/docs_skill.py export DOC_ID --format docx --output ~/Downloads/contract.docx

# Export to plain text
python3 ~/.claude/skills/google-docs-skill/docs_skill.py export DOC_ID --format txt
```

**Supported formats:** pdf, docx, txt, html, md, odt, rtf

### Create from Markdown File

```bash
# Convert markdown file to Google Doc
python3 ~/.claude/skills/google-docs-skill/docs_skill.py from-markdown ~/Documents/contract.md --title "Contract"

# Create from markdown and share
python3 ~/.claude/skills/google-docs-skill/docs_skill.py from-markdown ~/Documents/proposal.md --title "Proposal" --share client@example.com
```

### Account Management

```bash
# List accounts
python3 ~/.claude/skills/google-docs-skill/docs_skill.py accounts

# Login
python3 ~/.claude/skills/google-docs-skill/docs_skill.py login --account myemail@gmail.com

# Logout
python3 ~/.claude/skills/google-docs-skill/docs_skill.py logout --account myemail@gmail.com
```

### Upload Image to Drive

Upload an image to Google Drive and get a public URL for embedding in other services (Gamma, etc.):

```bash
python3 ~/.claude/skills/google-docs-skill/docs_skill.py upload-image /path/to/image.png [--folder-id FOLDER_ID]
```

Returns a direct `lh3.googleusercontent.com` URL that serves the image without redirects — works for embedding in Gamma presentations, web pages, etc.

**Integration with Gamma Skill:** To use custom images in Gamma presentations, upload them via this command, then embed the `directUrl` in your Gamma inputText with `--image-source noImages`. The `drive.google.com/uc` URLs do NOT work (303 redirect) — only the `lh3.googleusercontent.com/d/{id}` format serves direct.

## Markdown Formatting Support

The `create`, `update`, and `from-markdown` commands convert markdown to native Google Docs formatting:

| Markdown | Google Docs |
|----------|-------------|
| `# Heading` | Heading 1 |
| `## Heading` | Heading 2 |
| `### Heading` | Heading 3 |
| `#### Heading` | Heading 4 |
| `**bold**` | Bold text |
| `*italic*` | Italic text |
| `***bold italic***` | Bold + Italic |
| `- item` | Bullet list |
| `1. item` | Numbered list |
| `---` | Paragraph break |

## Document ID

Found in the URL: `https://docs.google.com/document/d/DOCUMENT_ID/edit`

## Output

All commands output JSON.

## Examples

### Create a contract from markdown, share, and export

```bash
# Create from file and share
python3 docs_skill.py from-markdown ~/vault/Epoch/Contracts/Agreement.md --title "Service Agreement" --share client@example.com

# Export as PDF for attachment
python3 docs_skill.py export DOC_ID --format pdf --output ~/Downloads/agreement.pdf
```

### Bulk find/replace for templates

```bash
python3 docs_skill.py replace DOC_ID --find "[CLIENT_NAME]" --replace "Epoch ML, Inc."
python3 docs_skill.py replace DOC_ID --find "[DATE]" --replace "February 20, 2026"
python3 docs_skill.py replace DOC_ID --find "[AMOUNT]" --replace "$50,000"
```

### Update existing doc with new content

```bash
python3 docs_skill.py update DOC_ID --body "# Updated Report\n\nNew content with **formatting**.\n\n- Item one\n- Item two"
```
