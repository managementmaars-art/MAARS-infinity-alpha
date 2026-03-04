"""Vibe Coding App Builder - Chat-based full-stack app building."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
import uuid
import os
import json
from db import db
from auth import get_current_user
from models.schemas import User

router = APIRouter()
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


async def _get_vibe_llm_config(user_id: str):
    """Get user's preferred LLM for vibe coding."""
    config = await db.system_config.find_one(
        {"user_id": user_id, "config_type": "llm_preference"}, {"_id": 0}
    )
    if config:
        return config.get("provider", "openai"), config.get("model", "gpt-5.2")
    return "openai", "gpt-5.2"


@router.post("/vibe/projects")
async def create_vibe_project(request: Request, current_user: User = Depends(get_current_user)):
    """Create a new Vibe Coding project from a description."""
    data = await request.json()
    description = data.get("description", "")
    if not description:
        raise HTTPException(400, "Project description required")

    project = {
        "vibe_id": f"vibe_{uuid.uuid4().hex[:10]}",
        "user_id": current_user.user_id,
        "description": description,
        "title": description[:80],
        "files": [],
        "chat_history": [],
        "status": "creating",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Generate initial app structure using LLM
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        provider, model = await _get_vibe_llm_config(current_user.user_id)

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"vibe_{project['vibe_id']}",
            system_message="""You are an expert full-stack developer. The user describes an app they want to build. Generate a complete, working single-page application.

RULES:
1. Generate a SINGLE HTML file that includes all CSS and JavaScript inline
2. Use modern design with Tailwind CSS via CDN
3. Make it fully functional with local state management
4. Include responsive design
5. Use clean, production-quality code
6. If a backend is needed, simulate it with localStorage

Return ONLY valid JSON in this exact format:
{
  "title": "App Name",
  "description": "Brief description",
  "files": [
    {"name": "index.html", "language": "html", "content": "<!DOCTYPE html>...full code..."}
  ],
  "tech_stack": ["HTML", "CSS", "JavaScript", "Tailwind CSS"]
}

Do NOT include markdown formatting or code blocks. Return ONLY the JSON object."""
        ).with_model(provider, model)

        response = await chat.send_message(UserMessage(text=f"Build this app: {description}"))

        # Parse the JSON response
        try:
            # Clean response - strip markdown if present
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

            app_data = json.loads(cleaned)
            project["title"] = app_data.get("title", description[:80])
            project["files"] = app_data.get("files", [])
            project["tech_stack"] = app_data.get("tech_stack", [])
            project["status"] = "ready"
        except json.JSONDecodeError:
            # If JSON parsing fails, wrap the response as a single HTML file
            project["files"] = [{"name": "index.html", "language": "html", "content": response}]
            project["tech_stack"] = ["HTML", "CSS", "JavaScript"]
            project["status"] = "ready"

        project["chat_history"] = [
            {"role": "user", "content": description, "timestamp": datetime.now(timezone.utc).isoformat()},
            {"role": "assistant", "content": f"Generated {len(project['files'])} file(s) for '{project['title']}'", "timestamp": datetime.now(timezone.utc).isoformat()},
        ]
    except Exception as e:
        project["status"] = "error"
        project["error"] = str(e)[:300]

    await db.vibe_projects.insert_one(project)
    project.pop("_id", None)
    return project


@router.get("/vibe/projects")
async def list_vibe_projects(current_user: User = Depends(get_current_user)):
    """List all Vibe Coding projects."""
    items = await db.vibe_projects.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "vibe_id": 1, "title": 1, "description": 1, "status": 1, "tech_stack": 1, "created_at": 1, "updated_at": 1}
    ).sort("created_at", -1).to_list(50)
    return {"items": items}


@router.get("/vibe/projects/{vibe_id}")
async def get_vibe_project(vibe_id: str, current_user: User = Depends(get_current_user)):
    """Get a single Vibe Coding project with all files."""
    project = await db.vibe_projects.find_one(
        {"vibe_id": vibe_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.post("/vibe/projects/{vibe_id}/chat")
async def vibe_chat(vibe_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Send a message to modify an existing Vibe project."""
    data = await request.json()
    message = data.get("message", "")
    if not message:
        raise HTTPException(400, "Message required")

    project = await db.vibe_projects.find_one(
        {"vibe_id": vibe_id, "user_id": current_user.user_id}, {"_id": 0}
    )
    if not project:
        raise HTTPException(404, "Project not found")

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        provider, model = await _get_vibe_llm_config(current_user.user_id)

        # Build context from existing files
        files_context = ""
        for f in project.get("files", []):
            files_context += f"\n--- {f['name']} ---\n{f['content'][:2000]}\n"

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"vibe_chat_{vibe_id}_{uuid.uuid4().hex[:6]}",
            system_message=f"""You are modifying an existing web application. Here are the current files:
{files_context}

The user wants to make changes. Generate the COMPLETE updated files.
Return ONLY valid JSON:
{{"files": [{{"name": "filename", "language": "lang", "content": "full updated code"}}], "changes_summary": "what changed"}}

Return the COMPLETE file content, not just the changes. Do NOT use markdown code blocks."""
        ).with_model(provider, model)

        response = await chat.send_message(UserMessage(text=message))

        # Parse response
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
            update_data = json.loads(cleaned)
            new_files = update_data.get("files", [])
            changes = update_data.get("changes_summary", "Files updated")
        except json.JSONDecodeError:
            new_files = project.get("files", [])
            changes = "Applied changes (response parsing issue)"

        # Update chat history
        chat_history = project.get("chat_history", [])
        chat_history.append({"role": "user", "content": message, "timestamp": datetime.now(timezone.utc).isoformat()})
        chat_history.append({"role": "assistant", "content": changes, "timestamp": datetime.now(timezone.utc).isoformat()})

        await db.vibe_projects.update_one(
            {"vibe_id": vibe_id},
            {"$set": {
                "files": new_files if new_files else project.get("files", []),
                "chat_history": chat_history[-20:],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }}
        )

        updated = await db.vibe_projects.find_one({"vibe_id": vibe_id}, {"_id": 0})
        return updated

    except Exception as e:
        raise HTTPException(500, f"Chat failed: {str(e)[:200]}")


@router.get("/vibe/projects/{vibe_id}/preview")
async def preview_vibe_project(vibe_id: str, current_user: User = Depends(get_current_user)):
    """Get the HTML preview content for a Vibe project."""
    project = await db.vibe_projects.find_one(
        {"vibe_id": vibe_id, "user_id": current_user.user_id}, {"_id": 0, "files": 1}
    )
    if not project:
        raise HTTPException(404, "Project not found")

    # Find the main HTML file
    html_file = None
    for f in project.get("files", []):
        if f.get("name", "").endswith(".html"):
            html_file = f
            break

    if not html_file:
        return {"html": "<h1>No HTML file found</h1>"}

    return {"html": html_file.get("content", "")}


@router.delete("/vibe/projects/{vibe_id}")
async def delete_vibe_project(vibe_id: str, current_user: User = Depends(get_current_user)):
    """Delete a Vibe project."""
    result = await db.vibe_projects.delete_one({"vibe_id": vibe_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Project not found")
    return {"success": True}
