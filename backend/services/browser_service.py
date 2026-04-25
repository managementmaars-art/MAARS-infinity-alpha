"""MAARS — Embedded Browser Runtime.

A Playwright-backed browser that lives INSIDE MAARS Command:
  - Chromium binary + user-data stored under `backend/browser_data/` (not in
    ~/AppData or anywhere else on the host), so when MAARS is packaged /
    containerised the browser ships with it.
  - One browser process per MAARS instance, a context-per-session model so
    cookies and localStorage are isolated per user.
  - Agents, the orchestrator, and the human UI all drive the *same* session
    via tool-mediated calls — a three-way shared workspace.
  - Control handoff: any driver (agent / system / user) can take or release
    exclusive control. While one side holds the lock others get read-only
    screenshot streaming until released.

Public API (async):
    pool = get_browser_pool()
    sess = await pool.open(user_id, agent_id=None, start_url=None)
    await sess.navigate(url)
    await sess.click(selector)
    await sess.fill(selector, value)
    await sess.type(text)
    await sess.evaluate(js)
    png = await sess.screenshot()
    text = await sess.extract_text(selector="body")
    await sess.close()

    # handoff
    await sess.take_control(driver="user")     # or "agent" / "system"
    await sess.release_control(driver="user")

The service gracefully degrades when Playwright is not installed — the pool
refuses to open sessions and emits a clear error; every other MAARS feature
keeps working. Install with `pip install playwright && playwright install
chromium` (both steps are triggered automatically on first use if the
environment allows subprocess execution, otherwise the operator is prompted
via the returned error message).
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import logging
import os
import subprocess
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Coroutine, TypeVar

_T = TypeVar("_T")

logger = logging.getLogger(__name__)

# ── Layout ──────────────────────────────────────────────────────────────────
# Everything is rooted inside the MAARS repo so the browser is portable with
# the app. When MAARS runs in docker-compose the whole tree is inside the
# container; on a dev laptop the tree is under the project folder, NOT under
# the OS user's home directory.
BACKEND_ROOT  = Path(__file__).resolve().parent.parent
BROWSER_ROOT  = BACKEND_ROOT / "browser_data"
USERDATA_ROOT = BROWSER_ROOT / "profiles"
CHROMIUM_ROOT = BROWSER_ROOT / "chromium"
STORAGE_STATE = BROWSER_ROOT / "storage_states"
for d in (BROWSER_ROOT, USERDATA_ROOT, CHROMIUM_ROOT, STORAGE_STATE):
    d.mkdir(parents=True, exist_ok=True)

# Tell Playwright to keep its browser download *inside* our repo. Setting the
# env var before importing `playwright.async_api` makes the next `playwright
# install` land Chromium at this path.
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(CHROMIUM_ROOT))

DEFAULT_VIEWPORT   = {"width": 1280, "height": 800}
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (MAARS-Command/1.0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/latest Safari/537.36"
)
IDLE_TIMEOUT_SEC   = 30 * 60   # kill sessions untouched for 30 min


# ── Optional Playwright import ──────────────────────────────────────────────
# Playwright is imported lazily so we don't cache an "unavailable" state at
# module load. Callers should use `_load_playwright()` to get a fresh check —
# that way the `/browser/health` endpoint reflects the *current* state even if
# pip-installed between backend boots and now.
Browser = BrowserContext = Page = object  # type: ignore[misc,assignment]
_LAST_IMPORT_ERROR: Exception | None = None


def _load_playwright():
    """Re-attempt to import Playwright. Returns (async_playwright, error_or_None)."""
    global Browser, BrowserContext, Page, _LAST_IMPORT_ERROR
    try:
        from playwright.async_api import (
            async_playwright as _ap,
            Browser as _B, BrowserContext as _BC, Page as _P,
        )
        # Publish real types so isinstance / type hints get refreshed.
        Browser, BrowserContext, Page = _B, _BC, _P  # type: ignore[misc,assignment]
        _LAST_IMPORT_ERROR = None
        return _ap, None
    except Exception as e:
        _LAST_IMPORT_ERROR = e
        return None, e


class BrowserUnavailable(RuntimeError):
    """Raised when the caller tries to use the browser but Playwright is not
    installed or Chromium is missing. The message tells the operator how to
    install it."""


# ── BrowserSession ──────────────────────────────────────────────────────────
class BrowserSession:
    """One browser context + one page. Lives as long as the session is open.

    `driver` is who currently has exclusive control — `"agent"`, `"system"`,
    or `"user"`. While the driver is set, other drivers can only read (fetch
    screenshots, inspect state). Use `take_control()` to become the driver;
    `release_control()` to hand off. `"shared"` means anyone can act.
    """

    def __init__(
        self, *, session_id: str, user_id: str, agent_id: str | None,
        context: "BrowserContext", page: "Page", pool: "BrowserPool",
    ):
        self.session_id   = session_id
        self.user_id      = user_id
        self.agent_id     = agent_id
        self.context      = context
        self._pool        = pool                      # for loop dispatch
        self.driver: str  = "shared"
        self.created_at   = datetime.now(timezone.utc)
        self.last_active  = datetime.now(timezone.utc)
        # Multi-tab state. `self.page` is a property always pointing at the
        # currently-active tab so every pre-existing method stays correct.
        initial_tab_id = f"tab_{uuid.uuid4().hex[:8]}"
        self.tabs: dict[str, "Page"] = {initial_tab_id: page}
        self.tab_meta: dict[str, dict] = {
            initial_tab_id: {"integration_id": None, "label": None},
        }
        self.active_tab_id: str = initial_tab_id
        # Listeners for screenshot streaming — each is an asyncio.Queue.
        self.watchers: set[asyncio.Queue[bytes]] = set()
        self._closed       = False
        self._lock         = asyncio.Lock()

    @property
    def page(self) -> "Page":
        """The Playwright page for the active tab. Kept as a property so every
        existing single-tab mutation method reads through to the right tab
        without changes."""
        return self.tabs[self.active_tab_id]

    async def _dispatch(self, coro: Coroutine[Any, Any, _T]) -> _T:
        """Run a Playwright coroutine on the pool's dedicated loop."""
        return await self._pool._run_in_pw(coro)

    # --- mutation primitives (require driver lock unless shared) ------------
    def _require_driver(self, caller: str) -> None:
        if self.driver in ("shared", caller):
            return
        raise PermissionError(
            f"Browser session {self.session_id} currently controlled by "
            f"'{self.driver}'. Caller '{caller}' must take control first."
        )

    def touch(self) -> None:
        self.last_active = datetime.now(timezone.utc)

    async def take_control(self, driver: str) -> None:
        async with self._lock:
            self.driver = driver
            self.touch()

    async def release_control(self, driver: str) -> None:
        async with self._lock:
            if self.driver == driver:
                self.driver = "shared"
            self.touch()

    # --- tabs ---------------------------------------------------------------
    async def open_tab(self, url: str | None = None, *,
                       integration_id: str | None = None,
                       label: str | None = None,
                       activate: bool = True) -> dict:
        """Open a new tab in this session's context. Defaults to making it
        the active tab. Returns a tab descriptor with id/url/title."""
        async def _make():
            return await self.context.new_page()
        new_page = await self._dispatch(_make())
        tid = f"tab_{uuid.uuid4().hex[:8]}"
        async with self._lock:
            self.tabs[tid] = new_page
            self.tab_meta[tid] = {"integration_id": integration_id, "label": label}
            if activate:
                self.active_tab_id = tid
            self.touch()
        if url:
            try:
                await self.navigate(url, caller="user" if not self.agent_id else "agent")
            except Exception as e:
                logger.warning(f"open_tab navigate failed: {e}")
        await self._broadcast_screenshot()
        return await self._tab_descriptor(tid)

    async def switch_tab(self, tab_id: str) -> dict:
        async with self._lock:
            if tab_id not in self.tabs:
                raise ValueError(f"unknown tab: {tab_id}")
            self.active_tab_id = tab_id
            self.touch()
        await self._broadcast_screenshot()
        return await self._state()

    async def close_tab(self, tab_id: str) -> bool:
        async def _shut(p): await p.close()
        async with self._lock:
            if tab_id not in self.tabs:
                return False
            page = self.tabs.pop(tab_id)
            self.tab_meta.pop(tab_id, None)
            # If we closed the active tab, switch to any remaining one; if the
            # session has no tabs left, re-create a blank one so the UI still
            # has something to render.
            if tab_id == self.active_tab_id:
                self.active_tab_id = next(iter(self.tabs), "")
            self.touch()
        with contextlib.suppress(Exception):
            await self._dispatch(_shut(page))
        if not self.tabs:
            await self.open_tab(url=None, activate=True)
        await self._broadcast_screenshot()
        return True

    async def list_tabs(self) -> list[dict]:
        out: list[dict] = []
        for tid in list(self.tabs.keys()):
            out.append(await self._tab_descriptor(tid))
        return out

    async def _tab_descriptor(self, tab_id: str) -> dict:
        p = self.tabs.get(tab_id)
        if p is None:
            return {"tab_id": tab_id, "closed": True}
        async def _title():
            try: return await p.title()
            except Exception: return ""
        title = await self._dispatch(_title())
        meta = self.tab_meta.get(tab_id, {})
        return {
            "tab_id":         tab_id,
            "url":            p.url,
            "title":          title,
            "is_active":      tab_id == self.active_tab_id,
            "integration_id": meta.get("integration_id"),
            "label":          meta.get("label"),
        }

    # --- actions ------------------------------------------------------------
    async def navigate(self, url: str, *, caller: str = "system",
                       wait_until: str = "domcontentloaded",
                       environment: str = "production") -> dict:
        self._require_driver(caller)
        from governance.browser_policy import check_domain
        await check_domain(url, environment=environment)
        async def _go():
            await self.page.goto(url, wait_until=wait_until)
        async with self._lock:
            await self._dispatch(_go())
            self.touch()
            await self._broadcast_screenshot()
            return await self._state()

    async def click(self, selector: str, *, caller: str = "system") -> dict:
        self._require_driver(caller)
        async def _do(): await self.page.click(selector, timeout=10_000)
        async with self._lock:
            await self._dispatch(_do())
            self.touch(); await self._broadcast_screenshot(); return await self._state()

    async def click_at(self, x: int, y: int, *, caller: str = "user") -> dict:
        self._require_driver(caller)
        async def _do(): await self.page.mouse.click(x, y)
        async with self._lock:
            await self._dispatch(_do())
            self.touch(); await self._broadcast_screenshot(); return await self._state()

    async def fill(self, selector: str, value: str, *, caller: str = "system") -> dict:
        self._require_driver(caller)
        async def _do(): await self.page.fill(selector, value, timeout=10_000)
        async with self._lock:
            await self._dispatch(_do())
            self.touch(); await self._broadcast_screenshot(); return await self._state()

    async def type_text(self, text: str, *, caller: str = "user") -> dict:
        self._require_driver(caller)
        async def _do(): await self.page.keyboard.type(text)
        async with self._lock:
            await self._dispatch(_do())
            self.touch(); await self._broadcast_screenshot(); return await self._state()

    async def press_key(self, key: str, *, caller: str = "user") -> dict:
        self._require_driver(caller)
        async def _do(): await self.page.keyboard.press(key)
        async with self._lock:
            await self._dispatch(_do())
            self.touch(); await self._broadcast_screenshot(); return await self._state()

    async def scroll(self, dy: int, *, caller: str = "user") -> dict:
        self._require_driver(caller)
        async def _do(): await self.page.mouse.wheel(0, dy)
        async with self._lock:
            await self._dispatch(_do())
            self.touch(); await self._broadcast_screenshot(); return await self._state()

    async def evaluate(self, expression: str, *, caller: str = "agent") -> Any:
        self._require_driver(caller)
        async def _do(): return await self.page.evaluate(expression)
        async with self._lock:
            result = await self._dispatch(_do())
            self.touch()
            return result

    async def screenshot(self, *, full_page: bool = False,
                          kind: str = "png", quality: int = 70) -> bytes:
        async def _shot():
            if kind == "jpeg":
                return await self.page.screenshot(
                    full_page=full_page, type="jpeg",
                    quality=max(10, min(100, quality)),
                )
            return await self.page.screenshot(full_page=full_page)
        async with self._lock:
            self.touch()
            return await self._dispatch(_shot())

    async def extract_text(self, selector: str = "body") -> str:
        async def _do():
            try:
                return await self.page.inner_text(selector, timeout=5_000)
            except Exception:
                return ""
        async with self._lock:
            self.touch()
            return await self._dispatch(_do())

    async def extract_html(self) -> str:
        async def _do(): return await self.page.content()
        async with self._lock:
            self.touch()
            return await self._dispatch(_do())

    async def _state(self) -> dict:
        async def _get():
            try:
                return await self.page.title()
            except Exception:
                return ""
        try:
            title = await self._dispatch(_get())
        except Exception:
            title = ""
        # Include tab list so WebSocket consumers can render the tab strip
        # without a follow-up HTTP call after every frame.
        tabs: list[dict] = []
        for tid, pg in self.tabs.items():
            meta = self.tab_meta.get(tid, {})
            tabs.append({
                "tab_id":         tid,
                "url":            pg.url,
                "is_active":      tid == self.active_tab_id,
                "integration_id": meta.get("integration_id"),
                "label":          meta.get("label"),
            })
        return {
            "session_id":    self.session_id,
            "user_id":       self.user_id,
            "agent_id":      self.agent_id,
            "url":           self.page.url,
            "title":         title,
            "driver":        self.driver,
            "created_at":    self.created_at.isoformat(),
            "last_active":   self.last_active.isoformat(),
            "active_tab_id": self.active_tab_id,
            "tabs":          tabs,
        }

    async def state(self) -> dict:
        async with self._lock:
            return await self._state()

    # --- streaming ----------------------------------------------------------
    async def _broadcast_screenshot(self) -> None:
        if not self.watchers:
            return
        async def _shot(): return await self.page.screenshot(full_page=False)
        try:
            png = await self._dispatch(_shot())
        except Exception:
            return
        for queue in list(self.watchers):
            with contextlib.suppress(Exception):
                queue.put_nowait(png)

    def attach_watcher(self) -> asyncio.Queue[bytes]:
        q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=4)
        self.watchers.add(q)
        return q

    def detach_watcher(self, q: asyncio.Queue[bytes]) -> None:
        self.watchers.discard(q)

    # --- teardown -----------------------------------------------------------
    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        # Charge wall-time minutes to the per-user quota.
        try:
            from governance.browser_policy import check_and_charge_minutes
            elapsed_min = (datetime.now(timezone.utc) - self.created_at).total_seconds() / 60.0
            with contextlib.suppress(Exception):
                await check_and_charge_minutes(self.user_id, elapsed_min)
        except Exception as e:
            logger.debug(f"browser usage charge skipped: {e}")
        async def _persist():
            storage_path = STORAGE_STATE / f"{self.user_id}.json"
            await self.context.storage_state(path=str(storage_path))
        try:
            await self._dispatch(_persist())
        except Exception as e:
            logger.warning(f"Failed to persist storage_state for {self.user_id}: {e}")
        # Closing the context closes every page it owns — no need to
        # individually close each tab. Also clear our in-memory tab map.
        async def _shut(): await self.context.close()
        with contextlib.suppress(Exception):
            await self._dispatch(_shut())
        self.tabs.clear()
        self.tab_meta.clear()


