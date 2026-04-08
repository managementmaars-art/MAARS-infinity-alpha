---
name: multi-agent-orchestration
description: Multi-agent orchestration patterns for MAARS — Commander delegation, task graphs, parallel execution, agent trust scoring, circuit breakers, and 27-network architecture
---

# Multi-Agent Orchestration — MAARS Reference

## MAARS Agent Architecture
```
User
  └── Commander Orion ∞ (Orchestrator)
        ├── Strategic Network (13 agents)
        ├── Engineering Network (22 agents)
        ├── Creative Network (17 agents)
        ├── Growth Network (20 agents)
        ├── Finance Network (19 agents)
        ├── Legal Network (16 agents)
        ├── Security Network (13 agents)
        ├── Web Intelligence Network (20 agents)
        └── 19 more specialized networks...
```

## Task Graph Structure
```python
class TaskNode:
    task_id: str
    agent_id: str
    task_type: str
    instructions: str
    depends_on: list[str]   # task_ids that must complete first
    status: str             # pending|running|completed|failed
    result: dict | None
    tool_calls: list[dict]
    trust_required: float   # minimum agent trust score

class TaskGraph:
    root_goal: str
    nodes: dict[str, TaskNode]
    execution_order: list[list[str]]  # batches for parallel execution
    
    def get_ready_tasks(self) -> list[TaskNode]:
        """Return tasks whose dependencies are all completed."""
        return [
            n for n in self.nodes.values()
            if n.status == "pending"
            and all(self.nodes[dep].status == "completed" for dep in n.depends_on)
        ]
```

## Commander Decomposition
```python
DECOMPOSE_PROMPT = """
Given this goal: {goal}

Decompose it into a task graph. For each task specify:
- task_id: unique identifier
- agent_role: which specialist handles it (e.g., "Marketing Specialist", "Data Analyst")
- instructions: exact instructions for that agent
- depends_on: list of task_ids that must complete first
- expected_output: what deliverable this produces

Optimize for: parallel execution where possible, correct dependencies, right agent for each task.

Return as JSON: {"tasks": [...]}
"""
```

## Parallel Execution Engine
```python
async def execute_task_graph(graph: TaskGraph) -> dict:
    results = {}
    
    while not all(n.status in ("completed", "failed") for n in graph.nodes.values()):
        ready = graph.get_ready_tasks()
        if not ready:
            break
        
        # Execute all ready tasks in parallel
        tasks = [execute_agent_task(node, results) for node in ready]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for node, result in zip(ready, batch_results):
            if isinstance(result, Exception):
                node.status = "failed"
                node.result = {"error": str(result)}
            else:
                node.status = "completed"
                node.result = result
                results[node.task_id] = result
    
    return results
```

## Agent Trust Scoring
```python
class TrustScore:
    """Dynamic trust score based on agent execution history."""
    
    def calculate(self, agent_id: str, history: list[dict]) -> float:
        if not history:
            return 0.5  # neutral default
        
        recent = history[-50:]  # last 50 executions
        success_rate = sum(1 for r in recent if r["success"]) / len(recent)
        avg_quality = sum(r.get("quality_score", 0.5) for r in recent) / len(recent)
        latency_score = self._score_latency(recent)
        
        return (
            success_rate * 0.5 +
            avg_quality * 0.35 +
            latency_score * 0.15
        )
    
    def requires_approval(self, agent_id: str, action: dict) -> bool:
        trust = self.get_trust(agent_id)
        action_risk = action.get("risk_level", 0.5)
        return trust * (1 - action_risk) < 0.6  # low trust + high risk = human review
```

## Circuit Breaker Pattern
```python
class AgentCircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=60):
        self.failures: dict[str, int] = {}
        self.open_until: dict[str, float] = {}
    
    def is_open(self, agent_id: str) -> bool:
        if agent_id in self.open_until:
            if time.time() < self.open_until[agent_id]:
                return True  # circuit is open, reject request
            else:
                del self.open_until[agent_id]
                self.failures[agent_id] = 0
        return False
    
    def record_failure(self, agent_id: str):
        self.failures[agent_id] = self.failures.get(agent_id, 0) + 1
        if self.failures[agent_id] >= self.failure_threshold:
            self.open_until[agent_id] = time.time() + self.reset_timeout
    
    def record_success(self, agent_id: str):
        self.failures[agent_id] = 0
```

