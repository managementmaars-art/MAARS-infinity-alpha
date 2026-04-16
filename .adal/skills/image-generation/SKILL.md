---
name: image-generation
description: Generate illustration images for articles and documentation using Gemini Nano Banana 2 API. Produces clean, minimal-style diagrams and concept illustrations.
---

# Image Generation Skill

Generate illustration images for blog posts, documentation, and technical articles using Google Gemini's Nano Banana 2 (gemini-3.1-flash-image-preview) model.

**Prerequisite:** `GEMINI_API_KEY` must be set in environment variables.

## When to Use

- User asks to generate an illustration, diagram, or concept image
- User is writing an article and needs visual explanations for concepts or workflows
- User explicitly asks for AI-generated images

## Step 1: Determine the Image Requirements

Before generating, clarify:

1. **What to illustrate** — the concept, architecture, flow, or scene
2. **Language** — default to English for both prompt and text in image. Only use other languages if the user explicitly requests it
3. **Save location** — see "Output Path" section below
4. **Style/color preferences** — if user has specific needs, otherwise use defaults

## Step 2: Craft the Prompt

### Default Style Prefix (always prepended unless user overrides)

The script automatically prepends this style prefix:

> Use a clean, modern color palette with soft tones. Minimalist flat illustration style with clear visual hierarchy. Professional and polished look suitable for technical blog articles. No photorealistic rendering. No excessive gradients or shadows.

### Prompt Writing Guidelines

- Be specific and descriptive about the visual elements
- For technical concepts: describe the components, their relationships, and layout
- For architecture diagrams: list the layers/components and how they connect
- For flow diagrams: describe the steps and direction of flow
- If text labels are needed in the image, spell them out explicitly in the prompt
- Default language is English. Only write the prompt and request in-image text in another language if the user specifically asks

### Example Prompts

**Architecture diagram:**
```
A system architecture diagram showing: User sends query to an API Gateway,
which routes to a Vector Database (labeled "Milvus") and an LLM service.
The Vector Database returns relevant documents, which are combined with the
original query and sent to the LLM for final response generation.
Arrows show data flow direction. Each component is a rounded rectangle with
an icon and label.
```

**Concept illustration:**
```
A visual comparison of keyword search vs semantic search. Left side shows
keyword search with exact word matching (highlighted matching words).
Right side shows semantic search with a brain icon understanding meaning
and connecting related concepts with dotted lines. A dividing line separates
the two approaches.
```

## Step 3: Generate the Image

Run the script:

```bash
python ${CLAUDE_SKILL_ROOT}/scripts/generate_image.py \
  --prompt "your prompt here" \
  --output "/path/to/save/image.png"
```

### Default Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| Model | `gemini-3.1-flash-image-preview` (Nano Banana 2) | Fastest with good quality |
| Aspect ratio | `3:2` | Landscape (width:height = 3:2), ideal for article illustrations |
| Image size | `1K` | Good balance of quality and cost |
| Style | Minimal, clean, soft tones | Auto-prepended to prompt |
| Language | English | Prompt and in-image text |

### Available Options

```
--model          Model ID (gemini-3.1-flash-image-preview, gemini-3-pro-image-preview, gemini-2.5-flash-image)
--aspect-ratio   1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, etc.
--image-size     512, 1K, 2K, 4K
--style-prefix   Custom style prefix (replaces the default)
--no-style       Skip default style prefix entirely
```

### When to Change Defaults

| Scenario | Change |
|----------|--------|
| User wants higher quality | `--image-size 2K` |
| User wants best quality | `--model gemini-3-pro-image-preview --image-size 2K` |
| Social media banner | `--aspect-ratio 16:9` |
| Portrait/vertical image | `--aspect-ratio 3:4` or `--aspect-ratio 9:16` |
| Square image (icon, avatar) | `--aspect-ratio 1:1` |
| User has their own style | `--style-prefix "your style"` or `--no-style` |
| Non-English content | Write prompt in target language, no parameter change needed |

## Step 4: Determine Output Path

Follow this priority order to decide where to save the generated image:

### Priority 1: Context from Current Conversation

If the user is working on a specific markdown file or article:

1. Check where existing images in that article are stored (look for `![` image references in the `.md` file)
2. Save the new image in the **same directory** as the existing images
3. Use a descriptive filename that matches the naming convention of existing images

Example: if the article has `![](images/architecture-overview.png)`, save to the same `images/` directory.

### Priority 2: Project Image Directory

If no specific article context but working within a project:

1. Look for existing image directories: `images/`, `assets/`, `static/`, `img/`, `figures/`
2. Save in the most appropriate existing directory
3. If none exists, create an `images/` directory at the project root or under the relevant content directory

### Priority 3: Fallback

If no clear project context:

1. Save to the current working directory
2. Use a descriptive filename: `concept-name-illustration.png`

### Filename Convention

- Use lowercase with hyphens: `vector-search-architecture.png`
- Be descriptive: prefer `rag-pipeline-overview.png` over `image1.png`
- Match existing naming patterns in the project if any

## Step 5: Verify the Result

After generating:

1. Read the image file to visually verify it matches the user's request
2. If the result is not satisfactory, refine the prompt and regenerate
3. If the image will be inserted into a markdown file, suggest the markdown syntax: `![alt text](relative/path/to/image.png)`
