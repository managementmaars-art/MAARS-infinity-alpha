---
name: hr-ai
description: AI HR skills — job descriptions, resume screening, interview questions, onboarding, performance reviews, HR policies, compensation benchmarking for MAARS HR agents
---

# HR AI — MAARS Reference

## Job Description Template
```python
JD_PROMPT = """
You are Amara Johnson, MAARS HR Specialist.

Write a job description for: {role}
Company: {company}
Seniority: {level}
Remote/Office: {work_type}
Salary range: {salary_range}

Structure:
1. HEADLINE: Role + company hook (why this opportunity is exciting)
2. ABOUT THE ROLE (3-4 sentences): What they'll do + impact
3. RESPONSIBILITIES (6-8 bullets): Concrete, action-verb led
4. REQUIREMENTS (5-6 bullets): Must-haves only, no "nice-to-haves" mixed in
5. NICE-TO-HAVE (3-4 bullets): Separate section
6. WHAT WE OFFER: Benefits, culture, growth
7. SALARY: Always include range (attracts better candidates)

Avoid: "Fast-paced environment", "rockstar/ninja", vague requirements, unnecessary degree requirements
"""
```

## Resume Screening Criteria
```python
RESUME_SCREENING_PROMPT = """
Screen this resume against the job requirements:

JOB REQUIREMENTS: {requirements}
RESUME: {resume_text}

Score on:
1. Required skills match (0-10)
2. Years of relevant experience (0-10)
3. Industry/domain fit (0-10)
4. Education relevance (0-5)
5. Career progression (0-5)

TOTAL SCORE: /40
RECOMMENDATION: Strong Yes / Yes / Maybe / No
KEY STRENGTHS: (3 bullets)
CONCERNS: (2 bullets)
INTERVIEW QUESTIONS to probe weaknesses:
"""
```

## Interview Question Banks
```python
INTERVIEW_QUESTIONS = {
    "behavioral": [
        "Tell me about a time you disagreed with a decision and how you handled it.",
        "Describe a project that failed. What did you learn?",
        "Tell me about the most complex problem you've solved.",
        "How have you handled a difficult stakeholder relationship?",
        "Give an example of when you had to influence without authority.",
    ],
    "technical_general": [
        "Walk me through your approach to a completely new problem.",
        "How do you stay current with developments in your field?",
        "What's the most important technical decision you've made recently?",
    ],
    "culture_fit": [
        "What type of work environment helps you do your best work?",
        "How do you prefer to receive feedback?",
        "What does career growth mean to you?",
        "Why are you looking to leave your current role?",
    ],
    "situational": [
        "You have 3 urgent tasks with the same deadline. How do you prioritize?",
        "You realize you've been working on the wrong problem for 2 weeks. What do you do?",
        "A team member is consistently missing deadlines. How do you address it?",
    ],
}
```

## Onboarding Checklist
```python
ONBOARDING_CHECKLIST = {
    "day_1": [
        "Account setup (email, Slack, GitHub, HRIS)",
        "Welcome meeting with manager",
        "Team introductions",
        "Company handbook + culture overview",
        "First week schedule",
    ],
    "week_1": [
        "Role-specific tool access",
        "1:1 with key stakeholders",
        "Review company strategy and OKRs",
        "Shadow 2-3 team meetings",
        "First small task/project assigned",
    ],
    "day_30": [
        "30-day check-in with manager",
        "Initial performance expectations set",
        "Key processes understood",
        "First deliverable completed",
    ],
    "day_90": [
        "90-day review",
        "OKRs for next quarter set",
        "Full team integration",
        "Independent project ownership",
    ],
}
```

## Performance Review Framework
```python
PERF_REVIEW_PROMPT = """
Generate a structured performance review for:
Employee: {name}
Role: {role}
Period: {period}
Manager's notes: {manager_notes}
Peer feedback: {peer_feedback}
Self-assessment: {self_assessment}
Goals from last period: {previous_goals}
Achievements: {achievements}

Structure:
1. OVERALL RATING: (Exceptional/Exceeds/Meets/Needs Improvement)
2. KEY ACHIEVEMENTS (3-5 specific, quantified where possible)
3. AREAS FOR DEVELOPMENT (2-3 constructive, actionable)
4. GOAL ATTAINMENT (% and commentary for each goal)
5. GOALS FOR NEXT PERIOD (3-5 SMART goals)
6. DEVELOPMENT PLAN (specific actions, resources, timeline)
7. MANAGER SUMMARY (2-3 sentences for HR records)
"""
```

## Models to Use
- **JD writing**: `claude-sonnet-4-6` (best writing quality)
- **Resume screening**: `gpt-4o` (fast + structured output)
- **Performance reviews**: `claude-opus-4-6`
- **Bulk screening**: `gpt-4o-mini` or `deepseek-chat`
