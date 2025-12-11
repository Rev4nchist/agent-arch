"""
Performance Baseline Tests for HMLR Memory System.

Tests establish baseline performance metrics:
- Routing latency (P50, P95, P99)
- Cache efficiency
- Concurrent user handling
- Memory usage patterns

These tests help ensure the system meets performance requirements
and detect regressions early.

Run with: pytest tests/test_hmlr_performance.py -v --tb=short
"""
import pytest
import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone
import uuid
import asyncio

from src.hmlr.cache import TTLLRUCache
from src.hmlr.models import BridgeBlock, Fact, FactCategory


def create_test_block(
    block_id: str = None,
    session_id: str = "test-session",
    user_id: str = "test-user"
) -> BridgeBlock:
    """Create a test BridgeBlock."""
    return BridgeBlock(
        id=block_id or f"bb_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        user_id=user_id,
        topic_label="Test Topic",
        summary="Test summary",
        keywords=["test"],
        open_loops=[],
        decisions_made=[],
        status="ACTIVE",
        last_activity=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc)
    )


class TestCachePerformance:
    """Test cache performance characteristics."""

    def test_cache_write_latency(self):
        """Cache write operations complete within target latency."""
        cache = TTLLRUCache(maxsize=1000, ttl_minutes=5)
        embedding = [0.1] * 1536

        latencies = []
        for i in range(100):
            start = time.perf_counter()
            cache.set(f"key_{i}", embedding.copy())
            latencies.append((time.perf_counter() - start) * 1000)

        p50 = statistics.median(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)

        assert p50 < 1.0, f"P50 write latency {p50:.3f}ms exceeds 1ms target"
        assert p99 < 5.0, f"P99 write latency {p99:.3f}ms exceeds 5ms target"

    def test_cache_read_latency(self):
        """Cache read operations complete within target latency."""
        cache = TTLLRUCache(maxsize=1000, ttl_minutes=5)
        embedding = [0.1] * 1536

        for i in range(100):
            cache.set(f"key_{i}", embedding.copy())

        latencies = []
        for i in range(100):
            start = time.perf_counter()
            cache.get(f"key_{i}")
            latencies.append((time.perf_counter() - start) * 1000)

        p50 = statistics.median(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)

        assert p50 < 0.5, f"P50 read latency {p50:.3f}ms exceeds 0.5ms target"
        assert p99 < 2.0, f"P99 read latency {p99:.3f}ms exceeds 2ms target"

    def test_cache_eviction_performance(self):
        """Cache maintains performance during eviction."""
        cache = TTLLRUCache(maxsize=100, ttl_minutes=5)
        embedding = [0.1] * 1536

        latencies = []
        for i in range(500):
            start = time.perf_counter()
            cache.set(f"key_{i}", embedding.copy())
            latencies.append((time.perf_counter() - start) * 1000)

        eviction_latencies = latencies[100:]
        p99 = statistics.quantiles(eviction_latencies, n=100)[98] if len(eviction_latencies) >= 100 else max(eviction_latencies)

        assert p99 < 10.0, f"P99 eviction latency {p99:.3f}ms exceeds 10ms target"

    def test_cache_hit_rate_improves_with_locality(self):
        """Cache hit rate improves with temporal locality."""
        cache = TTLLRUCache(maxsize=50, ttl_minutes=5)
        embedding = [0.1] * 1536

        for i in range(50):
            cache.set(f"key_{i}", embedding.copy())

        for i in range(50):
            cache.get(f"key_{i % 50}")

        stats = cache.stats()
        hit_rate = stats["hit_rate_percent"]

        assert hit_rate > 50, f"Hit rate {hit_rate}% should exceed 50% with locality"


