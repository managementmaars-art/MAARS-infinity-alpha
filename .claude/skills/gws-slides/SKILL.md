---
name: gws-slides
description: Google Slides API — presentations, slides, shapes, text, images, speaker notes
---

# Google Slides API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("slides", "v1", credentials=creds)
```

## Key Operations
```python
# Create presentation
pres = service.presentations().create(body={"title": "My Presentation"}).execute()
pres_id = pres["presentationId"]

# Get presentation
pres = service.presentations().get(presentationId=pres_id).execute()
slides = pres.get("slides", [])

# Add slide
requests = [{"duplicateObject": {"objectId": slides[0]["objectId"]}}]
service.presentations().batchUpdate(presentationId=pres_id, body={"requests": requests}).execute()

# Insert text box
requests = [{
    "createShape": {"objectId": "textBox1", "shapeType": "TEXT_BOX", "elementProperties": {"pageObjectId": slide_id, "size": {"width": {"magnitude": 3000000, "unit": "EMU"}, "height": {"magnitude": 3000000, "unit": "EMU"}}, "transform": {"scaleX": 1, "scaleY": 1, "translateX": 1000000, "translateY": 1000000, "unit": "EMU"}}},
}, {"insertText": {"objectId": "textBox1", "text": "Hello Slides!"}}]
service.presentations().batchUpdate(presentationId=pres_id, body={"requests": requests}).execute()
```

## Common Patterns
- Sizes in EMU (English Metric Units): 1 inch = 914400 EMU
- Use `replaceAllText` for template-based presentations
- Export via Drive API as PDF/PPTX
