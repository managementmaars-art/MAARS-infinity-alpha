"""Referral program — public + authenticated surface.

Public:
  GET /r/<code>  — redirects to signup with a tracking cookie that
                   /auth/signup reads to attach the referral.

Authenticated:
  GET  /referrals/me   — current user's code, stats, share URL
  POST /referrals/me   — force-create a code (idempotent — returns existing)
"""
from __future__ import annotations
import os

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse

from auth import get_current_user
from models.schemas import User
from services import referrals

router = APIRouter()

_COOKIE_NAME = "maars_ref"
_COOKIE_DAYS = 30


@router.get("/r/{code}")
async def referral_landing(code: str, request: Request):
    """Tracks the click + redirects to signup with the code in a cookie.

    30-day attribution window — industry standard. If the visitor signs
    up within 30 days, the cookie survives and /auth/signup attaches
    the referral. After 30 days the cookie expires naturally.
    """
    info = {
        "ip": request.client.host if request.client else None,
        "ua": request.headers.get("user-agent", ""),
        "referer": request.headers.get("referer", ""),
    }
    await referrals.record_click(code, request_info=info)
    # Redirect to signup page with cookie
    signup_url = os.environ.get("MAARS_SIGNUP_URL") or "/signup"
    resp = RedirectResponse(signup_url, status_code=302)
    resp.set_cookie(
        _COOKIE_NAME, code,
        max_age=60 * 60 * 24 * _COOKIE_DAYS,
        httponly=True, samesite="lax",
    )
    return resp


@router.get("/referrals/me")
async def my_referrals(current_user: User = Depends(get_current_user)):
    """Current user's code + stats + share URL."""
    # ensure code exists
    await referrals.get_or_create_code(current_user.user_id)
    return await referrals.stats_for_user(current_user.user_id)


@router.post("/referrals/me")
async def create_my_code(current_user: User = Depends(get_current_user)):
    """Force-create a referral code. Idempotent."""
    code = await referrals.get_or_create_code(current_user.user_id)
    return await referrals.stats_for_user(current_user.user_id)
