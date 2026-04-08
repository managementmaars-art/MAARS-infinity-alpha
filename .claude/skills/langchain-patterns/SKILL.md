---
name: langchain-patterns
description: LangChain chains, agents, tools, memory, LCEL composition, RAG pipelines, callbacks, and streaming patterns.
---

# LangChain Patterns

## Overview

LangChain provides composable primitives for building LLM applications: LCEL for chain composition, agents for tool use, memory for conversation state, and integrations for 100+ LLMs and vector stores.

## Installation

```bash
pip install langchain langchain-openai langchain-anthropic langchain-community
pip install langchain-chroma chromadb
pip install langgraph  # For agent graphs
```

## LCEL (LangChain Expression Language)

```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda

# Basic chain
model = ChatAnthropic(model="claude-opus-4-5")
prompt = ChatPromptTemplate.from_template("Summarize this in {language}: {text}")
parser = StrOutputParser()

chain = prompt | model | parser

result = chain.invoke({"text": "Long article...", "language": "English"})

# Streaming
async for chunk in chain.astream({"text": "...", "language": "French"}):
    print(chunk, end="", flush=True)

# Parallel execution
parallel_chain = RunnableParallel({
    "summary": prompt | model | parser,
    "keywords": ChatPromptTemplate.from_template("Extract keywords from: {text}") | model | parser,
    "sentiment": ChatPromptTemplate.from_template("Sentiment of: {text}") | model | parser,
})

results = parallel_chain.invoke({"text": "Article text...", "language": "English"})

# Branching with routing
from langchain_core.runnables import RunnableBranch

classification_prompt = ChatPromptTemplate.from_template(
    "Classify as 'technical', 'billing', or 'general': {question}"
)

def route_question(info):
    topic = info["topic"].lower()
    if "technical" in topic:
        return technical_chain
    elif "billing" in topic:
        return billing_chain
    return general_chain

routed_chain = (
    {"topic": classification_prompt | model | parser, "question": RunnablePassthrough()}
    | RunnableLambda(route_question)
)
```

## RAG Pipeline

```python
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough

# 1. Load documents
loader = PyPDFLoader("document.pdf")
docs = loader.load()

# Also supports web scraping
web_loader = WebBaseLoader(["https://example.com/page1", "https://example.com/page2"])
web_docs = web_loader.load()

# 2. Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", ".", " ", ""],
)
chunks = splitter.split_documents(docs + web_docs)

# 3. Embed and store
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
    collection_name="my_docs",
)

# 4. Retriever with reranking
retriever = vectorstore.as_retriever(
    search_type="mmr",              # Maximum Marginal Relevance (diversity)
    search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.7},
)

# 5. RAG chain
def format_docs(docs):
    return "\n\n".join(f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}" for doc in docs)

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Answer based on the context provided.
    If the answer isn't in the context, say you don't know.

    Context:
    {context}"""),
    ("human", "{question}"),
])

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | ChatAnthropic(model="claude-opus-4-5")
    | StrOutputParser()
)

answer = rag_chain.invoke("What is the main topic of the document?")

# With source attribution
from langchain_core.runnables import RunnableParallel

rag_chain_with_sources = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
).assign(answer=lambda x: rag_prompt | model | parser)
```

## Agents with LangGraph

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input should be a valid Python math expression."""
    import ast
    import math
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
    try:
        tree = ast.parse(expression, mode="eval")
        return str(eval(compile(tree, "<string>", "eval"), {"__builtins__": {}}, allowed_names))
    except Exception as e:
        return f"Error: {e}"

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    import httpx
    response = httpx.get(f"https://wttr.in/{city}?format=3")
    return response.text

@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

# Create agent
tools = [calculate, get_weather, search_web]
model = ChatAnthropic(model="claude-opus-4-5")

agent = create_react_agent(model, tools)

# Run agent
result = agent.invoke({
    "messages": [("user", "What's the weather in Paris and what is 1234 * 5678?")]
})

for message in result["messages"]:
    print(f"{message.type}: {message.content}")

# Streaming agent
async for event in agent.astream_events(
    {"messages": [("user", "Research the latest AI news")]},
    version="v1",
):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
```

## Memory & Conversation History

```python
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# In-memory history (per session)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Conversation chain with memory
conversational_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Be concise."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = conversational_prompt | model | StrOutputParser()

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# Use with session
config = {"configurable": {"session_id": "user-123"}}
response1 = chain_with_history.invoke({"input": "My name is Alice."}, config=config)
response2 = chain_with_history.invoke({"input": "What's my name?"}, config=config)
# response2 will remember "Alice"

# Redis-backed history for production
from langchain_community.chat_message_histories import RedisChatMessageHistory

def get_redis_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(session_id, url="redis://localhost:6379")
```

## Callbacks & Observability

```python
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any

class LoggingCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"LLM starting with {len(prompts)} prompts")

    def on_llm_end(self, response, **kwargs):
        usage = response.llm_output.get("usage", {})
        print(f"Tokens: {usage}")

    def on_chain_error(self, error, **kwargs):
        print(f"Chain error: {error}")

    def on_tool_start(self, serialized, input_str, **kwargs):
        print(f"Tool: {serialized['name']} <- {input_str[:100]}")

    def on_tool_end(self, output, **kwargs):
        print(f"Tool output: {output[:100]}")

# Use with chain
chain.invoke({"input": "Hello"}, config={"callbacks": [LoggingCallback()]})

# LangSmith tracing (set env vars)
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"
# All runs are automatically traced
```

## Structured Output

```python
from pydantic import BaseModel, Field
from typing import List

class ExtractedInfo(BaseModel):
    """Information extracted from the text."""
    person_names: List[str] = Field(description="Names of people mentioned")
    organizations: List[str] = Field(description="Organizations mentioned")
    dates: List[str] = Field(description="Dates mentioned in ISO format")
    summary: str = Field(description="One-sentence summary")

# Method 1: with_structured_output
structured_model = ChatAnthropic(model="claude-opus-4-5").with_structured_output(ExtractedInfo)
result = structured_model.invoke("Apple Inc. was founded by Steve Jobs in 1976.")
print(result.person_names)   # ["Steve Jobs"]
print(result.organizations)  # ["Apple Inc."]

# Method 2: JsonOutputParser
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=ExtractedInfo)
prompt = ChatPromptTemplate.from_template(
    "Extract info from: {text}\n\n{format_instructions}"
)

chain = prompt | model | parser
result = chain.invoke({
    "text": "Apple was founded in 1976...",
    "format_instructions": parser.get_format_instructions(),
})
```

## Key Patterns

- **LCEL `|` pipe operator** composes runnables — all are async/streaming-compatible
- **`RunnableParallel`** runs multiple chains concurrently — great for multi-step analysis
- **MMR retrieval** balances relevance and diversity for better RAG answers
- **`RunnableWithMessageHistory`** wraps any chain to add session-based memory
- **LangSmith** provides full trace visibility for debugging complex chains
- **`with_structured_output`** is the cleanest way to get typed responses

## Models to Use

- **claude-opus-4-5**: Complex agent design, multi-step reasoning chains, research pipelines
- **claude-sonnet-4-5**: RAG pipelines, structured extraction, conversational agents
- **claude-haiku-3-5**: Simple chains, prompt templates, output parsing