# ── BrowserPool ─────────────────────────────────────────────────────────────
class BrowserPool:
    """Single Playwright browser, many sessions.

    Sessions are keyed by session_id; each session carries its own context so
    cookies, cache, and localStorage are isolated per user.
    """

    def __init__(self) -> None:
        self._pw: Any = None
        self._browser: Browser | None = None
        self._sessions: dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()
        # Dedicated Playwright thread + event loop (Proactor on Windows).
        # Uvicorn's event loop on Windows is a SelectorEventLoop in --reload
        # mode, which CAN'T spawn subprocesses — Playwright needs a
        # ProactorEventLoop. So we run Playwright on our own thread and
        # dispatch coroutines to it from the FastAPI request handlers.
        self._pw_loop: asyncio.AbstractEventLoop | None = None
        self._pw_thread: threading.Thread | None = None
        self._pw_ready = threading.Event()

    def _ensure_pw_loop(self) -> None:
        if self._pw_loop is not None:
            return

        def _worker() -> None:
            try:
                if sys.platform == "win32":
                    # Pre-3.10 had ProactorEventLoop class; 3.10+ uses the
                    # WindowsProactorEventLoopPolicy — both expose an event
                    # loop that supports subprocess_exec.
                    loop = asyncio.ProactorEventLoop()
                else:
                    loop = asyncio.new_event_loop()
            except Exception:
                loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._pw_loop = loop
            self._pw_ready.set()
            try:
                loop.run_forever()
            finally:
                with contextlib.suppress(Exception):
                    loop.close()

        self._pw_thread = threading.Thread(
            target=_worker, daemon=True, name="maars-playwright-loop",
        )
        self._pw_thread.start()
        self._pw_ready.wait(timeout=5)

    async def _run_in_pw(self, coro: Coroutine[Any, Any, _T]) -> _T:
        """Dispatch a coroutine to the Playwright thread's event loop.

        Every Playwright object (browser/context/page) is bound to the loop
        that created it, so ALL operations on those objects must go through
        this helper.
        """
        self._ensure_pw_loop()
        assert self._pw_loop is not None
        fut = asyncio.run_coroutine_threadsafe(coro, self._pw_loop)
        return await asyncio.wrap_future(fut)

    # --- availability -------------------------------------------------------
    @staticmethod
    def available() -> bool:
        """Re-checks on every call — reflects whether Playwright is importable
        right now, not at backend-startup time."""
        ap, _err = _load_playwright()
        return ap is not None

    @staticmethod
    def install_hint() -> str:
        ap, err = _load_playwright()
        if ap is not None:
            return ""
        why = f"  (import error: {err})" if err else ""
        return (
            "Playwright is not installed. Run:\n"
            "    pip install playwright\n"
            "    playwright install chromium\n"
            "(Chromium will download into backend/browser_data/chromium/, "
            "keeping it inside the MAARS install.)" + why
        )

    def try_install(self) -> bool:
        """Best-effort auto-install Chromium on first use. Returns True on
        success, False otherwise. Safe to call repeatedly — idempotent."""
        ap, _err = _load_playwright()
        if ap is None:
            return False
        try:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                env={**os.environ, "PLAYWRIGHT_BROWSERS_PATH": str(CHROMIUM_ROOT)},
                check=True, capture_output=True, timeout=600,
            )
            return True
        except Exception as e:
            logger.warning(f"Auto-install of Chromium failed: {e}")
            return False

    # --- lifecycle ----------------------------------------------------------
    async def _ensure_browser(self) -> "Browser":
        if self._browser is not None:
            return self._browser
        async_playwright_fn, err = _load_playwright()
        if async_playwright_fn is None:
            raise BrowserUnavailable(self.install_hint())
        # Start + launch must happen on the Playwright thread's loop.
        async def _launch():
            if self._pw is None:
                self._pw = await async_playwright_fn().start()
            if self._browser is None:
                try:
                    self._browser = await self._pw.chromium.launch(headless=True)
                except Exception as e:
                    if self.try_install():
                        self._browser = await self._pw.chromium.launch(headless=True)
                    else:
                        raise BrowserUnavailable(
                            f"Could not launch Chromium: {e}\n\n{self.install_hint()}"
                        ) from e
            return self._browser
        async with self._lock:
            if self._browser is not None:
                return self._browser
            return await self._run_in_pw(_launch())

    async def open(
        self, *, user_id: str, agent_id: str | None = None,
        start_url: str | None = None,
        proxy: dict | None = None,
    ) -> BrowserSession:
        # Budget pre-check — fail fast before spinning up Chromium.
        try:
            from governance.browser_policy import (
                check_and_charge_minutes, increment_sessions_opened, BudgetExhausted,
            )
            # A zero-minute charge trips the BudgetExhausted check without
            # actually debiting anything — if the user is already over, stop.
            await check_and_charge_minutes(user_id, 0.0)
            await increment_sessions_opened(user_id)
        except Exception as e:
            # Re-raise BudgetExhausted; swallow others (e.g. Mongo unreachable).
            from governance.browser_policy import BudgetExhausted as _BE
            if isinstance(e, _BE):
                raise
            logger.debug(f"browser budget pre-check skipped: {e}")

        browser = await self._ensure_browser()

        storage_path = STORAGE_STATE / f"{user_id}.json"
        context_args: dict[str, Any] = {
            "viewport":      DEFAULT_VIEWPORT,
            "user_agent":    DEFAULT_USER_AGENT,
            "accept_downloads": False,
            "java_script_enabled": True,
        }
        if storage_path.exists():
            context_args["storage_state"] = str(storage_path)
        # Residential-proxy support for anti-detection scraping. Caller
        # passes a Playwright-compatible dict:
        # {"server": "http://host:port", "username": "...", "password": "..."}.
        # When omitted, the browser uses the host network as before.
        if proxy and isinstance(proxy, dict) and proxy.get("server"):
            context_args["proxy"] = proxy

        async def _make_context_and_page():
            ctx = await browser.new_context(**context_args)
            pg  = await ctx.new_page()
            return ctx, pg
        context, page = await self._run_in_pw(_make_context_and_page())

        sid = f"bs_{uuid.uuid4().hex[:12]}"
        session = BrowserSession(
            session_id=sid, user_id=user_id, agent_id=agent_id,
            context=context, page=page, pool=self,
        )
        self._sessions[sid] = session

        if start_url:
            try:
                await session.navigate(start_url, caller=agent_id and "agent" or "user")
            except Exception as e:
                logger.warning(f"navigate on open failed: {e}")
        return session

    def get(self, session_id: str) -> BrowserSession | None:
        return self._sessions.get(session_id)

    async def list_for_user(self, user_id: str) -> list[dict]:
        out = []
        for s in self._sessions.values():
            if s.user_id == user_id:
                out.append(await s.state())
        return out

    async def close_session(self, session_id: str) -> bool:
        s = self._sessions.pop(session_id, None)
        if s is None:
            return False
        await s.close()
        return True

    async def reap_idle(self) -> int:
        """Close sessions that haven't been touched recently. Call from a
        periodic background task."""
        now = datetime.now(timezone.utc)
        doomed = [
            sid for sid, s in self._sessions.items()
            if (now - s.last_active).total_seconds() > IDLE_TIMEOUT_SEC
        ]
        for sid in doomed:
            await self.close_session(sid)
        return len(doomed)

    async def shutdown(self) -> None:
        for sid in list(self._sessions):
            await self.close_session(sid)

        async def _close_browser():
            if self._browser is not None:
                with contextlib.suppress(Exception):
                    await self._browser.close()
                self._browser = None

        async def _stop_pw():
            if self._pw is not None:
                with contextlib.suppress(Exception):
                    await self._pw.stop()
                self._pw = None

        with contextlib.suppress(Exception):
            await self._run_in_pw(_close_browser())
        with contextlib.suppress(Exception):
            await self._run_in_pw(_stop_pw())

        if self._pw_loop is not None:
            self._pw_loop.call_soon_threadsafe(self._pw_loop.stop)
            self._pw_loop = None


