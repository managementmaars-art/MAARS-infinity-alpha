"""Service-specific workflow nodes — ergonomic wrappers around each
vendor's API. Thin; each one is essentially a signed http_request with
the right payload shape + auth.

Categories:
  Control-flow:  respond_webhook, wait_for_webhook, approval
  Dev tools:     github, gitlab, jira, linear, asana, trello, clickup, monday
  CRM/Support:   stripe_op, hubspot_op, salesforce_op, intercom_send,
                 zendesk_ticket, freshdesk_ticket
  Marketing:     mailchimp_subscribe, typeform_list, sendgrid_send
  Enrichment:    clearbit_enrich, dropcontact_enrich, openweather_get
  Storage:       google_drive_upload, dropbox_upload, box_upload
  Calendar/Mtg:  calendly_list, zoom_create_meeting
  Commerce:      shopify_op
  Search:        algolia_op, typesense_op
  Comms:         twilio_sms

All tools follow the same signature:
  async def fn(user_id, params, inp, ctx) -> dict
"""
from __future__ import annotations
import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────

async def _http(method: str, url: str, **kw) -> tuple[int, Any, dict]:
    """Small wrapper around the shared httpx client."""
    from services.http_client import get_client
    client = await get_client()
    timeout = kw.pop("timeout", 30)
    r = await client.request(method, url, timeout=timeout, **kw)
    try:
        body = r.json() if (r.headers.get("content-type") or "").startswith("application/json") else r.text
    except Exception:
        body = r.text
    return r.status_code, body, dict(r.headers)


def _tok(params: dict, *env_fallback: str) -> str | None:
    return params.get("token") or next((os.environ.get(n) for n in env_fallback if os.environ.get(n)), None)


async def _from_vault(user_id: str, provider: str, kind: str = "oauth") -> str | None:
    try:
        from services import credential_vault
        c = await credential_vault.get(provider, user_id=user_id, kind=kind)
        return c.secret if c else None
    except Exception:
        return None


def _ok(status: int, body: Any, **extra) -> dict:
    return {"ok": 200 <= status < 400, "status": status, "body": body, **extra}


# ── Phase C: control-flow nodes ──────────────────────────────────────

