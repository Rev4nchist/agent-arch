"""TTL-LRU Cache for HMLR embedding storage.

Thread-safe bounded cache with time-to-live expiration.
Used by Governor to cache block embeddings and avoid redundant API calls.
"""

import threading
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from collections import OrderedDict

logger = logging.getLogger(__name__)


class TTLLRUCache:
    """Thread-safe LRU cache with TTL expiration.

    Features:
    - Bounded size with LRU eviction
    - Time-to-live expiration per entry
    - Thread-safe operations
    - Statistics tracking for monitoring
    """

    def __init__(self, maxsize: int = 1000, ttl_minutes: int = 5):
        """Initialize cache.

        Args:
            maxsize: Maximum number of entries (default: 1000)
            ttl_minutes: Time-to-live in minutes (default: 5)
        """
        self.maxsize = maxsize
        self.ttl = timedelta(minutes=ttl_minutes)
        self._cache: OrderedDict[str, Tuple[List[float], datetime]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[List[float]]:
        """Get embedding from cache.

        Args:
            key: Cache key

        Returns:
            Embedding vector if found and not expired, None otherwise
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            embedding, timestamp = self._cache[key]
            now = datetime.now(timezone.utc)

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)

            if now - timestamp > self.ttl:
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache entry expired: {key[:50]}")
                return None

            self._cache.move_to_end(key)
            self._hits += 1
            return embedding

    def set(self, key: str, embedding: List[float]) -> None:
        """Store embedding in cache.

        Args:
            key: Cache key
            embedding: Embedding vector to store
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self.maxsize:
                oldest_key, _ = self._cache.popitem(last=False)
                logger.debug(f"Cache evicted LRU entry: {oldest_key[:50]}")

            self._cache[key] = (embedding, datetime.now(timezone.utc))

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")

    def __contains__(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None

    def __len__(self) -> int:
        """Return number of entries (may include expired)."""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache metrics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0

            return {
                "size": len(self._cache),
                "maxsize": self.maxsize,
                "ttl_minutes": self.ttl.total_seconds() / 60,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_percent": round(hit_rate, 2)
            }

    def cleanup_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            expired_keys = []

            for key, (_, timestamp) in self._cache.items():
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                if now - timestamp > self.ttl:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)
