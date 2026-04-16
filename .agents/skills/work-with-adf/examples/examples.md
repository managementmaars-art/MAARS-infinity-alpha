# ADF Examples and Use Cases

## Table of Contents
1. Simple Examples
2. Real-World Use Cases
3. Error Handling Patterns
4. Advanced Patterns

---

## Simple Examples

### Minimal Document

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()
adf = doc.build()

# Output:
# {
#   "version": 1,
#   "type": "doc",
#   "content": []
# }
```

### Single Paragraph

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()
doc.add_paragraph(doc.add_text("This is a simple paragraph."))
adf = doc.build()
```

### Heading and Paragraph

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()
doc.add_heading("Main Title", level=1)
doc.add_heading("Subtitle", level=2)
doc.add_paragraph(doc.add_text("Content goes here."))
adf = doc.build()
```

---

## Real-World Use Cases

### Use Case 1: Create a Bug Report Epic

```python
from jira_tool.formatter import EpicBuilder

def create_bug_epic(
    title: str,
    severity: str,
    reproduction_steps: list[str],
    expected: str,
    actual: str,
    affected_services: list[str]
) -> dict:
    """Create a standardized bug report epic."""

    epic = EpicBuilder(
        title=title,
        priority="P0" if severity == "Critical" else "P1",
        services=", ".join(affected_services),
    )

    epic.add_problem_statement(
        f"Bug reported with severity level: {severity}"
    )

    # Reproduction steps
    epic.add_heading("Reproduction Steps", 2)
    epic.add_ordered_list(reproduction_steps)

    # Expected vs Actual
    compare_content = {
        "type": "paragraph",
        "content": [
            epic.bold("Expected: "),
            epic.add_text(expected),
            epic.add_text("\n"),
            epic.bold("Actual: "),
            epic.add_text(actual)
        ]
    }
    epic.add_panel("error", compare_content)

    return epic.build()

# Usage
adf = create_bug_epic(
    title="Login Page Crashes on Mobile",
    severity="Critical",
    reproduction_steps=[
        "Navigate to login page on iPhone",
        "Enter credentials",
        "Tap login button",
        "Page crashes with white screen"
    ],
    expected="User is logged in and redirected to dashboard",
    actual="Application crashes with memory error",
    affected_services=["Auth Service", "Frontend"]
)
```

### Use Case 2: Create a Feature Request with Mockup

```python
from jira_tool.formatter import EpicBuilder

def create_feature_epic(
    title: str,
    use_case: str,
    technical_approach: str,
    implementation_steps: list[str],
    testing_strategy: str
) -> dict:
    """Create a feature request epic."""

    epic = EpicBuilder(
        title=title,
        priority="P1",
        dependencies="Feature Flag System"
    )

    # Use Case
    epic.add_heading("Use Case", 2)
    epic.add_paragraph(epic.add_text(use_case))

    # Technical Approach
    epic.add_heading("Technical Approach", 2)
    epic.add_panel("info",
        {"type": "paragraph", "content": [epic.add_text(technical_approach)]}
    )

    # Implementation Steps
    epic.add_heading("Implementation Steps", 2)
    epic.add_ordered_list(implementation_steps)

    # Testing Strategy
    epic.add_heading("Testing Strategy", 2)
    epic.add_panel("success",
        {"type": "paragraph", "content": [epic.add_text(testing_strategy)]}
    )

    return epic.build()

# Usage
adf = create_feature_epic(
    title="Dark Mode Support",
    use_case="Users want to use the application in low-light environments",
    technical_approach="Use CSS variables for theme switching with LocalStorage persistence",
    implementation_steps=[
        "Create theme CSS variables",
        "Build theme switcher component",
        "Add LocalStorage persistence",
        "Apply theme to all pages"
    ],
    testing_strategy="Test on multiple browsers and devices, verify theme persistence"
)
```

### Use Case 3: Create a Task with Code Examples

```python
from jira_tool.formatter import IssueBuilder

def create_backend_task(
    title: str,
    component: str,
    endpoint_path: str,
    parameters: dict,
    response_example: str,
    acceptance_criteria: list[str]
) -> dict:
    """Create a backend task with API documentation."""

    issue = IssueBuilder(
        title=title,
        component=component,
        story_points=8
    )

    # API Documentation
    issue.add_heading("API Specification", 2)

    api_info = {
        "type": "paragraph",
        "content": [
            issue.bold("Endpoint: "),
            issue.code(f"POST /api{endpoint_path}"),
        ]
    }
    issue.add_panel("info", api_info)

    # Parameters
    issue.add_heading("Request Parameters", 2)
    params_list = [f"{key}: {value}" for key, value in parameters.items()]
    issue.add_bullet_list(params_list)

    # Response Example
    issue.add_heading("Response Example", 2)
    issue.add_code_block(response_example, language="json")

    # Acceptance Criteria
    issue.add_acceptance_criteria(acceptance_criteria)

    return issue.build()

