# Blog Image Generation Prompts

**IMPORTANT**: Every article MUST have a unique, content-specific image. Do NOT use generic patterns.

## Core Principles

1. **Unique per article** - Each article gets its own custom image
2. **Content-relevant** - Image visually represents the article topic
3. **Title overlay** - Include article title as text
4. **Consistent style** - Dark theme, orange accents, modern SaaS aesthetic
5. **OG-ready size** - 1200x630 pixels

## Brand Colors

```
Primary Orange: #f97316
Dark Navy: #0f172a
Dark Slate: #1e293b
Dark Charcoal: #1a1a2e
Green (security): #22c55e
Blue (comparison): #3b82f6
Teal (progress): #14b8a6
```

---

## Prompt Templates by Article Type

### 1. Comparison/Alternatives Article

**Use when**: Comparing tools, "X vs Y", "alternatives to Z"

```
A sophisticated hero image for "[TITLE]" comparison article.
Modern minimalist design with floating app icons and comparison cards.
Deep navy background (#0f172a) with orange (#f97316) gradient accents.
Show multiple tools being compared with visual hierarchy.
Include title text: "[TITLE]" and subtitle "[SUBTITLE]".
Professional SaaS marketing style like Linear or Notion.
1200x630 pixels.
```

**Example file**: `example-comparison.png`

---

### 2. Guide/Tutorial Article

**Use when**: How-to guides, complete guides, tutorials

```
A sophisticated hero image for "[TITLE]" tutorial article.
Modern minimalist design showing [RELEVANT VISUAL ELEMENTS].
Dark slate background (#1e293b) with vibrant orange (#f97316) accents.
Clean 3D floating elements suggesting [TOPIC THEME].
Include title: "[TITLE]" and subtitle "[SUBTITLE]".
Professional SaaS style. 1200x630 pixels.
```

**Example file**: `example-guide.png`

---

### 3. VS/Head-to-Head Article

**Use when**: Direct comparisons, "X vs Y" battles

```
A sophisticated hero image for "[X] vs [Y]" comparison article.
Split design: left side shows [X VISUAL], right side shows [Y VISUAL].
Visual contrast between [X THEME] and [Y THEME].
Dark background with [COLOR 1] and [COLOR 2] accents.
Include title: "[X] VS [Y]" and tagline.
Editorial style. 1200x630 pixels.
```

---

### 4. Technical/Developer Article

**Use when**: Self-hosting, APIs, developer tools, privacy

```
A sophisticated hero image for "[TITLE]" technical article.
[RELEVANT TECHNICAL VISUAL: server, code, cloud, etc.].
Emphasizes [KEY THEME: privacy, control, performance, etc.].
Dark navy background (#0f172a) with green (#22c55e) accents and orange highlights.
Include tech-related iconography subtly integrated.
Include title and tagline. Developer-friendly aesthetic.
1200x630 pixels.
```

**Example file**: `example-technical.png`

---

### 5. Routine/Habit/Lifestyle Article

**Use when**: Daily routines, habits, work-life balance

```
A sophisticated hero image for "[TITLE]" lifestyle article.
[RELEVANT SCENE: desk, morning routine, workspace, etc.].
Soft gradient from [COLOR 1] to warm orange (#f97316).
Floating UI elements showing [RELEVANT ITEMS].
[MOOD: calm, productive, aspirational, etc.].
Include title. 1200x630 pixels.
```

---

### 6. Beginner/Getting Started Article

**Use when**: Introductory content, onboarding, basics

```
A sophisticated hero image for "[TITLE]" beginner's guide.
Friendly, approachable design with simple visual elements.
Soft dark blue background (#1e293b) with orange (#f97316) accents.
Clean, not overwhelming. "Start Here" type visual cue.
Welcoming to beginners. Include title and "A Beginner's Guide" subtitle.
1200x630 pixels.
```

---

## File Naming Convention

```
public/blog-{article-slug}.png

Examples:
- blog-sunsama-alternatives.png
- blog-time-blocking-guide.png
- blog-getting-started.png
- blog-self-hosted-apps.png
```

---

## Checklist Before Generation

1. [ ] Identify article type (comparison, guide, technical, etc.)
2. [ ] Choose appropriate template
3. [ ] Customize prompt with article title
4. [ ] Include relevant visual elements for topic
5. [ ] Specify title text to include
6. [ ] Generate at 1200x630 pixels
7. [ ] Save with proper naming: `blog-{slug}.png`
8. [ ] Update article frontmatter with image path

---

## Example Prompts Used

### Sunsama Alternatives
```
A sophisticated hero image for "Sunsama Alternatives" comparison article.
Modern minimalist design with floating calendar icons and task cards.
Deep navy background (#0f172a) with orange (#f97316) gradient accents.
Show multiple tools (Notion, Akiflow, Motion, Linear icons) being compared.
Include title: "Sunsama Alternatives" and subtitle "Compare the best daily planning tools".
Professional SaaS marketing style. 1200x630 pixels.
```

### Time Blocking Guide
```
A sophisticated hero image for "Time Blocking Guide" tutorial.
Modern minimalist showing calendar grid with colorful time blocks.
Dark slate background (#1e293b) with vibrant orange (#f97316) blocks.
3D floating calendar with labeled blocks (Focus, Deep Work, Email, Meeting).
Include title: "TIME BLOCKING GUIDE" and subtitle "Master Your Day".
1200x630 pixels.
```

### Self-Hosted Productivity Apps
```
A sophisticated hero image for "Self-Hosted Productivity Apps" article.
Server rack with data flowing to personal devices (laptop, phone, tablet).
Emphasizes privacy and control with lock and shield symbols.
Dark navy background (#0f172a) with green (#22c55e) security accents.
Include title: "SELF-HOSTED PRODUCTIVITY APPS" and tagline "Your Data, Your Rules".
1200x630 pixels.
```
