"""Real-World Action Layer - Google OAuth, Gmail, Calendar integration."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
import os
import warnings
from db import db
from auth import get_current_user
from models.schemas import User

router = APIRouter()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REACT_APP_BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "")
REDIRECT_URI = f"{REACT_APP_BACKEND_URL}/api/oauth/gmail/callback"

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def _get_client_config():
    return {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


@router.get("/oauth/gmail/status")
async def gmail_status(current_user: User = Depends(get_current_user)):
    """Check if Google OAuth is connected for this user."""
    token = await db.google_tokens.find_one(
        {"user_id": current_user.user_id}, {"_id": 0, "email": 1, "connected_at": 1}
    )
    configured = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    return {
        "connected": bool(token),
        "configured": configured,
        "email": token.get("email", "") if token else "",
    }


@router.get("/oauth/gmail/login")
async def gmail_login(current_user: User = Depends(get_current_user)):
    """Start Google OAuth flow."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(400, "Google OAuth not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env")

    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_config(_get_client_config(), scopes=GMAIL_SCOPES, redirect_uri=REDIRECT_URI)
    url, state = flow.authorization_url(access_type="offline", prompt="consent")

    # Store state for verification
    await db.oauth_states.insert_one({
        "state": state, "user_id": current_user.user_id,
        "created_at": datetime.now(timezone.utc)
    })
    return {"auth_url": url}


@router.get("/oauth/gmail/callback")
async def gmail_callback(code: str = "", state: str = "", error: str = ""):
    """Handle Google OAuth callback."""
    if error:
        return RedirectResponse(f"/settings?error={error}")

    state_doc = await db.oauth_states.find_one({"state": state})
    if not state_doc:
        return RedirectResponse("/settings?error=invalid_state")

    user_id = state_doc["user_id"]
    await db.oauth_states.delete_one({"state": state})

    try:
        from google_auth_oauthlib.flow import Flow
        flow = Flow.from_client_config(_get_client_config(), scopes=GMAIL_SCOPES, redirect_uri=REDIRECT_URI)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            flow.fetch_token(code=code)

        creds = flow.credentials

        # Get user email
        from googleapiclient.discovery import build
        service = build("oauth2", "v2", credentials=creds)
        user_info = service.userinfo().get().execute()

        token_data = {
            "user_id": user_id,
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "expires_at": creds.expiry.isoformat() if creds.expiry else None,
            "email": user_info.get("email", ""),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.google_tokens.update_one(
            {"user_id": user_id}, {"$set": token_data}, upsert=True
        )
        return RedirectResponse("/settings?google=connected")
    except Exception as e:
        return RedirectResponse(f"/settings?error={str(e)[:100]}")


async def get_google_creds(user_id: str):
    """Get valid Google credentials for a user, refreshing if needed."""
    token = await db.google_tokens.find_one({"user_id": user_id}, {"_id": 0})
    if not token:
        return None

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GoogleRequest

    creds = Credentials(
        token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        token_uri=token.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token.get("client_id", GOOGLE_CLIENT_ID),
        client_secret=token.get("client_secret", GOOGLE_CLIENT_SECRET),
    )

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(GoogleRequest())
            await db.google_tokens.update_one(
                {"user_id": user_id},
                {"$set": {"access_token": creds.token, "expires_at": creds.expiry.isoformat() if creds.expiry else None}}
            )
        except Exception:
            return None
    return creds


@router.post("/actions/send-email")
async def send_email_action(request: Request, current_user: User = Depends(get_current_user)):
    """Send an email via Gmail API."""
    # Check execution mode
    mode = await db.system_config.find_one({"user_id": current_user.user_id, "mode": {"$exists": True}}, {"_id": 0})
    if not mode or mode.get("mode") != "execution":
        return {"status": "simulated", "message": "Email would be sent. Switch to Execution Mode to send real emails."}

    data = await request.json()
    to = data.get("to", "")
    subject = data.get("subject", "")
    body = data.get("body", "")

    if not to or not subject:
        raise HTTPException(400, "to and subject required")

    creds = await get_google_creds(current_user.user_id)
    if not creds:
        raise HTTPException(400, "Google account not connected. Go to Settings to connect.")

    try:
        from googleapiclient.discovery import build
        import base64
        from email.mime.text import MIMEText

        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"status": "sent", "message_id": sent.get("id", ""), "to": to, "subject": subject}
    except Exception as e:
        raise HTTPException(500, f"Failed to send email: {str(e)[:200]}")


