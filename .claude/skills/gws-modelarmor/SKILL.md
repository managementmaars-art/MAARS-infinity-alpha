---
name: gws-modelarmor
description: Google Model Armor — AI safety filters, prompt sanitization, content moderation for Workspace AI
---

# Google Model Armor — MAARS Reference

## Overview
Model Armor provides configurable AI safety filters for prompt sanitization and response filtering, preventing misuse of AI features in Google Workspace and GCP.

## Setup
```python
from google.cloud import modelarmor_v1

client = modelarmor_v1.ModelArmorClient(client_options={"api_endpoint": "LOCATION-modelarmor.googleapis.com"})
parent = "projects/PROJECT_ID/locations/LOCATION"
```

## Create Safety Template
```python
template = client.create_template(
    parent=parent,
    template_id="production-safety",
    template=modelarmor_v1.Template(
        filter_config=modelarmor_v1.FilterConfig(
            rai_settings=modelarmor_v1.RaiFilterSettings(
                rai_filters=[
                    modelarmor_v1.RaiFilter(
                        filter_type=modelarmor_v1.RaiFilterType.SEXUALLY_EXPLICIT,
                        confidence_level=modelarmor_v1.DetectionConfidenceLevel.HIGH,
                    ),
                    modelarmor_v1.RaiFilter(
                        filter_type=modelarmor_v1.RaiFilterType.DANGEROUS_CONTENT,
                        confidence_level=modelarmor_v1.DetectionConfidenceLevel.MEDIUM_AND_ABOVE,
                    ),
                    modelarmor_v1.RaiFilter(
                        filter_type=modelarmor_v1.RaiFilterType.HATE_SPEECH,
                        confidence_level=modelarmor_v1.DetectionConfidenceLevel.LOW_AND_ABOVE,
                    ),
                ]
            ),
            pi_and_jailbreak_filter_settings=modelarmor_v1.PiAndJailbreakFilterSettings(
                filter_enforcement=modelarmor_v1.PiAndJailbreakFilterSettings.FilterEnforcement.ENABLED,
                confidence_level=modelarmor_v1.DetectionConfidenceLevel.MEDIUM_AND_ABOVE,
            ),
        )
    ),
)
```

## Sanitize Prompts
```python
template_name = f"{parent}/templates/production-safety"

# Check user prompt before sending to LLM
response = client.sanitize_user_prompt(
    name=template_name,
    user_prompt_data=modelarmor_v1.DataItem(text=user_input),
)

if response.sanitization_result.filter_match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND:
    matched = response.sanitization_result.filter_results
    raise ValueError(f"Unsafe content detected: {matched}")

# Safe to proceed with LLM call
llm_response = call_llm(user_input)

# Also sanitize LLM response before returning
model_response = client.sanitize_model_response(
    name=template_name,
    model_response_data=modelarmor_v1.DataItem(text=llm_response),
)
```

## Filter Types
- `SEXUALLY_EXPLICIT`, `HATE_SPEECH`, `HARASSMENT`, `DANGEROUS_CONTENT`
- Prompt injection and jailbreak detection
- Custom malicious URI detection
- Confidence levels: `LOW_AND_ABOVE`, `MEDIUM_AND_ABOVE`, `HIGH`
