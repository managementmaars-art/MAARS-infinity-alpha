---
title: Role-Based Access Control and Permissions
impact: MEDIUM
impactDescription: enables enterprise governance and content security
tags: security, rbac, roles, permissions, access-control, enterprise
---

## Role-Based Access Control and Permissions

**Impact: MEDIUM (enables enterprise governance and content security)**

Configure roles, permissions, and access controls to protect content and enforce governance policies. Essential for enterprise multi-team environments.

### Built-in Roles

| Role | Capabilities |
|------|-------------|
| **Owner** | Full access, billing, user management |
| **Admin** | Space settings, schema, all content |
| **Editor** | Edit and publish content |
| **Author** | Create and edit own content |

**Incorrect (no role strategy):**

```
# Bad: Everyone is Admin
- All team members have admin access
- No content approval workflow
- Schema changes by anyone
- No audit trail for compliance

# Bad: Overly permissive custom roles
{
  "name": "Content Editor",
  "permissions": ["*"]  // Everything allowed
}
```

**Correct (granular role configuration):**

```json
// Good: Custom role with specific permissions
{
  "name": "Blog Editor",
  "permissions": {
    "stories": {
      "create": true,
      "update": true,
      "delete": false,
      "publish": true
    },
    "assets": {
      "create": true,
      "update": true,
      "delete": false
    },
    "components": {
      "create": false,
      "update": false,
      "delete": false
    }
  },
  "folder_access": ["blog", "news"],
  "component_access": ["article", "news_post", "author"]
}
```

**Folder-level access restrictions:**

```json
// Good: Restrict access to specific folders
{
  "name": "Regional Editor - DACH",
  "folder_access": {
    "de": { "read": true, "write": true, "publish": true },
    "de-at": { "read": true, "write": true, "publish": true },
    "de-ch": { "read": true, "write": true, "publish": true },
    "en": { "read": true, "write": false, "publish": false },
    "fr": { "read": false, "write": false, "publish": false }
  }
}
```

```typescript
// Good: Check folder access programmatically
interface UserPermissions {
  folders: {
    [folderPath: string]: {
      read: boolean;
      write: boolean;
      publish: boolean;
    };
  };
}

function canEditFolder(
  userPermissions: UserPermissions,
  folderPath: string
): boolean {
  // Check exact match first
  if (userPermissions.folders[folderPath]?.write) {
    return true;
  }

  // Check parent folder permissions
  const pathParts = folderPath.split('/');
  while (pathParts.length > 0) {
    pathParts.pop();
    const parentPath = pathParts.join('/') || '/';
    if (userPermissions.folders[parentPath]?.write) {
      return true;
    }
  }

  return false;
}
```

**Component-level restrictions:**

```json
// Good: Restrict which components users can use
{
  "name": "Marketing Editor",
  "allowed_components": [
    "hero",
    "text_block",
    "image_gallery",
    "cta_button",
    "testimonial"
  ],
  "restricted_components": [
    "code_block",      // Technical components
    "api_integration", // Developer components
    "seo_advanced"     // SEO team only
  ]
}
```

```json
// Good: Component schema with role restrictions
{
  "name": "advanced_seo",
  "display_name": "Advanced SEO Settings",
  "schema": {
    "canonical_url": { "type": "text" },
    "robots_meta": { "type": "text" },
    "structured_data": { "type": "textarea" }
  },
  "role_whitelist": ["admin", "seo_specialist"],
  "is_nestable": false
}
```

**Field-level permissions:**

```json
// Good: Restrict sensitive fields within components
{
  "name": "product",
  "schema": {
    "name": {
      "type": "text",
      "required": true
    },
    "description": {
      "type": "richtext"
    },
    "price": {
      "type": "number",
      "field_permissions": {
        "roles": ["admin", "product_manager"],
        "action": "write"
      }
    },
    "internal_notes": {
      "type": "textarea",
      "field_permissions": {
        "roles": ["admin"],
        "action": "read"
      }
    },
    "api_key": {
      "type": "text",
      "field_permissions": {
        "roles": ["admin"],
        "action": "read"
      }
    }
  }
}
```

**Workflow-based permissions:**

```json
// Good: Different permissions per workflow stage
{
  "workflow": "content_approval",
  "stages": [
    {
      "name": "draft",
      "allowed_roles": ["author", "editor", "admin"],
      "actions": {
        "edit": ["author", "editor", "admin"],
        "submit_for_review": ["author", "editor"],
        "delete": ["admin"]
      }
    },
    {
      "name": "in_review",
      "allowed_roles": ["editor", "admin"],
      "actions": {
        "edit": ["editor", "admin"],
        "approve": ["editor", "admin"],
        "reject": ["editor", "admin"],
        "delete": ["admin"]
      }
    },
    {
      "name": "approved",
      "allowed_roles": ["admin"],
      "actions": {
        "publish": ["admin"],
        "unpublish": ["admin"],
        "revert_to_draft": ["admin"]
      }
    }
  ]
}
```

