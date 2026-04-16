---
title: Custom Sidebar and Tool Apps
impact: MEDIUM
impactDescription: extends Storyblok UI with custom functionality beyond field plugins
tags: apps, sidebar, tools, extensions, custom-app, oauth
---

## Custom Sidebar and Tool Apps

**Impact: MEDIUM (extends Storyblok UI with custom functionality beyond field plugins)**

Build custom sidebar apps and tool plugins to extend the Storyblok editor with integrations, custom workflows, and specialized tools. Unlike field plugins, these apps have access to the full story context.

### App Types

| Type | Location | Use Case |
|------|----------|----------|
| **Sidebar App** | Right sidebar panel | Story-level tools, integrations, analytics |
| **Tool Plugin** | Toolbar | Quick actions, content generation |
| **Field Plugin** | Within field | Custom field input (covered separately) |

**Incorrect (wrong app type or architecture):**

```typescript
// Bad: Using field plugin for story-level functionality
// Field plugins can't access other fields or story metadata

// Bad: Monolithic app without proper state management
function SidebarApp() {
  const [everything, setEverything] = useState({});
  // Unmanageable state, no separation of concerns
}

// Bad: Not using Storyblok's bridge for communication
window.postMessage({ type: 'save', data: content });
// Won't work - must use official SDK
```

**Correct (sidebar app setup):**

```typescript
// Good: Sidebar app with @storyblok/app-extension-auth
// package.json
{
  "name": "my-storyblok-sidebar-app",
  "dependencies": {
    "@storyblok/app-extension-auth": "^1.0.0",
    "@storyblok/design-system": "^3.0.0",
    "react": "^18.0.0"
  }
}
```

```typescript
// Good: App initialization with OAuth
// src/main.tsx
import { initAuth } from '@storyblok/app-extension-auth';

const { isAuthenticated, getToken, spaceId } = await initAuth({
  clientId: process.env.STORYBLOK_CLIENT_ID!,
  clientSecret: process.env.STORYBLOK_CLIENT_SECRET!,
  baseUrl: process.env.APP_URL!,
  endpointPrefix: '/api/auth'
});

if (!isAuthenticated) {
  // Redirect to OAuth flow
  window.location.href = '/api/auth/connect';
}

// Now can make authenticated API calls
const token = await getToken();
```

```typescript
// Good: Bridge communication for sidebar app
import { useStoryblokBridge } from '@storyblok/react';

function SidebarApp() {
  const [story, setStory] = useState<Story | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    // Listen for story changes from editor
    const handleMessage = (event: MessageEvent) => {
      if (event.data.action === 'loaded') {
        setStory(event.data.story);
      }
      if (event.data.action === 'change') {
        setStory(event.data.story);
        setIsEditing(true);
      }
      if (event.data.action === 'published') {
        setIsEditing(false);
      }
    };

    window.addEventListener('message', handleMessage);

    // Request initial story data
    window.parent.postMessage({ action: 'getStory' }, '*');

    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return (
    <div className="p-4">
      {story && <StoryTools story={story} />}
    </div>
  );
}
```

**Sidebar app with Management API access:**

```typescript
// Good: API route for authenticated Management API calls
// pages/api/stories/[id].ts (Next.js API route)
import { getServerSession } from '@storyblok/app-extension-auth';

export default async function handler(req, res) {
  const session = await getServerSession(req);

  if (!session) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const { id } = req.query;
  const { spaceId, accessToken } = session;

  try {
    const response = await fetch(
      `https://mapi.storyblok.com/v1/spaces/${spaceId}/stories/${id}`,
      {
        headers: {
          'Authorization': accessToken,
          'Content-Type': 'application/json'
        }
      }
    );

    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

```typescript
// Good: Sidebar component with API integration
function SEOAnalyzer({ story }: { story: Story }) {
  const [analysis, setAnalysis] = useState<SEOAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  const analyzeContent = async () => {
    setLoading(true);
    try {
      // Call your backend which processes the content
      const response = await fetch('/api/analyze-seo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: story.content,
          slug: story.full_slug
        })
      });

      const result = await response.json();
      setAnalysis(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <button
        onClick={analyzeContent}
        disabled={loading}
        className="sb-button sb-button--primary"
      >
        {loading ? 'Analyzing...' : 'Analyze SEO'}
      </button>

      {analysis && (
        <div className="space-y-2">
          <ScoreCard label="SEO Score" value={analysis.score} />
          <IssuesList issues={analysis.issues} />
          <SuggestionsList suggestions={analysis.suggestions} />
        </div>
      )}
    </div>
  );
}
```

**Tool plugin implementation:**

```typescript
// Good: Tool plugin for content generation
// Tool plugins appear in the editor toolbar

interface ToolPluginContext {
  story: Story;
  spaceId: string;
  token: string;
  selectedComponent?: string;
}

function AIContentGenerator({ context }: { context: ToolPluginContext }) {
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);

  const generateContent = async () => {
    setGenerating(true);
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          context: {
            storyTitle: context.story.name,
            existingContent: context.story.content,
            targetComponent: context.selectedComponent
          }
        })
      });

      const { generatedContent } = await response.json();

      // Send content back to editor
      window.parent.postMessage({
        action: 'insert',
        content: generatedContent,
        targetComponent: context.selectedComponent
      }, '*');

    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <textarea
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="Describe what content to generate..."
        className="sb-textarea w-full"
        rows={4}
      />
      <button
        onClick={generateContent}
        disabled={generating || !prompt}
        className="sb-button sb-button--primary w-full"
      >
        {generating ? 'Generating...' : 'Generate Content'}
      </button>
    </div>
  );
}
```

