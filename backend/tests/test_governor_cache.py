"""
Unit tests for Governor's TTLLRUCache.

Tests cover:
- Max size enforcement (LRU eviction)
- TTL expiration
- Thread safety under concurrent access
- Cache statistics
"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.hmlr.cache import TTLLRUCache


class TestCacheBasicOperations:
    """Test basic cache get/set operations."""

    def test_set_and_get(self):
        """Basic set and get works."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)
        embedding = [0.1, 0.2, 0.3]

        cache.set("key1", embedding)
        result = cache.get("key1")

        assert result == embedding

    def test_get_missing_key(self):
        """Get returns None for missing key."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)

        result = cache.get("nonexistent")

        assert result is None

    def test_overwrite_existing_key(self):
        """Setting existing key overwrites value."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)

        cache.set("key1", [1.0])
        cache.set("key1", [2.0])

        assert cache.get("key1") == [2.0]
        assert len(cache) == 1

    def test_contains_operator(self):
        """__contains__ checks existence and expiration."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)
        cache.set("key1", [1.0])

        assert "key1" in cache
        assert "nonexistent" not in cache

    def test_clear(self):
        """Clear removes all entries."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)
        cache.set("key1", [1.0])
        cache.set("key2", [2.0])

        cache.clear()

        assert len(cache) == 0
        assert cache.get("key1") is None


class TestCacheMaxSize:
    """Test max size enforcement and LRU eviction."""

    def test_cache_respects_max_size(self):
        """Cache evicts oldest when maxsize reached."""
        cache = TTLLRUCache(maxsize=3, ttl_minutes=5)

        cache.set("key1", [1.0])
        cache.set("key2", [2.0])
        cache.set("key3", [3.0])
        cache.set("key4", [4.0])

        assert len(cache) == 3
        assert cache.get("key1") is None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None
        assert cache.get("key4") is not None

    def test_lru_eviction_order(self):
        """Least recently used is evicted first."""
        cache = TTLLRUCache(maxsize=3, ttl_minutes=5)

        cache.set("key1", [1.0])
        cache.set("key2", [2.0])
        cache.set("key3", [3.0])

        cache.get("key1")

        cache.set("key4", [4.0])

        assert cache.get("key1") is not None
        assert cache.get("key2") is None
        assert cache.get("key3") is not None
        assert cache.get("key4") is not None

    def test_maxsize_one(self):
        """Cache with maxsize=1 works correctly."""
        cache = TTLLRUCache(maxsize=1, ttl_minutes=5)

        cache.set("key1", [1.0])
        cache.set("key2", [2.0])

        assert len(cache) == 1
        assert cache.get("key1") is None
        assert cache.get("key2") is not None


class TestCacheTTL:
    """Test TTL expiration."""

    def test_entry_expires_after_ttl(self):
        """Entry returns None after TTL expires."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=0.0167)

        cache.set("key1", [1.0])

        assert cache.get("key1") is not None

        time.sleep(1.5)

        assert cache.get("key1") is None

    def test_entry_valid_before_ttl(self):
        """Entry is accessible before TTL expires."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)

        cache.set("key1", [1.0])
        time.sleep(0.1)

        assert cache.get("key1") is not None

    def test_cleanup_expired_removes_old_entries(self):
        """cleanup_expired removes expired entries."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=0.0167)

        cache.set("key1", [1.0])
        cache.set("key2", [2.0])

        time.sleep(1.5)

        removed = cache.cleanup_expired()

        assert removed == 2
        assert len(cache) == 0


class TestCacheStatistics:
    """Test cache statistics tracking."""

    def test_stats_initial(self):
        """Stats start at zero."""
        cache = TTLLRUCache(maxsize=100, ttl_minutes=5)
        stats = cache.stats()

        assert stats["size"] == 0
        assert stats["maxsize"] == 100
        assert stats["ttl_minutes"] == 5.0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate_percent"] == 0.0

    def test_stats_tracks_hits_and_misses(self):
        """Stats correctly track hits and misses."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)

        cache.set("key1", [1.0])

        cache.get("key1")
        cache.get("key1")
        cache.get("nonexistent")
        cache.get("also_missing")

        stats = cache.stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["hit_rate_percent"] == 50.0


class TestCacheThreadSafety:
    """Test thread safety under concurrent access."""

    def test_concurrent_sets(self):
        """Concurrent sets don't corrupt cache."""
        cache = TTLLRUCache(maxsize=1000, ttl_minutes=5)

        def set_values(thread_id):
            for i in range(100):
                cache.set(f"thread_{thread_id}_key_{i}", [float(i)])

        threads = []
        for t_id in range(10):
            t = threading.Thread(target=set_values, args=(t_id,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(cache) == 1000

    def test_concurrent_gets_and_sets(self):
        """Concurrent reads and writes don't crash."""
        cache = TTLLRUCache(maxsize=100, ttl_minutes=5)
        errors = []

        def reader_writer(thread_id):
            try:
                for i in range(50):
                    cache.set(f"key_{thread_id}_{i}", [float(i)])
                    cache.get(f"key_{thread_id}_{i}")
                    cache.get(f"key_{(thread_id + 1) % 10}_{i}")
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(reader_writer, i) for i in range(10)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0

    def test_concurrent_eviction(self):
        """Concurrent access with eviction doesn't corrupt state."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)
        errors = []

        def writer(thread_id):
            try:
                for i in range(100):
                    cache.set(f"key_{thread_id}_{i}", [float(i)])
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(writer, i) for i in range(5)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0
        assert len(cache) <= 10


class TestCacheEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_embedding(self):
        """Empty embedding can be stored and retrieved."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)

        cache.set("empty", [])
        result = cache.get("empty")

        assert result == []

    def test_large_embedding(self):
        """Large embedding (1536 dims) works correctly."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)
        embedding = [0.001 * i for i in range(1536)]

        cache.set("large", embedding)
        result = cache.get("large")

        assert result == embedding
        assert len(result) == 1536

    def test_special_characters_in_key(self):
        """Keys with special characters work."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)

        cache.set("block_user@domain.com_123", [1.0])
        result = cache.get("block_user@domain.com_123")

        assert result == [1.0]

    def test_very_long_key(self):
        """Very long keys work."""
        cache = TTLLRUCache(maxsize=10, ttl_minutes=5)
        long_key = "k" * 10000

        cache.set(long_key, [1.0])
        result = cache.get(long_key)

        assert result == [1.0]
