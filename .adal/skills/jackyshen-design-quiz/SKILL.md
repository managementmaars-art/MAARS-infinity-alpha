---
name: jackyshen-design-quiz
description: Generate quiz questions, assessments, and knowledge checks for training programs. Use when user asks to "create quiz questions", "generate assessment", "make test paper", or similar requests for training evaluations after class.
version: 0.1.0
github: mebusw
social: xhs@敏捷的申导, wechat@申导-敏捷教练
email: mebusw@gmail.com
---

# Quiz Generator for Training

Create effective quiz questions that measure learning outcomes and validate knowledge application.

## Quiz Design Process

### 1. Align with Learning Outcomes

Start with learning outcomes, not topics. Map each outcome to question types:

| Learning Outcome | Question Type | Example |
|-----------------|---------------|---------|
| Apply [model] to [skill] | Scenario-based | Given [context], what would you do? |
| Distinguish concepts | Multiple choice | Which [concept] fits this situation? |
| Analyze using framework | Application | Which phase is happening in this dialogue? |
| Design action plan | Case analysis | Given this profile, what would you do? |

### 2. Ensure MECE Coverage

Cover all key topics without overlap:

```
[Topic] Coverage
├── Module 1: [Category] - X questions
├── Module 2: [Category] - X questions
└── Module 3: [Category] - X questions
```

**Verify:** proportional coverage per module, no gaps, minimal overlap, balanced difficulty.

### 3. Select Question Types

**Multiple Choice (Single Answer)**
- Best for: Testing concepts, models, frameworks
- 3-5 options, one clearly correct answer
- Avoid "all of the above" or "none of the above"

**Multiple Response (Select All)**
- Best for: Nuanced understanding, multiple correct approaches
- Specify how many options are correct
- All correct options must be equally valid

**Scenario/Case-Based**
- Best for: Application, judgment, higher-order thinking
- Provide realistic scenario, ask "what would you do?"
- Make relevant to learners' context

**True/False**
- Best for: Quick checks, clarifying misconceptions
- Statements clearly true or false
- Test important concepts, not trivia

**Fill-in-the-Blank**
- Best for: Key terms, models, frameworks
- Blanks have unique correct answers
- Provide sufficient context

**Open-Ended/Essay**
- Best for: Deep understanding, synthesis, personal application
- Provide clear evaluation criteria
- Use for higher-level learning (Bloom's evaluate/create)

### 4. Balance Bloom's Taxonomy

| Level | Percentage | Focus |
|-------|------------|-------|
| Remember/Understand | 30-40% | Basic knowledge, concepts |
| Apply | 30-40% | Using knowledge in scenarios |
| Analyze/Evaluate | 20-30% | Breaking down, judging |
| Create | 10-20% | Producing something new |

### 5. Set Difficulty Levels

- **Easy (20-30%)**: Basic recall, straightforward application
- **Medium (50-60%)**: Application, some analysis
- **Hard (10-20%)**: Complex scenarios, synthesis

### 6. Create Answer Keys

For each question include:
- Correct answer(s)
- Point value
- Explanation/rationale
- Common mistakes and why they're wrong

## Typical Quiz Structure

```
Total: 20 questions, 100 points, 30-45 minutes

Part 1: Knowledge Check (30 points)
- 10 multiple choice × 3 points

Part 2: Application (40 points)
- 4 scenario questions × 10 points

Part 3: Analysis (20 points)
- 2 true/false with explanation × 10 points

Part 4: Application (10 points)
- 1 open-ended question

Passing: 70/100 points
```

## Output Format

```markdown
# [Training Name] - Quiz

## Quiz Information
- **Total Questions:** X
- **Total Points:** X
- **Time Allowed:** X minutes
- **Passing Score:** X points

## Part 1: [Section Name] (X points)

### Question 1 (X points)
[Question text]

A. [Option]
B. [Option]
C. [Option]
D. [Option]

---

## Answer Key

### Question 1
**Correct Answer:** C
**Points:** X
**Explanation:** [Rationale]
```

## Best Practices Checklist

- [ ] Questions align with learning outcomes
- [ ] Test application, not just recall
- [ ] Clear and unambiguous
- [ ] One clearly correct answer
- [ ] Avoid trick questions
- [ ] Realistic and relevant
- [ ] All topics covered proportionally
- [ ] Balanced difficulty levels
- [ ] Language clear and unbiased

## Persona

You are an experienced corporate trainer creating assessments to reinforce learning and measure knowledge retention.

## Task

When provided with training content, generate quiz questions that:
1. Focus on core learning objectives and key frameworks
2. Test understanding and application (not just recall)
3. Include appropriate question variety
4. Provide clear answer keys with explanations

## Jinshuju Format

For Jinshuju (jinshuju.net) form imports, use this DSL format:

```
Form Title

Form Description

[Single Choice] Question text?
Option A
Option B
Option C
Option D

[True/False] Statement to judge
True
False

[Multiple Choice] Question text? (Select X options)
Option A
Option B
Option C
Option D

[Fill in the Blank] Question text?

[Short Answer] Open-ended question?

[Number] Numeric answer?

[Date] Date selection?

[Time] Time selection?

[Dropdown] Select from list
Option A
Option B
Option C

[Description] Informational text

[Address] Address field
```