**App manifest configuration:**

```json
// storyblok.config.json
{
  "name": "SEO Toolkit",
  "slug": "seo-toolkit",
  "description": "Analyze and optimize content for search engines",
  "icon": "search",
  "sidebar": {
    "enabled": true,
    "defaultOpen": false,
    "displayName": "SEO Tools"
  },
  "toolbar": {
    "enabled": true,
    "buttons": [
      {
        "icon": "search",
        "label": "Analyze SEO",
        "action": "openSidebar"
      },
      {
        "icon": "wand",
        "label": "Generate Meta",
        "action": "generateMeta"
      }
    ]
  },
  "settings": {
    "fields": [
      {
        "name": "apiKey",
        "type": "password",
        "label": "API Key",
        "required": true
      },
      {
        "name": "targetScore",
        "type": "number",
        "label": "Target SEO Score",
        "default": 80
      }
    ]
  },
  "scopes": [
    "read:stories",
    "write:stories",
    "read:assets"
  ]
}
```

**Using Storyblok Design System:**

```tsx
// Good: Consistent UI with Storyblok Design System
import {
  SbButton,
  SbCard,
  SbTextField,
  SbSelect,
  SbBadge,
  SbTooltip,
  SbModal
} from '@storyblok/design-system';

function IntegrationPanel({ story }: { story: Story }) {
  const [showModal, setShowModal] = useState(false);

  return (
    <SbCard>
      <SbCard.Header>
        <SbCard.Title>External Integrations</SbCard.Title>
        <SbBadge variant="positive">Connected</SbBadge>
      </SbCard.Header>

      <SbCard.Content>
        <div className="space-y-4">
          <SbSelect
            label="Sync Target"
            options={[
              { value: 'shopify', label: 'Shopify' },
              { value: 'algolia', label: 'Algolia' },
              { value: 'hubspot', label: 'HubSpot' }
            ]}
          />

          <SbTooltip content="Sync this content to external system">
            <SbButton
              variant="primary"
              onClick={() => setShowModal(true)}
            >
              Sync Now
            </SbButton>
          </SbTooltip>
        </div>
      </SbCard.Content>

      <SbModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Confirm Sync"
      >
        <p>This will update the external system with current content.</p>
        <SbButton onClick={handleSync}>Confirm</SbButton>
      </SbModal>
    </SbCard>
  );
}
```

**Handling app settings:**

```typescript
// Good: Access app settings configured by space admin
interface AppSettings {
  apiKey: string;
  targetScore: number;
  enabledFeatures: string[];
}

async function getAppSettings(spaceId: string): Promise<AppSettings> {
  const response = await fetch(`/api/settings?spaceId=${spaceId}`);
  return response.json();
}

function SettingsAwareApp() {
  const [settings, setSettings] = useState<AppSettings | null>(null);

  useEffect(() => {
    // Settings passed via postMessage from Storyblok
    const handleMessage = (event: MessageEvent) => {
      if (event.data.action === 'appSettings') {
        setSettings(event.data.settings);
      }
    };

    window.addEventListener('message', handleMessage);
    window.parent.postMessage({ action: 'getAppSettings' }, '*');

    return () => window.removeEventListener('message', handleMessage);
  }, []);

  if (!settings) return <Loading />;

  return <AppWithSettings settings={settings} />;
}
```

**Deployment and hosting:**

```typescript
// Good: Vercel deployment for sidebar app
// vercel.json
{
  "builds": [
    { "src": "package.json", "use": "@vercel/next" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/$1" },
    { "src": "/(.*)", "dest": "/$1" }
  ],
  "env": {
    "STORYBLOK_CLIENT_ID": "@storyblok-client-id",
    "STORYBLOK_CLIENT_SECRET": "@storyblok-client-secret"
  }
}
```

```typescript
// Good: App registration via CLI
// Register app with Storyblok
// npx storyblok-cli apps create \
//   --name "SEO Toolkit" \
//   --slug "seo-toolkit" \
//   --url "https://your-app.vercel.app" \
//   --scopes "read:stories,write:stories"
```

**Best practices:**

| Practice | Description |
|----------|-------------|
| Use Design System | Consistent look with Storyblok UI |
| OAuth properly | Use official auth SDK, not custom tokens |
| Scope minimally | Request only needed permissions |
| Cache responses | Reduce API calls, improve performance |
| Handle offline | Graceful degradation when API unavailable |
| Validate input | Sanitize data from editor context |
| Test in sandbox | Use dev space before production |

Reference: [App Extensions](https://www.storyblok.com/docs/plugins/app-extensions) | [OAuth Setup](https://www.storyblok.com/docs/plugins/authentication) | [Design System](https://www.storyblok.com/docs/guide/in-depth/design-system)
