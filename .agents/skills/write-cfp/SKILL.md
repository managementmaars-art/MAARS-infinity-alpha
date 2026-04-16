---
name: write-cfp
description: Draft a compelling conference proposal (Call for Papers) that gets accepted. Use when submitting to conferences, meetups, or internal tech talks.
argument-hint: [talk topic or title idea]
allowed-tools: Read, Write, AskUserQuestion, WebSearch
---

# Write CFP Proposal

Generate a compelling conference talk proposal with a hook-worthy title and structured abstract.

## Arguments

`$ARGUMENTS` - The talk topic, title idea, or subject matter

## Workflow

### Step 1: Gather Context

If `$ARGUMENTS` is insufficient, use AskUserQuestion to gather:

**Question 1: Talk Type** (header: "Type")

- Experience report (here's what we did and learned)
- Technical deep-dive (how X works under the hood)
- Best practices (patterns that work)
- Case study (specific project/problem)
- Introduction (beginner-friendly guide)

**Question 2: Target Audience** (header: "Audience")

- Junior developers (0-2 years)
- Mid-level developers (3-5 years)
- Senior/Staff (5+ years)
- Mixed levels
- Non-technical stakeholders

**Question 3: Duration** (header: "Duration")

- Lightning talk (5-10 minutes)
- Standard session (25-40 minutes)
- Deep dive (45-60 minutes)
- Workshop (90+ minutes)

**Question 4: Your Experience** (header: "Experience")

- I did this myself/led the project
- My team did this and I was involved
- I researched this extensively
- I have opinions from observation

### Step 2: Generate Title Options

Apply the CFP Title Formula:
`[What we did] + [Problem/Solution] + [Why it matters]`

Generate 3-5 title options using these patterns:

#### Pattern 1: The Story Hook

Implies a journey with conflict and resolution.

- "We Migrated to Microservices and Regretted It (For a While)"
- "How Our AI Onboarding Bot Confused Three New Devs"

#### Pattern 2: The Unexpected Outcome

Subverts expectations.

- "The Weirdest DevOps Hack I Ever Built—And Why It Worked"
- "How Deleting 10,000 Lines Made Us Ship Faster"

#### Pattern 3: The Specific Metric

Concrete results are compelling.

- "From 30-Second Deploys to 30-Minute Confidence"
- "How We Reduced Our Cloud Bill by 40%"

#### Pattern 4: The Honest Confession

Vulnerability is memorable.

- "All the Ways I've Broken Production (And How to Not Be Me)"
- "My First Year as Tech Lead: Everything I Did Wrong"

### Step 3: Structure the Abstract

Use this five-part structure:

**1. Hook (1-2 sentences)**
Why should anyone care? What's the problem or opportunity?

**2. Context (2-3 sentences)**
What was the situation? Brief setup that establishes credibility.

**3. Approach (2-3 sentences)**
What did you do? The journey, key decisions made.

**4. Results (1-2 sentences)**
What happened? Outcomes and lessons learned.

**5. Takeaways (3 bullet points)**
What will attendees walk away with? Be specific and actionable.

### Step 4: Generate Complete Proposal

Produce a submission-ready CFP:

```markdown
## Conference Talk Proposal

### Title Options

1. **[Primary title - strongest option]**
2. [Alternative title 1]
3. [Alternative title 2]

---

### Abstract

[HOOK: 1-2 sentences that establish relevance and grab attention]

[CONTEXT: 2-3 sentences setting up the situation, establishing credibility]

[APPROACH: 2-3 sentences about what you did, the journey, key decisions]

[RESULTS: 1-2 sentences about outcomes and key lessons]

**Attendees will walk away with:**
• [Specific, actionable takeaway 1]
• [Specific, actionable takeaway 2]
• [Specific, actionable takeaway 3]

This talk is ideal for [target audience] who are [dealing with what situation].

---

### Speaker Bio (100 words)

[Your name] is a [role] at [company/context] who [relevant experience].
[Brief credential that establishes expertise on this topic].
[Optional: Previous speaking experience or relevant content].

---

### Additional Notes (for reviewers)

**Why this talk matters now:** [Brief rationale]

**What makes this unique:** [Your angle/perspective]

**Technical requirements:** [Any special needs]

---

### Outline (if requested)

1. **Introduction** ([X] min) - [Brief description]
2. **[Section 1]** ([X] min) - [Brief description]
3. **[Section 2]** ([X] min) - [Brief description]
4. **[Section 3]** ([X] min) - [Brief description]
5. **Conclusion & Q&A** ([X] min) - [Brief description]
```

### Step 5: Quality Check

Before submission, verify:

- [ ] Title is compelling and specific (not generic)
- [ ] Hook grabs attention in first 2 sentences
- [ ] Abstract clearly states what attendees learn
- [ ] Takeaways are specific and actionable
- [ ] Target audience is explicitly stated
- [ ] Bio establishes credibility on this topic
- [ ] Length matches conference requirements

### Step 6: Offer Refinements

After presenting the proposal, offer:

1. **Title alternatives** - Different angles or hooks
2. **Audience adjustment** - More/less technical
3. **Abstract variations** - Shorter or expanded versions
4. **Conference targeting** - Suggestions for where to submit

## Example Usage

```bash
# With topic
/soft-skills:write-cfp How we reduced deployment time by 90%

# With rough idea
/soft-skills:write-cfp Talk about our microservices migration lessons

# Start with questions
/soft-skills:write-cfp
```

## Output

Present a complete conference proposal with:

1. **3-5 title options** ranked by strength
2. **Full abstract** using Hook-Context-Approach-Results-Takeaways structure
3. **Speaker bio** template
4. **Outline** for longer talks
5. **Submission tips** for the specific type

## Titles to Avoid

❌ "Introduction to [Technology]" - Too generic
❌ "Best Practices for [X]" - Vague, overused
❌ "[Technology] Deep Dive" - What specifically?
❌ "How to [Basic Thing]" - Sounds like a tutorial
❌ "[Technology]: A Comprehensive Overview" - Sounds like documentation

## Conference Targeting Tips

| Conference Type | What Works |
| --- | --- |
| **Language/Framework** | Technical depth, specific implementations |
| **DevOps/Platform** | Process improvements, tooling stories |
| **Leadership/Culture** | Team dynamics, organizational lessons |
| **Local/Regional** | Beginner-friendly, broad appeal |
| **Enterprise** | Scale challenges, case studies |