class TestConcurrencyPerformance:
    """Test performance under concurrent access."""

    def test_concurrent_cache_access_no_errors(self):
        """Concurrent cache access produces no errors."""
        cache = TTLLRUCache(maxsize=500, ttl_minutes=5)
        errors = []
        iterations = 100

        def worker(thread_id):
            try:
                for i in range(iterations):
                    embedding = [float(thread_id + i)] * 1536
                    cache.set(f"key_{thread_id}_{i}", embedding)
                    cache.get(f"key_{thread_id}_{i}")
                    cache.get(f"key_{(thread_id + 1) % 10}_{i}")
            except Exception as e:
                errors.append(str(e))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0, f"Concurrent access errors: {errors}"

    def test_concurrent_throughput(self):
        """Cache maintains throughput under concurrent load."""
        cache = TTLLRUCache(maxsize=1000, ttl_minutes=5)
        embedding = [0.1] * 1536
        operations = []
        duration = 1.0

        def worker():
            count = 0
            start = time.time()
            while time.time() - start < duration:
                cache.set(f"key_{threading.current_thread().name}_{count}", embedding.copy())
                cache.get(f"key_{threading.current_thread().name}_{count}")
                count += 1
            operations.append(count * 2)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        total_ops = sum(operations)
        ops_per_second = total_ops / duration

        assert ops_per_second > 1000, f"Throughput {ops_per_second:.0f} ops/s below 1000 target"


class TestMemoryEfficiency:
    """Test memory usage efficiency."""

    def test_cache_respects_size_limit(self):
        """Cache respects configured size limit."""
        cache = TTLLRUCache(maxsize=100, ttl_minutes=5)
        embedding = [0.1] * 1536

        for i in range(500):
            cache.set(f"key_{i}", embedding.copy())

        assert len(cache) <= 100, f"Cache size {len(cache)} exceeds maxsize 100"

    def test_ttl_cleanup_frees_memory(self):
        """TTL cleanup properly frees entries."""
        cache = TTLLRUCache(maxsize=100, ttl_minutes=0.0167)
        embedding = [0.1] * 1536

        for i in range(50):
            cache.set(f"key_{i}", embedding.copy())

        assert len(cache) == 50

        time.sleep(1.5)

        removed = cache.cleanup_expired()

        assert removed == 50, f"Expected 50 removed, got {removed}"
        assert len(cache) == 0, f"Cache should be empty, has {len(cache)} entries"


class TestLatencyDistribution:
    """Test latency distribution metrics."""

    def test_model_creation_latency(self):
        """Model creation latency within acceptable range."""
        latencies = []

        for _ in range(50):
            start = time.perf_counter()
            block = create_test_block()
            latencies.append((time.perf_counter() - start) * 1000)

        p50 = statistics.median(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)

        assert p50 < 5.0, f"P50 model creation latency {p50:.3f}ms exceeds 5ms"
        assert p99 < 20.0, f"P99 model creation latency {p99:.3f}ms exceeds 20ms"

    def test_fact_creation_latency(self):
        """Fact creation latency within acceptable range."""
        latencies = []

        for i in range(50):
            start = time.perf_counter()
            fact = Fact(
                user_id="test-user",
                key=f"key_{i}",
                value=f"value_{i}",
                category=FactCategory.DEFINITION,
                confidence=0.9,
                fact_id=i
            )
            latencies.append((time.perf_counter() - start) * 1000)

        p50 = statistics.median(latencies)
        p99 = max(latencies)

        assert p50 < 2.0, f"P50 fact creation latency {p50:.3f}ms exceeds 2ms"
        assert p99 < 10.0, f"P99 fact creation latency {p99:.3f}ms exceeds 10ms"


class TestScalabilityIndicators:
    """Test scalability characteristics."""

    def test_cache_performance_scales_linearly(self):
        """Cache performance scales reasonably with size."""
        embedding = [0.1] * 1536

        latencies_small = []
        cache_small = TTLLRUCache(maxsize=100, ttl_minutes=5)
        for i in range(100):
            cache_small.set(f"key_{i}", embedding.copy())
        for i in range(50):
            start = time.perf_counter()
            cache_small.get(f"key_{i}")
            latencies_small.append((time.perf_counter() - start) * 1000)

        latencies_large = []
        cache_large = TTLLRUCache(maxsize=1000, ttl_minutes=5)
        for i in range(1000):
            cache_large.set(f"key_{i}", embedding.copy())
        for i in range(50):
            start = time.perf_counter()
            cache_large.get(f"key_{i}")
            latencies_large.append((time.perf_counter() - start) * 1000)

        avg_small = statistics.mean(latencies_small)
        avg_large = statistics.mean(latencies_large)

        ratio = avg_large / avg_small if avg_small > 0 else 1.0
        assert ratio < 5.0, f"Large cache {ratio:.1f}x slower than small cache (should be <5x)"

    def test_concurrent_user_simulation(self):
        """Simulate concurrent users accessing cache."""
        cache = TTLLRUCache(maxsize=1000, ttl_minutes=5)
        embedding = [0.1] * 1536
        user_latencies = {}

        def user_workload(user_id):
            latencies = []
            for i in range(20):
                key = f"user_{user_id}_key_{i}"
                start = time.perf_counter()
                cache.set(key, embedding.copy())
                cache.get(key)
                latencies.append((time.perf_counter() - start) * 1000)
            return user_id, latencies

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(user_workload, uid) for uid in range(10)]
            for f in as_completed(futures):
                user_id, latencies = f.result()
                user_latencies[user_id] = statistics.median(latencies)

        all_medians = list(user_latencies.values())
        overall_p50 = statistics.median(all_medians)
        overall_max = max(all_medians)

        assert overall_p50 < 2.0, f"P50 user latency {overall_p50:.3f}ms exceeds 2ms"
        assert overall_max < 10.0, f"Max user latency {overall_max:.3f}ms exceeds 10ms"


