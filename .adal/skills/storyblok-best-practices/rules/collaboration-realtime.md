---
title: Real-Time Collaboration and Comments
impact: MEDIUM
impactDescription: enables efficient team workflows and contextual feedback
tags: collaboration, comments, real-time, editing, teams, conflict
---

## Real-Time Collaboration and Comments

**Impact: MEDIUM (enables efficient team workflows and contextual feedback)**

Leverage Storyblok's real-time collaboration features including simultaneous editing, component-level comments, and conflict resolution for agency team workflows.

### Real-Time Editing Features

| Feature | Description |
|---------|-------------|
| **Presence indicators** | See who's editing the same story |
| **Live cursors** | Track collaborator positions |
| **Auto-save** | Changes saved automatically |
| **Conflict detection** | Warning when same field edited |

**Incorrect (no collaboration awareness):**

```typescript
// Bad: No conflict handling
async function saveStory(storyId: string, content: object) {
  // Overwrites without checking for concurrent edits
  await managementApi.put(`spaces/${spaceId}/stories/${storyId}`, {
    story: { content }
  });
}

// Bad: Long editing sessions without saves
// User edits for 30 minutes, then saves
// Another user's changes are silently overwritten

// Bad: No awareness of other editors
function ContentEditor({ story }) {
  return <Editor content={story.content} />;
  // No indication if others are editing
}
```

**Correct (collaboration-aware implementation):**

```typescript
// Good: Check story version before saving
interface StoryVersion {
  id: string;
  updated_at: string;
  updated_by: string;
}

async function saveStoryWithConflictCheck(
  storyId: string,
  content: object,
  expectedVersion: string
) {
  // Fetch current version
  const { data: current } = await managementApi.get(
    `spaces/${spaceId}/stories/${storyId}`
  );

  if (current.story.updated_at !== expectedVersion) {
    throw new ConflictError({
      message: 'Story was modified by another user',
      currentVersion: current.story.updated_at,
      lastEditor: current.story.updated_by,
      yourVersion: expectedVersion
    });
  }

  // Safe to save
  return managementApi.put(`spaces/${spaceId}/stories/${storyId}`, {
    story: { content }
  });
}
```

```typescript
// Good: Optimistic locking with retry
async function saveWithRetry(
  storyId: string,
  updateFn: (content: object) => object,
  maxRetries: number = 3
) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const { data } = await managementApi.get(
        `spaces/${spaceId}/stories/${storyId}`
      );

      const updatedContent = updateFn(data.story.content);

      await saveStoryWithConflictCheck(
        storyId,
        updatedContent,
        data.story.updated_at
      );

      return { success: true };
    } catch (error) {
      if (error instanceof ConflictError && attempt < maxRetries - 1) {
        // Wait and retry with merged content
        await new Promise(r => setTimeout(r, 1000 * (attempt + 1)));
        continue;
      }
      throw error;
    }
  }
}
```

**Component-level comments:**

```typescript
// Good: Add comment to specific component
interface StoryComment {
  component_uuid: string; // Target component
  text: string;
  resolved: boolean;
  author: {
    id: string;
    name: string;
    avatar: string;
  };
  created_at: string;
  replies: StoryComment[];
}

async function addComponentComment(
  storyId: string,
  componentUuid: string,
  text: string
) {
  return managementApi.post(
    `spaces/${spaceId}/stories/${storyId}/comments`,
    {
      comment: {
        component_uuid: componentUuid,
        text,
        resolved: false
      }
    }
  );
}

// Good: Fetch comments for a story
async function getStoryComments(storyId: string) {
  const { data } = await managementApi.get(
    `spaces/${spaceId}/stories/${storyId}/comments`
  );

  // Group by component
  const byComponent = data.comments.reduce((acc, comment) => {
    const uuid = comment.component_uuid;
    if (!acc[uuid]) acc[uuid] = [];
    acc[uuid].push(comment);
    return acc;
  }, {} as Record<string, StoryComment[]>);

  return byComponent;
}
```

