# API Reference - Claude Agent SDK

Complete reference documentation for the Claude Agent SDK (Python).

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [claude_agent_examples.py](../examples/claude_agent_examples.py) - Core SDK usage patterns including queries, client connections, and message handling
- [hook_integration_example.py](../examples/hook_integration_example.py) - Hook system integration with practical event handling patterns
- [verify_sdk.py](../examples/verify_sdk.py) - SDK installation and environment verification utility

---

## Table of Contents

1. [Core Functions](#core-functions)
2. [ClaudeSDKClient Class](#claudesdkclient-class)
3. [Configuration Types](#configuration-types)
4. [Message Types](#message-types)
5. [MCP Tools](#mcp-tools)
6. [Permission System](#permission-system)
7. [Hooks System](#hooks-system)
8. [Error Types](#error-types)

---

## Core Functions

### `query()`

**Signature:**
```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None,
) -> AsyncIterator[Message]
```

**Purpose:** One-shot or unidirectional streaming interactions with Claude.

**Parameters:**
- `prompt` (required): String for single-shot queries or AsyncIterable for streaming mode
- `options` (optional): Configuration (defaults to `ClaudeAgentOptions()`)
- `transport` (optional): Custom transport implementation

**Returns:** AsyncIterator yielding Message objects

**Example:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="What is the capital of France?",
    options=ClaudeAgentOptions(
        system_prompt="You are a geography expert",
        cwd="/path/to/project"
    )
):
    print(message)
```

**When to use:**
- Simple one-off questions
- Batch processing
- Stateless operations
- All inputs known upfront

**When NOT to use:**
- Interactive conversations
- Need to send follow-ups based on responses
- Require interrupt capabilities

---

## ClaudeSDKClient Class

### Constructor

```python
def __init__(
    self,
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None,
)
```

**Parameters:**
- `options`: Configuration (defaults to `ClaudeAgentOptions()`)
- `transport`: Custom transport (defaults to subprocess CLI)

### Methods

#### `connect()`

```python
async def connect(
    self,
    prompt: str | AsyncIterable[dict[str, Any]] | None = None
) -> None
```

**Purpose:** Establish connection to Claude Code.

**Parameters:**
- `prompt` (optional): Initial prompt or message stream

**Example:**
```python
client = ClaudeSDKClient(options=options)
await client.connect()
# or with initial prompt
await client.connect("Hello!")
```

#### `query()`

```python
async def query(
    self,
    prompt: str | AsyncIterable[dict[str, Any]],
    session_id: str = "default"
) -> None
```

**Purpose:** Send a message in streaming mode.

**Parameters:**
- `prompt`: String message or async iterable of message dicts
- `session_id`: Session identifier (default: "default")

**Example:**
```python
await client.query("What's the weather today?")
await client.query("Follow-up question", session_id="chat-123")
```

#### `receive_messages()`

```python
async def receive_messages() -> AsyncIterator[Message]
```

**Purpose:** Receive all messages from Claude (continuous stream).

**Returns:** AsyncIterator yielding all messages

**Example:**
```python
async for message in client.receive_messages():
    print(message)
    # Continues indefinitely until disconnect
```

#### `receive_response()`

```python
async def receive_response() -> AsyncIterator[Message]
```

**Purpose:** Receive messages until and including a ResultMessage.

**Returns:** AsyncIterator yielding messages until ResultMessage

**Example:**
```python
await client.query("Question")
async for message in client.receive_response():
    print(message)
    # Automatically stops after ResultMessage
```

#### `interrupt()`

```python
async def interrupt() -> None
```

**Purpose:** Send interrupt signal to stop current operation.

**Example:**
```python
await client.query("Long-running task")
# ... decide to interrupt
await client.interrupt()
```

#### `set_permission_mode()`

```python
async def set_permission_mode(self, mode: str) -> None
```

**Purpose:** Change permission mode during conversation.

**Parameters:**
- `mode`: "default" | "acceptEdits" | "bypassPermissions"

**Example:**
```python
await client.set_permission_mode("acceptEdits")
```

#### `set_model()`

```python
async def set_model(self, model: str | None = None) -> None
```

**Purpose:** Change AI model during conversation.

**Parameters:**
- `model`: Model identifier or None for default

**Example:**
```python
await client.set_model("claude-sonnet-4-5")
```

#### `get_server_info()`

```python
async def get_server_info() -> dict[str, Any] | None
```

**Purpose:** Get server initialization info (commands, styles, capabilities).

**Returns:** Dictionary with server info or None

**Example:**
```python
info = await client.get_server_info()
print(f"Commands: {len(info.get('commands', []))}")
```

#### `disconnect()`

```python
async def disconnect() -> None
```

**Purpose:** Disconnect from Claude and clean up resources.

**Example:**
```python
await client.disconnect()
```

### Context Manager Support

```python
async with ClaudeSDKClient(options=options) as client:
    await client.query("Hello")
    async for msg in client.receive_response():
        print(msg)
    # Automatically disconnects
```

---

## Configuration Types

### `ClaudeAgentOptions`

**Full definition:**
```python
@dataclass
class ClaudeAgentOptions:
    # Tool access control
    allowed_tools: list[str] = field(default_factory=list)
    disallowed_tools: list[str] = field(default_factory=list)

    # System configuration
    system_prompt: str | SystemPromptPreset | None = None
    model: str | None = None
    cwd: str | Path | None = None

    # Permission system
    permission_mode: PermissionMode | None = None
    can_use_tool: CanUseTool | None = None
    permission_prompt_tool_name: str | None = None

    # MCP servers
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)

    # Session control
    continue_conversation: bool = False
    resume: str | None = None
    max_turns: int | None = None
    fork_session: bool = False

    # Context loading
    setting_sources: list[SettingSource] | None = None  # ["user", "project", "local"]

    # Agent definitions
    agents: dict[str, AgentDefinition] | None = None

    # Hooks
    hooks: dict[HookEvent, list[HookMatcher]] | None = None

    # Advanced
    add_dirs: list[str | Path] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    extra_args: dict[str, str | None] = field(default_factory=dict)
    max_buffer_size: int | None = None
    stderr: Callable[[str], None] | None = None
    include_partial_messages: bool = False
    user: str | None = None
```

**Key fields explained:**

#### `allowed_tools`
List of tool names Claude can use. Empty list = all tools allowed (subject to permission_mode).

```python
allowed_tools=["Read", "Grep", "search_code"]
```

#### `disallowed_tools`
List of tool names Claude cannot use. Takes precedence over `allowed_tools`.

```python
disallowed_tools=["Bash", "Write"]
```

#### `system_prompt`
System instructions for Claude. Can be string or preset.

```python
system_prompt="You are a Python expert focused on clean code"

# Or use preset
system_prompt={"type": "preset", "preset": "claude_code", "append": "Additional context"}
```

#### `model`
Model identifier. Defaults to "claude-sonnet-4".

```python
model="claude-sonnet-4"
model="claude-opus-4-1-20250805"
model="claude-haiku-4"
```

#### `permission_mode`
Controls how tool permissions are handled:
- `"default"`: CLI prompts for dangerous tools
- `"acceptEdits"`: Auto-accept file edits, prompt for others
- `"bypassPermissions"`: Allow all tools without prompts (use with caution)

```python
permission_mode="acceptEdits"
```

#### `setting_sources`
**IMPORTANT**: Load CLAUDE.md files for context.

```python
setting_sources=["user", "project"]

# "user": ~/.claude/CLAUDE.md (user-level)
# "project": ./CLAUDE.md or ./.claude/CLAUDE.md (project-level)
# "local": local settings
```

**Use cases:**
- `["project"]`: Load only project standards
- `["user", "project"]`: Load personal + project context (recommended)
- `["user"]`: Load only personal context

#### `can_use_tool`
Callback for dynamic permission control.

```python
async def can_use_tool(tool_name: str, tool_input: dict, context: ToolPermissionContext):
    if tool_name in ["Read", "Grep"]:
        return PermissionResultAllow()
    return PermissionResultDeny(message="Tool not allowed")

options = ClaudeAgentOptions(can_use_tool=can_use_tool)
```

#### `hooks`
Event-driven automation hooks.

```python
hooks={
    "PreToolUse": [
        HookMatcher(matcher="Bash", hooks=[my_hook_function])
    ],
    "PostToolUse": [
        HookMatcher(matcher=None, hooks=[log_tool_result])
    ]
}
```

#### `agents`
Custom agent definitions for delegation.

```python
agents={
    "python-expert": AgentDefinition(
        description="Python expert",
        prompt="You are a Python developer",
        tools=["Read", "Write"],
        model="opus"
    )
}
```

### `AgentDefinition`

```python
@dataclass
class AgentDefinition:
    description: str
    prompt: str
    tools: list[str] | None = None
    model: Literal["sonnet", "opus", "haiku", "inherit"] | None = None
```

**Example:**
```python
agent = AgentDefinition(
    description="Security expert",
    prompt="You are a security vulnerability analyst",
    tools=["Read", "Grep"],
    model="opus"
)
```

---

## Message Types

### `UserMessage`

```python
@dataclass
class UserMessage:
    content: str | list[ContentBlock]
    parent_tool_use_id: str | None = None
```

**Example:**
```python
msg = UserMessage(content="Hello, Claude!")
```

### `AssistantMessage`

```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    parent_tool_use_id: str | None = None
```

**Content blocks:**
- `TextBlock`: Text response
- `ThinkingBlock`: Extended thinking
- `ToolUseBlock`: Tool invocation
- `ToolResultBlock`: Tool result

**Example:**
```python
if isinstance(msg, AssistantMessage):
    for block in msg.content:
        if isinstance(block, TextBlock):
            print(block.text)
```

### `SystemMessage`

```python
@dataclass
class SystemMessage:
    subtype: str
    data: dict[str, Any]
```

**Example:**
```python
# System messages include status updates, errors, etc.
if isinstance(msg, SystemMessage):
    print(f"System: {msg.subtype}")
```

### `ResultMessage`

```python
@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None
```

**Example:**
```python
if isinstance(msg, ResultMessage):
    print(f"Cost: ${msg.total_cost_usd:.4f}")
    print(f"Duration: {msg.duration_ms}ms")
    print(f"Turns: {msg.num_turns}")
```

### Content Block Types

#### `TextBlock`

```python
@dataclass
class TextBlock:
    text: str
```

#### `ThinkingBlock`

```python
@dataclass
class ThinkingBlock:
    thinking: str
    signature: str
```

#### `ToolUseBlock`

```python
@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
```

#### `ToolResultBlock`

```python
@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str | list[dict[str, Any]] | None = None
    is_error: bool | None = None
```

---

## MCP Tools

### `@tool` Decorator

**Signature:**
```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any]
) -> Callable
```

**Parameters:**
- `name`: Unique tool identifier
- `description`: What the tool does (helps Claude choose when to use it)
- `input_schema`: Parameter schema (dict mapping names to types)

**Example:**
```python
@tool("greet", "Greet a user by name", {"name": str})
async def greet(args):
    return {
        "content": [{"type": "text", "text": f"Hello, {args['name']}!"}]
    }

@tool("add", "Add two numbers", {"a": float, "b": float})
async def add_numbers(args):
    result = args["a"] + args["b"]
    return {
        "content": [{"type": "text", "text": f"Sum: {result}"}]
    }
```

**Input schema formats:**

1. Simple dict:
```python
{"name": str, "age": int, "active": bool}
```

2. JSON Schema:
```python
{
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0}
    },
    "required": ["name"]
}
```

**Tool response format:**
```python
{
    "content": [
        {"type": "text", "text": "Result text"}
    ],
    "is_error": False  # Optional, default False
}
```

**Error handling:**
```python
@tool("divide", "Divide numbers", {"a": float, "b": float})
async def divide(args):
    if args["b"] == 0:
        return {
            "content": [{"type": "text", "text": "Error: Division by zero"}],
            "is_error": True
        }
    return {
        "content": [{"type": "text", "text": f"Result: {args['a'] / args['b']}"}]
    }
```

### `create_sdk_mcp_server()`

**Signature:**
```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

**Purpose:** Create in-process MCP server with tools.

**Parameters:**
- `name`: Server identifier
- `version`: Version string (default: "1.0.0")
- `tools`: List of tools created with `@tool`

**Returns:** `McpSdkServerConfig` for use in `ClaudeAgentOptions.mcp_servers`

**Example:**
```python
calculator = create_sdk_mcp_server(
    name="calculator",
    version="2.0.0",
    tools=[add, subtract, multiply, divide]
)

options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["add", "subtract", "multiply", "divide"]
)
```

**Benefits of SDK MCP servers:**
- Run in-process (no subprocess overhead)
- Direct access to application state
- Easier debugging (same process)
- Simpler deployment (single process)

---

## Permission System

### Permission Types

```python
PermissionMode = Literal["default", "acceptEdits", "plan", "bypassPermissions"]
PermissionBehavior = Literal["allow", "deny", "ask"]
```

### `ToolPermissionContext`

```python
@dataclass
class ToolPermissionContext:
    signal: Any | None = None
    suggestions: list[PermissionUpdate] = field(default_factory=list)
```

### `PermissionResultAllow`

```python
@dataclass
class PermissionResultAllow:
    behavior: Literal["allow"] = "allow"
    updated_input: dict[str, Any] | None = None
    updated_permissions: list[PermissionUpdate] | None = None
```

**Usage:**
```python
return PermissionResultAllow()

# With modified input
return PermissionResultAllow(
    updated_input={"command": "safer_command"}
)

# With permission updates
return PermissionResultAllow(
    updated_permissions=[
        PermissionUpdate(
            type="addRules",
            rules=[PermissionRuleValue(tool_name="Bash", rule_content="pattern")],
            behavior="allow"
        )
    ]
)
```

### `PermissionResultDeny`

```python
@dataclass
class PermissionResultDeny:
    behavior: Literal["deny"] = "deny"
    message: str = ""
    interrupt: bool = False
```

**Usage:**
```python
return PermissionResultDeny(
    message="Tool not allowed in production",
    interrupt=True
)
```

### `CanUseTool` Callback

```python
CanUseTool = Callable[
    [str, dict[str, Any], ToolPermissionContext],
    Awaitable[PermissionResult]
]
```

**Example implementation:**
```python
async def can_use_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    context: ToolPermissionContext
) -> PermissionResult:
    # Log all tool uses
    logger.info(f"Tool request: {tool_name}")

    # Allow read-only tools
    if tool_name in ["Read", "Grep", "Glob"]:
        return PermissionResultAllow()

    # Block dangerous commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if any(danger in command for danger in ["rm -rf", "dd if="]):
            return PermissionResultDeny(
                message="Dangerous command blocked",
                interrupt=True
            )

    # Allow with logging
    return PermissionResultAllow()
```

---

## Hooks System

### Hook Events

```python
HookEvent = (
    Literal["PreToolUse"]
    | Literal["PostToolUse"]
    | Literal["UserPromptSubmit"]
    | Literal["Stop"]
    | Literal["SubagentStop"]
    | Literal["PreCompact"]
)
```

**Note:** Python SDK does not support `SessionStart`, `SessionEnd`, and `Notification` hooks.

### `HookMatcher`

```python
@dataclass
class HookMatcher:
    matcher: str | None = None
    hooks: list[HookCallback] = field(default_factory=list)
```

**Matcher patterns:**
- `None`: Match all
- `"ToolName"`: Match specific tool
- `"Tool1|Tool2"`: Match multiple tools (regex)

**Example:**
```python
HookMatcher(
    matcher="Bash|Write|Edit",
    hooks=[log_tool_use, validate_operation]
)
```

### `HookCallback`

```python
HookCallback = Callable[
    [dict[str, Any], str | None, HookContext],
    Awaitable[HookJSONOutput]
]
```

**Parameters:**
- `input_data`: Hook input (varies by event type)
- `tool_use_id`: Tool use identifier (for PreToolUse/PostToolUse)
- `context`: Hook context with signal

**Returns:** `HookJSONOutput` dict

### `HookJSONOutput`

```python
class HookJSONOutput(TypedDict):
    decision: NotRequired[Literal["block"]]
    systemMessage: NotRequired[str]
    hookSpecificOutput: NotRequired[Any]
```

**Example hooks:**

#### PreToolUse Hook
```python
async def log_tool_use(input_data, tool_use_id, context):
    tool_name = input_data.get("tool", {}).get("name")
    print(f"[PRE] Tool: {tool_name}")
    return {}

async def block_dangerous_bash(input_data, tool_use_id, context):
    tool = input_data.get("tool", {})
    if tool.get("name") == "Bash":
        command = tool.get("input", {}).get("command", "")
        if "rm -rf" in command:
            return {
                "decision": "block",
                "systemMessage": "Blocked dangerous bash command"
            }
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher=None, hooks=[log_tool_use]),
            HookMatcher(matcher="Bash", hooks=[block_dangerous_bash])
        ]
    }
)
```

#### PostToolUse Hook
```python
async def log_tool_result(input_data, tool_use_id, context):
    result = input_data.get("result", {})
    success = not result.get("is_error", False)
    print(f"[POST] Result: {'success' if success else 'error'}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [
            HookMatcher(matcher=None, hooks=[log_tool_result])
        ]
    }
)
```

#### UserPromptSubmit Hook
```python
async def validate_prompt(input_data, tool_use_id, context):
    prompt = input_data.get("prompt", "")
    if len(prompt) > 10000:
        return {
            "decision": "block",
            "systemMessage": "Prompt too long"
        }
    return {}

options = ClaudeAgentOptions(
    hooks={
        "UserPromptSubmit": [
            HookMatcher(matcher=None, hooks=[validate_prompt])
        ]
    }
)
```

---

## Error Types

### `ClaudeSDKError`
Base exception for all SDK errors.

```python
try:
    async for msg in query(prompt="Hello"):
        print(msg)
except ClaudeSDKError as e:
    print(f"SDK error: {e}")
```

### `CLIConnectionError`
Raised when unable to connect to Claude Code.

```python
except CLIConnectionError as e:
    print(f"Connection failed: {e}")
    # Retry or exit
```

### `CLINotFoundError`
Raised when Claude CLI is not installed.

```python
except CLINotFoundError as e:
    print("Claude CLI not found. Install with: npm install -g claude-code")
```

### `ProcessError`
Raised when CLI process fails.

```python
except ProcessError as e:
    print(f"Process error (exit {e.exit_code}): {e.stderr}")
```

**Attributes:**
- `exit_code`: Process exit code
- `stderr`: Standard error output

### `CLIJSONDecodeError`
Raised when unable to decode JSON from CLI output.

```python
except CLIJSONDecodeError as e:
    print(f"JSON decode error: {e.line[:100]}")
    print(f"Original error: {e.original_error}")
```

---

## Advanced Configuration

### External MCP Servers

**Stdio server:**
```python
options = ClaudeAgentOptions(
    mcp_servers={
        "myserver": {
            "type": "stdio",
            "command": "python",
            "args": ["mcp_server.py"],
            "env": {"VAR": "value"}
        }
    }
)
```

**SSE server:**
```python
options = ClaudeAgentOptions(
    mcp_servers={
        "remote": {
            "type": "sse",
            "url": "https://api.example.com/mcp",
            "headers": {"Authorization": "Bearer token"}
        }
    }
)
```

**HTTP server:**
```python
options = ClaudeAgentOptions(
    mcp_servers={
        "http-server": {
            "type": "http",
            "url": "https://api.example.com/mcp",
            "headers": {"X-API-Key": "key"}
        }
    }
)
```

### Environment Variables

**Debugging:**
```bash
export CLAUDE_CODE_ENTRYPOINT=sdk-py  # Set by SDK automatically
export DEBUG=1  # Enable debug logging
```

**Authentication:**
```bash
# API Key
export ANTHROPIC_API_KEY=your_key

# Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_ACCESS_KEY_ID=key
export AWS_SECRET_ACCESS_KEY=secret

# Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
```

---

## Type Aliases

```python
PermissionMode = Literal["default", "acceptEdits", "plan", "bypassPermissions"]
SettingSource = Literal["user", "project", "local"]
PermissionBehavior = Literal["allow", "deny", "ask"]
HookEvent = Literal["PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop", "SubagentStop", "PreCompact"]

Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent
ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock
PermissionResult = PermissionResultAllow | PermissionResultDeny
McpServerConfig = McpStdioServerConfig | McpSSEServerConfig | McpHttpServerConfig | McpSdkServerConfig
```

---

## Quick Reference

### Common Patterns

**Simple query:**
```python
from claude_agent_sdk import query
async for msg in query(prompt="Hello"):
    print(msg)
```

**Interactive client:**
```python
from claude_agent_sdk import ClaudeSDKClient
async with ClaudeSDKClient(options=options) as client:
    await client.query("Hello")
    async for msg in client.receive_response():
        print(msg)
```

**Custom tool:**
```python
from claude_agent_sdk import tool, create_sdk_mcp_server
@tool("greet", "Greet user", {"name": str})
async def greet(args):
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}

server = create_sdk_mcp_server("greeter", tools=[greet])
```

**Permission callback:**
```python
async def can_use_tool(tool_name, tool_input, context):
    if tool_name in ["Read", "Grep"]:
        return PermissionResultAllow()
    return PermissionResultDeny(message="Not allowed")
```

**Hook:**
```python
async def my_hook(input_data, tool_use_id, context):
    print(f"Hook triggered: {tool_use_id}")
    return {}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[my_hook])]}
)
```

---

**Last Updated:** 2025-10-23
**SDK Version:** 0.0.20+
