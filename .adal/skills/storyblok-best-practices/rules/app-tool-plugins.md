---
title: Build Tool and Space Plugins
impact: HIGH
impactDescription: extends Storyblok with custom functionality
tags: app, tool-plugin, space-plugin, sidebar, extension
---

## Build Tool and Space Plugins

**Impact: HIGH (extends Storyblok with custom functionality)**

Tool plugins add functionality to the Visual Editor, while space plugins provide full-page applications in the sidebar. Use the App Bridge for authentication and communication.

**Incorrect (bypassing App Bridge):**

```jsx
// Bad: Direct API calls without proper auth
const SpacePlugin = () => {
  const fetchStories = async () => {
    // No authentication!
    const response = await fetch('https://mapi.storyblok.com/v1/spaces/123/stories');
  };
};

// Bad: Manual postMessage handling
const ToolPlugin = () => {
  useEffect(() => {
    window.parent.postMessage({ action: 'get-context' }, '*');
    // Error-prone, missing security
  }, []);
};
```

**Correct (using App Bridge):**

```jsx
// Good: Tool plugin with App Bridge
// src/ToolPlugin.jsx
import { useAppBridge } from '@storyblok/app-extension-sdk';

export default function ToolPlugin() {
  const { context, actions, loading } = useAppBridge();

  if (loading) {
    return <div>Loading...</div>;
  }

  const { story, spaceId, userId } = context;

  const handleAnalyze = async () => {
    // Access the current story being edited
    const content = story?.content;

    // Perform analysis
    const results = await analyzeContent(content);

    // Show notification
    actions.showNotification({
      type: 'success',
      message: 'Analysis complete!'
    });
  };

  const handleInsertBlock = () => {
    // Insert a block into the story
    actions.insertBlock({
      component: 'text_block',
      content: {
        text: 'Inserted from tool plugin'
      }
    });
  };

  return (
    <div className="tool-plugin">
      <h2>Content Analyzer</h2>
      <p>Editing: {story?.name}</p>

      <button onClick={handleAnalyze}>Analyze Content</button>
      <button onClick={handleInsertBlock}>Insert Block</button>
    </div>
  );
}
```

```jsx
// Good: Space plugin (sidebar app) with OAuth
// src/SpacePlugin.jsx
import { useAppBridge } from '@storyblok/app-extension-sdk';
import { useEffect, useState } from 'react';

export default function SpacePlugin() {
  const { context, actions, authToken, loading } = useAppBridge();
  const [stories, setStories] = useState([]);

  useEffect(() => {
    if (authToken) {
      fetchStories();
    }
  }, [authToken]);

  const fetchStories = async () => {
    const response = await fetch(
      `https://mapi.storyblok.com/v1/spaces/${context.spaceId}/stories`,
      {
        headers: {
          'Authorization': authToken // OAuth token from App Bridge
        }
      }
    );
    const data = await response.json();
    setStories(data.stories);
  };

  const handleCreateStory = async (data) => {
    const response = await fetch(
      `https://mapi.storyblok.com/v1/spaces/${context.spaceId}/stories`,
      {
        method: 'POST',
        headers: {
          'Authorization': authToken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ story: data })
      }
    );

    if (response.ok) {
      actions.showNotification({
        type: 'success',
        message: 'Story created!'
      });
      fetchStories();
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-plugin">
      <h1>Content Manager</h1>
      <p>Space: {context.spaceName}</p>

      <section>
        <h2>Stories</h2>
        <ul>
          {stories.map(story => (
            <li key={story.id}>
              <a
                href="#"
                onClick={() => actions.openStory(story.id)}
              >
                {story.name}
              </a>
            </li>
          ))}
        </ul>
      </section>

      <CreateStoryForm onSubmit={handleCreateStory} />
    </div>
  );
}
```

```jsx
// Good: manifest.json for plugin configuration
{
  "name": "Content Analyzer",
  "slug": "content-analyzer",
  "type": "tool", // or "sidebar" for space plugin
  "description": "Analyze and optimize your content",
  "icon": "https://example.com/icon.svg",
  "oauth": {
    "scopes": ["read_content", "write_content"]
  },
  "options": [
    {
      "name": "apiKey",
      "type": "text",
      "label": "External API Key"
    }
  ]
}
```

```jsx
// Good: Server-side OAuth handler (Next.js example)
// app/api/auth/callback/route.js
import { handleCallback } from '@storyblok/app-extension-auth';

export async function GET(request) {
  return handleCallback(request, {
    clientId: process.env.STORYBLOK_CLIENT_ID,
    clientSecret: process.env.STORYBLOK_CLIENT_SECRET,
    onSuccess: async ({ accessToken, spaceId }) => {
      // Store token securely
      await storeToken(spaceId, accessToken);
    }
  });
}
```

**Plugin types comparison:**

| Feature | Tool Plugin | Space Plugin |
|---------|-------------|--------------|
| Location | Visual Editor sidebar | Space sidebar |
| Story access | Current story only | All stories |
| Use case | Content analysis, quick actions | Full apps, bulk operations |
| OAuth scopes | Limited | Full Management API |

**App Bridge actions:**

| Action | Description |
|--------|-------------|
| `showNotification()` | Display notification |
| `openStory(id)` | Navigate to story |
| `insertBlock()` | Insert block (tool only) |
| `getUser()` | Get current user |
| `getValue()` | Get plugin option value |

Reference: [App Bridge](https://www.storyblok.com/docs/plugins/app-bridge)
