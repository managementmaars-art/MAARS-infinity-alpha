---
name: python-expert
description: Python expert patterns — async/await, dataclasses, typing, generators, decorators, context managers, performance, testing for MAARS Python agents
---

# Python Expert — MAARS Reference

## Modern Python Patterns

### Type Hints & Dataclasses
```python
from dataclasses import dataclass, field
from typing import Optional, Union, Literal, TypeVar, Generic
from collections.abc import Callable, AsyncIterator

T = TypeVar("T")

@dataclass
class Result(Generic[T]):
    value: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(value=value)
    
    @classmethod
    def err(cls, error: str) -> "Result[T]":
        return cls(error=error)
    
    @property
    def is_ok(self) -> bool:
        return self.error is None

# TypedDict for structured dicts
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    email: str
    name: str
    role: Literal["admin", "user", "guest"]
```

### Async Patterns
```python
import asyncio
from contextlib import asynccontextmanager

# Concurrent execution
async def fetch_all(urls: list[str]) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Semaphore for rate limiting
async def rate_limited_fetch(urls: list[str], limit: int = 10):
    semaphore = asyncio.Semaphore(limit)
    async def bounded_fetch(url):
        async with semaphore:
            return await fetch(url)
    return await asyncio.gather(*[bounded_fetch(url) for url in urls])

# Async context manager
@asynccontextmanager
async def managed_connection(url: str):
    conn = await connect(url)
    try:
        yield conn
    finally:
        await conn.close()

# Async generator
async def stream_data(source) -> AsyncIterator[dict]:
    async for chunk in source:
        yield process(chunk)
```

### Decorators
```python
import functools
import time
from typing import TypeVar, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")

def retry(max_attempts: int = 3, delay: float = 1.0, 
          exceptions: tuple = (Exception,)):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
        return async_wrapper
    return decorator

def cache_result(ttl_seconds: int = 300):
    cache = {}
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            key = str(args)
            if key in cache:
                result, ts = cache[key]
                if time.time() - ts < ttl_seconds:
                    return result
            result = func(*args)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator
```

### Context Managers
```python
from contextlib import contextmanager, suppress

@contextmanager
def timer(label: str = ""):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}s")

# Suppress specific exceptions
with suppress(FileNotFoundError):
    os.remove("temp.txt")
```

### Generators & Itertools
```python
import itertools
from collections import defaultdict

def batch(iterable, size: int):
    """Yield successive n-sized chunks"""
    it = iter(iterable)
    while chunk := list(itertools.islice(it, size)):
        yield chunk

def sliding_window(seq, n: int):
    """Sliding window of size n"""
    it = iter(seq)
    window = collections.deque(itertools.islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)

# GroupBy
from itertools import groupby
from operator import itemgetter

data = [{"dept": "eng", "name": "Alice"}, {"dept": "eng", "name": "Bob"},
        {"dept": "hr", "name": "Carol"}]
sorted_data = sorted(data, key=itemgetter("dept"))
groups = {k: list(v) for k, v in groupby(sorted_data, key=itemgetter("dept"))}
```

### Performance Patterns
```python
# Use __slots__ for memory-efficient classes
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

# Profile code
import cProfile, pstats, io
def profile(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(20)
        print(s.getvalue())
        return result
    return wrapper

# List comprehension vs map — use comprehension for clarity
squares = [x**2 for x in range(1000)]  # preferred
filtered = [x for x in data if x > 0 and x < 100]

# Use walrus operator := (3.8+)
if match := pattern.search(text):
    print(match.group(0))

while chunk := file.read(8192):
    process(chunk)
```

### Testing with pytest
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_db():
    with patch("myapp.db.get_connection") as mock:
        mock.return_value.__aenter__ = AsyncMock(return_value=MagicMock())
        yield mock

@pytest.mark.asyncio
async def test_create_user(mock_db):
    result = await create_user(email="test@test.com")
    assert result.id is not None
    mock_db.assert_called_once()

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected

# Fixtures with teardown
@pytest.fixture
async def test_db():
    db = await create_test_database()
    yield db
    await db.drop_all()
```

## Models to Use
- **Python code generation**: `claude-opus-4-6` (best Python quality)
- **Code review/optimization**: `claude-opus-4-6`
- **Bug fixing**: `claude-sonnet-4-6`
- **Test writing**: `claude-sonnet-4-6`
