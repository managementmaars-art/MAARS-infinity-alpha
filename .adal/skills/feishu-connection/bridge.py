#!/usr/bin/env python3
"""
Feishu ↔ Moltbot bridge.

Receives messages from Feishu via WebSocket long-connection,
forwards them to Moltbot Gateway, and sends replies back.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
import uuid
from typing import Any, Awaitable, Dict, List, Optional

import websockets

try:
    import lark_oapi as lark
    from lark_oapi.event.dispatcher import EventDispatcherHandler
    from lark_oapi.ws import Client as LarkWsClient
    from lark_oapi.api.im.v1 import (
        MessageCreateRequest,
        MessageCreateRequestBody,
        MessageUpdateRequest,
        MessageUpdateRequestBody,
        MessageDeleteRequest,
    )
except Exception as exc:  # pragma: no cover - import guard for runtime
    print(f"[FATAL] Failed to import lark_oapi: {exc}", file=sys.stderr)
    sys.exit(1)

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET_PATH = os.getenv("FEISHU_APP_SECRET_PATH", "~/.clawdbot/secrets/feishu_app_secret")
CLAWDBOT_CONFIG_PATH = os.getenv("CLAWDBOT_CONFIG_PATH", "~/.clawdbot/clawdbot.json")
CLAWDBOT_AGENT_ID = os.getenv("CLAWDBOT_AGENT_ID", "main")
THINKING_THRESHOLD_MS = int(os.getenv("FEISHU_THINKING_THRESHOLD_MS", "2500"))

SEEN_TTL_MS = 10 * 60 * 1000
_seen: Dict[str, float] = {}


class GatewayConfig:
    def __init__(self, port: int, token: str) -> None:
        self.port = port
        self.token = token


def resolve_path(path: str) -> str:
    return os.path.expanduser(path)


def must_read(path: str, label: str) -> str:
    resolved = resolve_path(path)
    if not os.path.exists(resolved):
        print(f"[FATAL] {label} not found: {resolved}", file=sys.stderr)
        sys.exit(1)
    with open(resolved, "r", encoding="utf-8") as f:
        value = f.read().strip()
    if not value:
        print(f"[FATAL] {label} is empty: {resolved}", file=sys.stderr)
        sys.exit(1)
    return value


def load_gateway_config() -> GatewayConfig:
    raw = must_read(CLAWDBOT_CONFIG_PATH, "Clawdbot config")
    data = json.loads(raw)
    port = int(data.get("gateway", {}).get("port", 18789))
    token = data.get("gateway", {}).get("auth", {}).get("token")
    if not token:
        print("[FATAL] gateway.auth.token missing in Clawdbot config", file=sys.stderr)
        sys.exit(1)
    return GatewayConfig(port=port, token=str(token))


def is_duplicate(message_id: Optional[str]) -> bool:
    if not message_id:
        return False
    now = time.time() * 1000
    expired = [k for k, ts in _seen.items() if now - ts > SEEN_TTL_MS]
    for k in expired:
        _seen.pop(k, None)
    if message_id in _seen:
        return True
    _seen[message_id] = now
    return False


def should_respond_in_group(text: str, mentions: List[Any]) -> bool:
    if mentions:
        return True
    lowered = text.lower()
    if text.endswith("?") or text.endswith("？"):
        return True
    if any(word in lowered.split() for word in ["why", "how", "what", "when", "where", "who", "help"]):
        return True
    verbs = ["帮", "麻烦", "请", "能否", "可以", "解释", "看看", "排查", "分析", "总结", "写", "改", "修", "查", "对比", "翻译"]
    if any(v in text for v in verbs):
        return True
    if text.lower().startswith(("alen", "clawdbot", "bot", "助手", "智能体")):
        return True
    return False


def normalize_event(data: Any) -> Dict[str, Any]:
    if isinstance(data, dict):
        return data
    try:
        return lark.JSON.marshal(data)  # type: ignore[attr-defined]
    except Exception:
        pass
    if hasattr(data, "event"):
        return normalize_event(getattr(data, "event"))
    if hasattr(data, "__dict__"):
        return {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
    return {}


async def ask_gateway(config: GatewayConfig, text: str, session_key: str) -> str:
    uri = f"ws://127.0.0.1:{config.port}"
    async with websockets.connect(uri) as ws:
        run_id: Optional[str] = None
        buf = ""
        while True:
            raw = await ws.recv()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("type") == "event" and msg.get("event") == "connect.challenge":
                await ws.send(
                    json.dumps(
                        {
                            "type": "req",
                            "id": "connect",
                            "method": "connect",
                            "params": {
                                "minProtocol": 3,
                                "maxProtocol": 3,
                                "client": {
                                    "id": "gateway-client",
                                    "version": "0.2.0",
                                    "platform": "macos",
                                    "mode": "backend",
                                },
                                "role": "operator",
                                "scopes": ["operator.read", "operator.write"],
                                "auth": {"token": config.token},
                                "locale": "zh-CN",
                                "userAgent": "feishu-moltbot-bridge",
                            },
                        }
                    )
                )
                continue

            if msg.get("type") == "res" and msg.get("id") == "connect":
                if not msg.get("ok"):
                    raise RuntimeError(msg.get("error", {}).get("message", "connect failed"))
                await ws.send(
                    json.dumps(
                        {
                            "type": "req",
                            "id": "agent",
                            "method": "agent",
                            "params": {
                                "message": text,
                                "agentId": CLAWDBOT_AGENT_ID,
                                "sessionKey": session_key,
                                "deliver": False,
                                "idempotencyKey": str(uuid.uuid4()),
                            },
                        }
                    )
                )
                continue

            if msg.get("type") == "res" and msg.get("id") == "agent":
                if not msg.get("ok"):
                    raise RuntimeError(msg.get("error", {}).get("message", "agent error"))
                payload = msg.get("payload", {})
                run_id = payload.get("runId")
                continue

            if msg.get("type") == "event" and msg.get("event") == "agent":
                payload = msg.get("payload") or {}
                if run_id and payload.get("runId") != run_id:
                    continue
                if payload.get("stream") == "assistant":
                    data = payload.get("data") or {}
                    if isinstance(data.get("text"), str):
                        buf = data["text"]
                    elif isinstance(data.get("delta"), str):
                        buf += data["delta"]
                    continue
                if payload.get("stream") == "lifecycle":
                    phase = payload.get("data", {}).get("phase")
                    if phase == "end":
                        return buf.strip()
                    if phase == "error":
                        raise RuntimeError(payload.get("data", {}).get("message", "agent error"))


class FeishuBridge:
    def __init__(self) -> None:
        if not APP_ID:
            print("[FATAL] FEISHU_APP_ID environment variable is required", file=sys.stderr)
            sys.exit(1)
        self.app_secret = must_read(APP_SECRET_PATH, "Feishu App Secret")
        self.gateway = load_gateway_config()
        self.client = lark.Client.builder().app_id(APP_ID).app_secret(self.app_secret).build()

    def send_text(self, chat_id: str, text: str) -> Optional[str]:
        content = json.dumps({"text": text}, ensure_ascii=False)
        req = (
            MessageCreateRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                MessageCreateRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("text")
                .content(content)
                .build()
            )
            .build()
        )
        resp = self.client.im.v1.message.create(req)
        if not resp.success():
            print(f"[ERROR] Feishu send failed: {resp.code} {resp.msg}", file=sys.stderr)
            return None
        return getattr(resp.data, "message_id", None)

    def update_text(self, message_id: str, text: str) -> bool:
        content = json.dumps({"text": text}, ensure_ascii=False)
        req = (
            MessageUpdateRequest.builder()
            .message_id(message_id)
            .request_body(MessageUpdateRequestBody.builder().msg_type("text").content(content).build())
            .build()
        )
        resp = self.client.im.v1.message.update(req)
        if not resp.success():
            print(f"[ERROR] Feishu update failed: {resp.code} {resp.msg}", file=sys.stderr)
            return False
        return True

    def delete_message(self, message_id: str) -> None:
        req = MessageDeleteRequest.builder().message_id(message_id).build()
        _ = self.client.im.v1.message.delete(req)

    async def handle(self, data: Any) -> None:
        event = normalize_event(data)
        event_body = event.get("event", event)
        message = event_body.get("message") or {}

        message_id = message.get("message_id") or message.get("messageId")
        if is_duplicate(message_id):
            return
        if message.get("message_type") != "text" and message.get("messageType") != "text":
            return

        content = message.get("content") or ""
        try:
            text = json.loads(content).get("text", "").strip()
        except Exception:
            text = ""
        if not text:
            return

        chat_id = message.get("chat_id") or message.get("chatId")
        if not chat_id:
            return

        chat_type = message.get("chat_type") or message.get("chatType")
        mentions = event_body.get("mentions") or message.get("mentions") or []
        if chat_type == "group":
            text = re.sub(r"@_user_\\d+\\s*", "", text).strip()
            if not text or not should_respond_in_group(text, mentions):
                return

        session_key = f"feishu:{chat_id}"

        placeholder_id: Optional[str] = None
        thinking_task: Optional[asyncio.Task[None]] = None
        done = False

        async def send_thinking() -> None:
            nonlocal placeholder_id
            await asyncio.sleep(max(0, THINKING_THRESHOLD_MS) / 1000)
            if done:
                return
            placeholder_id = self.send_text(chat_id, "正在思考…")

        if THINKING_THRESHOLD_MS > 0:
            thinking_task = asyncio.create_task(send_thinking())

        reply = ""
        try:
            reply = await ask_gateway(self.gateway, text, session_key)
        except Exception as exc:
            reply = f"（系统出错）{exc}"
        finally:
            done = True
            if thinking_task:
                thinking_task.cancel()

        trimmed = reply.strip()
        if not trimmed or trimmed == "NO_REPLY" or trimmed.endswith("NO_REPLY"):
            if placeholder_id:
                self.delete_message(placeholder_id)
            return

        if placeholder_id:
            if self.update_text(placeholder_id, reply):
                return

        self.send_text(chat_id, reply)


def run_async(coro: Awaitable[Any]) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coro)
    else:
        loop.create_task(coro)


def main() -> None:
    bridge = FeishuBridge()

    def handler(data: Any) -> None:
        run_async(bridge.handle(data))

    event_handler = EventDispatcherHandler.builder(APP_ID, bridge.app_secret).register_p2_im_message_receive_v1(handler).build()

    ws_client = LarkWsClient(
        app_id=APP_ID,
        app_secret=bridge.app_secret,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )
    ws_client.start()
    print(f"[OK] Feishu bridge started (appId={APP_ID})")


if __name__ == "__main__":
    main()
