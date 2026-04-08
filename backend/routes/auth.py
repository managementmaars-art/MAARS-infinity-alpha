"""Authentication routes - register, login, session, google oauth, logout."""
import os
import uuid
import httpx
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from db import db
from auth import (
    hash_password, verify_password, create_jwt_token,
    get_current_user, ADMIN_EMAIL
)
from models.schemas import UserCreate, UserLogin, User

router = APIRouter()

# Google OAuth config — set these in .env
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
# Where the browser is served from (frontend)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
# Where the API is served from (this backend)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


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

    # Auto-provision MAARS gateway key for this user (free plan budget)
    import secrets as _secrets
    await db.client_gateway_keys.insert_one({
        "user_id":            user_id,
        "key":                f"maars-sk-{_secrets.token_hex(20)}",
        "plan_id":            "free",
        "monthly_budget_usd": 0.0,
        "used_usd":           0.0,
        "cycle_start":        datetime.now(timezone.utc).isoformat(),
        "status":             "active",
        "created_at":         datetime.now(timezone.utc).isoformat(),
        "notes":              "",
    })

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


@router.get("/user/gateway-key")
async def get_user_gateway_key(current_user: User = Depends(get_current_user), reveal: bool = False):
    """Return the current user's MAARS gateway API key, usage stats, and connection info."""
    key_doc = await db.client_gateway_keys.find_one({"user_id": current_user.user_id}, {"_id": 0})
    if not key_doc:
        # Auto-provision if missing
        import secrets as _sec
        new_key = f"maars-sk-{_sec.token_hex(20)}"
        key_doc = {
            "user_id": current_user.user_id,
            "key": new_key,
            "plan_id": "free",
            "monthly_budget_usd": 0.0,
            "used_usd": 0.0,
            "total_calls": 0,
            "cycle_start": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.client_gateway_keys.insert_one(key_doc)

    key = key_doc.get("key", "")
    # Mask: show first 12 chars + dots + last 4
    if len(key) > 16:
        masked = key[:12] + "•" * 20 + key[-4:]
    else:
        masked = "•" * len(key)

    budget       = key_doc.get("monthly_budget_usd", 0.0)
    used         = key_doc.get("used_usd", 0.0)
    billing_mode = key_doc.get("billing_mode", "subscription")
    balance      = key_doc.get("balance_usd", 0.0)
    markup_pct   = key_doc.get("markup_pct", 0.0)

    # Compute remaining based on billing mode
    if billing_mode == "payg":
        remaining = round(balance, 6)
    elif billing_mode == "hybrid":
        sub_left = budget - used
        remaining = round(max(sub_left, 0) + max(balance, 0), 6)
    else:
        remaining = round(max(budget - used, 0), 6) if budget > 0 else None

    return {
        "key":                masked if not reveal else key,
        "key_revealed":       key if reveal else None,
        "masked_key":         masked,
        "status":             key_doc.get("status", "active"),
        "plan_id":            key_doc.get("plan_id", "free"),
        "billing_mode":       billing_mode,
        "monthly_budget_usd": budget,
        "balance_usd":        round(balance, 6),
        "markup_pct":         markup_pct,
        "used_usd":           round(used, 6),
        "remaining_usd":      remaining,
        "total_calls":        key_doc.get("total_calls", 0),
        "cycle_start":        key_doc.get("cycle_start", ""),
        "rpm_limit":          key_doc.get("rpm_limit", 60),
        "base_url":           "/api",
        "docs_url":           "/developer",
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


# ─── Google OAuth 2.0 ────────────────────────────────────────────────────────

@router.get("/auth/google")
async def google_login():
    """Redirect the browser to Google's OAuth consent screen."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth not configured — set GOOGLE_CLIENT_ID in .env")

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": f"{BACKEND_URL}/api/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    return RedirectResponse(url="https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))


@router.get("/auth/google/callback")
async def google_callback(code: str = None, error: str = None):
    """Handle Google's redirect back. Exchange code → user info → JWT → redirect to frontend."""
    frontend_error = f"{FRONTEND_URL}/login?error="

    if error or not code:
        return RedirectResponse(url=frontend_error + "oauth_cancelled")

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return RedirectResponse(url=frontend_error + "not_configured")

    async with httpx.AsyncClient() as client:
        try:
            # 1. Exchange authorization code for access token
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": f"{BACKEND_URL}/api/auth/google/callback",
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                return RedirectResponse(url=frontend_error + "token_exchange_failed")

            access_token = token_resp.json().get("access_token")

            # 2. Fetch Google user info
            info_resp = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if info_resp.status_code != 200:
                return RedirectResponse(url=frontend_error + "user_info_failed")

            google_user = info_resp.json()
        except Exception:
            return RedirectResponse(url=frontend_error + "oauth_failed")

    email = google_user.get("email")
    name = google_user.get("name") or email
    picture = google_user.get("picture", "")

    if not email:
        return RedirectResponse(url=frontend_error + "no_email")

    # 3. Find or create user in DB
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_doc = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(user_doc)
        await create_notification(
            user_id, "welcome",
            "Welcome to MAARS Command!",
            "Your AI team is ready. Start by chatting with any agent.",
            "/dashboard",
        )
        user = user_doc
    else:
        user_id = user["user_id"]
        update = {}
        if picture and picture != user.get("picture"):
            update["picture"] = picture
        if name and not user.get("name"):
            update["name"] = name
        if update:
            await db.users.update_one({"user_id": user_id}, {"$set": update})
            user.update(update)

    # 4. Mint JWT and redirect to frontend callback page
    token = create_jwt_token(user_id, email)
    is_admin = email == ADMIN_EMAIL

    qs = urlencode({
        "token": token,
        "user_id": user_id,
        "name": name,
        "email": email,
        "picture": picture,
        "is_admin": "true" if is_admin else "false",
    })
    return RedirectResponse(url=f"{FRONTEND_URL}/auth/google/callback?{qs}")
