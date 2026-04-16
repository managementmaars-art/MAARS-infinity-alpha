# Epic Builder Examples

## Example 1: Database Migration Epic

Create a structured epic for a PostgreSQL migration:

```python
from jira_tool.formatter import EpicBuilder

epic = EpicBuilder("Migrate to PostgreSQL 15", "P1")
epic.add_problem_statement(
    "Current MySQL 5.7 is EOL. Must upgrade for security patches and performance."
)
epic.add_description(
    "Migrate data, update connection pools, test thoroughly, then cutover to PostgreSQL 15."
)
epic.add_technical_details(
    requirements=[
        "Schema migration preserves all data",
        "Zero downtime migration",
        "Rollback plan ready",
        "Performance benchmarking complete"
    ],
    code_example="""
    -- Migration strategy
    1. Create PostgreSQL schema
    2. Use logical replication for sync
    3. Test with production data copy
    4. Cutover during maintenance window
    5. Verify integrity
    """,
    code_language="sql"
)
epic.add_acceptance_criteria([
    "Data migrated with zero loss",
    "Query performance >= MySQL baseline",
    "All tests pass",
    "Rollback tested and documented",
    "Production data verified"
])

adf = epic.build()
```

## Example 2: Two-Factor Authentication Feature

Complex feature request with use cases, design, and risk assessment:

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()

# Overview
doc.add_heading("Add Two-Factor Authentication", 1)
doc.add_paragraph(
    doc.bold("User Impact: "),
    doc.add_text("Users can secure accounts with TOTP/SMS")
)

# Use cases
doc.add_heading("Use Cases", 2)
doc.add_ordered_list([
    "User enables 2FA with TOTP app (Authy/Google Authenticator)",
    "User enables 2FA with SMS verification code",
    "User signs in with password + 2FA code",
    "User recovers account with backup codes"
])

# Design
doc.add_heading("Technical Design", 2)

doc.add_heading("Components", 3)
doc.add_bullet_list([
    "TOTP generator (time-based one-time password)",
    "SMS gateway integration (Twilio)",
    "Recovery code generation",
    "Session validation with 2FA"
])

doc.add_heading("Database Changes", 3)
doc.add_code_block("""
ALTER TABLE users ADD COLUMN totp_secret VARCHAR(32);
ALTER TABLE users ADD COLUMN totp_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN sms_number VARCHAR(20);

CREATE TABLE recovery_codes (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users,
    code VARCHAR(12) UNIQUE,
    used_at TIMESTAMP
);
""", language="sql")

# Acceptance criteria
doc.add_heading("Acceptance Criteria", 2)
doc.add_ordered_list([
    "User can enable TOTP via settings",
    "QR code generated for authenticator apps",
    "Recovery codes downloaded or emailed",
    "Login validates TOTP token",
    "SMS 2FA available as alternative",
    "Backup codes work for account recovery",
    "All tests pass (unit + integration)"
])

# Risks
doc.add_heading("Risks & Mitigation", 2)

doc.add_heading("Risk: Lost 2FA Device", 3)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("User can't access account. Mitigation: Backup codes + email recovery")]
})

doc.add_heading("Risk: SMS Spoofing", 3)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("SMS codes intercepted. Mitigation: Prefer TOTP, SMS as fallback only")]
})

adf = doc.build()
```

## Example 3: Bug Report with Custom Builder

Use a specialized builder for consistent bug reporting:

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

# Usage
bug = BugReportBuilder("Login button unresponsive on mobile", "Critical")
bug.add_environment("Safari 17", "iOS 17.1")
bug.add_reproduction_steps([
    "Open app on iPhone 14",
    "Tap login button",
    "Wait 3 seconds"
])
bug.add_expected_result("Login form appears immediately")
bug.add_actual_result("Button freezes, requires page refresh")
bug.add_error_log("""
TypeError: Cannot read property 'click' of null
    at Object.<anonymous> (app.js:234:15)
    at Module._load (internal/modules/loader.js:580:5)
""")

adf = bug.build()
```

## Example 4: Authentication System Epic

Complete epic with problem statement, approach, and technical details:

```python
from jira_tool.formatter import EpicBuilder

# Create epic with builder
epic = EpicBuilder("Authentication Overhaul", "P0")
epic.add_problem_statement("Current auth is vulnerable to timing attacks")
epic.add_description("Implement OAuth2 with PKCE and secure session management")
epic.add_technical_details(
    requirements=[
        "PKCE flow support",
        "Session token encryption",
        "Rate limiting"
    ],
    code_example="""
    # OAuth2 flow
    token = oauth_client.get_token(code, pkce_verifier)
    session.set_secure_cookie(token)
    """,
    code_language="python"
)
epic.add_acceptance_criteria([
    "All authentication tests pass",
    "Security audit complete",
    "Rate limiting works per RFC 6749"
])

# Get ADF for Jira API
adf = epic.build()
```

## Example 5: Method Chaining

Build documents step-by-step with fluent API:

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()
doc.add_heading("Epic: Authentication System", 1)
doc.add_heading("Problem", 2)
doc.add_panel("warning",
    {"type": "paragraph", "content": [
        doc.add_text("Current authentication has security vulnerabilities")
    ]}
)
doc.add_heading("Approach", 2)
doc.add_bullet_list([
    "Implement OAuth2 with PKCE",
    "Use session token encryption",
    "Add rate limiting"
])
doc.add_heading("Acceptance Criteria", 2)
doc.add_ordered_list([
    "All tests pass",
    "Security audit complete",
    "Rate limiting implemented"
])

adf = doc.build()
```

## Example 6: Complex Nested Structure

Payment system redesign with multi-level sections:

```python
from jira_tool.formatter import JiraDocumentBuilder

doc = JiraDocumentBuilder()

# Header
doc.add_heading("🚀 Payment System Redesign", 1)
doc.add_paragraph(
    doc.bold("Priority: "), doc.add_text("P0"),
    doc.add_text(" | "),
    doc.bold("Timeline: "), doc.add_text("Q2 2024")
)

# Problem section
doc.add_heading("Problem", 2)
doc.add_panel("warning", {
    "type": "paragraph",
    "content": [doc.add_text("Current system handles only credit cards; enterprise needs ACH/wire")]
})

# Solution approach
doc.add_heading("Solution Approach", 2)
doc.add_bullet_list([
    "Abstract payment gateway interface",
    "Implement ACH driver with bank reconciliation",
    "Add webhook for transaction status"
])

# Technical requirements
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

# Risk assessment with subsections
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
