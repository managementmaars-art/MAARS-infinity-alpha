---
name: gws-classroom
description: Google Classroom API — courses, assignments, grades, students, teachers, submissions
---

# Google Classroom API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("classroom", "v1", credentials=creds)
```

## Key Operations
```python
# List courses (as teacher)
courses = service.courses().list(teacherId="me").execute()

# Create course
course = service.courses().create(body={
    "name": "Introduction to Python",
    "section": "Section A",
    "descriptionHeading": "Learn Python programming",
    "ownerId": "me",
    "courseState": "ACTIVE",
}).execute()

# Create assignment
assignment = service.courses().courseWork().create(courseId=course["id"], body={
    "title": "Homework 1",
    "description": "Complete all exercises in Chapter 3",
    "workType": "ASSIGNMENT",
    "dueDate": {"year": 2025, "month": 6, "day": 1},
    "dueTime": {"hours": 23, "minutes": 59},
    "maxPoints": 100,
    "state": "PUBLISHED",
}).execute()

# List student submissions
submissions = service.courses().courseWork().studentSubmissions().list(
    courseId=course["id"], courseWorkId=assignment["id"]
).execute()

# Grade submission
service.courses().courseWork().studentSubmissions().patch(
    courseId=course["id"], courseWorkId=assignment["id"], id=submission_id,
    updateMask="assignedGrade,draftGrade",
    body={"assignedGrade": 95, "draftGrade": 95}
).execute()

# Invite student
service.invitations().create(body={"userId": "student@school.edu", "courseId": course["id"], "role": "STUDENT"}).execute()
```

## Common Patterns
- Requires domain-wide delegation for admin operations
- Students can join via enrollment code or invitation
- `courseWork` types: ASSIGNMENT, SHORT_ANSWER_QUESTION, MULTIPLE_CHOICE_QUESTION