# ── Module-level singleton ──────────────────────────────────────────────────
_POOL: BrowserPool | None = None


def get_browser_pool() -> BrowserPool:
    global _POOL
    if _POOL is None:
        _POOL = BrowserPool()
    return _POOL


# ── Agent-tool helpers ──────────────────────────────────────────────────────
# Thin wrappers that the agent runtime calls by tool name. Each looks up (or
# opens) a session for the (user_id, agent_id) pair so every agent gets its
# own browser context unless they explicitly join an existing one.

async def tool_browser_open(user_id: str, agent_id: str,
                            start_url: str | None = None) -> dict:
    pool = get_browser_pool()
    session = await pool.open(user_id=user_id, agent_id=agent_id, start_url=start_url)
    return await session.state()


async def tool_browser_navigate(session_id: str, url: str, *,
                                caller: str = "agent") -> dict:
    s = get_browser_pool().get(session_id)
    if s is None:
        raise ValueError(f"no such browser session: {session_id}")
    return await s.navigate(url, caller=caller)


async def tool_browser_click(session_id: str, selector: str, *,
                             caller: str = "agent") -> dict:
    s = get_browser_pool().get(session_id)
    if s is None:
        raise ValueError(f"no such browser session: {session_id}")
    return await s.click(selector, caller=caller)


