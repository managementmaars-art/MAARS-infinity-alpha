---
title: Leverage AI Content Features
impact: MEDIUM
impactDescription: automates content creation and optimization
tags: ai, automation, alt-text, seo, content-generation
---

## Leverage AI Content Features

**Impact: MEDIUM (automates content creation and optimization)**

Storyblok offers AI-powered features for content optimization including automatic alt text, SEO suggestions, and content generation. Use these to improve productivity and accessibility.

**Incorrect (manual, inconsistent approach):**

```javascript
// Bad: No alt text on images
const Image = ({ asset }) => (
  <img src={asset.filename} /> // Missing alt text - accessibility fail
);

// Bad: Manual alt text that's often skipped
{
  "name": "image_block",
  "schema": {
    "image": { "type": "asset" },
    "alt_text": { "type": "text" }  // Editors often leave blank
  }
}

// Bad: No SEO optimization workflow
// Editors manually write meta descriptions without guidance
```

**Correct (AI-enhanced workflow):**

```javascript
// Good: Enable AI alt text generation in space settings
// Settings → AI Features → Enable "AI Alt Text Generation"

// When editors upload images, AI automatically suggests alt text
// Editors can review and modify before saving

// Component that uses AI-generated alt text with fallback
const OptimizedImage = ({ asset }) => {
  // Storyblok AI populates asset.alt automatically
  const alt = asset.alt || asset.title || 'Image';

  return (
    <img
      src={`${asset.filename}/m/800x600`}
      alt={alt}
      loading="lazy"
    />
  );
};
```

```json
// Good: Component schema leveraging AI features
{
  "name": "article",
  "schema": {
    "title": {
      "type": "text",
      "display_name": "Article Title",
      "required": true,
      "ai_enabled": true
    },
    "content": {
      "type": "richtext",
      "display_name": "Content",
      "ai_enabled": true
    },
    "seo_meta": {
      "type": "bloks",
      "component_whitelist": ["seo_settings"],
      "description": "AI can help generate SEO metadata"
    },
    "featured_image": {
      "type": "asset",
      "filetypes": ["images"],
      "description": "AI will auto-generate alt text"
    }
  }
}
```

```javascript
// Good: AI-powered SEO optimization workflow
// Field plugin that uses AI for SEO suggestions

import { useFieldPlugin } from '@storyblok/field-plugin/react';

const AISeoHelper = () => {
  const { data, actions } = useFieldPlugin();
  const [suggestions, setSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateSeoSuggestions = async () => {
    setLoading(true);

    // Call your AI service or Storyblok's AI features
    const response = await fetch('/api/ai/seo-suggestions', {
      method: 'POST',
      body: JSON.stringify({
        title: data.story?.content?.title,
        content: data.story?.content?.body
      })
    });

    const suggestions = await response.json();
    setSuggestions(suggestions);
    setLoading(false);
  };

  const applySuggestion = (field, value) => {
    actions.setContent({
      ...data.content,
      [field]: value
    });
  };

  return (
    <div className="ai-seo-helper">
      <button onClick={generateSeoSuggestions} disabled={loading}>
        {loading ? 'Analyzing...' : 'Generate SEO Suggestions'}
      </button>

      {suggestions && (
        <div className="suggestions">
          <div className="suggestion">
            <h4>Meta Title</h4>
            <p>{suggestions.metaTitle}</p>
            <button onClick={() => applySuggestion('meta_title', suggestions.metaTitle)}>
              Apply
            </button>
          </div>

          <div className="suggestion">
            <h4>Meta Description</h4>
            <p>{suggestions.metaDescription}</p>
            <button onClick={() => applySuggestion('meta_description', suggestions.metaDescription)}>
              Apply
            </button>
          </div>

          <div className="suggestion">
            <h4>Keywords</h4>
            <p>{suggestions.keywords.join(', ')}</p>
          </div>
        </div>
      )}
    </div>
  );
};
```

