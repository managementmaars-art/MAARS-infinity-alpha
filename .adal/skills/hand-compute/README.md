# hand-compute

Force AI coding agents to walk system execution by hand, catching races and state bugs that abstract review would miss.

## Install

```bash
npx skills add gbasin/hand-compute --all -g
```

## What it does

Before electronic computers, "computer" was a job: a person who executed a procedure by hand, step by step, writing each intermediate value down. This skill asks agents to do the same thing when debugging state machines or scoping work against an unfamiliar system.

Abstract reasoning hand-waves the exact thing state bugs hinge on: what state does each actor hold at what moment, and what transitions fire in what order. The act of maintaining concrete state across steps forces contradictions to surface that review never catches.

The skill covers three use cases:

1. **New work.** Execute the task manually as the human computer, hit the pitfalls, then distill the trace into code.
2. **Debugging an existing system.** Hand-compute the *broken* flow with concrete state first (not the fix), find where the invariant breaks, propose a fix, re-walk it, *then* write code. The trap is skipping the broken-flow walk and going straight to "validate my theory."
3. **Scoping a new feature on an existing system.** Walk the new flow end-to-end against the current state machine and write down every time you have to invent state or bend a field. Those are your design decisions.

It also documents the failure modes that make this technique collapse back into abstract reasoning (narrative walks, fanning out to sub-agents, wrong level of abstraction) and how to notice them in yourself.
	
## Hat tip [Eric Jang's tweet](https://x.com/ericjang11/status/2042321708686983627?s=20) for inspiration