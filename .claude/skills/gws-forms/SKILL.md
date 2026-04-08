---
name: gws-forms
description: Google Forms API — create forms, add questions, collect responses, watch for submissions
---

# Google Forms API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("forms", "v1", credentials=creds)
```

## Create Form with Questions
```python
# Create form
form = service.forms().create(body={"info": {"title": "Customer Satisfaction Survey"}}).execute()
form_id = form["formId"]

# Add questions via batchUpdate
service.forms().batchUpdate(formId=form_id, body={"requests": [
    {"createItem": {
        "item": {
            "title": "How satisfied are you?",
            "questionItem": {"question": {
                "required": True,
                "scaleQuestion": {"low": 1, "high": 5, "lowLabel": "Not satisfied", "highLabel": "Very satisfied"}
            }}
        },
        "location": {"index": 0}
    }},
    {"createItem": {
        "item": {
            "title": "What can we improve?",
            "questionItem": {"question": {"required": False, "textQuestion": {"paragraph": True}}}
        },
        "location": {"index": 1}
    }},
    {"createItem": {
        "item": {
            "title": "Which features do you use?",
            "questionItem": {"question": {"choiceQuestion": {
                "type": "CHECKBOX",
                "options": [{"value": "Analytics"}, {"value": "Reports"}, {"value": "API"}]
            }}}
        },
        "location": {"index": 2}
    }},
]}).execute()
```

## Get Responses
```python
# List all responses
responses = service.forms().responses().list(formId=form_id).execute()
for response in responses.get("responses", []):
    for q_id, answer in response.get("answers", {}).items():
        print(q_id, answer["textAnswers"]["answers"])

# Watch for new responses via Pub/Sub
watch = service.forms().watches().create(formId=form_id, body={
    "watch": {
        "target": {"topic": {"topicName": "projects/PROJECT/topics/TOPIC"}},
        "eventType": "RESPONSES"
    }
}).execute()
```

## Question Types
- `textQuestion` (paragraph=True/False), `scaleQuestion`, `choiceQuestion` (RADIO/CHECKBOX/DROP_DOWN)
- `dateQuestion`, `timeQuestion`, `fileUploadQuestion`, `ratingQuestion`
