# Interview Protocol

How to conduct the RootSpec interview process.

## Core Principles

1. **One question at a time** — don't dump a list. Ask, listen, adapt your next question based on the answer.

2. **Challenge anti-patterns inline** — if a Design Pillar describes a feature instead of a feeling, push back immediately. If a strategy is too vague, ask for specifics.

3. **Summarize understanding** — after each answer, briefly reflect back what you heard before asking the next question. This builds trust and catches misunderstandings early.

4. **Gate progression** — don't move to drafting until the developer confirms satisfaction with the interview answers. Ask: "Ready for me to draft this, or anything to adjust?"

5. **Adapt to context** — if editing an existing spec, start by asking what feels wrong or has changed. If creating new, start from scratch with open questions.

6. **Skip when parameterized** — if the skill was invoked with a focus (e.g., `/rs-spec add push notifications`), use that as context and skip the "what do you want?" question. Jump to the deeper questions.

## Anti-Pattern Challenges

When you see these, push back:

- **Feature-as-pillar**: "Fast Search" → "What feeling does fast search create? Relief? Control?"
- **Vague mission**: "Make a great app" → "Great for whom? What specific problem does it solve?"
- **Too many pillars**: 6+ pillars → "Which of these could be merged? Which is most essential?"
- **Technology in philosophy**: "Use React" → "That's an L4 concern. What user experience drives that choice?"
- **Numbers in L1-L4**: "500ms response time" → "Use a placeholder like [brief duration]. Actual values go in L5."

## Question Ordering

Within each level, order questions from abstract to concrete:
1. **Why** — motivation, purpose, feelings
2. **What** — scope, boundaries, trade-offs
3. **How** — patterns, flows, mechanisms
4. **How much** — only at L5
