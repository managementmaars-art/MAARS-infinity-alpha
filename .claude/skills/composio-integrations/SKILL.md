---
name: composio-integrations
description: "Composio tool integrations: GitHub, Slack, Notion, Linear, Google Workspace for AI agents"
---

# Composio Integrations

Building AI agents with Composio: connecting to GitHub, Slack, Notion, Linear, Google Workspace, and other tools with managed authentication and LLM-ready tool schemas.

## Setup and Authentication

```python
pip install composio-core composio-openai composio-langchain composio-anthropic

# CLI authentication
composio login
composio add github     # OAuth flow for GitHub
composio add slack      # OAuth flow for Slack
composio add notion     # OAuth flow for Notion
composio add linear     # OAuth flow for Linear
composio add googleworkspace

# List connected accounts
composio connections list

# List available tools for an app
composio tools list --app github
```

```python
from composio_openai import ComposioToolSet, App, Action
from openai import OpenAI

# Initialize
toolset = ComposioToolSet(api_key=os.environ["COMPOSIO_API_KEY"])
openai_client = OpenAI()

# Get tools for specific apps
github_tools = toolset.get_tools(apps=[App.GITHUB])
slack_tools = toolset.get_tools(apps=[App.SLACK])
notion_tools = toolset.get_tools(apps=[App.NOTION])

# Or get specific actions only
issue_tools = toolset.get_tools(actions=[
    Action.GITHUB_CREATE_AN_ISSUE,
    Action.GITHUB_LIST_ISSUES,
    Action.GITHUB_CREATE_ISSUE_COMMENT,
])
```

## OpenAI Function Calling Agent

```python
from composio_openai import ComposioToolSet, App, Action
from openai import OpenAI
import json

client = OpenAI()
toolset = ComposioToolSet()

def run_agent(task: str, apps: list[App] | None = None, max_iterations: int = 10) -> str:
    """Run an AI agent with Composio tools."""
    tools = toolset.get_tools(apps=apps or [App.GITHUB, App.SLACK, App.NOTION])

    messages = [
        {
            "role": "system",
            "content": """You are a helpful AI assistant with access to productivity tools.
Complete the task efficiently. When done, provide a clear summary of what was accomplished."""
        },
        {"role": "user", "content": task}
    ]

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        # Execute tool calls via Composio
        tool_results = toolset.handle_tool_calls(response)
        messages.extend(tool_results)

    return "Max iterations reached"

# Example usage
result = run_agent(
    "Create a GitHub issue titled 'Fix login bug' with a description of the bug, "
    "then post a Slack message to #dev-team with the issue link.",
    apps=[App.GITHUB, App.SLACK]
)
print(result)
```

## GitHub Integration

```python
from composio_openai import ComposioToolSet, Action
from composio.client.enums import Action as ComposioAction

toolset = ComposioToolSet()

# Direct action execution (no LLM needed)
def create_github_issue(repo: str, title: str, body: str, labels: list[str] | None = None) -> dict:
    """Create a GitHub issue directly."""
    result = toolset.execute_action(
        action=Action.GITHUB_CREATE_AN_ISSUE,
        params={
            "owner": repo.split("/")[0],
            "repo": repo.split("/")[1],
            "title": title,
            "body": body,
            "labels": labels or [],
        }
    )
    return result["data"]

def list_open_prs(owner: str, repo: str) -> list[dict]:
    result = toolset.execute_action(
        action=Action.GITHUB_LIST_PULL_REQUESTS,
        params={"owner": owner, "repo": repo, "state": "open", "per_page": 50}
    )
    return result["data"]["items"]

def create_pr_review(owner: str, repo: str, pull_number: int, review_body: str, event: str = "COMMENT") -> dict:
    result = toolset.execute_action(
        action=Action.GITHUB_CREATE_A_REVIEW_FOR_A_PULL_REQUEST,
        params={
            "owner": owner, "repo": repo,
            "pull_number": pull_number,
            "body": review_body,
            "event": event,   # APPROVE, REQUEST_CHANGES, COMMENT
        }
    )
    return result["data"]

# AI-powered PR review agent
def ai_review_pr(owner: str, repo: str, pull_number: int) -> str:
    tools = toolset.get_tools(actions=[
        Action.GITHUB_GET_A_PULL_REQUEST,
        Action.GITHUB_LIST_PULL_REQUESTS_FILES,
        Action.GITHUB_CREATE_A_REVIEW_FOR_A_PULL_REQUEST,
        Action.GITHUB_CREATE_ISSUE_COMMENT,
    ])

    task = f"""Review the pull request #{pull_number} in {owner}/{repo}.
1. Fetch the PR details and changed files
2. Analyze the code changes for bugs, security issues, and code quality
3. Create a constructive review comment on the PR
4. Return a summary of your findings"""

    return run_agent(task, max_iterations=8)
```

