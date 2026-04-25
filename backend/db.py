"""Shared database connection module - used by server.py and all route modules."""

import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).parent
PROJECT_ROOT = ROOT_DIR.parent

# Match server.py so direct imports behave the same way in scripts and tests.
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(ROOT_DIR / ".env", override=False)


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if value:
        return value
    raise RuntimeError(
        f"Missing required environment variable: {name}. "
        "Copy .env.example to .env and provide the required values."
    )


mongo_url = _require_env("MONGO_URL")
client = AsyncIOMotorClient(mongo_url)
db = client[_require_env("DB_NAME")]