# Usage
adf = create_backend_task(
    title="Implement User Profile Endpoint",
    component="API",
    endpoint_path="/users/{userId}/profile",
    parameters={
        "userId": "string - User ID",
        "include": "string - Comma-separated fields to include"
    },
    response_example="""{
  "id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "avatar_url": "https://example.com/avatar.jpg",
  "created_at": "2025-01-01T00:00:00Z"
}""",
    acceptance_criteria=[
        "Endpoint returns user profile data",
        "Handles invalid user IDs gracefully",
        "Supports field filtering via include parameter",
        "All tests pass with >90% coverage"
    ]
)
```

### Use Case 4: Create a Meeting Notes Document

```python
from jira_tool.formatter import JiraDocumentBuilder

def create_meeting_notes(
    title: str,
    attendees: list[str],
    agenda_items: list[tuple[str, str]],
    action_items: list[tuple[str, str]]  # (action, owner)
) -> dict:
    """Create meeting notes document."""

    doc = JiraDocumentBuilder()

    doc.add_heading(f"📅 {title}", 1)

    # Attendees
    doc.add_heading("Attendees", 2)
    doc.add_bullet_list(attendees)

    doc.add_rule()

    # Agenda
    doc.add_heading("Agenda", 2)
    for item, notes in agenda_items:
        doc.add_heading(item, 3)
        doc.add_paragraph(doc.add_text(notes))

    doc.add_rule()

    # Action Items
    doc.add_heading("Action Items", 2)
    action_content = []
    for action, owner in action_items:
        action_content.append({
            "type": "listItem",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        doc.bold(f"{owner}: "),
                        doc.add_text(action)
                    ]
                }
            ]
        })

    doc.content.append({
        "type": "bulletList",
        "content": action_content
    })

    return doc.build()

# Usage
adf = create_meeting_notes(
    title="Sprint Planning - Week 45",
    attendees=["Alice (PM)", "Bob (Lead)", "Carol (Dev)", "Dave (QA)"],
    agenda_items=[
        ("Sprint Goals", "Implement OAuth and dark mode"),
        ("Risks", "Dependency on third-party library"),
        ("Timeline", "Expected completion by end of sprint")
    ],
    action_items=[
        ("Finalize OAuth requirements", "Alice"),
        ("Set up feature flag", "Bob"),
        ("Create test plan for dark mode", "Dave")
    ]
)
```

### Use Case 5: Create a Release Notes Document

```python
from jira_tool.formatter import JiraDocumentBuilder

def create_release_notes(
    version: str,
    release_date: str,
    features: list[str],
    improvements: list[str],
    bug_fixes: list[str],
    breaking_changes: list[str] = None,
    upgrade_notes: str = None
) -> dict:
    """Create release notes document."""

    doc = JiraDocumentBuilder()

    doc.add_heading(f"Release {version}", 1)

    date_content = {
        "type": "paragraph",
        "content": [
            doc.bold("Release Date: "),
            doc.add_text(release_date)
        ]
    }
    doc.add_panel("info", date_content)

    # Features
    if features:
        doc.add_heading("✨ New Features", 2)
        doc.add_bullet_list(features)

    # Improvements
    if improvements:
        doc.add_heading("⚡ Improvements", 2)
        doc.add_bullet_list(improvements)

    # Bug Fixes
    if bug_fixes:
        doc.add_heading("🐛 Bug Fixes", 2)
        doc.add_bullet_list(bug_fixes)

    # Breaking Changes
    if breaking_changes:
        doc.add_heading("⚠️ Breaking Changes", 2)
        doc.add_panel("warning",
            {"type": "bulletList", "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [doc.add_text(change)]}
                ]}
                for change in breaking_changes
            ]}
        )

    # Upgrade Notes
    if upgrade_notes:
        doc.add_heading("📝 Upgrade Notes", 2)
        doc.add_panel("success",
            {"type": "paragraph", "content": [doc.add_text(upgrade_notes)]}
        )

    return doc.build()

