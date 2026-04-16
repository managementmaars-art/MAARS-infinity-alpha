# harness-creator Skill

Production harness engineering skill for AI coding agents, distilled from Learn Harness Engineering course and industry best practices.

## Installation

```bash
npx skills add github:harness-creator
```

Or manually copy the `skills/harness-creator/` directory to your skill path.

## What This Skill Does

This skill helps you:
- **Create harnesses from scratch** — AGENTS.md, feature lists, verification workflows
- **Improve existing harnesses** — Five-subsystem assessment with prioritized improvements  
- **Design session continuity** — Memory persistence, progress tracking, handoff procedures
- **Benchmark effectiveness** — Before/after comparison with quantitative metrics
- **Apply production patterns** — Memory, context engineering, tool safety, multi-agent coordination

## Core Framework: Five Subsystems

Every harness consists of five subsystems:

1. **Instructions** — AGENTS.md as routing layer, progressive disclosure via docs/ hierarchy
2. **State** — feature_list.json, progress.md, session handoff files
3. **Verification** — Explicit commands that agent MUST run before claiming done
4. **Scope** — One-feature-at-a-time policy, clear definition of done
5. **Lifecycle** — init.sh, clean-state checklists, session continuity mechanisms

## Reference Patterns

This skill includes 6 deep-dive reference documents:

| Pattern | When to Use |
|---------|-------------|
| [Memory Persistence](references/memory-persistence-pattern.md) | Agent forgets between sessions, need persistent project knowledge |
| [Context Engineering](references/context-engineering-pattern.md) | Context budget management, JIT loading, delegation isolation |
| [Tool Registry](references/tool-registry-pattern.md) | Tool safety, concurrency control, permission pipelines |
| [Multi-Agent Coordination](references/multi-agent-pattern.md) | Parallelism, specialization, researcher→implementer workflows |
| [Lifecycle & Bootstrap](references/lifecycle-bootstrap-pattern.md) | Hooks, background tasks, initialization sequences |
| [Gotchas](references/gotchas.md) | 15 non-obvious failure modes with fixes |

## Usage Examples

### Create Minimal Harness

```
User: "I need to set up AGENTS.md for my TypeScript project"

Skill will:
1. Ask about project context (stack, size, agent tool)
2. Generate AGENTS.md with startup workflow and working rules
3. Create feature_list.json template with placeholder features
4. Create init.sh with verification commands
5. Explain how to use each file
```

### Assess Existing Harness

```
User: "My agent still breaks things even with AGENTS.md"

Skill will:
1. Request current AGENTS.md content
2. Score each of 5 subsystems (1-5 scale)
3. Identify lowest-scoring subsystem as bottleneck
4. Provide prioritized improvement plan with concrete steps
```

### Design Session Continuity

```
User: "Agent forgets everything between sessions"

Skill will:
1. Explain memory layers (instruction vs auto-memory)
2. Design progress.md template for session tracking
3. Create session-handoff.md structure
4. Implement two-step save invariant (topic file → index)
```

## When to Trigger

This skill triggers on:
- "Create AGENTS.md / CLAUDE.md"
- "Improve agent reliability"
- "Agent forgets between sessions"
- "Multi-session continuity needed"
- "Benchmark harness effectiveness"
- "Design verification workflow"
- "Memory persistence patterns"
- "Context engineering for agents"

## When NOT to Use

This skill does NOT cover:
- Prompt engineering or system prompt design
- Model selection or fine-tuning
- Generic software architecture
- LLM API integration basics

## Templates Included

- `templates/agents.md` — AGENTS.md scaffold with working rules
- `templates/feature-list.json` — JSON Schema + example
- `templates/init.sh` — Standard initialization script
- `templates/progress.md` — Session progress log template
- `templates/session-handoff.md` — Handoff structure

## EvaluationFramework

5 test cases in `evals/evals.json`:
1. **Minimal Harness Creation** — Full setup from scratch
2. **Session Continuity Setup** — Memory and handoff design
3. **Harness Assessment** — Five-subsystem scoring
4. **Verification Workflow Design** — Force agent to verify before done
5. **Memory Taxonomy Design** — What to save vs skip

Run evaluation with skill-creator framework for quantitative benchmarks.

## Compatibility

- **Agents**: Claude Code, Codex, Cursor, Windsurf, generic
- **License**: MIT
- **Languages**: English / 中文 (bilingual support in SKILL.md)

## 兼容性

- **代理工具**: Claude Code, Codex, Cursor, Windsurf, generic
- **许可证**: MIT
- **语言**: 英文 / 中文 (SKILL.md 中双语支持)

## Project Structure

```
harness-creator/
├── SKILL.md                          # Main skill definition
├── metadata.json                     # Skill metadata, triggers, compatibility
├── evals/
│   └── evals.json                    # 5 test cases with expectations
├── templates/
│   ├── agents.md                     # AGENTS.md template
│   ├── feature-list.json             # Feature tracker template
│   ├── init.sh                       # Initialization script
│   └── progress.md                   # Session progress template
└── references/
    ├── memory-persistence-pattern.md
    ├── context-engineering-pattern.md
    ├── tool-registry-pattern.md
    ├── multi-agent-pattern.md
    ├── lifecycle-bootstrap-pattern.md
    └── gotchas.md                    # 15 failure modes
```

## Development Roadmap

- [x] Chinese translation in SKILL.md (bilingual support added)
- [ ] Python scripts for automated harness generation
- [ ] HTML viewer for harness assessment results
- [ ] Expanded eval set (10+ test cases)
- [ ] Integration with skill-creator benchmark framework
- [ ] Full Chinese localization (harness-creator-zh directory)

## 开发路线图

- [x] SKILL.md 中文翻译（已添加双语支持）
- [ ] Harness 自动生成 Python 脚本
- [ ] Harness 评估结果 HTML 查看器
- [ ] 扩展测试用例（10+ 个）
- [ ] 集成 skill-creator 基准测试框架
- [ ] 完整中文本地化（harness-creator-zh 目录）

## Contributing

Issues and PRs welcome. Key areas for contribution:
- Additional reference patterns (skill runtime, hook lifecycle, etc.)
- More eval test cases covering edge cases
- Script automation for common harness tasks
- Case studies from production deployments

## License

MIT — See LICENSE file for details.

## Acknowledgments

This skill synthesizes:
- Learn Harness Engineering course framework
- OpenAI Harness Engineering principles
- Anthropic effective harnesses research
- Agentic Harness Patterns skill (pattern extraction methodology)