## Slack Integration

```python
def send_slack_message(channel: str, message: str, blocks: list | None = None) -> dict:
    """Send a Slack message to a channel."""
    params = {"channel": channel, "text": message}
    if blocks:
        params["blocks"] = json.dumps(blocks)

    result = toolset.execute_action(
        action=Action.SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL,
        params=params
    )
    return result["data"]

def create_slack_channel_and_invite(name: str, user_ids: list[str]) -> dict:
    # Create channel
    channel_result = toolset.execute_action(
        action=Action.SLACK_CREATE_A_NEW_CHANNEL,
        params={"name": name, "is_private": False}
    )
    channel_id = channel_result["data"]["channel"]["id"]

    # Invite users
    invite_result = toolset.execute_action(
        action=Action.SLACK_INVITE_USERS_TO_CHANNEL,
        params={"channel": channel_id, "users": ",".join(user_ids)}
    )
    return {"channel_id": channel_id, "members": invite_result["data"]}

# Slack message with rich formatting (Block Kit)
def send_incident_alert(channel: str, incident: dict) -> dict:
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"Incident: {incident['title']}"}},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*Severity:*\n{incident['severity']}"},
            {"type": "mrkdwn", "text": f"*Status:*\n{incident['status']}"},
        ]},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Description:*\n{incident['description']}"}},
        {"type": "actions", "elements": [
            {"type": "button", "text": {"type": "plain_text", "text": "View Dashboard"},
             "url": incident["dashboard_url"], "style": "danger"},
        ]},
    ]
    return send_slack_message(channel, f"Incident: {incident['title']}", blocks)
```

## Notion Integration

```python
def create_notion_page(database_id: str, title: str, content: str, properties: dict | None = None) -> dict:
    """Create a page in a Notion database."""
    result = toolset.execute_action(
        action=Action.NOTION_CREATE_PAGE,
        params={
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": title}}]},
                **(properties or {})
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
                }
            ]
        }
    )
    return result["data"]

def query_notion_database(database_id: str, filter_dict: dict | None = None) -> list[dict]:
    result = toolset.execute_action(
        action=Action.NOTION_QUERY_DATABASE,
        params={"database_id": database_id, **({"filter": filter_dict} if filter_dict else {})}
    )
    return result["data"]["results"]
```

## Linear Integration

```python
def create_linear_issue(
    team_id: str,
    title: str,
    description: str,
    priority: int = 2,  # 0=No priority, 1=Urgent, 2=High, 3=Medium, 4=Low
    label_ids: list[str] | None = None,
) -> dict:
    result = toolset.execute_action(
        action=Action.LINEAR_CREATE_LINEAR_ISSUE,
        params={
            "teamId": team_id,
            "title": title,
            "description": description,
            "priority": priority,
            "labelIds": label_ids or [],
        }
    )
    return result["data"]

def ai_triage_and_create_issues(
    support_tickets: list[dict],
    team_id: str,
) -> list[dict]:
    """Use AI to triage support tickets and create Linear issues."""
    tools = toolset.get_tools(actions=[
        Action.LINEAR_CREATE_LINEAR_ISSUE,
        Action.LINEAR_LIST_TEAMS,
        Action.LINEAR_GET_ISSUE_LABELS,
    ])

    task = f"""Analyze these support tickets and create appropriate Linear issues for engineering:
{json.dumps(support_tickets, indent=2)}

For each ticket that requires engineering work:
1. Determine priority (1=Urgent, 2=High, 3=Medium, 4=Low)
2. Write a clear title and description for engineers
3. Create the Linear issue in team {team_id}
Report which issues were created."""

    return run_agent(task, max_iterations=len(support_tickets) * 2 + 3)
```