# Usage
adf = create_release_notes(
    version="2.5.0",
    release_date="2025-11-03",
    features=[
        "Dark mode support",
        "OAuth 2.0 integration",
        "Real-time collaboration"
    ],
    improvements=[
        "20% faster page load time",
        "Improved mobile responsiveness",
        "Better error messages"
    ],
    bug_fixes=[
        "Fixed login page crash on iOS",
        "Fixed memory leak in real-time sync"
    ],
    breaking_changes=[
        "Removed deprecated /api/v1/users endpoint",
        "OAuth redirect_uri now required in requests"
    ],
    upgrade_notes="See migration guide at docs/upgrade-v2.5.md"
)
```

---

## Error Handling Patterns

### Pattern 1: Validate Before Creating

```python
from jira_tool.formatter import JiraDocumentBuilder

def safe_add_content(doc: JiraDocumentBuilder, content: str) -> JiraDocumentBuilder:
    """Add content with validation."""
    if not content or not content.strip():
        return doc  # Skip empty content

    doc.add_paragraph(doc.add_text(content))
    return doc

# Usage
doc = JiraDocumentBuilder()
safe_add_content(doc, "")  # Skipped
safe_add_content(doc, "Valid content")  # Added
adf = doc.build()
```

### Pattern 2: Handle None Values

```python
from jira_tool.formatter import IssueBuilder

def create_issue_safe(
    title: str,
    component: str,
    story_points: int = None,
    epic_key: str = None,
    description: str = None
) -> dict:
    """Create issue with optional fields."""

    issue = IssueBuilder(
        title=title,
        component=component,
        story_points=story_points,
        epic_key=epic_key
    )

    if description:
        issue.add_description(description)

    return issue.build()

# Usage - some fields optional
adf = create_issue_safe(
    title="Fix typo",
    component="Docs",
    description="Fix spelling in README"
)
```

### Pattern 3: Conditional Sections

```python
from jira_tool.formatter import EpicBuilder

def create_epic_with_options(
    title: str,
    priority: str,
    include_technical: bool = True,
    include_timeline: bool = False,
    custom_sections: dict = None
) -> dict:
    """Create epic with optional sections."""

    epic = EpicBuilder(title=title, priority=priority)

    if include_technical:
        epic.add_technical_details(
            requirements=["Requirement 1", "Requirement 2"]
        )

    if include_timeline:
        epic.add_heading("Timeline", 2)
        epic.add_bullet_list(["Phase 1: Research", "Phase 2: Implementation"])

    if custom_sections:
        for section_title, section_content in custom_sections.items():
            epic.add_heading(section_title, 2)
            epic.add_paragraph(epic.add_text(section_content))

    return epic.build()

# Usage
adf = create_epic_with_options(
    title="My Epic",
    priority="P1",
    include_technical=True,
    include_timeline=True,
    custom_sections={
        "Business Impact": "This will improve user retention by 10%"
    }
)
```

---

## Advanced Patterns

### Pattern 1: Nested Lists

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()

# Top-level list
doc.add_bullet_list([
    "First item",
    "Second item"
])

# Add nested content via raw ADF
nested_list = {
    "type": "bulletList",
    "content": [
        {
            "type": "listItem",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Nested item 1"}]}
            ]
        }
    ]
}

doc.content.append(nested_list)
adf = doc.build()
```

### Pattern 2: Side-by-Side Content via Table

```python
from jira_tool.formatter import JiraDocumentBuilder

def create_comparison_table(items: list[tuple[str, str]]) -> dict:
    """Create a 2-column comparison table."""

    doc = JiraDocumentBuilder()

    rows = []
    for label, value in items:
        rows.append({
            "type": "tableRow",
            "content": [
                {
                    "type": "tableCell",
                    "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": label}]}
                    ]
                },
                {
                    "type": "tableCell",
                    "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": value}]}
                    ]
                }
            ]
        })

    table = {
        "type": "table",
        "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
        "content": rows
    }

    doc.content.append(table)
    return doc.build()

# Usage
comparison = create_comparison_table([
    ("Feature", "Status"),
    ("OAuth", "Complete"),
    ("Dark Mode", "In Progress"),
    ("Analytics", "Planned")
])
```

### Pattern 3: Multi-Format Content

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()

# Combine different node types
doc.add_heading("Report Summary", 1)