class TestPerformanceRegression:
    """Tests to detect performance regressions."""

    def test_baseline_operations_per_second(self):
        """Establish baseline operations per second."""
        cache = TTLLRUCache(maxsize=500, ttl_minutes=5)
        embedding = [0.1] * 1536

        start = time.time()
        ops = 0
        target_duration = 1.0

        while time.time() - start < target_duration:
            cache.set(f"key_{ops}", embedding.copy())
            cache.get(f"key_{ops % 100}")
            ops += 1

        ops_per_second = ops / (time.time() - start)

        assert ops_per_second > 5000, f"Baseline {ops_per_second:.0f} ops/s below 5000 minimum"

    def test_stats_collection_overhead(self):
        """Stats collection has minimal overhead."""
        cache = TTLLRUCache(maxsize=500, ttl_minutes=5)
        embedding = [0.1] * 1536

        for i in range(100):
            cache.set(f"key_{i}", embedding.copy())
            cache.get(f"key_{i}")

        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            cache.stats()
            latencies.append((time.perf_counter() - start) * 1000)

        p99 = max(latencies)
        assert p99 < 1.0, f"Stats collection P99 {p99:.3f}ms exceeds 1ms"


class TestDataIsolationPerformance:
    """Test that user isolation doesn't impact performance."""

    def test_user_key_isolation_performance(self):
        """User-namespaced keys don't impact lookup performance."""
        cache = TTLLRUCache(maxsize=1000, ttl_minutes=5)
        embedding = [0.1] * 1536

        for user_id in range(10):
            for i in range(50):
                cache.set(f"user_{user_id}_key_{i}", embedding.copy())

        latencies = []
        for _ in range(100):
            user_id = _ % 10
            key_id = _ % 50
            start = time.perf_counter()
            cache.get(f"user_{user_id}_key_{key_id}")
            latencies.append((time.perf_counter() - start) * 1000)

        p50 = statistics.median(latencies)
        p99 = max(latencies)

        assert p50 < 0.5, f"P50 isolated lookup {p50:.3f}ms exceeds 0.5ms"
        assert p99 < 2.0, f"P99 isolated lookup {p99:.3f}ms exceeds 2ms"


class TestEdgeCasePerformance:
    """Test performance in edge cases."""

    def test_empty_cache_lookup_fast(self):
        """Empty cache lookup is fast."""
        cache = TTLLRUCache(maxsize=100, ttl_minutes=5)

        latencies = []
        for i in range(100):
            start = time.perf_counter()
            cache.get(f"nonexistent_{i}")
            latencies.append((time.perf_counter() - start) * 1000)

        p99 = max(latencies)
        assert p99 < 0.5, f"Empty cache lookup P99 {p99:.3f}ms exceeds 0.5ms"

    def test_full_cache_write_performance(self):
        """Writing to full cache maintains performance."""
        cache = TTLLRUCache(maxsize=100, ttl_minutes=5)
        embedding = [0.1] * 1536

        for i in range(100):
            cache.set(f"initial_{i}", embedding.copy())

        latencies = []
        for i in range(100):
            start = time.perf_counter()
            cache.set(f"new_{i}", embedding.copy())
            latencies.append((time.perf_counter() - start) * 1000)

        p99 = max(latencies)
        assert p99 < 5.0, f"Full cache write P99 {p99:.3f}ms exceeds 5ms"