## Google Workspace Integration

```python
def create_google_doc(title: str, content: str, folder_id: str | None = None) -> dict:
    result = toolset.execute_action(
        action=Action.GOOGLEDOCS_CREATE_DOCUMENT,
        params={"title": title, "content": content}
    )
    return result["data"]

def send_gmail(to: list[str], subject: str, body: str, cc: list[str] | None = None) -> dict:
    result = toolset.execute_action(
        action=Action.GMAIL_SEND_EMAIL,
        params={
            "to": to,
            "subject": subject,
            "body": body,
            "cc": cc or [],
        }
    )
    return result["data"]

def create_calendar_event(
    summary: str,
    start_time: str,   # ISO 8601
    end_time: str,
    attendees: list[str],
    description: str = "",
) -> dict:
    result = toolset.execute_action(
        action=Action.GOOGLECALENDAR_CREATE_EVENT,
        params={
            "summary": summary,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"},
            "attendees": [{"email": e} for e in attendees],
            "description": description,
        }
    )
    return result["data"]
```

## Multi-App Orchestration Agent

```python
from composio_langchain import ComposioToolSet as LangchainToolSet
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

def create_orchestration_agent(apps: list[App]):
    """Create a LangChain agent with Composio tools."""
    toolset = LangchainToolSet()
    tools = toolset.get_tools(apps=apps)

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant with access to productivity tools. "
                   "Complete tasks efficiently and always confirm what you've done."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=15)

# Run the full workflow
agent_executor = create_orchestration_agent([
    App.GITHUB, App.SLACK, App.NOTION, App.LINEAR, App.GOOGLEWORKSPACE
])

result = agent_executor.invoke({
    "input": """Weekly engineering sync workflow:
    1. Get all open GitHub PRs from org/my-repo that are over 3 days old
    2. For each stale PR, create a Linear issue to nudge the reviewer
    3. Create a Notion page summarizing this week's PR activity
    4. Post a Slack summary to #engineering with key metrics
    5. Schedule a 30-min Google Calendar event for Friday review""",
    "chat_history": []
})
```

## User-Specific Connections (Multi-Tenant)

```python
# Composio supports per-user OAuth connections for SaaS apps
from composio import ComposioClient

composio_client = ComposioClient(api_key=os.environ["COMPOSIO_API_KEY"])

def get_connection_url(user_id: str, app: str) -> str:
    """Generate OAuth URL for a specific user to connect an app."""
    connection = composio_client.get_entity(user_id).initiate_connection(app)
    return connection.redirectUrl

def execute_for_user(user_id: str, action: Action, params: dict) -> dict:
    """Execute an action as a specific user using their OAuth connection."""
    toolset = ComposioToolSet(entity_id=user_id)
    return toolset.execute_action(action=action, params=params)
```

## Best Practices

- Use `entity_id` for multi-tenant apps — each user gets their own OAuth connection
- Filter to specific `actions` rather than entire `apps` to reduce token usage in prompts
- Implement retry logic around `execute_action` for transient API failures (GitHub rate limits, Slack 429s)
- Use direct `execute_action` calls for deterministic workflows; LLM agents for open-ended tasks
- Log all tool calls with their parameters for debugging and audit trails
- Validate webhook signatures when receiving Slack/GitHub webhooks — Composio provides managed webhooks too
- Use Composio's **triggers** for event-driven automation (e.g., new GitHub PR → run review agent)
- Cache tool schemas — they don't change frequently and reduce API calls
- Set `max_iterations` conservatively (8-15) to prevent runaway agents
- Test integrations with sandbox/test accounts before connecting production systems

## Models to Use

- **Default**: `claude-sonnet-4-5` — agent orchestration, tool selection, multi-app workflows
- **Complex agentic systems**: `claude-opus-4-5` — multi-step planning, decision logic, error recovery
- **Simple integrations**: `claude-haiku-3-5` — direct `execute_action` calls, simple Slack/GitHub tasks