```javascript
// Good: AI-powered content generation integration
// app/api/ai/generate-content/route.js

import { OpenAI } from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export async function POST(request) {
  const { prompt, contentType, tone, length } = await request.json();

  // Validate input
  if (!prompt) {
    return Response.json({ error: 'Prompt required' }, { status: 400 });
  }

  const systemPrompt = `You are a content writer creating ${contentType} content.
    Tone: ${tone || 'professional'}
    Length: ${length || 'medium'}
    Output format: Return structured content suitable for a CMS.`;

  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: prompt }
    ]
  });

  return Response.json({
    content: response.choices[0].message.content
  });
}
```

```javascript
// Good: Prepare content for RAG (Retrieval Augmented Generation)
// Export structured content for vector database

const exportForRAG = async () => {
  const { data } = await storyblokApi.get('cdn/stories', {
    version: 'published',
    per_page: 100
  });

  const documents = data.stories.map(story => ({
    id: story.uuid,
    slug: story.full_slug,
    title: story.name,
    content: extractTextContent(story.content),
    metadata: {
      component: story.content.component,
      published_at: story.published_at,
      tags: story.tag_list
    }
  }));

  // Send to vector database (Pinecone, Weaviate, etc.)
  await vectorDb.upsert(documents);
};

const extractTextContent = (content) => {
  // Recursively extract text from Storyblok content
  let text = '';

  const extract = (obj) => {
    if (typeof obj === 'string') {
      text += obj + ' ';
    } else if (Array.isArray(obj)) {
      obj.forEach(extract);
    } else if (typeof obj === 'object' && obj !== null) {
      // Skip non-text fields
      const skipFields = ['_uid', 'component', '_editable'];
      Object.entries(obj).forEach(([key, value]) => {
        if (!skipFields.includes(key)) {
          extract(value);
        }
      });
    }
  };

  extract(content);
  return text.trim();
};
```

```javascript
// Good: AI Branding consistency check
// Ensure content matches brand voice

const checkBrandConsistency = async (content) => {
  const brandGuidelines = await fetchBrandGuidelines();

  const response = await fetch('/api/ai/brand-check', {
    method: 'POST',
    body: JSON.stringify({
      content,
      guidelines: brandGuidelines
    })
  });

  const result = await response.json();

  return {
    isConsistent: result.score > 0.8,
    score: result.score,
    suggestions: result.suggestions,
    issues: result.issues
  };
};

// Use in editorial workflow
const beforePublish = async (story) => {
  const textContent = extractTextContent(story.content);
  const brandCheck = await checkBrandConsistency(textContent);

  if (!brandCheck.isConsistent) {
    console.warn('Brand consistency issues:', brandCheck.issues);
    // Optionally block publish or warn editor
  }

  return brandCheck;
};
```

**AI features in Storyblok:**

| Feature | Description | Availability |
|---------|-------------|--------------|
| AI Alt Text | Auto-generate image descriptions | Enterprise |
| AI SEO | Suggest meta titles/descriptions | Enterprise |
| AI Branding | Check content against brand voice | Enterprise |
| AI Translation | Assist with translations | Enterprise |
| Content Suggestions | Writing assistance in editor | Enterprise |

**Best practices:**

1. **Review AI output** - Always have editors review AI-generated content
2. **Maintain brand voice** - Configure AI with your style guidelines
3. **Accessibility first** - Use AI alt text as starting point, refine for context
4. **SEO balance** - AI suggestions should complement, not replace SEO strategy
5. **Privacy** - Ensure AI processing complies with data policies

**Future-ready: Strata vector layer:**

```javascript
// Storyblok Strata (upcoming) - Vector-based content retrieval
// Prepare content structure for semantic search

const prepareForStrata = (story) => ({
  // Structured for vector embedding
  segments: [
    { type: 'title', content: story.content.title },
    { type: 'summary', content: story.content.excerpt },
    { type: 'body', content: story.content.body }
  ],
  relationships: story.content.related_articles,
  taxonomy: story.tag_list
});
```

Reference: [AI Features](https://www.storyblok.com/mp/structured-content)
