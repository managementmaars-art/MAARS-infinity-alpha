"""Chat CRUD, message sending, and feedback endpoints."""
import re as _re
import uuid
import asyncio
import base64
import logging
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Request
from db import db
from auth import get_current_user, User, ADMIN_EMAIL
from models.schemas import Chat, ChatCreate, MessageCreate
from shared.constants import SUBSCRIPTION_PLANS, EMERGENT_LLM_KEY, UPLOAD_DIR
from shared.utils import get_api_keys, create_notification
from services.llm_service import (
    auto_select_model, call_llm_with_fallback, detect_video_generation_request,
    detect_image_generation_request, detect_file_format_request, generate_file_from_content,
    MODEL_COSTS_MAP, get_credit_cost
)
from services.agent_service import (
    agent_execute_with_tools, build_workspace_context,
    background_commander_delegate, CLARIFICATION_INSTRUCTION as _AGENT_CLARIFICATION
)
from config import AGENT_TOOL_MAP

logger = logging.getLogger(__name__)
router = APIRouter()

CLARIFICATION_INSTRUCTION = """

IMPORTANT RESPONSE GUIDELINES:
- If the user's request is clear and specific, respond directly with your best professional output. Do NOT ask questions.
- Only ask a clarifying question if the request is genuinely ambiguous (e.g., "help me with marketing" with no details).
- When you DO need clarification, ask ONE focused question, not multiple.
- Default to action over clarification. When in doubt, give a comprehensive answer that covers likely interpretations.
- For technical/creative tasks, just do the work. Don't ask "what style" or "what tone" — use your professional judgment.
"""