```tsx
// Good: Visual Editor component with comment indicator
import { storyblokEditable } from '@storyblok/react';

interface CommentableComponentProps {
  blok: any;
  comments?: StoryComment[];
}

function CommentableComponent({ blok, comments = [] }: CommentableComponentProps) {
  const unresolvedCount = comments.filter(c => !c.resolved).length;

  return (
    <div {...storyblokEditable(blok)} className="relative">
      {/* Comment indicator */}
      {unresolvedCount > 0 && (
        <div className="absolute -top-2 -right-2 bg-yellow-400 text-xs
                        rounded-full w-5 h-5 flex items-center justify-center">
          {unresolvedCount}
        </div>
      )}

      {/* Component content */}
      <ComponentContent blok={blok} />
    </div>
  );
}
```

**Presence and activity tracking:**

```typescript
// Good: Track active editors using webhooks
interface EditorPresence {
  storyId: string;
  userId: string;
  userName: string;
  lastActivity: Date;
  activeComponent?: string;
}

class PresenceTracker {
  private presence = new Map<string, EditorPresence[]>();
  private readonly TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

  addEditor(storyId: string, editor: Omit<EditorPresence, 'lastActivity'>) {
    const editors = this.presence.get(storyId) || [];
    const existing = editors.findIndex(e => e.userId === editor.userId);

    const presence: EditorPresence = {
      ...editor,
      storyId,
      lastActivity: new Date()
    };

    if (existing >= 0) {
      editors[existing] = presence;
    } else {
      editors.push(presence);
    }

    this.presence.set(storyId, editors);
    this.cleanStale(storyId);
  }

  getEditors(storyId: string): EditorPresence[] {
    this.cleanStale(storyId);
    return this.presence.get(storyId) || [];
  }

  private cleanStale(storyId: string) {
    const editors = this.presence.get(storyId) || [];
    const now = Date.now();
    const active = editors.filter(
      e => now - e.lastActivity.getTime() < this.TIMEOUT_MS
    );
    this.presence.set(storyId, active);
  }
}
```

**Conflict resolution strategies:**

```typescript
// Good: Three-way merge for content conflicts
interface ConflictResolution {
  strategy: 'mine' | 'theirs' | 'merge' | 'manual';
  mergedContent?: object;
}

function detectFieldConflicts(
  base: object,
  mine: object,
  theirs: object
): string[] {
  const conflicts: string[] = [];

  const allKeys = new Set([
    ...Object.keys(base),
    ...Object.keys(mine),
    ...Object.keys(theirs)
  ]);

  for (const key of allKeys) {
    const baseVal = JSON.stringify(base[key]);
    const mineVal = JSON.stringify(mine[key]);
    const theirsVal = JSON.stringify(theirs[key]);

    // Both changed the same field differently
    if (mineVal !== baseVal && theirsVal !== baseVal && mineVal !== theirsVal) {
      conflicts.push(key);
    }
  }

  return conflicts;
}

function autoMerge(
  base: object,
  mine: object,
  theirs: object
): { merged: object; conflicts: string[] } {
  const conflicts = detectFieldConflicts(base, mine, theirs);
  const merged = { ...base };

  for (const key of Object.keys({ ...mine, ...theirs })) {
    const baseVal = JSON.stringify(base[key]);
    const mineVal = JSON.stringify(mine[key]);
    const theirsVal = JSON.stringify(theirs[key]);

    if (conflicts.includes(key)) {
      // Keep mine for conflicts (user can override)
      merged[key] = mine[key];
    } else if (mineVal !== baseVal) {
      // I changed it
      merged[key] = mine[key];
    } else if (theirsVal !== baseVal) {
      // They changed it
      merged[key] = theirs[key];
    }
  }

  return { merged, conflicts };
}
```