async def t_respond_webhook(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Send a custom response to the inbound webhook that triggered this
    run. The response is stored under `pending_webhook_responses.{run_id}`;
    the webhooks_in route polls for it and returns when set.

    params.status: HTTP status (default 200)
    params.body:   response body (dict or string)
    params.headers: optional response headers

    n8n calls this "Respond to Webhook" — lets you return something
    meaningful to the caller from within the flow.
    """
    from db import db
    run_id = (ctx or {}).get("run", {}).get("id")
    if not run_id:
        return {"ok": False, "error": "run_id missing from ctx"}
    await db.pending_webhook_responses.update_one(
        {"_id": run_id},
        {"$set": {
            "_id": run_id,
            "status": int(params.get("status", 200)),
            "body": params.get("body", {}),
            "headers": params.get("headers") or {},
            "set_at": time.time(),
        }},
        upsert=True,
    )
    return {"ok": True, "run_id": run_id, "response_set": True}


async def t_wait_for_webhook(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Pause the workflow until an external event hits
    `/api/webhooks/resume/{resume_token}`. Returns the resume payload
    as this node's output.

    params.timeout_s: max wait (default 3600 / 1 hour, hard cap 86400)
    params.description: optional — shown in the resume UI

    On timeout, returns {ok:false, error:"timeout"} so downstream on_failure
    branches can fire.
    """
    from db import db
    run_id = (ctx or {}).get("run", {}).get("id")
    token = secrets.token_urlsafe(24)
    timeout_s = max(10, min(int(params.get("timeout_s", 3600)), 86400))

    await db.workflow_wait_tokens.insert_one({
        "token": token,
        "run_id": run_id,
        "user_id": user_id,
        "created_at": time.time(),
        "expires_at": time.time() + timeout_s,
        "description": params.get("description", ""),
        "resolved": False,
    })

    # Publish the resume URL so humans can approve/respond.
    from services.workflows.workflow_executor import _publish
    base = os.environ.get("MAARS_BASE_URL", "").rstrip("/")
    resume_url = f"{base}/api/webhooks/resume/{token}" if base else f"/api/webhooks/resume/{token}"
    await _publish(run_id, {
        "event": "wait_for_webhook", "token": token, "resume_url": resume_url,
        "description": params.get("description", ""),
    })

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        await asyncio.sleep(2)
        doc = await db.workflow_wait_tokens.find_one({"token": token})
        if doc and doc.get("resolved"):
            return {"ok": True, "payload": doc.get("payload") or {}, "resumed_at": doc.get("resolved_at")}
    # expired
    await db.workflow_wait_tokens.update_one({"token": token}, {"$set": {"resolved": True, "expired": True}})
    return {"ok": False, "error": "timeout", "token": token}


async def t_approval(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Human-in-the-loop: block until someone hits approve / reject.

    Shares the wait_for_webhook infra. Exposes two URLs: approve +
    reject. Branch on the result via on_failure (reject) or next (approve).

    params.timeout_s: default 86400 (1 day)
    params.approver_email: optional — log for audit
    params.notification_channel: "slack" | "email" | None — where to ping
    """
    from db import db
    run_id = (ctx or {}).get("run", {}).get("id")
    token = secrets.token_urlsafe(24)
    timeout_s = max(60, min(int(params.get("timeout_s", 86400)), 7 * 86400))

    await db.workflow_wait_tokens.insert_one({
        "token": token,
        "run_id": run_id,
        "user_id": user_id,
        "kind": "approval",
        "created_at": time.time(),
        "expires_at": time.time() + timeout_s,
        "description": params.get("description", "Workflow approval requested"),
        "resolved": False,
    })

    base = os.environ.get("MAARS_BASE_URL", "").rstrip("/")
    approve_url = f"{base}/api/webhooks/resume/{token}?decision=approved" if base else f"/api/webhooks/resume/{token}?decision=approved"
    reject_url  = f"{base}/api/webhooks/resume/{token}?decision=rejected" if base else f"/api/webhooks/resume/{token}?decision=rejected"

    # Notify the approver (best-effort).
    approver = params.get("approver_email")
    channel = params.get("notification_channel")
    try:
        if channel == "email" and approver:
            from services.email_sender import send_email
            body = (f"{params.get('description','Approval requested')}\n\n"
                    f"Approve: {approve_url}\nReject: {reject_url}")
            await send_email(user_id=user_id, to=approver,
                             subject=params.get("subject", "Workflow approval"),
                             body=body)
        elif channel == "slack":
            slack_token = params.get("slack_token") or os.environ.get("SLACK_BOT_TOKEN")
            slack_channel = params.get("slack_channel")
            if slack_token and slack_channel:
                await _http("POST", "https://slack.com/api/chat.postMessage",
                            headers={"Authorization": f"Bearer {slack_token}"},
                            json={"channel": slack_channel,
                                  "text": f"{params.get('description','Approval requested')}\n<{approve_url}|Approve> · <{reject_url}|Reject>"})
    except Exception as exc:
        logger.info("approval notification failed: %s", exc)

    # Publish to SSE so UI shows the approval ping.
    try:
        from services.workflows.workflow_executor import _publish
        await _publish(run_id, {
            "event": "approval_requested", "token": token,
            "approve_url": approve_url, "reject_url": reject_url,
            "description": params.get("description", ""),
        })
    except Exception:
        pass

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        await asyncio.sleep(3)
        doc = await db.workflow_wait_tokens.find_one({"token": token})
        if doc and doc.get("resolved"):
            dec = (doc.get("payload") or {}).get("decision") or "approved"
            if dec == "rejected":
                return {"ok": False, "error": "rejected", "decision": "rejected",
                        "approver": approver, "token": token}
            return {"ok": True, "decision": "approved", "approver": approver,
                    "resolved_at": doc.get("resolved_at"), "token": token}
    await db.workflow_wait_tokens.update_one({"token": token}, {"$set": {"resolved": True, "expired": True}})
    return {"ok": False, "error": "approval_timeout", "token": token}


# ── Phase B: Dev tools ───────────────────────────────────────────────

async def t_github(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """GitHub — op: create_issue | comment_issue | create_pr | merge_pr | read_file."""
    token = _tok(params, "GITHUB_TOKEN") or await _from_vault(user_id, "github")
    if not token: return {"ok": False, "error": "no github token"}
    op = params.get("op", "create_issue")
    repo = params.get("repo")   # "owner/name"
    H = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    if op == "create_issue":
        s, b, _ = await _http("POST", f"https://api.github.com/repos/{repo}/issues",
                              headers=H, json={"title": params.get("title",""),
                                               "body": params.get("body",""),
                                               "labels": params.get("labels") or []})
        return _ok(s, b)
    if op == "comment_issue":
        s, b, _ = await _http("POST",
            f"https://api.github.com/repos/{repo}/issues/{params['number']}/comments",
            headers=H, json={"body": params.get("body","")})
        return _ok(s, b)
    if op == "create_pr":
        s, b, _ = await _http("POST", f"https://api.github.com/repos/{repo}/pulls",
                              headers=H, json={"title": params.get("title",""),
                                               "body": params.get("body",""),
                                               "head": params.get("head"),
                                               "base": params.get("base","main")})
        return _ok(s, b)
    if op == "merge_pr":
        s, b, _ = await _http("PUT",
            f"https://api.github.com/repos/{repo}/pulls/{params['number']}/merge",
            headers=H, json={"merge_method": params.get("method","squash")})
        return _ok(s, b)
    if op == "read_file":
        s, b, _ = await _http("GET",
            f"https://api.github.com/repos/{repo}/contents/{params['path']}",
            headers=H, params={"ref": params.get("ref", "main")})
        if s < 400 and isinstance(b, dict) and b.get("content"):
            try: b["decoded"] = base64.b64decode(b["content"]).decode("utf-8", errors="replace")
            except Exception: pass
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'"}


async def t_gitlab(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """GitLab — op: create_issue | comment_issue | create_mr."""
    token = _tok(params, "GITLAB_TOKEN")
    if not token: return {"ok": False, "error": "no gitlab token"}
    base = params.get("base_url", "https://gitlab.com/api/v4")
    pid = params.get("project_id")   # numeric or url-encoded path
    H = {"PRIVATE-TOKEN": token}
    op = params.get("op", "create_issue")
    if op == "create_issue":
        s, b, _ = await _http("POST", f"{base}/projects/{pid}/issues",
                              headers=H, json={"title": params.get("title",""),
                                               "description": params.get("body","")})
        return _ok(s, b)
    if op == "comment_issue":
        s, b, _ = await _http("POST",
            f"{base}/projects/{pid}/issues/{params['iid']}/notes",
            headers=H, json={"body": params.get("body","")})
        return _ok(s, b)
    if op == "create_mr":
        s, b, _ = await _http("POST", f"{base}/projects/{pid}/merge_requests",
                              headers=H, json={"source_branch": params.get("head"),
                                               "target_branch": params.get("base","main"),
                                               "title": params.get("title","")})
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'"}


async def t_jira(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Jira Cloud — op: create_issue | transition | comment."""
    email = params.get("email") or os.environ.get("JIRA_EMAIL")
    token = _tok(params, "JIRA_API_TOKEN")
    host  = params.get("host") or os.environ.get("JIRA_HOST")   # "https://yours.atlassian.net"
    if not (email and token and host): return {"ok": False, "error": "jira creds missing"}
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    H = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
    op = params.get("op", "create_issue")
    if op == "create_issue":
        payload = {"fields": {
            "project": {"key": params["project"]},
            "summary": params.get("summary",""),
            "issuetype": {"name": params.get("type","Task")},
        }}
        if params.get("description"):
            payload["fields"]["description"] = {
                "type":"doc","version":1,
                "content":[{"type":"paragraph","content":[{"type":"text","text":params["description"]}]}]}
        s, b, _ = await _http("POST", f"{host}/rest/api/3/issue", headers=H, json=payload)
        return _ok(s, b)
    if op == "transition":
        s, b, _ = await _http("POST", f"{host}/rest/api/3/issue/{params['key']}/transitions",
                              headers=H, json={"transition": {"id": str(params['transition_id'])}})
        return _ok(s, b)
    if op == "comment":
        s, b, _ = await _http("POST", f"{host}/rest/api/3/issue/{params['key']}/comment",
                              headers=H, json={"body": {"type":"doc","version":1,
                                "content":[{"type":"paragraph","content":[{"type":"text","text":params.get("body","")}]}]}})
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'"}


async def t_linear(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Linear — op: create_issue (GraphQL)."""
    token = _tok(params, "LINEAR_API_KEY")
    if not token: return {"ok": False, "error": "no linear api key"}
    query = """
    mutation($title:String!,$description:String,$teamId:String!,$priority:Int){
      issueCreate(input:{title:$title,description:$description,teamId:$teamId,priority:$priority}){
        success issue{id identifier url}
      }
    }"""
    s, b, _ = await _http("POST", "https://api.linear.app/graphql",
                          headers={"Authorization": token, "Content-Type": "application/json"},
                          json={"query": query, "variables": {
                              "title": params.get("title",""),
                              "description": params.get("description",""),
                              "teamId": params.get("team_id",""),
                              "priority": int(params.get("priority", 3))}})
    return _ok(s, b)


async def t_asana(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Asana — create_task."""
    token = _tok(params, "ASANA_TOKEN")
    if not token: return {"ok": False, "error": "no asana token"}
    s, b, _ = await _http("POST", "https://app.asana.com/api/1.0/tasks",
                          headers={"Authorization": f"Bearer {token}"},
                          json={"data": {"name": params.get("name",""),
                                         "notes": params.get("notes",""),
                                         "projects": params.get("projects") or [],
                                         "assignee": params.get("assignee")}})
    return _ok(s, b)


async def t_trello(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Trello — create_card."""
    key = params.get("api_key") or os.environ.get("TRELLO_API_KEY")
    token = _tok(params, "TRELLO_TOKEN")
    if not (key and token): return {"ok": False, "error": "trello key+token required"}
    s, b, _ = await _http("POST", "https://api.trello.com/1/cards",
                          params={"key": key, "token": token,
                                  "idList": params.get("list_id"),
                                  "name": params.get("name",""),
                                  "desc": params.get("desc","")})
    return _ok(s, b)


async def t_clickup(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """ClickUp — create_task."""
    token = _tok(params, "CLICKUP_TOKEN")
    if not token: return {"ok": False, "error": "no clickup token"}
    s, b, _ = await _http("POST",
        f"https://api.clickup.com/api/v2/list/{params.get('list_id')}/task",
        headers={"Authorization": token, "Content-Type": "application/json"},
        json={"name": params.get("name",""), "description": params.get("description",""),
              "priority": params.get("priority"), "assignees": params.get("assignees") or []})
    return _ok(s, b)


async def t_monday(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Monday.com — create_item via GraphQL."""
    token = _tok(params, "MONDAY_TOKEN")
    if not token: return {"ok": False, "error": "no monday token"}
    q = """mutation($board:ID!,$name:String!,$vals:JSON){
      create_item(board_id:$board,item_name:$name,column_values:$vals){id}
    }"""
    s, b, _ = await _http("POST", "https://api.monday.com/v2",
                          headers={"Authorization": token, "Content-Type": "application/json"},
                          json={"query": q, "variables": {
                              "board": str(params.get("board_id")),
                              "name": params.get("name",""),
                              "vals": json.dumps(params.get("column_values") or {})}})
    return _ok(s, b)


# ── Phase B: CRM / Support ───────────────────────────────────────────

async def t_stripe_op(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Stripe workflow node — full CRUD across customers/charges/subs/invoices.

    op: create_customer | update_customer | get_customer | list_customers |
        create_charge | refund_charge | get_charge | list_charges |
        create_subscription | cancel_subscription | update_subscription |
        create_invoice | send_invoice | finalize_invoice | void_invoice |
        create_payment_intent | capture_payment_intent |
        create_product | create_price | list_prices |
        retrieve (generic: pass resource + id)
    """
    token = _tok(params, "STRIPE_SECRET_KEY")
    if not token: return {"ok": False, "error": "no stripe key"}
    op = params.get("op", "create_customer")
    H = {"Authorization": f"Bearer {token}"}

    def _flatten(d, prefix=""):
        out = {}
        for k, v in (d or {}).items():
            key = f"{prefix}[{k}]" if prefix else k
            if isinstance(v, dict): out.update(_flatten(v, key))
            elif isinstance(v, list):
                for i, x in enumerate(v):
                    if isinstance(x, dict): out.update(_flatten(x, f"{key}[{i}]"))
                    else: out[f"{key}[{i}]"] = x
            else: out[key] = v
        return out
    data = _flatten(params.get("fields") or {})

    op_map = {
        # Customers
        "create_customer":        ("POST",   "https://api.stripe.com/v1/customers"),
        "update_customer":        ("POST",   f"https://api.stripe.com/v1/customers/{params.get('id','')}"),
        "get_customer":           ("GET",    f"https://api.stripe.com/v1/customers/{params.get('id','')}"),
        "list_customers":         ("GET",    "https://api.stripe.com/v1/customers"),
        # Charges
        "create_charge":          ("POST",   "https://api.stripe.com/v1/charges"),
        "refund_charge":          ("POST",   "https://api.stripe.com/v1/refunds"),
        "get_charge":             ("GET",    f"https://api.stripe.com/v1/charges/{params.get('id','')}"),
        "list_charges":           ("GET",    "https://api.stripe.com/v1/charges"),
        # Subscriptions
        "create_subscription":    ("POST",   "https://api.stripe.com/v1/subscriptions"),
        "update_subscription":    ("POST",   f"https://api.stripe.com/v1/subscriptions/{params.get('id','')}"),
        "cancel_subscription":    ("DELETE", f"https://api.stripe.com/v1/subscriptions/{params.get('id','')}"),
        # Invoices
        "create_invoice":         ("POST",   "https://api.stripe.com/v1/invoices"),
        "send_invoice":           ("POST",   f"https://api.stripe.com/v1/invoices/{params.get('id','')}/send"),
        "finalize_invoice":       ("POST",   f"https://api.stripe.com/v1/invoices/{params.get('id','')}/finalize"),
        "void_invoice":           ("POST",   f"https://api.stripe.com/v1/invoices/{params.get('id','')}/void"),
        # Payment intents
        "create_payment_intent":  ("POST",   "https://api.stripe.com/v1/payment_intents"),
        "capture_payment_intent": ("POST",   f"https://api.stripe.com/v1/payment_intents/{params.get('id','')}/capture"),
        # Products + prices
        "create_product":         ("POST",   "https://api.stripe.com/v1/products"),
        "create_price":           ("POST",   "https://api.stripe.com/v1/prices"),
        "list_prices":            ("GET",    "https://api.stripe.com/v1/prices"),
        # Generic retrieve
        "retrieve":               ("GET",    f"https://api.stripe.com/v1/{params.get('resource','customers')}/{params.get('id','')}"),
    }
    spec = op_map.get(op)
    if not spec: return {"ok": False, "error": f"unknown op '{op}'",
                         "available_ops": sorted(op_map.keys())}
    method, url = spec
    kwargs = {"headers": H}
    if method in ("POST", "PUT"):
        kwargs["data"] = data
    elif method == "GET" and data:
        kwargs["params"] = data
    s, b, _ = await _http(method, url, **kwargs)
    return _ok(s, b)


async def t_hubspot_op(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """HubSpot — full CRUD over contacts/companies/deals/tickets + engagements.

    op: create_contact | update_contact | get_contact | delete_contact | list_contacts | search_contacts |
        create_company | update_company | get_company | list_companies |
        create_deal | update_deal | get_deal | list_deals |
        create_ticket | update_ticket | get_ticket |
        associate (two objects) |
        add_note (engagement on any object) |
        enroll_in_workflow (v3 workflows API)
    """
    token = _tok(params, "HUBSPOT_TOKEN")
    if not token: return {"ok": False, "error": "no hubspot token"}
    H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    op = params.get("op", "create_contact")
    base = "https://api.hubapi.com"
    # One row per op: (method, url_template, body_shape)
    # body_shape = "properties" | "raw" | None
    table = {
        "create_contact":   ("POST",   f"{base}/crm/v3/objects/contacts",              "properties"),
        "update_contact":   ("PATCH",  f"{base}/crm/v3/objects/contacts/{params.get('id','')}", "properties"),
        "get_contact":      ("GET",    f"{base}/crm/v3/objects/contacts/{params.get('id','')}", None),
        "delete_contact":   ("DELETE", f"{base}/crm/v3/objects/contacts/{params.get('id','')}", None),
        "list_contacts":    ("GET",    f"{base}/crm/v3/objects/contacts",              None),
        "search_contacts":  ("POST",   f"{base}/crm/v3/objects/contacts/search",       "raw"),
        "create_company":   ("POST",   f"{base}/crm/v3/objects/companies",             "properties"),
        "update_company":   ("PATCH",  f"{base}/crm/v3/objects/companies/{params.get('id','')}", "properties"),
        "get_company":      ("GET",    f"{base}/crm/v3/objects/companies/{params.get('id','')}", None),
        "list_companies":   ("GET",    f"{base}/crm/v3/objects/companies",             None),
        "create_deal":      ("POST",   f"{base}/crm/v3/objects/deals",                 "properties"),
        "update_deal":      ("PATCH",  f"{base}/crm/v3/objects/deals/{params.get('id','')}", "properties"),
        "get_deal":         ("GET",    f"{base}/crm/v3/objects/deals/{params.get('id','')}", None),
        "list_deals":       ("GET",    f"{base}/crm/v3/objects/deals",                 None),
        "create_ticket":    ("POST",   f"{base}/crm/v3/objects/tickets",               "properties"),
        "update_ticket":    ("PATCH",  f"{base}/crm/v3/objects/tickets/{params.get('id','')}", "properties"),
        "get_ticket":       ("GET",    f"{base}/crm/v3/objects/tickets/{params.get('id','')}", None),
        "add_note":         ("POST",   f"{base}/crm/v3/objects/notes",                 "properties"),
        "associate":        ("PUT",    f"{base}/crm/v4/objects/{params.get('from_type','contacts')}/{params.get('from_id','')}/associations/default/{params.get('to_type','companies')}/{params.get('to_id','')}", None),
    }
    spec = table.get(op)
    if not spec: return {"ok": False, "error": f"unknown op '{op}'",
                         "available_ops": sorted(table.keys())}
    method, url, body_kind = spec
    kwargs: dict = {"headers": H}
    if method in ("POST", "PATCH", "PUT") and body_kind:
        body = {"properties": params.get("properties") or {}} if body_kind == "properties" else (params.get("body") or {})
        kwargs["json"] = body
    elif method == "GET":
        qs = params.get("query") or {}
        if qs: kwargs["params"] = qs
    s, b, _ = await _http(method, url, **kwargs)
    return _ok(s, b)


async def t_salesforce_op(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Salesforce — full CRUD over Lead/Contact/Opportunity/Account/Case + SOQL.

    op: create | update | get | delete  (with object = Lead|Contact|Opportunity|Account|Case|Task|Event)
        soql_query  (params.soql = "SELECT ...")
        upsert      (object + external_id_field + external_id + fields)
    """
    inst = params.get("instance_url") or os.environ.get("SALESFORCE_INSTANCE_URL")
    token = _tok(params, "SALESFORCE_ACCESS_TOKEN") or await _from_vault(user_id, "salesforce")
    if not (inst and token): return {"ok": False, "error": "salesforce creds missing"}
    H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    op = params.get("op", "create")
    base = f"{inst.rstrip('/')}/services/data/v60.0"
    obj = params.get("object") or params.get("sobject") or "Lead"
    rec_id = params.get("id", "")
    fields = params.get("fields") or {}

    if op == "soql_query":
        import urllib.parse as _up
        soql = params.get("soql", "")
        if not soql: return {"ok": False, "error": "soql required"}
        s, b, _ = await _http("GET", f"{base}/query?q={_up.quote(soql)}", headers=H)
        return _ok(s, b)
    if op == "create":
        s, b, _ = await _http("POST", f"{base}/sobjects/{obj}", headers=H, json=fields)
        return _ok(s, b)
    if op == "update":
        s, b, _ = await _http("PATCH", f"{base}/sobjects/{obj}/{rec_id}", headers=H, json=fields)
        return _ok(s, b)
    if op == "get":
        s, b, _ = await _http("GET", f"{base}/sobjects/{obj}/{rec_id}", headers=H)
        return _ok(s, b)
    if op == "delete":
        s, b, _ = await _http("DELETE", f"{base}/sobjects/{obj}/{rec_id}", headers=H)
        return _ok(s, b)
    if op == "upsert":
        ext_field = params.get("external_id_field")
        ext_id    = params.get("external_id")
        if not (ext_field and ext_id):
            return {"ok": False, "error": "upsert requires external_id_field + external_id"}
        s, b, _ = await _http("PATCH",
            f"{base}/sobjects/{obj}/{ext_field}/{ext_id}",
            headers=H, json=fields)
        return _ok(s, b)
    # Legacy: create_lead / create_opportunity / create_contact / create_account
    legacy = {"create_lead":"Lead","create_opportunity":"Opportunity",
              "create_contact":"Contact","create_account":"Account"}.get(op)
    if legacy:
        s, b, _ = await _http("POST", f"{base}/sobjects/{legacy}",
                              headers=H, json=fields)
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'",
            "available_ops": ["create","update","get","delete","upsert","soql_query"]}


async def t_gmail_op(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Gmail — full CRUD via Google Gmail API v1.

    op: send | list_messages | get_message | search |
        create_draft | list_labels | add_label | remove_label | trash_message
    Auth: Bearer OAuth access_token (params.token or GMAIL_ACCESS_TOKEN env
    or vault google_oauth).
    """
    import base64 as _b64
    token = (_tok(params, "GMAIL_ACCESS_TOKEN")
             or await _from_vault(user_id, "google_oauth")
             or _tok(params, "GOOGLE_OAUTH_TOKEN"))
    if not token: return {"ok": False, "error": "no gmail token (set GMAIL_ACCESS_TOKEN or vault google_oauth)"}
    H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    op = params.get("op", "send")
    base = "https://gmail.googleapis.com/gmail/v1/users/me"
    uid = params.get("message_id", "")

    if op == "send":
        to   = params.get("to", "")
        subj = params.get("subject", "")
        body = params.get("body", "")
        is_html = bool(params.get("html"))
        ctype = "text/html" if is_html else "text/plain"
        mime = f"To: {to}\r\nSubject: {subj}\r\nContent-Type: {ctype}; charset=utf-8\r\n\r\n{body}"
        raw = _b64.urlsafe_b64encode(mime.encode("utf-8")).decode("ascii")
        s, b, _ = await _http("POST", f"{base}/messages/send",
                              headers=H, json={"raw": raw})
        return _ok(s, b)
    if op == "list_messages":
        q = params.get("query") or {}
        if params.get("q"): q["q"] = params["q"]
        s, b, _ = await _http("GET", f"{base}/messages", headers=H, params=q)
        return _ok(s, b)
    if op == "get_message":
        s, b, _ = await _http("GET", f"{base}/messages/{uid}", headers=H)
        return _ok(s, b)
    if op == "search":
        s, b, _ = await _http("GET", f"{base}/messages",
                              headers=H, params={"q": params.get("q", "")})
        return _ok(s, b)
    if op == "create_draft":
        to   = params.get("to", ""); subj = params.get("subject", ""); body = params.get("body", "")
        mime = f"To: {to}\r\nSubject: {subj}\r\n\r\n{body}"
        raw = _b64.urlsafe_b64encode(mime.encode("utf-8")).decode("ascii")
        s, b, _ = await _http("POST", f"{base}/drafts",
                              headers=H, json={"message": {"raw": raw}})
        return _ok(s, b)
    if op == "list_labels":
        s, b, _ = await _http("GET", f"{base}/labels", headers=H)
        return _ok(s, b)
    if op in ("add_label", "remove_label"):
        action_key = "addLabelIds" if op == "add_label" else "removeLabelIds"
        s, b, _ = await _http("POST", f"{base}/messages/{uid}/modify",
                              headers=H, json={action_key: params.get("label_ids") or []})
        return _ok(s, b)
    if op == "trash_message":
        s, b, _ = await _http("POST", f"{base}/messages/{uid}/trash", headers=H)
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'",
            "available_ops": ["send","list_messages","get_message","search",
                              "create_draft","list_labels","add_label",
                              "remove_label","trash_message"]}


async def t_notion_op(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Notion — full CRUD on pages/databases.

    op: create_page | update_page | get_page | archive_page |
        query_database | create_database | update_database |
        append_blocks | list_block_children
    """
    token = _tok(params, "NOTION_TOKEN") or await _from_vault(user_id, "notion")
    if not token: return {"ok": False, "error": "no notion token"}
    H = {"Authorization": f"Bearer {token}",
         "Notion-Version": "2022-06-28",
         "Content-Type": "application/json"}
    op = params.get("op", "create_page")
    base = "https://api.notion.com/v1"
    pid = params.get("id", "")

    if op == "create_page":
        parent = params.get("parent") or (
            {"database_id": params["database_id"]} if params.get("database_id")
            else {"page_id": params["page_id"]} if params.get("page_id") else None
        )
        if not parent: return {"ok": False, "error": "create_page needs parent / database_id / page_id"}
        body = {
            "parent":     parent,
            "properties": params.get("properties") or {},
        }
        if params.get("children"): body["children"] = params["children"]
        s, b, _ = await _http("POST", f"{base}/pages", headers=H, json=body)
        return _ok(s, b)
    if op == "update_page":
        body = {"properties": params.get("properties") or {}}
        if params.get("archived") is not None: body["archived"] = bool(params["archived"])
        s, b, _ = await _http("PATCH", f"{base}/pages/{pid}", headers=H, json=body)
        return _ok(s, b)
    if op == "get_page":
        s, b, _ = await _http("GET", f"{base}/pages/{pid}", headers=H)
        return _ok(s, b)
    if op == "archive_page":
        s, b, _ = await _http("PATCH", f"{base}/pages/{pid}",
                              headers=H, json={"archived": True})
        return _ok(s, b)
    if op == "query_database":
        body = {}
        if params.get("filter"): body["filter"] = params["filter"]
        if params.get("sorts"):  body["sorts"]  = params["sorts"]
        if params.get("page_size"): body["page_size"] = params["page_size"]
        s, b, _ = await _http("POST",
            f"{base}/databases/{params.get('database_id','')}/query",
            headers=H, json=body)
        return _ok(s, b)
    if op == "create_database":
        s, b, _ = await _http("POST", f"{base}/databases",
                              headers=H, json={
                                  "parent": params.get("parent") or {"page_id": params.get("page_id")},
                                  "title":  params.get("title") or [],
                                  "properties": params.get("properties") or {},
                              })
        return _ok(s, b)
    if op == "update_database":
        body = {}
        for k in ("title", "description", "properties"):
            if params.get(k) is not None: body[k] = params[k]
        s, b, _ = await _http("PATCH", f"{base}/databases/{pid}",
                              headers=H, json=body)
        return _ok(s, b)
    if op == "append_blocks":
        s, b, _ = await _http("PATCH", f"{base}/blocks/{pid}/children",
                              headers=H, json={"children": params.get("children") or []})
        return _ok(s, b)
    if op == "list_block_children":
        s, b, _ = await _http("GET", f"{base}/blocks/{pid}/children", headers=H)
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'",
            "available_ops": ["create_page","update_page","get_page","archive_page",
                              "query_database","create_database","update_database",
                              "append_blocks","list_block_children"]}


async def t_intercom_send(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Intercom — send an admin-initiated conversation."""
    token = _tok(params, "INTERCOM_TOKEN")
    if not token: return {"ok": False, "error": "no intercom token"}
    s, b, _ = await _http("POST", "https://api.intercom.io/messages",
                          headers={"Authorization": f"Bearer {token}",
                                   "Content-Type":"application/json",
                                   "Accept":"application/json"},
                          json={
                              "message_type": params.get("message_type","inapp"),
                              "body": params.get("body",""),
                              "from": {"type":"admin","id": params.get("admin_id")},
                              "to": {"type":"user", **({"id": params["user_id"]} if params.get("user_id") else {"email": params.get("email")})},
                          })
    return _ok(s, b)


async def t_zendesk_ticket(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Zendesk — create a ticket."""
    sub = params.get("subdomain")
    email = params.get("email")
    token = _tok(params, "ZENDESK_API_TOKEN")
    if not (sub and email and token): return {"ok": False, "error": "zendesk creds missing"}
    auth = base64.b64encode(f"{email}/token:{token}".encode()).decode()
    s, b, _ = await _http("POST", f"https://{sub}.zendesk.com/api/v2/tickets.json",
                          headers={"Authorization": f"Basic {auth}", "Content-Type":"application/json"},
                          json={"ticket": {"subject": params.get("subject",""),
                                            "comment": {"body": params.get("body","")},
                                            "priority": params.get("priority","normal"),
                                            "requester": {"email": params.get("requester_email","")}}})
    return _ok(s, b)


async def t_freshdesk_ticket(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Freshdesk — create a ticket."""
    sub = params.get("subdomain")
    token = _tok(params, "FRESHDESK_API_KEY")
    if not (sub and token): return {"ok": False, "error": "freshdesk creds missing"}
    auth = base64.b64encode(f"{token}:X".encode()).decode()
    s, b, _ = await _http("POST", f"https://{sub}.freshdesk.com/api/v2/tickets",
                          headers={"Authorization": f"Basic {auth}", "Content-Type":"application/json"},
                          json={"subject": params.get("subject",""),
                                "description": params.get("body",""),
                                "email": params.get("requester_email"),
                                "priority": int(params.get("priority", 1)),
                                "status": int(params.get("status", 2))})
    return _ok(s, b)


# ── Phase B: Marketing ───────────────────────────────────────────────

async def t_mailchimp_subscribe(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Mailchimp — add subscriber to an audience."""
    key = _tok(params, "MAILCHIMP_API_KEY")
    dc = params.get("dc")     # data-center suffix from your API key, eg "us18"
    list_id = params.get("list_id")
    if not (key and dc and list_id): return {"ok": False, "error": "mailchimp creds + list_id required"}
    auth = base64.b64encode(f"anystring:{key}".encode()).decode()
    email = params.get("email") or inp.get("email", "")
    email_hash = hashlib.md5(email.lower().encode()).hexdigest()
    s, b, _ = await _http("PUT",
        f"https://{dc}.api.mailchimp.com/3.0/lists/{list_id}/members/{email_hash}",
        headers={"Authorization": f"Basic {auth}", "Content-Type":"application/json"},
        json={"email_address": email,
              "status_if_new": params.get("status","subscribed"),
              "status": params.get("status","subscribed"),
              "merge_fields": params.get("merge_fields") or {}})
    return _ok(s, b)


async def t_typeform_list(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Typeform — list responses for a form."""
    token = _tok(params, "TYPEFORM_TOKEN")
    fid = params.get("form_id")
    if not (token and fid): return {"ok": False, "error": "typeform token+form_id required"}
    s, b, _ = await _http("GET", f"https://api.typeform.com/forms/{fid}/responses",
                          headers={"Authorization": f"Bearer {token}"},
                          params={"page_size": params.get("page_size", 25),
                                  "since": params.get("since", "")})
    return _ok(s, b)


async def t_sendgrid_send(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Direct SendGrid send (bypassing email_sender for power users)."""
    key = _tok(params, "SENDGRID_API_KEY")
    if not key: return {"ok": False, "error": "no sendgrid key"}
    s, b, _ = await _http("POST", "https://api.sendgrid.com/v3/mail/send",
                          headers={"Authorization": f"Bearer {key}", "Content-Type":"application/json"},
                          json={"personalizations": [{"to":[{"email": params.get("to")}]}],
                                "from": {"email": params.get("from")},
                                "subject": params.get("subject",""),
                                "content": [{"type":"text/html","value": params.get("body","")}]})
    return _ok(s, b)


# ── Phase B: Enrichment ──────────────────────────────────────────────

async def t_clearbit_enrich(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    key = _tok(params, "CLEARBIT_KEY")
    email = params.get("email") or inp.get("email","")
    if not (key and email): return {"ok": False, "error": "clearbit key + email required"}
    s, b, _ = await _http("GET", f"https://person.clearbit.com/v2/combined/find",
                          headers={"Authorization": f"Bearer {key}"},
                          params={"email": email})
    return _ok(s, b)


async def t_dropcontact_enrich(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    key = _tok(params, "DROPCONTACT_KEY")
    if not key: return {"ok": False, "error": "no dropcontact key"}
    s, b, _ = await _http("POST", "https://api.dropcontact.com/v1/enrich/all",
                          headers={"X-Access-Token": key, "Content-Type":"application/json"},
                          json={"data": params.get("data") or [{"email": inp.get("email","")}]})
    return _ok(s, b)


async def t_openweather_get(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    key = _tok(params, "OPENWEATHER_KEY")
    if not key: return {"ok": False, "error": "no openweather key"}
    s, b, _ = await _http("GET", "https://api.openweathermap.org/data/2.5/weather",
                          params={"q": params.get("city",""), "units": params.get("units","metric"),
                                  "appid": key})
    return _ok(s, b)


# ── Phase B: Storage ─────────────────────────────────────────────────

async def t_google_drive_upload(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    token = await _from_vault(user_id, "google") or _tok(params, "GOOGLE_ACCESS_TOKEN")
    if not token: return {"ok": False, "error": "no google oauth credential"}
    name = params.get("name","file.txt")
    content = params.get("content", inp.get("content",""))
    # Multipart upload via simple path.
    boundary = "maars_boundary_" + secrets.token_hex(8)
    meta = {"name": name, "mimeType": params.get("mime","text/plain")}
    if params.get("folder_id"): meta["parents"] = [params["folder_id"]]
    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(meta)}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: {meta['mimeType']}\r\n\r\n"
        f"{content}\r\n"
        f"--{boundary}--"
    )
    s, b, _ = await _http("POST",
        "https://www.googleapis.com/upload/drive/v3/files",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": f"multipart/related; boundary={boundary}"},
        params={"uploadType": "multipart"},
        content=body.encode())
    return _ok(s, b)


async def t_dropbox_upload(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    token = _tok(params, "DROPBOX_TOKEN")
    if not token: return {"ok": False, "error": "no dropbox token"}
    path = params.get("path","/maars.txt")
    content = params.get("content", inp.get("content",""))
    s, b, _ = await _http("POST", "https://content.dropboxapi.com/2/files/upload",
                          headers={"Authorization": f"Bearer {token}",
                                   "Content-Type": "application/octet-stream",
                                   "Dropbox-API-Arg": json.dumps({"path": path, "mode":"overwrite", "autorename":False})},
                          content=content.encode() if isinstance(content, str) else content)
    return _ok(s, b)


async def t_box_upload(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    token = _tok(params, "BOX_TOKEN")
    if not token: return {"ok": False, "error": "no box token"}
    folder = str(params.get("folder_id","0"))
    name = params.get("name","maars.txt")
    content = params.get("content", inp.get("content",""))
    files = {"file": (name, content.encode() if isinstance(content, str) else content)}
    attrs = json.dumps({"name": name, "parent": {"id": folder}})
    from services.http_client import get_client
    client = await get_client()
    r = await client.post("https://upload.box.com/api/2.0/files/content",
                          headers={"Authorization": f"Bearer {token}"},
                          files={**files, "attributes": (None, attrs)})
    try: body = r.json()
    except Exception: body = r.text
    return _ok(r.status_code, body)


# ── Phase B: Calendar / Meetings ─────────────────────────────────────

async def t_calendly_list(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    token = _tok(params, "CALENDLY_TOKEN")
    if not token: return {"ok": False, "error": "no calendly token"}
    s, b, _ = await _http("GET", "https://api.calendly.com/scheduled_events",
                          headers={"Authorization": f"Bearer {token}"},
                          params={"user": params.get("user_uri",""),
                                  "min_start_time": params.get("since",""),
                                  "count": params.get("count", 20)})
    return _ok(s, b)


async def t_zoom_create_meeting(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    token = await _from_vault(user_id, "zoom") or _tok(params, "ZOOM_ACCESS_TOKEN")
    if not token: return {"ok": False, "error": "no zoom token"}
    s, b, _ = await _http("POST", "https://api.zoom.us/v2/users/me/meetings",
                          headers={"Authorization": f"Bearer {token}", "Content-Type":"application/json"},
                          json={"topic": params.get("topic","Meeting"),
                                "type": params.get("type", 2),
                                "start_time": params.get("start_time"),
                                "duration": int(params.get("duration", 30)),
                                "timezone": params.get("timezone","UTC"),
                                "agenda": params.get("agenda","")})
    return _ok(s, b)


# ── Phase B: Commerce ────────────────────────────────────────────────

async def t_shopify_op(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Shopify — list_orders | create_product | list_products."""
    token = _tok(params, "SHOPIFY_ACCESS_TOKEN")
    store = params.get("store")   # "mystore.myshopify.com"
    ver = params.get("api_version","2024-10")
    if not (token and store): return {"ok": False, "error": "shopify store + token required"}
    H = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    op = params.get("op", "list_orders")
    base = f"https://{store}/admin/api/{ver}"
    if op == "list_orders":
        s, b, _ = await _http("GET", f"{base}/orders.json", headers=H,
                              params={"status": params.get("status","any"),
                                      "limit": params.get("limit", 50)})
        return _ok(s, b)
    if op == "list_products":
        s, b, _ = await _http("GET", f"{base}/products.json", headers=H,
                              params={"limit": params.get("limit", 50)})
        return _ok(s, b)
    if op == "create_product":
        s, b, _ = await _http("POST", f"{base}/products.json", headers=H,
                              json={"product": params.get("product") or {}})
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'"}


# ── Phase B: Search ──────────────────────────────────────────────────

async def t_algolia_op(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Algolia — index | search."""
    app = params.get("app_id") or os.environ.get("ALGOLIA_APP_ID")
    key = _tok(params, "ALGOLIA_ADMIN_KEY") or _tok(params, "ALGOLIA_SEARCH_KEY")
    if not (app and key): return {"ok": False, "error": "algolia app_id + key required"}
    index = params.get("index")
    H = {"X-Algolia-Application-Id": app, "X-Algolia-API-Key": key}
    op = params.get("op", "search")
    if op == "search":
        s, b, _ = await _http("POST", f"https://{app}-dsn.algolia.net/1/indexes/{index}/query",
                              headers={**H, "Content-Type":"application/json"},
                              json={"query": params.get("query","")})
        return _ok(s, b)
    if op == "index":
        obj = params.get("object") or inp
        s, b, _ = await _http("POST", f"https://{app}.algolia.net/1/indexes/{index}",
                              headers={**H, "Content-Type":"application/json"},
                              json=obj)
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'"}


async def t_typesense_op(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    """Typesense — index (upsert doc) | search."""
    host = params.get("host") or os.environ.get("TYPESENSE_HOST", "http://localhost:8108")
    key = _tok(params, "TYPESENSE_API_KEY")
    coll = params.get("collection")
    if not (key and coll): return {"ok": False, "error": "typesense key+collection required"}
    H = {"X-TYPESENSE-API-KEY": key, "Content-Type":"application/json"}
    op = params.get("op", "search")
    if op == "index":
        s, b, _ = await _http("POST", f"{host}/collections/{coll}/documents", headers=H,
                              params={"action": "upsert"},
                              json=params.get("doc") or inp)
        return _ok(s, b)
    if op == "search":
        s, b, _ = await _http("GET", f"{host}/collections/{coll}/documents/search", headers=H,
                              params={"q": params.get("query","*"),
                                      "query_by": params.get("query_by","name"),
                                      "per_page": params.get("per_page",10)})
        return _ok(s, b)
    return {"ok": False, "error": f"unknown op '{op}'"}


# ── Phase B: Twilio SMS ──────────────────────────────────────────────

async def t_twilio_sms(user_id: str, params: dict, inp: dict, ctx: dict) -> dict:
    sid = params.get("account_sid") or os.environ.get("TWILIO_ACCOUNT_SID")
    tok = _tok(params, "TWILIO_AUTH_TOKEN")
    if not (sid and tok): return {"ok": False, "error": "twilio creds missing"}
    auth = base64.b64encode(f"{sid}:{tok}".encode()).decode()
    s, b, _ = await _http("POST",
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
        headers={"Authorization": f"Basic {auth}", "Content-Type":"application/x-www-form-urlencoded"},
        data={"From": params.get("from",""), "To": params.get("to",""),
              "Body": params.get("body","")})
    return _ok(s, b)


# ── Registration ─────────────────────────────────────────────────────

CONTROL_TOOLS: dict = {
    "respond_webhook":  t_respond_webhook,
    "wait_for_webhook": t_wait_for_webhook,
    "approval":         t_approval,
}

SERVICE_TOOLS: dict = {
    "github":             t_github,
    "gitlab":             t_gitlab,
    "jira":               t_jira,
    "linear":             t_linear,
    "asana":              t_asana,
    "trello":             t_trello,
    "clickup":            t_clickup,
    "monday":             t_monday,
    "stripe_op":          t_stripe_op,
    "hubspot_op":         t_hubspot_op,
    "salesforce_op":      t_salesforce_op,
    "gmail_op":           t_gmail_op,
    "notion_op":          t_notion_op,
    "intercom_send":      t_intercom_send,
    "zendesk_ticket":     t_zendesk_ticket,
    "freshdesk_ticket":   t_freshdesk_ticket,
    "mailchimp_subscribe": t_mailchimp_subscribe,
    "typeform_list":      t_typeform_list,
    "sendgrid_send":      t_sendgrid_send,
    "clearbit_enrich":    t_clearbit_enrich,
    "dropcontact_enrich": t_dropcontact_enrich,
    "openweather_get":    t_openweather_get,
    "google_drive_upload": t_google_drive_upload,
    "dropbox_upload":     t_dropbox_upload,
    "box_upload":         t_box_upload,
    "calendly_list":      t_calendly_list,
    "zoom_create_meeting": t_zoom_create_meeting,
    "shopify_op":         t_shopify_op,
    "algolia_op":         t_algolia_op,
    "typesense_op":       t_typesense_op,
    "twilio_sms":         t_twilio_sms,
}
