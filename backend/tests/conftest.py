"""
Shared pytest config for the MAARS backend test suite.

Exposes a module-scoped event loop (`MAARS_TEST_LOOP`) so every test file
can share one loop across the session. Motor's AsyncIOMotorClient binds to
the loop it's first awaited on, so running two test files with independent
`asyncio.run()` calls leaves the second loop unable to reuse the Mongo client.
"""
from __future__ import annotations

import asyncio

# Session-wide loop. Assigned once at import; never replaced.
MAARS_TEST_LOOP: asyncio.AbstractEventLoop = asyncio.new_event_loop()
asyncio.set_event_loop(MAARS_TEST_LOOP)