```tsx
// Good: Conflict resolution UI
function ConflictResolver({
  fieldName,
  baseValue,
  myValue,
  theirValue,
  theirAuthor,
  onResolve
}: {
  fieldName: string;
  baseValue: any;
  myValue: any;
  theirValue: any;
  theirAuthor: string;
  onResolve: (value: any) => void;
}) {
  return (
    <div className="border-l-4 border-yellow-500 p-4 bg-yellow-50">
      <h4 className="font-bold text-yellow-800">
        Conflict in "{fieldName}"
      </h4>
      <p className="text-sm text-yellow-700 mb-4">
        {theirAuthor} also modified this field
      </p>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-sm font-medium">Your version:</label>
          <pre className="bg-white p-2 rounded text-sm">
            {JSON.stringify(myValue, null, 2)}
          </pre>
          <button
            onClick={() => onResolve(myValue)}
            className="mt-2 px-3 py-1 bg-blue-500 text-white rounded"
          >
            Keep mine
          </button>
        </div>

        <div>
          <label className="text-sm font-medium">Their version:</label>
          <pre className="bg-white p-2 rounded text-sm">
            {JSON.stringify(theirValue, null, 2)}
          </pre>
          <button
            onClick={() => onResolve(theirValue)}
            className="mt-2 px-3 py-1 bg-green-500 text-white rounded"
          >
            Keep theirs
          </button>
        </div>
      </div>
    </div>
  );
}
```

**Notification patterns:**

```typescript
// Good: Notify collaborators of changes
interface CollaborationEvent {
  type: 'edit' | 'comment' | 'publish' | 'review_request';
  storyId: string;
  storyName: string;
  actor: { id: string; name: string };
  details?: string;
}

async function notifyCollaborators(
  event: CollaborationEvent,
  excludeUserId?: string
) {
  // Get story collaborators
  const { data: story } = await managementApi.get(
    `spaces/${spaceId}/stories/${event.storyId}`
  );

  // Get recent editors from activity
  const { data: activities } = await managementApi.get(
    `spaces/${spaceId}/activities`,
    {
      params: {
        story_id: event.storyId,
        per_page: 50
      }
    }
  );

  const collaboratorIds = new Set(
    activities.activities
      .map(a => a.user_id)
      .filter(id => id !== excludeUserId)
  );

  // Send notifications (integrate with Slack, email, etc.)
  for (const userId of collaboratorIds) {
    await sendNotification(userId, {
      title: getNotificationTitle(event),
      body: getNotificationBody(event),
      link: `https://app.storyblok.com/#!/me/spaces/${spaceId}/stories/${event.storyId}`
    });
  }
}
```

**Review request workflow:**

```typescript
// Good: Request review from specific team members
interface ReviewRequest {
  storyId: string;
  requesterId: string;
  reviewerIds: string[];
  message?: string;
  dueDate?: Date;
  priority: 'low' | 'normal' | 'high' | 'urgent';
}

async function requestReview(request: ReviewRequest) {
  // Add comment mentioning reviewers
  const mentions = request.reviewerIds
    .map(id => `@[user:${id}]`)
    .join(' ');

  await addComponentComment(
    request.storyId,
    'root', // Top-level comment
    `📝 Review requested: ${request.message || 'Please review this content'}\n\n${mentions}`
  );

  // Update story workflow stage
  await managementApi.put(
    `spaces/${spaceId}/stories/${request.storyId}`,
    {
      story: {
        stage: 'in_review',
        reviewer_ids: request.reviewerIds
      }
    }
  );

  // Notify reviewers
  await notifyCollaborators({
    type: 'review_request',
    storyId: request.storyId,
    storyName: '', // Fetch from story
    actor: { id: request.requesterId, name: '' },
    details: request.message
  });
}
```

**Best practices:**

| Practice | Description |
|----------|-------------|
| Auto-save frequently | Reduce conflict window |
| Show presence | Display who's currently editing |
| Lock on focus | Optional field-level locking |
| Comment context | Always comment on specific components |
| Resolve promptly | Don't leave comments hanging |
| Notify changes | Alert collaborators of significant edits |
| Version history | Use for recovery, not conflict prevention |

Reference: [Collaboration Features](https://www.storyblok.com/docs/editor-guides/collaboration) | [Comments](https://www.storyblok.com/docs/editor-guides/comments) | [Activity Log](https://www.storyblok.com/docs/api/management/activities)