summary_content = {
    "type": "paragraph",
    "content": [
        doc.bold("Total Issues: "),
        doc.add_text("42 | "),
        doc.bold("Open: "),
        doc.add_text("15 | "),
        doc.bold("Closed: "),
        doc.add_text("27")
    ]
}
doc.add_panel("info", summary_content)

doc.add_heading("Top Issues", 2)
doc.add_ordered_list([
    "Critical bug in auth system",
    "Performance degradation on homepage",
    "Mobile layout issues"
])

doc.add_heading("Code Quality Metrics", 2)
doc.add_code_block(
    "Coverage: 85%\nComplexity: 3.2\nMaintainability: 92",
    language="text"
)

adf = doc.build()
```

### Pattern 4: Dynamic Table Generation

```python
from jira_tool.formatter import JiraDocumentBuilder

def create_data_table(headers: list[str], rows: list[list[str]]) -> dict:
    """Create a dynamic table from headers and rows."""

    doc = JiraDocumentBuilder()

    # Header row
    header_cells = [
        {
            "type": "tableHeader",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": h}]}
            ]
        }
        for h in headers
    ]

    header_row = {
        "type": "tableRow",
        "content": header_cells
    }

    # Data rows
    data_rows = []
    for row in rows:
        cells = [
            {
                "type": "tableCell",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": cell}]}
                ]
            }
            for cell in row
        ]
        data_rows.append({
            "type": "tableRow",
            "content": cells
        })

    table = {
        "type": "table",
        "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
        "content": [header_row] + data_rows
    }

    doc.content.append(table)
    return doc.build()

# Usage
adf = create_data_table(
    headers=["Name", "Status", "Priority"],
    rows=[
        ["OAuth Integration", "In Progress", "High"],
        ["Dark Mode", "Planned", "Medium"],
        ["Analytics", "Not Started", "Low"]
    ]
)
```

---

## New Node Type Examples

### Example 12: Status Badges

Status badges provide visual indicators for ticket or task status.

```python
def create_ticket_with_status():
    """Create a ticket description with status badges."""
    doc = {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": "API Integration Task"}]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Current Status: "},
                    {
                        "type": "status",
                        "attrs": {
                            "text": "In Progress",
                            "color": "blue",
                            "localId": "status-1"
                        }
                    }
                ]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Priority: "},
                    {
                        "type": "status",
                        "attrs": {
                            "text": "High",
                            "color": "red",
                            "localId": "status-2"
                        }
                    }
                ]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Review Status: "},
                    {
                        "type": "status",
                        "attrs": {
                            "text": "Approved",
                            "color": "green",
                            "localId": "status-3"
                        }
                    }
                ]
            }
        ]
    }
    return doc

# Status color options: neutral, purple, blue, red, yellow, green
```

### Example 13: Task Lists (Todo Lists)

Task lists allow creating interactive checkboxes in Jira.

```python
def create_implementation_checklist():
    """Create a ticket with task list."""
    doc = {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Implementation Checklist"}]
            },
            {
                "type": "taskList",
                "attrs": {"localId": "task-list-1"},
                "content": [
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-1", "state": "DONE"},
                        "content": [
                            {"type": "text", "text": "Set up database schema"}
                        ]
                    },
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-2", "state": "DONE"},
                        "content": [
                            {"type": "text", "text": "Create API endpoints"}
                        ]
                    },
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-3", "state": "TODO"},
                        "content": [
                            {"type": "text", "text": "Write unit tests"}
                        ]
                    },
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-4", "state": "TODO"},
                        "content": [
                            {"type": "text", "text": "Deploy to staging"}
                        ]
                    }
                ]
            }
        ]
    }
    return doc

# Task states: TODO, DONE
```

### Example 14: Blockquotes

Blockquotes are useful for highlighting important information or quotes.

```python
def create_requirement_with_quote():
    """Create a requirement document with blockquote."""
    from jira_tool.formatter import JiraDocumentBuilder

    doc = JiraDocumentBuilder()

    doc.add_heading("Product Requirements", 1)

    doc.add_paragraph(
        doc.add_text("The product manager stated:")
    )

    # Add blockquote using raw ADF
    blockquote = {
        "type": "blockquote",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "We need to support OAuth 2.0 authentication with at least 3 providers (Google, GitHub, Microsoft) by Q2. This is critical for enterprise adoption.",
                        "marks": [{"type": "em"}]
                    }
                ]
            }
        ]
    }
    doc.content.append(blockquote)

    doc.add_heading("Implementation Notes", 2)
    doc.add_paragraph(
        doc.add_text("Based on this requirement, we will prioritize...")
    )

    return doc.build()