**SSO and 2FA configuration:**

```typescript
// Good: Enterprise SSO integration check
interface SpaceSettings {
  sso: {
    enabled: boolean;
    provider: 'okta' | 'azure_ad' | 'google' | 'saml';
    enforce_sso: boolean; // Disable password login
    auto_provision: boolean; // Auto-create users
    default_role: string;
  };
  security: {
    two_factor_required: boolean;
    session_timeout_minutes: number;
    ip_whitelist: string[];
  };
}

// Recommended enterprise settings
const enterpriseSettings: SpaceSettings = {
  sso: {
    enabled: true,
    provider: 'okta',
    enforce_sso: true,
    auto_provision: true,
    default_role: 'author'
  },
  security: {
    two_factor_required: true,
    session_timeout_minutes: 480, // 8 hours
    ip_whitelist: ['10.0.0.0/8', '192.168.1.0/24']
  }
};
```

**Audit logging for compliance:**

```typescript
// Good: Track permission-related events
interface AuditEvent {
  timestamp: string;
  user_id: string;
  user_email: string;
  action: 'create' | 'update' | 'delete' | 'publish' | 'permission_change';
  resource_type: 'story' | 'asset' | 'component' | 'user' | 'role';
  resource_id: string;
  changes?: Record<string, { from: any; to: any }>;
  ip_address: string;
}

// Use Management API to fetch activity logs
async function getAuditLog(
  spaceId: string,
  filters: {
    startDate?: string;
    endDate?: string;
    userId?: string;
    action?: string;
  }
) {
  const { data } = await managementApi.get(
    `spaces/${spaceId}/activities`,
    {
      params: {
        created_at_gte: filters.startDate,
        created_at_lte: filters.endDate,
        user_id: filters.userId,
        activity_type: filters.action,
        per_page: 100
      }
    }
  );

  return data.activities;
}
```

**Role assignment patterns:**

```typescript
// Good: Team-based role assignment
interface TeamConfig {
  name: string;
  defaultRole: string;
  folders: string[];
  components: string[];
}

const teams: TeamConfig[] = [
  {
    name: 'Marketing',
    defaultRole: 'editor',
    folders: ['marketing', 'campaigns', 'landing-pages'],
    components: ['hero', 'cta', 'testimonial', 'feature_grid']
  },
  {
    name: 'Product',
    defaultRole: 'editor',
    folders: ['products', 'documentation'],
    components: ['product_card', 'spec_table', 'comparison']
  },
  {
    name: 'Engineering',
    defaultRole: 'author',
    folders: ['docs', 'api-reference', 'changelog'],
    components: ['code_block', 'api_endpoint', 'technical_note']
  }
];

// Provision user based on team
async function provisionTeamMember(
  email: string,
  team: TeamConfig
) {
  await managementApi.post(`spaces/${spaceId}/collaborators`, {
    email,
    role: team.defaultRole,
    space_role_access: {
      folder_access: team.folders,
      component_access: team.components
    }
  });
}
```

**Content approval matrix:**

```typescript
// Good: Define approval requirements by content type
interface ApprovalMatrix {
  [contentType: string]: {
    requiresApproval: boolean;
    approverRoles: string[];
    minApprovers: number;
    escalationTimeout: number; // hours
  };
}

const approvalMatrix: ApprovalMatrix = {
  'legal_page': {
    requiresApproval: true,
    approverRoles: ['legal_team', 'admin'],
    minApprovers: 2,
    escalationTimeout: 48
  },
  'product_page': {
    requiresApproval: true,
    approverRoles: ['product_manager', 'marketing_lead'],
    minApprovers: 1,
    escalationTimeout: 24
  },
  'blog_post': {
    requiresApproval: true,
    approverRoles: ['editor'],
    minApprovers: 1,
    escalationTimeout: 12
  },
  'news_update': {
    requiresApproval: false,
    approverRoles: [],
    minApprovers: 0,
    escalationTimeout: 0
  }
};
```

**Best practices:**

| Practice | Description |
|----------|-------------|
| Least privilege | Grant minimum permissions needed |
| Role hierarchy | Build roles from base permissions up |
| Folder isolation | Separate content by team/region |
| Audit regularly | Review access logs quarterly |
| SSO enforcement | Disable password login for enterprise |
| 2FA requirement | Mandatory for admin roles |
| Offboarding process | Revoke access immediately on departure |

Reference: [User Management](https://www.storyblok.com/docs/guide/in-depth/user-management) | [Roles and Permissions](https://www.storyblok.com/docs/guide/in-depth/roles-permissions) | [SSO Configuration](https://www.storyblok.com/docs/guide/in-depth/sso)