async def tool_browser_fill(session_id: str, selector: str, value: str, *,
                            caller: str = "agent") -> dict:
    s = get_browser_pool().get(session_id)
    if s is None:
        raise ValueError(f"no such browser session: {session_id}")
    return await s.fill(selector, value, caller=caller)


async def tool_browser_extract(session_id: str, selector: str = "body") -> str:
    s = get_browser_pool().get(session_id)
    if s is None:
        raise ValueError(f"no such browser session: {session_id}")
    return await s.extract_text(selector)


async def tool_browser_screenshot(session_id: str) -> str:
    """Returns a base64-encoded PNG so it can travel through the LLM tool
    channel as a string."""
    s = get_browser_pool().get(session_id)
    if s is None:
        raise ValueError(f"no such browser session: {session_id}")
    png = await s.screenshot()
    return base64.b64encode(png).decode()


async def tool_browser_evaluate(session_id: str, expression: str, *,
                                caller: str = "agent") -> Any:
    s = get_browser_pool().get(session_id)
    if s is None:
        raise ValueError(f"no such browser session: {session_id}")
    return await s.evaluate(expression, caller=caller)


async def tool_browser_close(session_id: str) -> bool:
    return await get_browser_pool().close_session(session_id)


async def tool_browser_see_and_act(session_id: str, goal: str, *,
                                    execute: bool = True,
                                    caller: str = "agent") -> dict:
    """One-shot vision decision on the current page.

    Captures a screenshot, asks a vision-capable model what to do next toward
    the goal, optionally executes the action, and returns the decided action.
    Use this when an agent needs to 'see' the page without committing to the
    full autonomous loop.
    """
    from services.browser_vision import decide_next_action, action_to_dict

    s = get_browser_pool().get(session_id)
    if s is None:
        raise ValueError(f"no such browser session: {session_id}")
    png = await s.screenshot()
    state = await s.state()
    action = await decide_next_action(
        goal=goal, history=[], current_url=state.get("url", ""), screenshot_png=png,
    )
    if execute and action.kind in {"click", "type", "key", "navigate", "scroll"}:
        try:
            if action.kind == "click" and action.x is not None and action.y is not None:
                await s.click_at(action.x, action.y, caller=caller)
            elif action.kind == "type":
                await s.type_text(action.text or "", caller=caller)
            elif action.kind == "key":
                await s.press_key(action.key or "Enter", caller=caller)
            elif action.kind == "navigate":
                await s.navigate(action.url or "about:blank", caller=caller)
            elif action.kind == "scroll":
                await s.scroll(int(action.dy or 400), caller=caller)
        except PermissionError as e:
            action.reason = f"{action.reason} (blocked: {e})"
    return {"action": action_to_dict(action), "state": await s.state()}


async def tool_browser_run_goal(user_id: str, goal: str, *,
                                start_url: str | None = None,
                                max_steps: int = 20,
                                session_id: str | None = None) -> list[dict]:
    """Run the autonomous BrowserAgent until it finishes, errors, or hits
    max_steps. Returns the full event list — use the SSE endpoint for
    streaming UIs. Safe for agent-initiated calls."""
    from services.browser_agent import run_goal
    events: list[dict] = []
    async for evt in run_goal(
        user_id=user_id, goal=goal, start_url=start_url, max_steps=max_steps,
        existing_session_id=session_id,
    ):
        events.append(evt.to_dict())
        if evt.kind in {"done", "error"}:
            break
    return events
