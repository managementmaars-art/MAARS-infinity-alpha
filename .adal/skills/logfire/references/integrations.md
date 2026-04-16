# Logfire Integrations Guide

Detailed setup for each supported framework and library.

## Web Frameworks

### FastAPI

```python
import logfire
from fastapi import FastAPI

logfire.configure(service_name="my-api")
logfire.instrument_fastapi()  # Global instrumentation

app = FastAPI()

# Or instrument specific app
logfire.instrument_fastapi(app)
```

Features:
- Automatic request/response spans
- Pydantic validation logging (422 errors)
- Exception tracking
- Request timing

### Starlette

```python
import logfire
from starlette.applications import Starlette

logfire.configure()
app = Starlette()
logfire.instrument_starlette(app)
```

### Django

```python
# settings.py
import logfire

logfire.configure(service_name="django-app")
logfire.instrument_django()
```

### Flask

```python
import logfire
from flask import Flask

logfire.configure()
app = Flask(__name__)
logfire.instrument_flask(app)
```

### AIOHTTP Server

```python
import logfire
from aiohttp import web

logfire.configure()
logfire.instrument_aiohttp_server()

async def hello(request):
    return web.Response(text="Hello, World!")

app = web.Application()
app.router.add_get("/", hello)

if __name__ == "__main__":
    web.run_app(app, host="localhost", port=8080)
```

### ASGI (Generic)

```python
import logfire
from my_asgi_app import app

logfire.configure()
logfire.instrument_asgi(app)
```

### WSGI (Generic)

```python
import logfire
from my_wsgi_app import app

logfire.configure()
logfire.instrument_wsgi(app)
```

## HTTP Clients

### HTTPX

```python
import logfire
import httpx

logfire.configure()
logfire.instrument_httpx()

# All HTTPX requests are now traced
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/users")
```

### Requests

```python
import logfire
import requests

logfire.configure()
logfire.instrument_requests()

response = requests.get("https://api.example.com/data")
```

### AIOHTTP Client

```python
import logfire
import aiohttp

logfire.configure()
logfire.instrument_aiohttp_client()

async with aiohttp.ClientSession() as session:
    async with session.get("https://api.example.com") as response:
        data = await response.text()
```

## Databases

### SQLAlchemy

```python
import logfire
from sqlalchemy import create_engine

logfire.configure()

# Instrument specific engine
engine = create_engine("postgresql://user:pass@localhost/db")
logfire.instrument_sqlalchemy(engine=engine)

# Or instrument all engines globally
logfire.instrument_sqlalchemy()
```

Features:
- SQL query logging
- Parameter capture
- Duration tracking
- Row counts

### Asyncpg

```python
import logfire
import asyncpg

logfire.configure()
logfire.instrument_asyncpg()

conn = await asyncpg.connect("postgresql://user:pass@localhost/db")
```

### Psycopg

```python
import logfire

logfire.configure()
logfire.instrument_psycopg()
```

### Redis

```python
import logfire

logfire.configure()
logfire.instrument_redis()
```

### PyMongo

```python
import logfire

logfire.configure()
logfire.instrument_pymongo()
```

## LLM Integrations

### Pydantic AI (Recommended)

```python
import logfire
from pydantic_ai import Agent

logfire.configure()
logfire.instrument_pydantic_ai()

agent = Agent("openai:gpt-4o", system_prompt="You are helpful.")
result = agent.run_sync("What is the capital of France?")
```

Traces:
- Agent interactions
- Tool calls
- Token usage
- Costs (with `collect_in_spans=True`)

### OpenAI

```python
import logfire
from openai import OpenAI

logfire.configure()
logfire.instrument_openai()

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Anthropic

```python
import logfire
from anthropic import Anthropic

logfire.configure()
logfire.instrument_anthropic()

client = Anthropic()
response = client.messages.create(
    model="claude-3-sonnet",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### LangChain

```python
import os
import logfire

# Set environment variables BEFORE importing langchain
os.environ["LANGSMITH_OTEL_ENABLED"] = "true"
os.environ["LANGSMITH_TRACING"] = "true"

from langchain.agents import create_agent

logfire.configure()

agent = create_agent("openai:gpt-4o", tools=[my_tool])
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
```

### Mirascope

```python
import logfire
from mirascope.core import anthropic, prompt_template
from mirascope.integrations.logfire import with_logfire

logfire.configure()

@with_logfire()
@anthropic.call("claude-3-5-sonnet")
@prompt_template("Recommend some {genre} books")
def recommend_books(genre: str): ...

response = recommend_books("fantasy")
```

### MCP (Model Context Protocol)

```python
import logfire
from mcp.server.fastmcp import FastMCP

logfire.configure(service_name="mcp-server")
logfire.instrument_mcp()

app = FastMCP()

@app.tool()
def add(a: int, b: int) -> int:
    return a + b
```

## Task Queues

### Celery

```python
import logfire
from celery import Celery
from celery.signals import worker_init

@worker_init.connect()
def init_worker(*args, **kwargs):
    logfire.configure(service_name="celery-worker")
    logfire.instrument_celery()

app = Celery("tasks", broker="redis://localhost:6379/0")

@app.task
def add(x: int, y: int):
    return x + y
```

### AWS Lambda

```bash
pip install logfire[aws-lambda]
```

```python
import logfire

logfire.configure()
logfire.instrument_aws_lambda()

def lambda_handler(event, context):
    logfire.info("Processing Lambda event", event_type=event.get("type"))
    
    with logfire.span("Business logic"):
        result = process_event(event)
    
    return {"statusCode": 200, "body": result}
```

Features:
- Invocation details
- Duration tracking
- Cold start detection
- Error capture

## Logging Libraries

### Standard Logging

```python
import logfire
import logging

logfire.configure()
logfire.instrument_logging()

logger = logging.getLogger(__name__)
logger.info("This goes to Logfire")
```

### Structlog

```python
import logfire
import structlog

logfire.configure()
logfire.instrument_structlog()

logger = structlog.get_logger()
logger.info("Structured log", user_id=123)
```

### Loguru

```python
import logfire
from loguru import logger

logfire.configure()
logfire.instrument_loguru()

logger.info("Loguru message")
```

### Print Statements

```python
import logfire

logfire.configure()
logfire.instrument_print()

# Now all print() calls are captured as logs
name = "World"
print("Hello", name)  # Logged with arguments

# Or use as context manager
with logfire.instrument_print():
    print("This is logged")
print("This is NOT logged")
```

## Pydantic Validation

```python
import logfire
from pydantic import BaseModel

logfire.configure()
logfire.instrument_pydantic()

class User(BaseModel):
    name: str
    email: str

# Validation is now traced
user = User(name="Alice", email="alice@example.com")
```

## System Metrics

```python
import logfire

logfire.configure()
logfire.instrument_system_metrics()

# Captures: CPU, memory, disk, network metrics
```

## JavaScript/TypeScript

### Next.js

```ts
import * as logfire from "logfire";

logfire.configure({
  serviceName: "my-nextjs-app",
  environment: "production",
});
```

### Cloudflare Workers

```ts
import * as logfire from "logfire";
import { instrument } from "@pydantic/logfire-cf-workers";

const handler = {
  async fetch(): Promise<Response> {
    logfire.info("Worker invoked");
    return new Response("Hello!");
  },
} satisfies ExportedHandler;

export default instrument(handler, {
  service: { name: "my-worker", version: "1.0.0" },
});
```
