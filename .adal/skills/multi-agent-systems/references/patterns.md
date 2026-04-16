# Multi-Agent Patterns Reference

## Pattern Catalog

### 1. Context Isolation Pattern

**Problem:** Main agent context polluted by large subtask results.

**Solution:** Subagent extracts and returns only essential summary.

```python
class OrderLookupSubagent(Subagent):
    def _get_system_prompt(self) -> str:
        return """You are an order lookup specialist. Retrieve order details
        and return ONLY: order_id, status, date, customer_name, items (names only).
        Do NOT include full history, shipping details, or payment info."""

    def lookup(self, order_id: str) -> dict:
        response = self.run(f"Get details for order {order_id}", max_tokens=1024)
        return {
            "order_id": order_id,
            "status": extract_status(response),
            "date": extract_date(response),
            "items": extract_item_names(response)
        }
```

### 2. Parallel Research Pattern

**Problem:** Single agent cannot cover multiple research facets within context limits.

**Solution:** Lead agent decomposes query, subagents research in parallel.

```python
class ResearchOrchestrator(AgentBase):
    def _get_system_prompt(self) -> str:
        return """You coordinate research projects. Decompose complex queries
        into independent research facets that can be investigated in parallel."""

    def research(self, query: str) -> dict:
        # Decompose into facets
        facets = self.run(f"Break this into independent research facets:\n{query}")
        # Run subagents in parallel
        subagents = [ResearchSubagent() for _ in facets]
        results = asyncio.run(self._run_parallel(subagents, facets))
        # Synthesize
        return self.run(f"Synthesize these findings:\n{results}")

    async def _run_parallel(self, subagents: list, tasks: list) -> list:
        async with AsyncAnthropic() as client:
            async_subagents = [AsyncSubagent(client) for _ in subagents]
            coroutines = [sa.run_async(task) for sa, task in zip(async_subagents, tasks)]
            return await asyncio.gather(*coroutines)
```

### 3. Platform Specialization Pattern

**Problem:** Single agent confused by tools across multiple platforms.

**Solution:** Separate agents per platform with focused tool sets.

```python
class PlatformOrchestrator(OrchestratorAgent):
    def __init__(self, client: Anthropic = None):
        super().__init__(client)
        self.register_subagent("crm", CRMAgent(client))
        self.register_subagent("marketing", MarketingAgent(client))
        self.register_subagent("messaging", MessagingAgent(client))

    def _get_system_prompt(self) -> str:
        return """You are a platform integration coordinator.
        Route requests to the appropriate specialist:
        - CRM: Contacts, opportunities, accounts, sales pipeline
        - Marketing: Campaigns, lead nurturing, email sequences, scoring
        - Messaging: Notifications, alerts, team communication"""


class CRMAgent(Subagent):
    def _get_system_prompt(self) -> str:
        return """You are a CRM specialist. Manage contacts, opportunities,
        and account records. Always verify ownership before updates."""

    def _get_tools(self) -> list:
        return [crm_get_contacts, crm_create_opportunity, crm_update_account]
```

### 4. Verification Subagent Pattern

**Problem:** Main agent may not thoroughly validate its own work.

**Solution:** Independent verifier with explicit success criteria.

```python
class VerificationAgent(Subagent):
    def _get_system_prompt(self) -> str:
        return """You are a verification specialist. Test thoroughly before
        marking anything as passed. Run complete test suites. Report all failures."""

    def verify(self, requirements: str, artifact: Any) -> dict:
        prompt = f"""
        Requirements: {requirements}
        Artifact: {artifact}

        Verify:
        1. All existing tests pass
        2. New functionality works as specified
        3. No obvious errors or security issues
        4. Edge cases are handled

        You MUST run the complete test suite.
        Report ALL failures, even minor ones.
        """
        response = self.run(prompt, max_tokens=4096)
        return {
            "passed": "FAIL" not in response,
            "details": extract_verification_details(response)
        }


class CodingAgentWithVerification(AgentBase):
    def implement_feature(self, requirements: str, max_attempts: int = 3) -> dict:
        for attempt in range(max_attempts):
            # Implement
            result = self.run(f"Implement: {requirements}", max_tokens=4096)
            # Verify
            verifier = VerificationAgent(self.client)
            verification = verifier.verify(requirements, result)
            if verification["passed"]:
                return result
            # Retry with feedback
            requirements += f"\n\nPrevious attempt issues:\n{verification['details']}"
        raise Exception(f"Failed verification after {max_attempts} attempts")
```

### 5. Summary Extraction Pattern

**Problem:** Need to reduce large context before passing to main agent.

**Solution:** Subagent extracts concise summary using system prompt.

```python
class SummaryExtractor(Subagent):
    def _get_system_prompt(self) -> str:
        return """You extract essential information from documents.
        Return a concise summary (50-100 tokens) containing ONLY:
        - Key findings or conclusions
        - Critical data points
        - Any items requiring follow-up

        Do NOT include: background, methodology, or full details."""

    def extract_summary(self, document: str) -> str:
        response = self.run(f"Extract summary:\n{document}", max_tokens=256)
        return response.content.strip()
```

## Anti-Patterns to Avoid

### 1. Sequential Handoffs
**Bad:** Planning agent → Implementation agent → Testing agent
- Each handoff loses context
- Coordination overhead exceeds benefits

### 2. Over-Fragmentation
**Bad:** Splitting work into too many small agents
- More coordination messages than actual work
- Token overhead multiplies

### 3. Ignoring Context Boundaries
**Bad:** Separating work that shares critical context
- "Telephone game" effect degrades results

### 4. Missing Verification Criteria
**Bad:** "Make sure it works" instead of specific tests
- Leads to early victory problem

## Scaling Guidelines

| Factor | Single Agent | Multi-Agent |
|--------|--------------|-------------|
| Tools | < 15 | > 20 |
| Context per task | < 1000 tokens | > 1000 tokens |
| Task types | 1-2 domains | 3+ independent domains |
| Parallelizable | No | Yes |

## Tool Search Optimization

Before adopting multi-agent for tool management, consider:
- Anthropic's Tool Search Tool can reduce token usage by 85%
- Dynamically discover tools instead of loading all definitions
- May eliminate need for tool specialization in some cases

## Source

This guide is based on Anthropic's research and practical experience:
- [Building multi-agent systems: when and how to use them](https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them)
