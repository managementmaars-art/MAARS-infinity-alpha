# Example: Implementation Plan Workflow

## Scenario

User asks: "Plan implementation of user authentication"

## Workflow Steps

### 1. Create Plan

```bash
python /path/to/scripts/create_implementation_plan.py \
  --feature "User Authentication" \
  --overview "Add OAuth2 and JWT-based authentication system" \
  --steps "Research OAuth2 providers" "Add authentication library" "Create login flow" "Add JWT middleware" "Write integration tests"
```

### 2. Add Testing Strategy

Edit the IMPLEMENTATION_PLAN.md to add:
- Unit tests for auth middleware
- Integration tests for login flow
- End-to-end tests for complete auth workflow
- Security testing checklist

### 3. Document Risks

Add to Risks section:
- **Risk:** Token expiration handling
  - **Mitigation:** Implement refresh token flow
- **Risk:** OAuth provider downtime
  - **Mitigation:** Add fallback authentication method
- **Risk:** Session hijacking
  - **Mitigation:** Implement CSRF protection

### 4. Track Progress

Update task table as work progresses:
- Mark tasks as "In Progress" or "Complete"
- Update overall progress percentage
- Add notes in Session Log section

### 5. Use Plan to Guide Implementation

Follow the plan step by step:
- Review prerequisites before starting
- Work through tasks in order
- Update status after each task
- Add blockers if encountered
- Document technical decisions in Technical Notes

## Expected Output

**File:** `.claude/artifacts/YYYY-MM-DD/plans/user-authentication/IMPLEMENTATION_PLAN.md`

**Structure:**
- Feature overview
- Prerequisites checklist
- Task table with phases and agents
- Progress tracking (percentage complete)
- Technical notes (architecture, dependencies, risks)
- Blockers table
- Related artifacts (ADRs, research)
- Session log

**Usage:**
- Reference during implementation
- Track progress in real-time
- Document decisions as they're made
- Update with lessons learned
