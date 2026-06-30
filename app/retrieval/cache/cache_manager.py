import time
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, Tuple


class BaseCacheManager(ABC):
    """Abstract interface defining required interactions for caching subsystems."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Fetch value from cache. Returns None if key is expired or missing."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store value inside cache alongside a TTL expiration timeout."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Purge key entry from cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Purge all entries from cache."""
        pass


class InMemoryCacheManager(BaseCacheManager):
    """TTL-aware in-memory dictionary-backed cache manager."""

    def __init__(self):
        self._store: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        
        value, expires_at = self._store[key]
        if time.time() > expires_at:
            self.delete(key)
            return None
            
        return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        # Default fallback to 5 minutes
        ttl = ttl_seconds if ttl_seconds is not None else 300
        expires_at = time.time() + ttl
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
