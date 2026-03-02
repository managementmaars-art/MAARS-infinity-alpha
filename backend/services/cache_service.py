"""In-memory TTL cache for frequently accessed data."""
import time
import logging

logger = logging.getLogger(__name__)

class TTLCache:
    def __init__(self):
        self._store = {}
    
    def get(self, key):
        entry = self._store.get(key)
        if entry and entry["expires"] > time.time():
            return entry["value"]
        if entry:
            del self._store[key]
        return None
    
    def set(self, key, value, ttl=60):
        self._store[key] = {"value": value, "expires": time.time() + ttl}
    
    def invalidate(self, key):
        self._store.pop(key, None)
    
    def invalidate_prefix(self, prefix):
        keys = [k for k in self._store if k.startswith(prefix)]
        for k in keys:
            del self._store[k]
    
    def clear(self):
        self._store.clear()

cache = TTLCache()
