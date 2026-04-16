# Advanced Builder Patterns

## Custom Builders for Specific Use Cases

### Pattern 1: Builder Inheritance

Build hierarchies of builders for related document types:

```python
class BaseIssueBuilder(JiraDocumentBuilder):
    """Base for all issue templates."""

    def add_standard_header(self, title: str, issue_type: str):
        self.add_heading(title, 1)
        self.add_paragraph(
            self.bold(f"Type: "),
            self.add_text(issue_type)
        )
        return self

class BugBuilder(BaseIssueBuilder):
    """Specialized builder for bug reports."""

    def add_reproduction_steps(self, steps: list[str]):
        self.add_heading("Steps to Reproduce", 2)
        self.add_ordered_list(steps)
        return self

    def add_expected_vs_actual(self, expected: str, actual: str):
        self.add_heading("Expected vs Actual", 2)
        self.add_paragraph(
            self.bold("Expected: "),
            self.add_text(expected)
        )
        self.add_paragraph(
            self.bold("Actual: "),
            self.add_text(actual)
        )
        return self

# Usage
bug = BugBuilder()
bug.add_standard_header("Login fails on Safari", "Bug")
bug.add_reproduction_steps([
    "Open Safari 17",
    "Visit login.example.com",
    "Click 'Sign In with Google'",
    "Approve permissions"
])
bug.add_expected_vs_actual(
    "Redirect to dashboard",
    "Blank page with JS console error"
)

adf = bug.build()
```

### Pattern 2: Composition-Based Builders

Use composition instead of inheritance for flexibility:

```python
class DocumentSection:
    """Reusable document section."""

    def __init__(self, title: str):
        self.title = title
        self.content = []

    def render(self, builder: JiraDocumentBuilder):
        """Render this section to a builder."""
        builder.add_heading(self.title, 2)
        for item in self.content:
            if isinstance(item, str):
                builder.add_paragraph(builder.add_text(item))
            elif isinstance(item, dict):
                builder.add_panel(item['type'], item['content'])
        return builder

class RiskSection(DocumentSection):
    """Pre-configured risk assessment section."""

    def __init__(self):
        super().__init__("Risk Assessment")

    def add_risk(self, level: str, description: str):
        panel_type = "error" if level == "high" else "warning"
        self.content.append({
            'type': panel_type,
            'content': {
                "type": "paragraph",
                "content": [{"type": "text", "text": description}]
            }
        })
        return self

# Usage
doc = JiraDocumentBuilder()
doc.add_heading("Payment System Redesign", 1)

risk_section = RiskSection()
risk_section.add_risk("high", "Financial risk: ACH reversals")
risk_section.add_risk("medium", "Integration complexity")
risk_section.render(doc)

adf = doc.build()
```

### Pattern 3: Template Methods

Create template methods for common document structures:

```python
class TemplateBuilder(JiraDocumentBuilder):
    """Builder with template methods."""

    def add_titled_panel(self, title: str, panel_type: str, content: str):
        """Add a heading followed by a panel."""
        self.add_heading(title, 2)
        self.add_panel(panel_type, {
            "type": "paragraph",
            "content": [self.add_text(content)]
        })
        return self

    def add_kv_section(self, title: str, pairs: dict):
        """Add a section with key-value pairs."""
        self.add_heading(title, 2)
        items = [f"{key}: {value}" for key, value in pairs.items()]
        self.add_bullet_list(items)
        return self

    def add_feature_list(self, title: str, features: list[str]):
        """Add a section with feature checklist."""
        self.add_heading(title, 2)
        items = [f"☐ {f}" for f in features]
        self.add_bullet_list(items)
        return self

# Usage
doc = TemplateBuilder()
doc.add_titled_panel("⚠️ Risks", "warning", "Performance impact on v1 API")
doc.add_kv_section("Specifications", {
    "Language": "Python 3.10+",
    "Framework": "FastAPI",
    "Database": "PostgreSQL 13"
})
doc.add_feature_list("Must-Have Features", [
    "User authentication",
    "Database persistence",
    "API rate limiting"
])

adf = doc.build()
```

## Complex Nested Structures

### Multi-Level Hierarchical Documents

Build deeply nested structures with sections, subsections, and panels:

```python
doc = JiraDocumentBuilder()

# Level 1: Main title
doc.add_heading("🚀 Payment System Redesign", 1)
doc.add_paragraph(
    doc.bold("Priority: "), doc.add_text("P0"),
    doc.add_text(" | "),
    doc.bold("Timeline: "), doc.add_text("Q2 2024")
)

# Level 2: Main sections
doc.add_heading("Problem", 2)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("Current system handles only credit cards; enterprise needs ACH/wire")]
})

doc.add_heading("Solution Approach", 2)
doc.add_bullet_list([
    "Abstract payment gateway interface",
    "Implement ACH driver with bank reconciliation",
    "Add webhook for transaction status"
])

doc.add_heading("Technical Requirements", 2)
doc.add_ordered_list([
    "Design payment abstraction",
    "Implement ACH provider integration",
    "Add transaction state machine",
    "Create reconciliation batch process"
])

# Code example
doc.add_heading("Reference Implementation", 2)
doc.add_code_block("""
class PaymentGateway:
    def process(self, amount, method):
        driver = self._get_driver(method)
        return driver.charge(amount)

    def _get_driver(self, method):
        if method == 'ach':
            return ACHDriver()
        elif method == 'credit':
            return CreditCardDriver()
""", language="python")

# Level 3: Risk subsections
doc.add_heading("Risk Assessment", 2)
doc.add_heading("Financial Risk", 3)
doc.add_panel("error", {
    "type": "paragraph",
    "content": [doc.add_text("ACH payments are slow and reversible; implement hold period")]
})
doc.add_heading("Integration Risk", 3)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("Requires new bank partnership; 2-week setup time")]
})

# Acceptance criteria
doc.add_heading("Acceptance Criteria", 2)
doc.add_ordered_list([
    "ACH charges succeed with test account",
    "Reconciliation matches bank records",
    "All error cases handled",
    "Documentation complete",
    "Load test passes (100+ TPS)"
])

# Dependencies
doc.add_heading("Dependencies", 2)
doc.add_bullet_list([
    "Bank partnership agreement",
    "Infrastructure team support",
    "Security review approval"
])

adf = doc.build()
```

### Combining Multiple Content Types

Mix formatted text, lists, code blocks, and panels:

```python
doc = JiraDocumentBuilder()

# Rich paragraph with mixed formatting
doc.add_heading("Authentication Enhancement", 1)
doc.add_paragraph(
    doc.bold("Status: "),
    doc.add_text("In Progress"),
    doc.add_text(" | "),
    doc.bold("Owner: "),
    doc.link("Sarah Chen", "https://jira.example.com/browse/USER-123"),
    doc.add_text(" | "),
    doc.add_emoji(":rocket:", "🚀"),
    doc.add_text(" Priority: P0")
)

# Nested lists with inline formatting
doc.add_heading("Implementation Plan", 2)
doc.add_ordered_list([
    "Phase 1: Add OAuth2 support (2 weeks)",
    "Phase 2: Migrate existing users (1 week)",
    "Phase 3: Deprecate old auth (1 week)"
])

# Code block with context
doc.add_heading("Key Changes", 2)
doc.add_paragraph(
    doc.add_text("The new "),
    doc.code("OAuth2Handler"),
    doc.add_text(" class replaces "),
    doc.code("LegacyAuth"),
    doc.add_text(":")
)
doc.add_code_block("""
class OAuth2Handler:
    def authenticate(self, token: str) -> User:
        payload = self.verify_token(token)
        return User.get_by_id(payload['user_id'])
""", language="python")

# Panel with rich content
doc.add_heading("Migration Warning", 2)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [
        doc.bold("Breaking Change: "),
        doc.add_text("Legacy auth endpoints will be removed in v3.0")
    ]
})

adf = doc.build()
```

## Builder Best Practices

### 1. Return Self for Chaining

```python
class CustomBuilder:
    def add_something(self) -> "CustomBuilder":
        # ... implementation
        return self  # Allow chaining

# Usage
builder.add_a().add_b().add_c().add_d()
```

### 2. Lazy Content Building

```python
# ❌ Don't require all content upfront
def __init__(self, title, items, criteria):
    pass

# ✅ Build step-by-step
def __init__(self, title):
    self.title = title

def add_items(self, items):
    # ...
    return self

def add_criteria(self, criteria):
    # ...
    return self
```

### 3. Validate Before Building

```python
def build(self) -> dict:
    """Build and validate before returning."""
    if not self.title:
        raise ValueError("Title is required")
    if not self.builder.content:
        raise ValueError("Content is empty")

    return self.builder.build()
```

### 4. Document Builder Structure

```python
class DocumentTemplate:
    """
    Template for standard epic documentation.

    Structure:
    - Header (title, priority, timeline)
    - Problem statement (warning panel)
    - Solution approach (bullet list)
    - Technical requirements (ordered list)
    - Code examples (code blocks)
    - Risk assessment (info/warning panels)
    - Acceptance criteria (ordered list)
    - Dependencies (bullet list)
    """

    def __init__(self, title: str):
        pass
```

## EpicBuilder Implementation Reference

Full implementation of the specialized EpicBuilder:

```python
from jira_tool.formatter import JiraDocumentBuilder

class EpicBuilder:
    """Pre-formatted epic template with consistent structure."""

    def __init__(self, title: str, priority: str = "P1"):
        self.title = title
        self.priority = priority
        self.builder = JiraDocumentBuilder()
        self._add_header()

    def _add_header(self):
        """Add standardized header."""
        self.builder.add_heading(f"🎯 {self.title}", 1)
        self.builder.add_paragraph(
            self.builder.bold("Priority: "),
            self.builder.add_text(self.priority)
        )

    def add_problem_statement(self, statement: str):
        """Add problem section with warning panel."""
        self.builder.add_heading("Problem Statement", 2)
        self.builder.add_panel("warning", {
            "type": "paragraph",
            "content": [self.builder.add_text(statement)]
        })
        return self

    def add_description(self, description: str):
        """Add description section."""
        self.builder.add_heading("Description", 2)
        self.builder.add_paragraph(self.builder.add_text(description))
        return self

    def add_technical_details(self, requirements: list[str],
                            code_example: str = None,
                            code_language: str = "python"):
        """Add technical requirements and optional code."""
        self.builder.add_heading("Technical Details", 2)
        self.builder.add_bullet_list(requirements)

        if code_example:
            self.builder.add_heading("Reference Implementation", 3)
            self.builder.add_code_block(code_example, language=code_language)

        return self

    def add_acceptance_criteria(self, criteria: list[str]):
        """Add acceptance criteria."""
        self.builder.add_heading("Acceptance Criteria", 2)
        self.builder.add_ordered_list(criteria)
        return self

    def build(self):
        """Return final ADF document."""
        return self.builder.build()
```