@router.get("/chats")
async def get_chats(page: int = 1, limit: int = 50, current_user: User = Depends(get_current_user)):
    skip = (page - 1) * limit
    total = await db.chats.count_documents({"user_id": current_user.user_id})
    chats = await db.chats.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "messages": {"$slice": -1}, "chat_id": 1, "title": 1, "agent_id": 1, "user_id": 1, "created_at": 1, "updated_at": 1, "pinned_messages": 1, "shared_with_team": 1}
    ).sort("updated_at", -1).skip(skip).to_list(limit)
    
    for chat in chats:
        if isinstance(chat.get('created_at'), str):
            chat['created_at'] = datetime.fromisoformat(chat['created_at'])
        if isinstance(chat.get('updated_at'), str):
            chat['updated_at'] = datetime.fromisoformat(chat['updated_at'])
        for msg in chat.get('messages', []):
            if isinstance(msg.get('created_at'), str):
                msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    
    return {"chats": chats, "total": total, "page": page, "pages": max(1, -(-total // limit))}

@router.post("/chats", response_model=Chat)
async def create_chat(chat_data: ChatCreate, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"agent_id": chat_data.agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    chat_id = f"chat_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    
    chat_doc = {
        "chat_id": chat_id,
        "user_id": current_user.user_id,
        "agent_id": chat_data.agent_id,
        "title": chat_data.title or f"Chat with {agent['name']}",
        "messages": [],
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    await db.chats.insert_one(chat_doc)
    chat_doc['created_at'] = now
    chat_doc['updated_at'] = now
    return Chat(**chat_doc)

# ============== CHAT SEARCH ==============

@router.get("/chats/search")
async def search_chats(q: str = "", current_user: User = Depends(get_current_user)):
    """Search across all user's chats by message content."""
    if not q or len(q) < 2:
        raise HTTPException(400, "Search query must be at least 2 characters")

    query_lower = q.lower()
    user_chats = await db.chats.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "chat_id": 1, "title": 1, "agent_id": 1, "messages": 1, "updated_at": 1}
    ).sort("updated_at", -1).to_list(200)

    results = []
    for chat in user_chats:
        matching_messages = []
        for msg in chat.get("messages", []):
            content = msg.get("content", "")
            if query_lower in content.lower():
                # Get a snippet around the match
                idx = content.lower().find(query_lower)
                start = max(0, idx - 50)
                end = min(len(content), idx + len(q) + 50)
                snippet = ("..." if start > 0 else "") + content[start:end] + ("..." if end < len(content) else "")
                matching_messages.append({
                    "message_id": msg.get("message_id", ""),
                    "role": msg.get("role", ""),
                    "snippet": snippet,
                    "created_at": msg.get("created_at", "")
                })

        if matching_messages:
            results.append({
                "chat_id": chat["chat_id"],
                "title": chat.get("title", "Untitled"),
                "agent_id": chat.get("agent_id", ""),
                "match_count": len(matching_messages),
                "matches": matching_messages[:3],  # Top 3 matches per chat
                "updated_at": chat.get("updated_at", "")
            })

    return {"results": results, "total_matches": sum(r["match_count"] for r in results), "query": q}

@router.get("/chats/{chat_id}", response_model=Chat)
async def get_chat(chat_id: str, current_user: User = Depends(get_current_user)):
    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id}, {"_id": 0})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if isinstance(chat.get('created_at'), str):
        chat['created_at'] = datetime.fromisoformat(chat['created_at'])
    if isinstance(chat.get('updated_at'), str):
        chat['updated_at'] = datetime.fromisoformat(chat['updated_at'])
    for msg in chat.get('messages', []):
        if isinstance(msg.get('created_at'), str):
            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    
    return chat


@router.post("/chats/{chat_id}/messages")
async def send_message(chat_id: str, message_data: MessageCreate, current_user: User = Depends(get_current_user)):
    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id}, {"_id": 0})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    agent = await db.agents.find_one({"agent_id": chat["agent_id"]}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check user credits (admin bypasses credit check)
    is_admin = current_user.email == ADMIN_EMAIL
    user_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not user_sub:
        # Create default free subscription
        user_sub = {
            "user_id": current_user.user_id,
            "plan_id": "free" if not is_admin else "business",
            "credits": 50 if not is_admin else 999999,
            "credits_used": 0,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.subscriptions.insert_one(user_sub)
    
    # Enforce agent access based on subscription
    if not is_admin:
        agent_id = chat["agent_id"]
        is_commander = agent_id == "agent_commander"
        plan_id = user_sub.get("plan_id", "free")
        selected_agents = user_sub.get("selected_agents", [])
        
        if plan_id == "custom":
            has_commander = user_sub.get("has_commander", False)
            if is_commander and not has_commander:
                raise HTTPException(status_code=403, detail="Commander AI is not included in your custom package. Please upgrade or add Commander to your package.")
            if not is_commander and selected_agents and agent_id not in selected_agents:
                raise HTTPException(status_code=403, detail="This agent is not in your custom package. Please update your package to include this agent.")
        else:
            plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS.get("free"))
            if is_commander and not plan.get("includes_commander", False):
                raise HTTPException(status_code=403, detail="Commander AI is only available on Pro and Business plans. Please upgrade your plan.")
            if selected_agents and not is_commander and agent_id not in selected_agents:
                raise HTTPException(status_code=403, detail="This agent is not in your selected agents. Go to Settings to update your agent selection.")
    
    credits_remaining = user_sub.get("credits", 0)
    if credits_remaining <= 0 and not is_admin:
        raise HTTPException(status_code=402, detail="Insufficient credits. Please upgrade your plan or purchase more credits.")
    
    # Auto-select model if set to "auto" or not specified
    auto_selected = False
    model_reason = ""
    
    if message_data.model_provider == "auto" or (not message_data.model_provider and not message_data.model_name):
        # Auto-select based on content and agent role
        model_provider, model_name, model_reason = auto_select_model(message_data.content, agent.get("role", ""))
        auto_selected = True
    else:
        model_provider = message_data.model_provider or "openai"
        model_name = message_data.model_name or "gpt-5.2"
    
    # Create user message
    now = datetime.now(timezone.utc)
    user_msg = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "chat_id": chat_id,
        "role": "user",
        "content": message_data.content,
        "attachments": message_data.attachments,
        "model_used": f"{model_provider}/{model_name}",
        "auto_selected": auto_selected,
        "model_reason": model_reason if auto_selected else None,
        "created_at": now.isoformat()
    }
    
    # Get AI response
    try:
        api_keys = await get_api_keys()
        
        # Build conversation history for context
        chat_messages = chat.get("messages", [])
        history_lines = []
        for prev_msg in chat_messages[-20:]:  # Last 20 messages for context
            role_label = "User" if prev_msg.get("role") == "user" else "Assistant"
            history_lines.append(f"{role_label}: {prev_msg.get('content', '')[:1500]}")
        
        conversation_context = ""
        if history_lines:
            conversation_context = "--- CONVERSATION HISTORY ---\n" + "\n".join(history_lines) + "\n--- END HISTORY ---\n\nLatest message from user:\n"
        
        full_user_content = conversation_context + message_data.content
        
        # Image Analysis: When user uploads images, add vision instructions
        has_images = bool(message_data.attachments and any(
            att.startswith("data:image") or att.startswith("/files/") 
            for att in (message_data.attachments or []) if isinstance(att, str)
        ))
        if has_images:
            image_instruction = (
                "\n\n[VISION ACTIVE: The user has attached image(s). Analyze them carefully and thoroughly. "
                "1) IDENTIFY: Detect and name any products, brands, models, objects, text, people, or locations visible. "
                "Be as specific as possible (e.g. 'iPhone 16 Pro Max in Desert Titanium' not just 'a phone'). "
                "2) DESCRIBE: Note colors, materials, condition, setting, and distinguishing features. "
                "3) RESEARCH: If you identify a product, use the product_scan tool to search for detailed specs, pricing, "
                "reviews, and high-quality reference images from the web. "
                "4) ACT: If the user asks for a commercial video, ad, or marketing content about the product, "
                "use all gathered data (your visual analysis + product scan results) to create the best possible output. "
                "5) For video generation requests, craft a detailed cinematic prompt using the identified product name "
                "and professional reference imagery found via product_scan.]"
            )
            full_user_content += image_instruction
        
        # Build enhanced system prompt with clarification instruction
        enhanced_agent_prompt = agent["system_prompt"] + CLARIFICATION_INSTRUCTION
        
        # Web Search: Auto-browse the internet when the question needs current data
        web_search_context = None
        try:
            from services.web_search import browse_web_for_message
            web_ctx = await browse_web_for_message(message_data.content)
            if web_ctx:
                # Inject into user message content so LLM treats it as input to respond to
                full_user_content = web_ctx + "\n\nUser's question: " + full_user_content
                web_search_context = True
                logger.info(f"Web browse: Injected web data for '{message_data.content[:60]}...'")
        except Exception as ws_err:
            logger.error(f"Web browse error: {ws_err}")
        
        # Inject shared workspace context (tasks, other agents' work)
        workspace_ctx = await build_workspace_context(current_user.user_id, agent.get("agent_id", ""))
        if workspace_ctx:
            enhanced_agent_prompt += workspace_ctx
        
        # RAG: Search agent's knowledge base and inject relevant context
        try:
            from services.rag_service import search_knowledge_base, build_rag_context
            kb_count = await db.knowledge_chunks.count_documents({"agent_id": agent.get("agent_id", "")})
            if kb_count > 0:
                rag_results = await search_knowledge_base(
                    db, agent.get("agent_id", ""), message_data.content,
                    top_k=5, threshold=0.10
                )
                if rag_results:
                    rag_context = build_rag_context(rag_results)
                    enhanced_agent_prompt += rag_context
                    logger.info(f"RAG: Injected {len(rag_results)} knowledge chunks for {agent.get('agent_id')}")
        except Exception as rag_err:
            logger.error(f"RAG retrieval error: {rag_err}")
        
        # Apply user-specific agent overrides (personality, temperature, etc.)
        user_override = await db.user_agent_overrides.find_one(
            {"user_id": current_user.user_id, "agent_id": agent.get("agent_id")}, {"_id": 0}
        )
        if user_override:
            override_parts = []
            if user_override.get("personality_tone"):
                override_parts.append(f"User-requested personality adjustment: {user_override['personality_tone']}")
            if user_override.get("custom_instructions"):
                override_parts.append(f"User-specific instructions: {user_override['custom_instructions']}")
            if override_parts:
                enhanced_agent_prompt += "\n\n--- USER CUSTOMIZATION ---\n" + "\n".join(override_parts)
        
        # Check if this is Commander AI - use delegation
        is_commander = agent.get("is_commander", False) or agent.get("agent_id") == "agent_commander"
        
        delegation_data = None
        execution_steps = None
        
        if is_commander:
            # Run Commander delegation as background task (takes 2-3 min for multiple agents)
            processing_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
            processing_msg = {
                "message_id": processing_msg_id,
                "chat_id": chat_id,
                "role": "assistant",
                "content": f"Analyzing your goal and deploying specialists... This will take a moment as I coordinate multiple agents.\n\nGoal: {message_data.content}",
                "model_used": f"{model_provider}/{model_name}",
                "agent_id": agent.get("agent_id"),
                "created_at": now.isoformat(),
                "commander_status": "processing"
            }
            
            # Save user msg + processing msg immediately
            await db.chats.update_one(
                {"chat_id": chat_id},
                {"$push": {"messages": {"$each": [user_msg, processing_msg]}}, "$set": {"updated_at": now.isoformat()}}
            )
            
            # Start background task
            asyncio.create_task(background_commander_delegate(
                message_data.content, chat_id, processing_msg_id, api_keys, current_user.user_id
            ))
            
            # Deduct 1 credit for the commander call
            await db.subscriptions.update_one({"user_id": current_user.user_id}, {"$inc": {"credits": -1}})
            
            return {
                "user_message": user_msg,
                "assistant_message": processing_msg,
                "credits_used": 1
            }
        else:
            # Try tool-augmented execution first
            tool_result = await agent_execute_with_tools(
                agent, full_user_content, chat_id, api_keys,
                model_provider, model_name, current_user.user_id,
                message_data.attachments
            )
            
            if tool_result:
                response_text = tool_result["content"]
                execution_steps = tool_result.get("execution_steps")
            else:
                # Get agent-level temperature and max_tokens settings, with user overrides taking priority
                agent_temp = agent.get("temperature")
                agent_max_tokens = agent.get("max_tokens")
                if user_override:
                    if user_override.get("temperature") is not None:
                        agent_temp = user_override["temperature"]
                    if user_override.get("max_tokens") is not None:
                        agent_max_tokens = user_override["max_tokens"]
                response_text, model_provider, model_name = await call_llm_with_fallback(
                    api_keys, model_provider, model_name,
                    enhanced_agent_prompt, full_user_content,
                    message_data.attachments, chat_id,
                    temperature=agent_temp, max_tokens=agent_max_tokens
                )
        
    except Exception as e:
        logger.error(f"LLM error: {e}")
        response_text = f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    # Agent-to-Agent Collaboration: check if response contains consultation requests
    try:
        if "[CONSULT:" in response_text:
            import re
            consult_matches = re.findall(r'\[CONSULT:(\w+)\](.*?)\[/CONSULT\]', response_text, re.DOTALL)
            for consult_agent_id, consult_query in consult_matches:
                consult_agent = await db.agents.find_one({"agent_id": consult_agent_id})
                if consult_agent:
                    try:
                        consult_prompt = f"A colleague ({agent.get('name')}, {agent.get('role')}) is asking for your expert input. Give a concise, direct answer. Do not ask questions.\n\nTheir question: {consult_query.strip()}"
                        consult_response, _, _ = await call_llm_with_fallback(
                            api_keys, consult_agent.get("model_provider", "openai"),
                            consult_agent.get("model_name", "gpt-5.2"),
                            consult_agent["system_prompt"], consult_prompt, [], chat_id
                        )
                        # Replace the consultation tag with the actual response
                        tag = f"[CONSULT:{consult_agent_id}]{consult_query}[/CONSULT]"
                        replacement = f"\n\n**Input from {consult_agent['name']} ({consult_agent['role']}):**\n{consult_response}\n"
                        response_text = response_text.replace(tag, replacement)
                    except Exception as ce:
                        logger.error(f"Consultation with {consult_agent_id} failed: {ce}")
                        response_text = response_text.replace(f"[CONSULT:{consult_agent_id}]{consult_query}[/CONSULT]", f"\n(Tried to consult {consult_agent.get('name')} but they were unavailable)\n")
    except Exception as collab_err:
        logger.error(f"Collaboration processing error: {collab_err}")
    
    # Auto-detect image generation requests (only if agent has can_generate_image permission)
    generated_image = None
    if agent.get("can_generate_image", False) and detect_image_generation_request(message_data.content, agent.get("role", "")):
        try:
            api_keys_img = await get_api_keys()
            img_api_key = api_keys_img.get("emergent") or EMERGENT_LLM_KEY
            
            # Refine prompt for professional-grade image output
            img_prompt = message_data.content
            try:
                from emergentintegrations.llm.chat import LlmChat, UserMessage as UM
                prompt_chat = LlmChat(
                    api_key=img_api_key,
                    session_id=f"imgprompt_{uuid.uuid4().hex[:8]}",
                    system_message="""You are an expert prompt engineer for Gemini image generation. Write prompts that produce stunning, professional images.
Rules:
- Output ONLY the image prompt. No explanations.
- Be detailed about every visual element: style, composition, color palette, lighting, mood.
- For LOGOS: vector-style clean design, typography, exact colors, white background.
- For ILLUSTRATIONS: art style, medium, palette, mood, lighting.
- For MARKETING: layout, hierarchy, brand colors, call-to-action placement."""
                ).with_model("openai", "gpt-4o-mini")
                img_prompt = await prompt_chat.send_message(UM(text=f"User request: {message_data.content}\n\nCreative brief:\n{response_text[:2000]}"))
            except Exception as prompt_err:
                logger.warning(f"Prompt refinement failed, using original: {prompt_err}")
            
            # Use Gemini Nano Banana 2 for image generation
            import base64 as b64
            from emergentintegrations.llm.chat import LlmChat as ImgChat, UserMessage as ImgMsg
            img_chat = ImgChat(
                api_key=img_api_key,
                session_id=f"imggen_{uuid.uuid4().hex[:8]}",
                system_message="You are an image generation assistant. Generate the requested image."
            )
            img_chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
            _, gen_images = await img_chat.send_message_multimodal_response(ImgMsg(text=img_prompt[:2000]))
            
            if gen_images and len(gen_images) > 0:
                file_id = uuid.uuid4().hex[:10]
                filename = f"{file_id}_generated.png"
                filepath = UPLOAD_DIR / filename
                image_bytes = b64.b64decode(gen_images[0]["data"])
                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                generated_image = {
                    "filename": filename,
                    "url": f"/files/{filename}",
                    "model": "gemini-nano-banana-2",
                    "prompt": img_prompt[:500]
                }
                logger.info(f"Generated image via Nano Banana 2: {message_data.content[:80]}")
                # Log image generation usage separately
                try:
                    img_usage = {
                        "log_id": f"usage_{uuid.uuid4().hex[:10]}",
                        "user_id": current_user.user_id,
                        "chat_id": chat_id,
                        "agent_id": chat["agent_id"],
                        "model": "gemini/gemini-3-pro-image-preview",
                        "provider": "gemini",
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "images_generated": 1,
                        "estimated_cost_usd": 0.02,
                        "type": "image_generation",
                        "key_source": "emergent",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                    await db.usage_logs.insert_one(img_usage)
                except Exception:
                    pass
        except Exception as img_err:
            logger.error(f"Image generation failed: {img_err}")
            # Don't fail the entire message, just skip image generation
    
    # Auto-detect video generation requests (only if agent has can_generate_video permission)
    generated_video = None
    video_generating = False
    if agent.get("can_generate_video", False) and not generated_image and detect_video_generation_request(message_data.content, agent.get("role", "")):
        video_generating = True
        # Video generation happens in background after response is sent
    
    # Auto-detect file format requests (check agent permissions)
    generated_file = None
    requested_format = detect_file_format_request(message_data.content)
    can_gen_files = agent.get("can_generate_files", True)
    can_gen_pdf = agent.get("can_generate_pdf", True)
    if requested_format and response_text and not generated_image and can_gen_files:
        if requested_format == "pdf" and not can_gen_pdf:
            pass  # Agent not allowed to generate PDFs
        else:
            try:
                # Create a clean filename from the chat context
                words = _re.sub(r'[^\w\s]', '', message_data.content.lower()).split()[:4]
                filename_base = '_'.join(words) if words else 'document'
                filepath, filename, content_type = generate_file_from_content(
                    response_text, requested_format, filename_base
                )
                generated_file = {
                    "filename": filename,
                    "url": f"/files/{filename}",
                    "format": requested_format,
                    "content_type": content_type,
                    "size": filepath.stat().st_size
                }
                logger.info(f"Auto-generated {requested_format} file: {filename}")
            except Exception as file_err:
                logger.error(f"Auto file generation failed: {file_err}")
    
    # Create assistant message
    assistant_msg = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "chat_id": chat_id,
        "role": "assistant",
        "content": response_text,
        "model_used": f"{model_provider}/{model_name}",
        "agent_id": agent.get("agent_id"),
        "agent_name": agent.get("name"),
        "agent_avatar": agent.get("avatar"),
        "web_searched": bool(web_search_context),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if delegation_data:
        assistant_msg["delegation_data"] = delegation_data
    if execution_steps:
        assistant_msg["execution_steps"] = execution_steps
    if generated_image:
        assistant_msg["generated_image"] = generated_image
    if generated_video:
        assistant_msg["generated_video"] = generated_video
    if generated_file:
        assistant_msg["generated_file"] = generated_file
    if video_generating:
        assistant_msg["video_generating"] = True
    
    # Update chat
    await db.chats.update_one(
        {"chat_id": chat_id},
        {
            "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    # Deduct credits based on model used
    model_used_for_credits = assistant_msg.get("model_used", "gpt-5.2")
    credits_to_deduct = get_credit_cost(model_used_for_credits, has_image=bool(generated_image), has_video=video_generating)
    await db.subscriptions.update_one(
        {"user_id": current_user.user_id},
        {"$inc": {"credits": -credits_to_deduct, "credits_used": credits_to_deduct}}
    )
    
    # Log API usage for cost tracking
    try:
        input_text = message_data.content + (agent.get("system_prompt", "") or "")
        est_input_tokens = max(len(input_text) // 4, 50)
        est_output_tokens = max(len(response_text) // 4, 50)
        
        model_used = assistant_msg.get("model_used", "gpt-5.2")
        provider_used = agent.get("model_provider", "openai")
        
        model_clean = model_used.split("/")[-1] if "/" in model_used else model_used
        costs = MODEL_COSTS_MAP.get(model_clean, {"input": 2.50, "output": 10.00, "provider": provider_used})
        est_cost = (est_input_tokens * costs["input"] / 1_000_000) + (est_output_tokens * costs["output"] / 1_000_000)
        
        usage_log = {
            "log_id": f"usage_{uuid.uuid4().hex[:10]}",
            "user_id": current_user.user_id,
            "chat_id": chat_id,
            "agent_id": chat["agent_id"],
            "model": model_used,
            "provider": provider_used,
            "input_tokens": est_input_tokens,
            "output_tokens": est_output_tokens,
            "estimated_cost_usd": round(est_cost, 6),
            "key_source": api_keys.get("active_provider", "emergent"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.usage_logs.insert_one(usage_log)
    except Exception as log_err:
        logger.error(f"Usage logging error: {log_err}")
    
    # Update title if first message
    if len(chat.get("messages", [])) == 0:
        title = message_data.content[:50] + "..." if len(message_data.content) > 50 else message_data.content
        await db.chats.update_one({"chat_id": chat_id}, {"$set": {"title": title}})
    
    # Get updated credits
    updated_sub = await db.subscriptions.find_one({"user_id": current_user.user_id}, {"_id": 0})
    credits_remaining = updated_sub.get("credits", 0) if updated_sub else 0
    
    # Low credits notification
    if credits_remaining > 0 and credits_remaining <= 20:
        existing_low = await db.notifications.find_one({"user_id": current_user.user_id, "type": "credits_low", "read": False})
        if not existing_low:
            await create_notification(current_user.user_id, "credits_low", "Credits Running Low!", f"You have {credits_remaining} credits left. Consider upgrading your plan or purchasing more credits.", "/pricing")
    
    # Start background video generation if needed
    if video_generating:
        user_attachments = message_data.attachments or []
        user_attachment_files = message_data.attachment_files or []
        async def _bg_video_gen():
            try:
                api_keys_vid = await get_api_keys()
                vid_api_key = api_keys_vid.get("emergent") or EMERGENT_LLM_KEY
                
                vid_prompt = message_data.content
                if len(response_text) > 50:
                    try:
                        from emergentintegrations.llm.chat import LlmChat, UserMessage as UM
                        # Include product scan data if agent found any via tools
                        extra_context = ""
                        if execution_steps:
                            for step in execution_steps:
                                if step.get("tool") == "product_scan" and step.get("result"):
                                    extra_context = f"\n\nProduct Research Data:\n{step['result'][:1500]}"
                                    break
                        pc = LlmChat(api_key=vid_api_key, session_id=f"vidp_{uuid.uuid4().hex[:6]}", system_message="You are a professional video prompt engineer for Sora 2 AI. Convert the description into a detailed cinematic video prompt (max 200 words). Include: scene composition, camera movement (dolly, crane, tracking shot), lighting (golden hour, studio, neon), subject action/motion, mood/atmosphere, color grading style, depth of field. If product research data is provided, use the EXACT product name and key features in the prompt for accuracy. Be specific and visual. Output ONLY the prompt.").with_model("openai", "gpt-4o-mini")
                        vid_prompt = await pc.send_message(UM(text=f"User: {message_data.content}\n\nDirector's brief:\n{response_text[:2000]}{extra_context}"))
                    except Exception:
                        pass
                
                from emergentintegrations.llm.openai.video_generation import OpenAIVideoGeneration
                vg = OpenAIVideoGeneration(api_key=vid_api_key)
                
                # Check if user attached an image for image-to-video
                source_image_path = None
                source_mime = "image/jpeg"
                
                # Check attachment_files first (saved files with paths)
                for af in user_attachment_files:
                    if af.get("type", "").startswith("image/"):
                        file_url = af.get("file_url", "")
                        fname = file_url.split("/")[-1] if file_url else ""
                        fpath = UPLOAD_DIR / fname
                        if fpath.exists():
                            source_image_path = str(fpath)
                            source_mime = af.get("type", "image/jpeg")
                            logger.info(f"Using uploaded image for video: {fname}")
                            break
                
                # Fallback: check base64 attachments
                if not source_image_path:
                    for att in user_attachments:
                        if isinstance(att, str) and att.startswith("data:image/"):
                            # Save base64 image to disk
                            try:
                                header, b64data = att.split(",", 1)
                                mime = header.split(":")[1].split(";")[0]
                                ext = mime.split("/")[1].replace("jpeg", "jpg")
                                img_bytes = base64.b64decode(b64data)
                                tmp_name = f"{uuid.uuid4().hex[:10]}_vidref.{ext}"
                                tmp_path = UPLOAD_DIR / tmp_name
                                with open(tmp_path, 'wb') as f:
                                    f.write(img_bytes)
                                source_image_path = str(tmp_path)
                                source_mime = mime
                                logger.info(f"Saved base64 image for video: {tmp_name}")
                                break
                            except Exception as b64_err:
                                logger.warning(f"Failed to decode base64 image: {b64_err}")
                
                # Also check if we just generated an image - use it as source for video
                if not source_image_path and generated_image and generated_image.get("filename"):
                    img_path = UPLOAD_DIR / generated_image["filename"]
                    if img_path.exists():
                        source_image_path = str(img_path)
                        source_mime = "image/png"
                
                # Check if product_scan downloaded a high-quality reference image
                if not source_image_path and execution_steps:
                    for step in execution_steps:
                        if step.get("tool") == "product_scan" and step.get("result"):
                            # Extract downloaded reference image path from product scan result
                            import re as _re_vid
                            ref_match = _re_vid.search(r'Downloaded high-res reference image: (.+?)\]', step["result"])
                            if ref_match:
                                ref_path = ref_match.group(1).strip()
                                from pathlib import Path as _P
                                if _P(ref_path).exists():
                                    source_image_path = ref_path
                                    source_mime = "image/jpeg"
                                    logger.info(f"Using product scan reference image for video: {ref_path}")
                                    break
                
                if source_image_path:
                    logger.info(f"Starting Sora 2 image-to-video: image={source_image_path}, prompt={vid_prompt[:80]}...")
                else:
                    logger.info(f"Starting Sora 2 text-to-video: prompt={vid_prompt[:100]}...")
                
                def _sync_gen():
                    kwargs = dict(prompt=vid_prompt[:2000], model="sora-2", size="1280x720", duration=8, max_wait_time=600)
                    if source_image_path:
                        kwargs["image_path"] = source_image_path
                        kwargs["mime_type"] = source_mime
                    return vg.text_to_video(**kwargs)
                
                vb = await asyncio.to_thread(_sync_gen)
                logger.info(f"Video gen result: type={type(vb)}, has_data={bool(vb)}, size={len(vb) if vb else 0}")
                
                # Retry once if empty
                if not vb:
                    logger.warning("Sora 2 returned empty on first attempt, retrying in 30s...")
                    await asyncio.sleep(30)
                    vb = await asyncio.to_thread(_sync_gen)
                    logger.info(f"Video gen retry result: type={type(vb)}, has_data={bool(vb)}, size={len(vb) if vb else 0}")
                
                if vb:
                    fid = uuid.uuid4().hex[:10]
                    fn = f"{fid}_video.mp4"
                    fp = UPLOAD_DIR / fn
                    vg.save_video(vb, str(fp))
                    vid_data = {"filename": fn, "url": f"/files/{fn}", "model": "sora-2", "prompt": vid_prompt[:500]}
                    await db.chats.update_one(
                        {"chat_id": chat_id, "messages.message_id": assistant_msg["message_id"]},
                        {"$set": {"messages.$.generated_video": vid_data, "messages.$.video_generating": False}}
                    )
                    logger.info(f"Background video generated: {fn}")
                else:
                    error_msg = "Sora 2 returned no video data after retry. The generation may have timed out or been rejected."
                    logger.error(error_msg)
                    await db.chats.update_one(
                        {"chat_id": chat_id, "messages.message_id": assistant_msg["message_id"]},
                        {"$set": {"messages.$.video_generating": False, "messages.$.video_error": error_msg}}
                    )
            except Exception as ve:
                error_detail = str(ve)[:300]
                logger.error(f"Background video gen failed: {error_detail}")
                await db.chats.update_one(
                    {"chat_id": chat_id, "messages.message_id": assistant_msg["message_id"]},
                    {"$set": {"messages.$.video_generating": False, "messages.$.video_error": f"Video generation error: {error_detail}"}}
                )
        asyncio.create_task(_bg_video_gen())
    
    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg,
        "model_used": f"{model_provider}/{model_name}",
        "auto_selected": auto_selected,
        "model_reason": model_reason if auto_selected else None,
        "credits_deducted": credits_to_deduct,
        "credits_remaining": credits_remaining,
        "generated_image": generated_image,
        "generated_video": generated_video,
        "generated_file": generated_file
    }


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str, current_user: User = Depends(get_current_user)):
    result = await db.chats.delete_one({"chat_id": chat_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"message": "Chat deleted"}



# ============== MESSAGE FEEDBACK ==============

@router.post("/chats/{chat_id}/messages/{message_id}/feedback")
async def submit_message_feedback(chat_id: str, message_id: str, request: Request, current_user: User = Depends(get_current_user)):
    """Submit thumbs up/down feedback on an assistant message."""
    data = await request.json()
    feedback = data.get("feedback")  # "up", "down", or null (remove)
    if feedback not in ("up", "down", None):
        raise HTTPException(400, "feedback must be 'up', 'down', or null")

    chat = await db.chats.find_one({"chat_id": chat_id, "user_id": current_user.user_id}, {"_id": 0})
    if not chat:
        raise HTTPException(404, "Chat not found")

    # Find the message and update feedback
    messages = chat.get("messages", [])
    found = False
    for msg in messages:
        if msg.get("message_id") == message_id and msg.get("role") == "assistant":
            msg["feedback"] = feedback
            msg["feedback_at"] = datetime.now(timezone.utc).isoformat()
            msg["feedback_by"] = current_user.user_id
            found = True
            break

    if not found:
        raise HTTPException(404, "Message not found")

    await db.chats.update_one({"chat_id": chat_id}, {"$set": {"messages": messages}})
    return {"success": True, "feedback": feedback}




# ============== CHAT EXPORT ==============

@router.get("/chats/{chat_id}/export")
async def export_chat(chat_id: str, current_user: User = Depends(get_current_user)):
    """Export a chat as a formatted text document."""
    chat = await db.chats.find_one(
        {"chat_id": chat_id, "user_id": current_user.user_id},
        {"_id": 0}
    )
    if not chat:
        raise HTTPException(404, "Chat not found")

    # Get agent info
    agent = await db.agents.find_one(
        {"agent_id": chat.get("agent_id", "")},
        {"_id": 0, "name": 1, "role": 1}
    )
    agent_name = agent.get("name", "AI Agent") if agent else "AI Agent"
    agent_role = agent.get("role", "") if agent else ""

    lines = [
        f"Chat Export: {chat.get('title', 'Untitled')}",
        f"Agent: {agent_name} ({agent_role})",
        f"Date: {chat.get('created_at', 'Unknown')}",
        "=" * 60,
        "",
    ]

    for msg in chat.get("messages", []):
        role = "You" if msg.get("role") == "user" else agent_name
        timestamp = msg.get("created_at", "")
        content = msg.get("content", "")
        lines.append(f"[{role}] {timestamp}")
        lines.append(content)
        lines.append("")

    return {"content": "\n".join(lines), "title": chat.get("title", "chat_export"), "message_count": len(chat.get("messages", []))}


# ============== PIN MESSAGES ==============

@router.post("/chats/{chat_id}/messages/{message_id}/pin")
async def toggle_pin_message(chat_id: str, message_id: str, current_user: User = Depends(get_current_user)):
    """Toggle pin status on a message."""
    chat = await db.chats.find_one(
        {"chat_id": chat_id, "user_id": current_user.user_id},
        {"_id": 0, "messages": 1}
    )
    if not chat:
        raise HTTPException(404, "Chat not found")

    messages = chat.get("messages", [])
    found = False
    new_pinned = False
    for msg in messages:
        if msg.get("message_id") == message_id:
            msg["pinned"] = not msg.get("pinned", False)
            new_pinned = msg["pinned"]
            found = True
            break

    if not found:
        raise HTTPException(404, "Message not found")

    await db.chats.update_one({"chat_id": chat_id}, {"$set": {"messages": messages}})
    return {"success": True, "pinned": new_pinned, "message_id": message_id}


@router.get("/chats/{chat_id}/pinned")
async def get_pinned_messages(chat_id: str, current_user: User = Depends(get_current_user)):
    """Get all pinned messages in a chat."""
    chat = await db.chats.find_one(
        {"chat_id": chat_id, "user_id": current_user.user_id},
        {"_id": 0, "messages": 1}
    )
    if not chat:
        raise HTTPException(404, "Chat not found")

    pinned = [m for m in chat.get("messages", []) if m.get("pinned")]
    return pinned
