---
name: write-1on1-agenda
description: Generate a structured agenda for a 1:1 meeting with your manager, mentor, or direct report. Includes discussion questions and follow-up sections.
argument-hint: [meeting type or topics to discuss]
allowed-tools: Read, Write, AskUserQuestion, Skill
---

# 1:1 Agenda Generator

Generate structured agendas for effective 1:1 meetings based on your role and topics.

## Instructions

### Step 1: Understand the Context

Ask the user for:

1. **Relationship type** - Are they the manager/mentor or the report/mentee?
2. **Meeting type** - Regular check-in, performance discussion, growth-focused, or first meeting?
3. **Topics** - What do they want to discuss?
4. **Duration** - How long is the meeting? (default: 30 min)

If the user has already provided this information, proceed directly to generating.

### Step 2: Generate Appropriate Template

Select and customize the template based on context:

#### Regular 1:1 (Default)

```markdown
# 1:1 Agenda - [Date]

**With:** [Name]
**Duration:** [30 min]

---

## Check-in (5 min)
- How are you doing generally?
- Any wins from this week?

## Your Topics (10 min)
[Mentee/report adds items here]
- [Topic 1]
- [Topic 2]

## Development Focus (10 min)
- Progress on current goals
- Blockers or challenges
- Skills to develop

## Open Discussion (5 min)
- Anything else?

---

## Action Items
- [ ] [Owner] Task
- [ ] [Owner] Task

## Notes
[Space for meeting notes]
```

#### First 1:1 / Kickoff

```markdown
# Kickoff 1:1 - [Date]

**With:** [Name]
**Duration:** [45-60 min]

---

## Getting to Know Each Other (15 min)

### For you to share:
- Your background and how you got here
- What you're excited about
- Where you want to be in 1-2 years

### Questions to ask them:
- What's their management/mentoring style?
- How do they prefer to give and receive feedback?
- What does success look like in this role?

## Expectations (10 min)
- What they expect from you
- What you can expect from them
- How you'll measure progress

## Logistics (5 min)
- Meeting frequency and duration
- Communication preferences
- How to cancel/reschedule

## Immediate Priorities (10 min)
- What you're currently working on
- Where you need help
- First 30-60 day goals

---

## Action Items
- [ ] Set up recurring 1:1s
- [ ] [Any other follow-ups]
```

#### Growth-Focused 1:1

```markdown
# Growth 1:1 - [Date]

**With:** [Name]
**Duration:** [45 min]

---

## Reflection (10 min)
- What's been going well?
- What's been challenging?
- What have you learned recently?

## Skills Assessment (15 min)

### Technical Skills
- What do you want to get better at?
- What gaps are affecting your work?

### Soft Skills
- Communication, leadership, collaboration?
- What feedback have you received?

## Goal Setting (15 min)

### 3-Month Goals
- What do you want to accomplish?
- What skills should you develop?
- What stretch assignments interest you?

### Support Needed
- What resources would help?
- What blockers need to be removed?

## Action Items
- [ ] Draft SMART goals
- [ ] Identify stretch opportunities
- [ ] Schedule follow-up review
```

### Step 3: Customize Based on Topics

If the user provided specific topics, weave them into the appropriate section:

```markdown
## Your Topics

### [Topic from user]
**Context:** [Add brief context if needed]
**Questions to discuss:**
- [Relevant question 1]
- [Relevant question 2]
**Desired outcome:** [What they want from discussing this]
```

### Step 4: Add Suggested Discussion Questions

Based on topics, suggest relevant questions:

**For blockers/challenges:**

- What have you tried so far?
- What resources or support would help?
- Is there a deadline pressure?

**For career growth:**

- What does the next level look like?
- What skills gap is biggest?
- Who could you learn from?

**For project concerns:**

- What's the risk if this continues?
- What would success look like?
- Who else needs to be involved?

**For feedback:**

- Is there specific feedback you've received?
- What would you like feedback on?
- How can I give you feedback more effectively?

## Output Format

Provide the agenda in clean markdown, ready to copy into a document or notes app.

Include:

- Clear sections with time allocations
- Placeholder brackets for customization
- Action items section
- Notes section

## Related Resources

- `mentoring-developers` skill - Mentoring frameworks
- `references/one-on-one-structure.md` - Detailed 1:1 guidance
- `feedback-conversations` skill - Giving and receiving feedback
