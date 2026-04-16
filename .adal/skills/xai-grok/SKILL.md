---
name: xai-grok
cluster: ai-apis
description: "xAI Grok API: OpenAI-compatible at api.x.ai/v1, grok-3/grok-3-mini for fast AI reasoning"
tags: ["ai-apis","xai"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "xai-grok ai-apis"
---

# xai-grok

## Purpose
This skill enables interaction with the xAI Grok API, an OpenAI-compatible service for fast AI reasoning tasks. It provides access to models like grok-3 and grok-3-mini via api.x.ai/v1, allowing developers to integrate advanced AI capabilities for text generation, reasoning, and more.

## When to Use
Use this skill when you need quick AI inference for applications requiring natural language processing, such as chatbots, code generation, or data analysis. Opt for it over other APIs if you're already using OpenAI-compatible tools and want xAI's specialized models for faster responses, especially in scenarios with real-time constraints like live customer support or dynamic content creation.

## Key Capabilities
- Access endpoints at api.x.ai/v1 for chat completions, embeddings, and model streaming.
- Support models like "grok-3" for general reasoning and "grok-3-mini" for lightweight, high-speed tasks.
- Handle requests with JSON payloads, including parameters for temperature (0.0-2.0), max tokens (up to 4096), and stop sequences.
- Provide OpenAI-like responses, including choices array with text and usage stats.
- Authenticate via API key in the Authorization header as "Bearer $XAI_API_KEY".

## Usage Patterns
To use this skill, set the API key in your environment (e.g., export XAI_API_KEY=your_key), then make HTTP requests to api.x.ai/v1. Structure requests as POST calls with JSON bodies. For chat interactions, specify the model and messages array. Always include error checking in your code loops. If using in a script, handle retries for rate limits. For asynchronous patterns, use webhooks or polling on response IDs.

## Common Commands/API
- Endpoint for chat completions: POST https://api.x.ai/v1/chat/completions
  - Required headers: Authorization: Bearer $XAI_API_KEY, Content-Type: application/json
  - Example body: {"model": "grok-3", "messages": [{"role": "user", "content": "Explain quantum computing"}]}
  - CLI command: curl -X POST -H "Authorization: Bearer $XAI_API_KEY" -H "Content-Type: application/json" -d '{"model":"grok-3","messages":[{"role":"user","content":"Summarize this text"}]}' https://api.x.ai/v1/chat/completions
- Endpoint for model info: GET https://api.x.ai/v1/models
  - Query params: None required; returns available models like grok-3 and grok-3-mini.
  - CLI command: curl -H "Authorization: Bearer $XAI_API_KEY" https://api.x.ai/v1/models
- Common flags in requests: Add "temperature": 0.7 for creativity, or "max_tokens": 150 to limit output length.
- Config format: Store settings in a JSON file, e.g., {"api_key": "$XAI_API_KEY", "default_model": "grok-3-mini"} and load it in code.

## Integration Notes
Integrate by setting $XAI_API_KEY as an environment variable before runtime. In Python, use requests library: import os; api_key = os.environ.get('XAI_API_KEY'). For Node.js, use fetch with headers. Avoid hardcoding keys; use secure vaults. If proxying requests, ensure HTTPS passthrough. Test with a simple script first, and handle rate limits by checking response headers for X-RateLimit-Remaining. For embedding, map xAI models to OpenAI formats in your codebase.

## Error Handling
Check HTTP status codes: 401 for invalid API key (retry with correct $XAI_API_KEY); 429 for rate limits (implement exponential backoff, e.g., wait 5 seconds then retry). Parse JSON errors for messages like "context_length_exceeded" and truncate input accordingly. In code, wrap requests in try-except blocks: try: response = requests.post(url, headers=headers, json=data) except requests.exceptions.RequestException as e: log_error(e) and raise. For model-specific errors, validate inputs before sending, e.g., ensure messages array is not empty.

## Concrete Usage Examples
1. Generate a text summary: Use this to summarize content quickly. Code snippet:
   import requests; os.environ['XAI_API_KEY'] = 'your_key'; response = requests.post('https://api.x.ai/v1/chat/completions', headers={'Authorization': 'Bearer ' + os.environ['XAI_API_KEY']], json={'model': 'grok-3-mini', 'messages': [{'role': 'user', 'content': 'Summarize AI ethics'}]}); print(response.json()['choices'][0]['message']['content'])
2. Perform reasoning task: Query for problem-solving. Code snippet:
   import requests; response = requests.post('https://api.x.ai/v1/chat/completions', headers={'Authorization': 'Bearer $XAI_API_KEY'}, json={'model': 'grok-3', 'messages': [{'role': 'user', 'content': 'Solve: What is 15% of 200?'}], 'temperature': 0.2}); print(response.json()['choices'][0]['message']['content'])

## Graph Relationships
- Belongs to cluster: ai-apis
- Tagged with: ai-apis, xai
- Related via embedding hint: xai-grok (links to ai-apis cluster)