```

### Example 15: Expandable Sections

Expandable sections help organize long content by allowing users to collapse details.

```python
def create_troubleshooting_guide():
    """Create a guide with expandable sections for each issue."""
    doc = {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": "Troubleshooting Guide"}]
            },
            {
                "type": "expand",
                "attrs": {"title": "🔴 Error: Connection Timeout"},
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Symptoms"}]
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Requests hang for 30+ seconds"}]
                                    }
                                ]
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Connection timeout errors in logs"}]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Solution"}]
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "python"},
                        "content": [
                            {"type": "text", "text": "# Increase timeout in config\nCONNECTION_TIMEOUT = 60"}
                        ]
                    }
                ]
            },
            {
                "type": "expand",
                "attrs": {"title": "🟡 Warning: High Memory Usage"},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Check for memory leaks in data processing..."}]
                    }
                ]
            },
            {
                "type": "expand",
                "attrs": {"title": "🟢 Info: Performance Optimization"},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Enable caching to improve response times..."}]
                    }
                ]
            }
        ]
    }
    return doc
```

### Example 16: Combining Status, Tasks, and Panels

A comprehensive example showing multiple new node types together.

```python
def create_sprint_summary():
    """Create a sprint summary with status badges, tasks, and panels."""
    doc = {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "heading",
                "attrs": {"level": 1},
                "content": [{"type": "text", "text": "Sprint 23 Summary"}]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Sprint Status: "},
                    {
                        "type": "status",
                        "attrs": {"text": "Active", "color": "blue", "localId": "sprint-status"}
                    },
                    {"type": "text", "text": " | Velocity: "},
                    {
                        "type": "status",
                        "attrs": {"text": "On Track", "color": "green", "localId": "velocity"}
                    }
                ]
            },
            {
                "type": "panel",
                "attrs": {"panelType": "info"},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Team completed 45 story points out of 50 planned.", "marks": [{"type": "strong"}]}
                        ]
                    }
                ]
            },
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Completed Work"}]
            },
            {
                "type": "taskList",
                "attrs": {"localId": "completed-tasks"},
                "content": [
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-c1", "state": "DONE"},
                        "content": [
                            {"type": "text", "text": "User authentication with OAuth (8 points)"}
                        ]
                    },
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-c2", "state": "DONE"},
                        "content": [
                            {"type": "text", "text": "API endpoint for user profiles (5 points)"}
                        ]
                    },
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-c3", "state": "DONE"},
                        "content": [
                            {"type": "text", "text": "Database migration for new schema (3 points)"}
                        ]
                    }
                ]
            },
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Blockers"}]
            },
            {
                "type": "panel",
                "attrs": {"panelType": "warning"},
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "status",
                                "attrs": {"text": "BLOCKED", "color": "red", "localId": "blocker-1"}
                            },
                            {"type": "text", "text": " Third-party API access pending (waiting on external team)"}
                        ]
                    }
                ]
            },
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Next Sprint Goals"}]
            },
            {
                "type": "taskList",
                "attrs": {"localId": "next-sprint"},
                "content": [
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-n1", "state": "TODO"},
                        "content": [
                            {"type": "text", "text": "Implement password reset flow"}
                        ]
                    },
                    {
                        "type": "taskItem",
                        "attrs": {"localId": "task-n2", "state": "TODO"},
                        "content": [
                            {"type": "text", "text": "Add two-factor authentication"}
                        ]
                    }
                ]
            }
        ]
    }
    return doc
```

---

## Usage Tips for New Node Types

### Status Badges
- Use consistent colors across your organization (e.g., blue = in progress, green = done)
- Add meaningful localIds for tracking
- Combine with text for context

### Task Lists
- Use for checklists, acceptance criteria, or implementation steps
- Update state to DONE as work progresses
- Nest tasks by using multiple task lists

### Blockquotes
- Highlight requirements, quotes from stakeholders, or important passages
- Use with italic marks for emphasis
- Keep quotes concise for readability

### Expandable Sections
- Organize long troubleshooting guides, FAQs, or detailed technical specs
- Use descriptive titles with emojis for visual scanning
- Nest multiple content types inside (headings, code, lists, panels)

### Best Practices
1. **Combine node types** for richer documents (status + panels, tasks + expand)
2. **Use localIds consistently** for tracking and updates
3. **Test ADF structure** with the validation script before submitting
4. **Keep accessibility in mind** - screen readers should navigate cleanly