## Human-in-the-Loop Approvals
```python
HIGH_RISK_ACTIONS = {
    "send_email",
    "post_social_media",
    "execute_code",
    "delete_data",
    "make_payment",
    "deploy_service",
}

async def check_approval(agent_id: str, action: str, details: dict) -> bool:
    if action not in HIGH_RISK_ACTIONS:
        return True  # auto-approve low-risk
    
    trust = await get_agent_trust(agent_id)
    if trust > 0.9:
        return True  # highly trusted agents auto-approved
    
    # Create approval request
    approval_id = await create_approval_request(
        agent_id=agent_id,
        action=action,
        details=details,
        expires_at=datetime.now() + timedelta(hours=1),
    )
    
    # Wait for human approval (WebSocket or polling)
    return await wait_for_approval(approval_id, timeout=3600)
```

## Agent Handoff Protocol
```python
async def handoff_to_agent(
    from_agent: str,
    to_agent: str,
    task: str,
    context: dict,
    deliverable_from_prior: dict | None = None,
) -> dict:
    handoff_message = {
        "role": "system",
        "content": f"""You are receiving a task handoff from {from_agent}.

TASK: {task}
CONTEXT: {json.dumps(context, indent=2)}
PRIOR WORK: {json.dumps(deliverable_from_prior, indent=2) if deliverable_from_prior else "None"}

Complete your portion and return structured results."""
    }
    return await execute_agent(to_agent, [handoff_message])
```

## Observability
```python
# Log every agent execution to audit trail
async def log_agent_execution(
    session_id: str,
    agent_id: str,
    task: str,
    result: dict,
    tokens_used: int,
    cost_usd: float,
    duration_ms: int,
):
    await db.execute("""
        INSERT INTO agent_executions 
        (session_id, agent_id, task, result, tokens_used, cost_usd, duration_ms, created_at)
        VALUES ($1,$2,$3,$4,$5,$6,$7,NOW())
    """, session_id, agent_id, task, result, tokens_used, cost_usd, duration_ms)
    
    # Update trust score
    await update_trust_score(agent_id, success=not result.get("error"))
```

## 27 Network Reference
| # | Network | Agents | Primary Models |
|---|---------|--------|---------------|
| 1 | Core Platform | 18 | gpt-5.2, claude-opus |
| 2 | Strategic | 13 | gpt-5.2, o3 |
| 3 | Venture Creation | 18 | gpt-5.2, claude-sonnet |
| 4 | Product | 17 | gpt-4o, claude-sonnet |
| 5 | Engineering | 22 | claude-sonnet, gpt-4o, codestral |
| 6 | Creative | 17 | claude-opus, gpt-4o |
| 7 | Growth | 20 | gpt-4o, mistral-large |
| 8 | Sales | 14 | gpt-4o, grok-3 |
| 9 | Customer Experience | 14 | gpt-4o, claude-sonnet |
| 10 | Operations | 14 | gpt-4o, deepseek-chat |
| 11 | Finance | 19 | gpt-5.2, o3 |
| 12 | Investment | 14 | gpt-5.2, o3 |
| 13 | Research | 17 | perplexity-sonar-pro, grok-3 |
| 14 | Simulation | 12 | o3, gpt-5.2 |
| 15 | Legal | 16 | claude-opus, gpt-5.2 |
| 16 | Security | 13 | gpt-5.2, claude-opus |
| 17 | Memory | 12 | text-embedding-3-large |
| 18 | Tooling | 12 | gpt-4o, claude-sonnet |
| 19 | Execution | 11 | gpt-4o, groq-llama |
| 20 | Verification | 12 | o3, claude-opus |
| 21 | Experimentation | 11 | gpt-4o, deepseek-reasoner |
| 22 | Conflict Resolution | 10 | claude-opus, gpt-5.2 |
| 23 | Observability | 12 | gpt-4o, deepseek-chat |
| 24 | Recovery | 10 | gpt-4o, claude-sonnet |
| 25 | Communication | 10 | gpt-4o, eleven_turbo_v2_5 |
| 26 | Web Intelligence | 20 | grok-3, perplexity-sonar |
| 27 | Industry-Specific | 45 | varies by domain |