## BugReportBuilder Implementation Reference

Full implementation of a specialized bug report builder:

```python
from jira_tool.formatter import JiraDocumentBuilder

class BugReportBuilder(JiraDocumentBuilder):
    """Specialized builder for structured bug reports."""

    def __init__(self, title: str, severity: str = "Medium"):
        super().__init__()
        self.title = title
        self.severity = severity
        self.add_header()

    def add_header(self):
        self.add_heading(f"🐛 {self.title}", 1)
        self.add_paragraph(
            self.bold("Severity: "),
            self.add_text(self.severity)
        )
        return self

    def add_environment(self, browser: str, os: str):
        self.add_heading("Environment", 2)
        self.add_bullet_list([
            f"Browser: {browser}",
            f"OS: {os}"
        ])
        return self

    def add_reproduction_steps(self, steps: list[str]):
        self.add_heading("Steps to Reproduce", 2)
        self.add_ordered_list(steps)
        return self

    def add_expected_result(self, result: str):
        self.add_heading("Expected Result", 2)
        self.add_panel("success", {
            "type": "paragraph",
            "content": [self.add_text(result)]
        })
        return self

    def add_actual_result(self, result: str):
        self.add_heading("Actual Result", 2)
        self.add_panel("error", {
            "type": "paragraph",
            "content": [self.add_text(result)]
        })
        return self

    def add_error_log(self, error: str):
        self.add_heading("Error Log", 2)
        self.add_code_block(error, language="text")
        return self
```

## Testing Builders

### Unit Testing Builder Output

```python
import pytest
from jira_tool.formatter import EpicBuilder

def test_epic_builder_structure():
    """Verify EpicBuilder generates valid ADF."""
    epic = EpicBuilder("Test Epic", "P0")
    epic.add_problem_statement("Test problem")
    epic.add_acceptance_criteria(["Criterion 1", "Criterion 2"])

    adf = epic.build()

    assert adf['version'] == 1
    assert adf['type'] == 'doc'
    assert len(adf['content']) > 0

    # Find heading
    headings = [c for c in adf['content'] if c['type'] == 'heading']
    assert any("Test Epic" in str(h) for h in headings)

def test_builder_chaining():
    """Verify method chaining works."""
    epic = (EpicBuilder("Chain Test", "P1")
            .add_problem_statement("Problem")
            .add_acceptance_criteria(["Criterion"]))

    adf = epic.build()
    assert adf is not None
```

### Integration Testing with Jira

```python
import requests
from jira_tool.formatter import EpicBuilder

def test_submit_to_jira():
    """Submit built document to Jira (requires test instance)."""
    epic = EpicBuilder("Integration Test Epic", "P2")
    epic.add_problem_statement("Test problem statement")
    epic.add_acceptance_criteria(["Must work", "Must validate"])

    adf = epic.build()

    # Submit to Jira
    response = requests.post(
        f"{JIRA_BASE_URL}/rest/api/3/issue",
        auth=(JIRA_USERNAME, JIRA_API_TOKEN),
        json={
            "fields": {
                "project": {"key": "TEST"},
                "issuetype": {"name": "Epic"},
                "summary": "Integration Test",
                "description": adf
            }
        }
    )

    assert response.status_code == 201
    issue_key = response.json()['key']
    print(f"Created issue: {issue_key}")
```

## Performance Considerations

### Large Documents

For documents with 100+ content blocks, consider:

1. **Batch Building**: Build sections separately, then combine
2. **Lazy Evaluation**: Don't build ADF until `build()` is called
3. **Memory**: Clear temporary data after building

```python
class OptimizedBuilder(JiraDocumentBuilder):
    def build(self):
        """Build and clear internal state."""
        adf = super().build()
        self.content.clear()  # Free memory
        return adf
```

### Builder Reuse

```python
# ❌ Don't reuse builders
builder = JiraDocumentBuilder()
doc1 = builder.add_heading("Doc 1", 1).build()
doc2 = builder.add_heading("Doc 2", 1).build()  # Contains Doc 1 content!

# ✅ Create new builder for each document
builder1 = JiraDocumentBuilder()
doc1 = builder1.add_heading("Doc 1", 1).build()

builder2 = JiraDocumentBuilder()
doc2 = builder2.add_heading("Doc 2", 1).build()
```
