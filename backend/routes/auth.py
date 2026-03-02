"""Authentication routes - register, login, session, logout."""
import uuid
import httpx
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from db import db
from auth import (
    hash_password, verify_password, create_jwt_token,
    get_current_user, ADMIN_EMAIL
)
from models.schemas import UserCreate, UserLogin, User

router = APIRouter()


async def create_notification(user_id: str, ntype: str, title: str, message: str, link: str = None):
    await db.notifications.insert_one({
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "type": ntype,
        "title": title,
        "message": message,
        "link": link,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })


@router.post("/auth/register")
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_pw = hash_password(user_data.password)

    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hashed_pw,
        "picture": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)

    await create_notification(user_id, "welcome", "Welcome to MAARS Command!", "Your AI team of 21 specialists is ready. Start by chatting with any agent.", "/dashboard")

    token = create_jwt_token(user_id, user_data.email)
    is_admin = user_data.email == ADMIN_EMAIL
    return {"token": token, "user": {"user_id": user_id, "email": user_data.email, "name": user_data.name, "is_admin": is_admin}}


@router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user or not verify_password(user_data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token(user["user_id"], user["email"])
    is_admin = user["email"] == ADMIN_EMAIL
    return {"token": token, "user": {"user_id": user["user_id"], "email": user["email"], "name": user["name"], "is_admin": is_admin}}


@router.post("/auth/session")
async def exchange_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session")

            data = resp.json()
        except Exception:
            raise HTTPException(status_code=401, detail="Authentication failed")

    user = await db.users.find_one({"email": data["email"]}, {"_id": 0})
    if not user:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_doc = {
            "user_id": user_id,
            "email": data["email"],
            "name": data["name"],
            "picture": data.get("picture"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_doc)
        user = user_doc
    else:
        user_id = user["user_id"]
        if data.get("picture") and data["picture"] != user.get("picture"):
            await db.users.update_one({"user_id": user_id}, {"$set": {"picture": data["picture"]}})
            user["picture"] = data["picture"]

    session_token = data.get("session_token", f"session_{uuid.uuid4().hex}")
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    await db.user_sessions.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )

    return {"user_id": user_id, "email": user["email"], "name": user["name"], "picture": user.get("picture"), "is_admin": user["email"] == ADMIN_EMAIL}


@router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    user_doc = await db.users.find_one({"user_id": current_user.user_id}, {"_id": 0})
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at.isoformat() if isinstance(current_user.created_at, datetime) else current_user.created_at,
        "onboarding_completed": user_doc.get("onboarding_completed", False) if user_doc else False
    }


@router.post("/auth/onboarding-complete")
async def complete_onboarding(current_user: User = Depends(get_current_user)):
    await db.users.update_one(
        {"user_id": current_user.user_id},
        {"$set": {"onboarding_completed": True}}
    )
    return {"success": True}


@router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out"}
