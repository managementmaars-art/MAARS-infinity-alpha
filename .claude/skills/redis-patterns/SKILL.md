---
name: redis-patterns
description: Redis patterns — caching, sessions, pub/sub, queues, rate limiting, leaderboards, distributed locks, Redis Stack for MAARS caching agents
---

# Redis Patterns — MAARS Reference

## Core Data Structures
```python
import redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Strings — simple cache
r.set("user:123", json.dumps(user_data), ex=3600)  # TTL 1 hour
user = json.loads(r.get("user:123") or "{}")

# Hash — object storage
r.hset("user:123", mapping={"name": "Alice", "email": "alice@example.com"})
r.hget("user:123", "name")
r.hgetall("user:123")
r.hincrby("user:123", "login_count", 1)

# List — queues, recent items
r.lpush("notifications:user:123", notification_json)  # prepend
r.lrange("notifications:user:123", 0, 19)  # latest 20
r.ltrim("notifications:user:123", 0, 99)  # keep only 100

# Set — unique collections
r.sadd("active_users", user_id)
r.sismember("active_users", user_id)
r.smembers("active_users")
r.sinterstore("mutual_friends", "friends:alice", "friends:bob")

# Sorted Set — leaderboards, priority queues
r.zadd("leaderboard", {player_id: score})
r.zrevrange("leaderboard", 0, 9, withscores=True)  # top 10
r.zrank("leaderboard", player_id)  # rank (0-based)
r.zincrby("leaderboard", points, player_id)
```

## Caching Patterns
```python
from functools import wraps
import hashlib

def cache(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix or func.__name__}:{hashlib.md5(str(args+tuple(sorted(kwargs.items()))).encode()).hexdigest()}"
            
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            r.set(cache_key, json.dumps(result, default=str), ex=ttl)
            return result
        return wrapper
    return decorator

@cache(ttl=3600, key_prefix="user")
async def get_user(user_id: int) -> dict:
    return await db.fetch_user(user_id)

# Cache-aside pattern
def get_with_cache(key: str, fetch_fn, ttl: int = 300):
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    
    data = fetch_fn()
    r.set(key, json.dumps(data), ex=ttl)
    return data

# Cache invalidation
def invalidate_user_cache(user_id: int):
    keys = r.keys(f"user:*{user_id}*")
    if keys:
        r.delete(*keys)
```

## Rate Limiting
```python
def rate_limit(user_id: str, limit: int, window_seconds: int) -> bool:
    """Sliding window rate limiter. Returns True if allowed."""
    key = f"rate:{user_id}:{int(time.time() // window_seconds)}"
    
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_seconds * 2)
    count, _ = pipe.execute()
    
    return count <= limit

# Token bucket (smoother)
def token_bucket_allow(user_id: str, rate: float = 10, burst: int = 20) -> bool:
    """rate = tokens per second, burst = max tokens"""
    key = f"token_bucket:{user_id}"
    now = time.time()
    
    script = """
    local tokens = tonumber(redis.call('hget', KEYS[1], 'tokens') or ARGV[3])
    local last = tonumber(redis.call('hget', KEYS[1], 'last') or ARGV[2])
    local delta = math.max(0, tonumber(ARGV[2]) - last) * tonumber(ARGV[1])
    tokens = math.min(tonumber(ARGV[3]), tokens + delta)
    if tokens >= 1 then
        tokens = tokens - 1
        redis.call('hset', KEYS[1], 'tokens', tokens, 'last', ARGV[2])
        redis.call('expire', KEYS[1], 3600)
        return 1
    end
    redis.call('hset', KEYS[1], 'last', ARGV[2])
    return 0
    """
    return bool(r.eval(script, 1, key, rate, now, burst))
```

## Pub/Sub & Queues
```python
# Publisher
def publish_event(channel: str, event: dict):
    r.publish(channel, json.dumps(event))

# Subscriber
def subscribe_to_events(channels: list[str]):
    pubsub = r.pubsub()
    pubsub.subscribe(*channels)
    for message in pubsub.listen():
        if message["type"] == "message":
            event = json.loads(message["data"])
            handle_event(channel=message["channel"], event=event)

# Redis Streams (durable queues, like Kafka-lite)
def publish_to_stream(stream: str, data: dict) -> str:
    return r.xadd(stream, data, maxlen=10000)  # returns message ID

def consume_stream(stream: str, group: str, consumer: str, count: int = 10):
    # Create group if not exists
    try:
        r.xgroup_create(stream, group, id="0", mkstream=True)
    except redis.exceptions.ResponseError:
        pass  # Group already exists
    
    messages = r.xreadgroup(group, consumer, {stream: ">"}, count=count, block=5000)
    for stream_name, msg_list in (messages or []):
        for msg_id, fields in msg_list:
            yield msg_id, fields
            r.xack(stream_name, group, msg_id)  # acknowledge
```

## Distributed Lock
```python
import uuid

def acquire_lock(lock_name: str, timeout: int = 10) -> str | None:
    """Returns lock token if acquired, None if already locked"""
    token = str(uuid.uuid4())
    acquired = r.set(f"lock:{lock_name}", token, ex=timeout, nx=True)
    return token if acquired else None

def release_lock(lock_name: str, token: str) -> bool:
    """Only release if we own the lock (prevents accidental release)"""
    script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    return bool(r.eval(script, 1, f"lock:{lock_name}", token))

# Context manager
from contextlib import contextmanager

@contextmanager
def redis_lock(name: str, timeout: int = 10):
    token = acquire_lock(name, timeout)
    if not token:
        raise RuntimeError(f"Could not acquire lock: {name}")
    try:
        yield
    finally:
        release_lock(name, token)
```

## Session Storage
```python
# Fast session management
def create_session(user_id: int, data: dict, ttl: int = 86400) -> str:
    session_id = str(uuid.uuid4())
    r.hset(f"session:{session_id}", mapping={
        "user_id": str(user_id),
        "created_at": str(time.time()),
        **{k: json.dumps(v) for k, v in data.items()}
    })
    r.expire(f"session:{session_id}", ttl)
    return session_id

def get_session(session_id: str) -> dict | None:
    data = r.hgetall(f"session:{session_id}")
    if not data:
        return None
    r.expire(f"session:{session_id}", 86400)  # Slide expiry
    return data
```

## Models to Use
- **Cache strategy design**: `claude-sonnet-4-6`
- **Lua scripting for Redis**: `claude-opus-4-6`
- **Rate limiting logic**: `claude-sonnet-4-6`
