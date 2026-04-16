# Architecture Decision Record Template

Use this template to document architectural decisions. Store ADRs in a `docs/adr/` directory in the project root, numbered sequentially (e.g., `001-use-postgresql.md`).

---

## ADR-NNN: [Short Title]

**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-NNN]

**Date:** YYYY-MM-DD

**Deciders:** [List of people involved in the decision]

---

### Context

Describe the situation that requires a decision. Include:
- What is the problem or opportunity?
- What are the constraints (technical, business, timeline)?
- What forces are at play (team skills, existing infrastructure, dependencies)?

Example:
> The application needs to store user-uploaded files. Currently files are stored on the local filesystem, which does not scale across multiple application instances. We need a shared storage solution that supports the expected growth from 1,000 to 100,000 users within the next year.

---

### Decision

State the decision clearly in one sentence, then elaborate on the details.

Example:
> We will use Amazon S3 for file storage, accessed via the `aioboto3` library for async operations.

Details:
- Files will be organized by `user_id/year/month/filename`
- Access will be via presigned URLs with 1-hour expiration
- Maximum file size: 50MB (enforced at upload)
- Allowed MIME types: images (JPEG, PNG, WebP), documents (PDF)

---

### Options Considered

#### Option 1: [Name]
- **Description:** Brief technical description
- **Pros:** List advantages
- **Cons:** List disadvantages
- **Estimated effort:** [trivial / small / medium / large]

#### Option 2: [Name]
- **Description:** Brief technical description
- **Pros:** List advantages
- **Cons:** List disadvantages
- **Estimated effort:** [trivial / small / medium / large]

#### Option 3: [Name] (if applicable)
- **Description:** Brief technical description
- **Pros:** List advantages
- **Cons:** List disadvantages
- **Estimated effort:** [trivial / small / medium / large]

---

### Evaluation Criteria

| Criterion | Weight | Option 1 | Option 2 | Option 3 |
|-----------|--------|----------|----------|----------|
| Maintainability | High | | | |
| Testability | High | | | |
| Performance | Medium | | | |
| Team familiarity | Medium | | | |
| Operational cost | Low | | | |

---

### Consequences

#### Positive
- List expected benefits of this decision

#### Negative
- List expected drawbacks or trade-offs

#### Risks
- List risks and their mitigations

---

### Reversibility

**Is this a one-way or two-way door?**

- **One-way door:** Difficult or expensive to reverse (e.g., database engine change, programming language switch). Requires careful consideration.
- **Two-way door:** Easy to reverse if it doesn't work out (e.g., library choice, caching strategy). Prefer fast execution over extensive analysis.

---

### Follow-Up Actions

- [ ] Action 1: [Description] — Owner: [Name] — Due: [Date]
- [ ] Action 2: [Description] — Owner: [Name] — Due: [Date]

---

### References

- [Link to relevant documentation]
- [Link to related ADRs]
- [Link to technical research or benchmarks]

---

## ADR Lifecycle

1. **Proposed** — Draft written, under discussion
2. **Accepted** — Team agrees, ready for implementation
3. **Deprecated** — No longer relevant (explain why in the document)
4. **Superseded** — Replaced by a newer ADR (link to the replacement)

Keep all ADRs in the repository, even deprecated ones. They provide valuable historical context for future decisions.
