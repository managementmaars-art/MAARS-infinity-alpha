---
name: arch-distributed
cluster: se-architecture
description: "Distributed systems: CAP, Raft/Paxos, eventual consistency, distributed transactions 2PC/SAGA, CRDTs"
tags: ["distributed","consensus","cap","architecture"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "distributed systems cap theorem consensus raft eventual consistency saga"
---

# arch-distributed

## Purpose
This skill equips OpenClaw to analyze, design, and implement distributed systems concepts, including CAP theorem, consensus algorithms like Raft and Paxos, eventual consistency, distributed transactions (2PC and SAGA), and CRDTs. Use it to generate code snippets, evaluate trade-offs, or simulate behaviors in distributed architectures.

## When to Use
Apply this skill when building scalable applications facing network partitions, such as microservices, cloud databases, or blockchain systems. Use it for CAP theorem decisions (e.g., prioritizing availability over consistency), consensus in fault-tolerant clusters, or handling eventual consistency in data replication. Avoid it for non-distributed tasks like single-server apps.

## Key Capabilities
- Analyze CAP theorem: Evaluate system designs for consistency, availability, and partition tolerance using predefined checks.
- Implement consensus: Generate Raft or Paxos logic, including leader election and log replication.
- Handle eventual consistency: Simulate resolution mechanisms like anti-entropy or read-repair.
- Manage transactions: Produce 2PC for atomic commits or SAGA for long-running processes with compensating actions.
- Work with CRDTs: Create implementations for counters or sets that merge without conflicts.

## Usage Patterns
Invoke this skill via OpenClaw's CLI or API by specifying the skill ID and parameters. For CLI, use `openclaw run arch-distributed --input <JSON_FILE>` to process a configuration file. In code, import OpenClaw's SDK and call `openclaw.skills.execute('arch-distributed', params={})`. Always provide a JSON input with keys like "topic" (e.g., "cap") and "action" (e.g., "analyze"). For example, to check CAP trade-offs, structure input as: {"topic": "cap", "system": {"consistency": "strong", "availability": "high"}}. Chain skills by piping outputs, e.g., run this after a database design skill.

## Common Commands/API
Use OpenClaw's CLI for quick tasks: `openclaw run arch-distributed --topic consensus --algorithm raft --output json` (flags: --topic for CAP/Raft, --algorithm for Paxos/Raft, --output for format). For API, send a POST to `/api/v1/skills/arch-distributed` with body: {"apiKey": "$OPENCLAW_API_KEY", "params": {"action": "implement", "type": "2pc"}}. Code snippet for SDK integration:
```python
import openclaw
response = openclaw.execute_skill('arch-distributed', {'topic': 'crdts', 'type': 'counter'})
print(response['code'])  # Outputs CRDT implementation code
```
Config formats: Use JSON files like {"consensus": {"algorithm": "raft", "nodes": 5}} for multi-node simulations. Set auth via environment variable: export OPENCLAW_API_KEY=$SERVICE_API_KEY.

## Integration Notes
Integrate by wrapping OpenClaw outputs in your app's workflow, e.g., call this skill from a CI/CD pipeline to validate distributed designs. For external tools, pass outputs to systems like Kubernetes (e.g., generate YAML for Raft-based stateful sets). If using with databases, ensure compatibility by specifying drivers in params, like {"db": "cassandra", "consistency": "eventual"}. Handle dependencies by installing OpenClaw SDK via `pip install openclaw` and setting $OPENCLAW_API_KEY for authenticated requests. Test integrations in a sandbox environment to avoid production issues.

## Error Handling
Common errors include invalid parameters (e.g., unsupported algorithm), network failures in simulations, or authentication issues. Check response codes: HTTP 400 for bad input, 401 for missing $OPENCLAW_API_KEY. In code, wrap calls in try-except blocks:
```python
try:
    result = openclaw.execute_skill('arch-distributed', {'topic': 'cap'})
except openclaw.SkillError as e:
    if e.code == 'INVALID_TOPIC':
        print("Use a valid topic like 'consensus'")  # Handle specifically
```
For CLI, parse errors with `openclaw run arch-distributed --debug` to get detailed logs. Retry transient errors (e.g., consensus failures) up to 3 times with exponential backoff.

## Usage Examples
1. To design a system using CAP theorem: Run `openclaw run arch-distributed --topic cap --system '{"consistency": "weak", "availability": "high"}'` to get an analysis output like JSON: {"recommendation": "Prioritize availability; use eventual consistency for reads."}. Use this to generate code for a simple key-value store.
2. For implementing Raft consensus: Execute via API: POST /api/v1/skills/arch-distributed with {"params": {"action": "implement", "algorithm": "raft"}}, which returns a snippet like:
```go
type RaftNode struct {
    ID int
    State string  // "follower", "candidate", "leader"
}
```
Integrate this into your Go application for a distributed log.

## Graph Relationships
- Related to cluster: se-architecture (e.g., shares tags with skills like arch-microservices).
- Connected via tags: "distributed" links to skills like data-processing; "consensus" to security-auth; "cap" to database-design; "architecture" to deployment-tools.