@router.post("/actions/create-event")
async def create_calendar_event(request: Request, current_user: User = Depends(get_current_user)):
    """Create a Google Calendar event."""
    mode = await db.system_config.find_one({"user_id": current_user.user_id, "mode": {"$exists": True}}, {"_id": 0})
    if not mode or mode.get("mode") != "execution":
        return {"status": "simulated", "message": "Calendar event would be created. Switch to Execution Mode."}

    data = await request.json()
    summary = data.get("summary", "")
    start = data.get("start", "")
    end = data.get("end", "")

    if not summary or not start:
        raise HTTPException(400, "summary and start required")

    creds = await get_google_creds(current_user.user_id)
    if not creds:
        raise HTTPException(400, "Google account not connected. Go to Settings to connect.")

    try:
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": summary,
            "description": data.get("description", ""),
            "start": {"dateTime": start, "timeZone": data.get("timezone", "UTC")},
            "end": {"dateTime": end or start, "timeZone": data.get("timezone", "UTC")},
            "attendees": [{"email": e} for e in data.get("attendees", [])],
        }
        created = service.events().insert(calendarId="primary", body=event).execute()
        return {"status": "created", "event_id": created.get("id", ""), "link": created.get("htmlLink", "")}
    except Exception as e:
        raise HTTPException(500, f"Failed to create event: {str(e)[:200]}")


@router.get("/oauth/gmail/disconnect")
async def disconnect_gmail(current_user: User = Depends(get_current_user)):
    """Disconnect Google OAuth."""
    await db.google_tokens.delete_one({"user_id": current_user.user_id})
    return {"success": True}


@router.get("/actions/integrations")
async def list_action_integrations(current_user: User = Depends(get_current_user)):
    """List all available action integrations and their connection status."""
    google_token = await db.google_tokens.find_one(
        {"user_id": current_user.user_id}, {"_id": 0, "email": 1, "connected_at": 1}
    )
    google_configured = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

    integrations = [
        {
            "id": "google",
            "name": "Google Suite",
            "description": "Gmail, Calendar, Drive integration via OAuth",
            "connected": bool(google_token),
            "configured": google_configured,
            "email": google_token.get("email", "") if google_token else "",
            "actions": ["send_email", "create_event", "list_events"],
        },
    ]

    # Check system mode
    mode_config = await db.system_config.find_one(
        {"user_id": current_user.user_id, "mode": {"$exists": True}}, {"_id": 0}
    )
    current_mode = mode_config.get("mode", "simulation") if mode_config else "simulation"

    return {
        "integrations": integrations,
        "system_mode": current_mode,
    }


@router.post("/actions/test")
async def test_action(request: Request, current_user: User = Depends(get_current_user)):
    """Test an action to check if it would succeed without actually executing."""
    data = await request.json()
    action = data.get("action", "")

    if action == "send_email":
        creds = await get_google_creds(current_user.user_id)
        if not creds:
            return {"status": "error", "message": "Google account not connected"}
        return {"status": "ok", "message": "Email sending is available. Connected to Google."}

    elif action == "create_event":
        creds = await get_google_creds(current_user.user_id)
        if not creds:
            return {"status": "error", "message": "Google account not connected"}
        return {"status": "ok", "message": "Calendar access is available. Connected to Google."}

    return {"status": "error", "message": f"Unknown action: {action}"}
