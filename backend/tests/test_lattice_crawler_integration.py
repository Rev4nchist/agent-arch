"""
Integration tests for LatticeCrawler against real Azure AI Search.

These tests require:
- AZURE_SEARCH_ENDPOINT configured
- AZURE_SEARCH_API_KEY configured
- AZURE_OPENAI_ENDPOINT configured for embeddings

Tests use a dedicated test index that is cleaned up after tests.

Run with: pytest tests/test_lattice_crawler_integration.py -v --tb=short
Skip with: pytest tests/test_lattice_crawler_integration.py -v -m "not integration"
"""
import pytest
import asyncio
import uuid
from datetime import datetime, timezone

from src.hmlr.lattice_crawler import LatticeCrawler
from src.hmlr.models import Fact, BridgeBlock, FactCategory, MemoryType
from src.config import settings


TEST_INDEX_NAME = "hmlr-test-integration"


def is_azure_configured():
    """Check if Azure services are configured."""
    return bool(
        settings.azure_search_endpoint and
        settings.azure_search_api_key and
        settings.azure_openai_endpoint and
        settings.azure_openai_api_key
    )


pytestmark = pytest.mark.skipif(
    not is_azure_configured(),
    reason="Azure services not configured"
)


@pytest.fixture(scope="module")
def integration_crawler():
    """Create LatticeCrawler with test index for integration tests."""
    crawler = LatticeCrawler(
        index_name=TEST_INDEX_NAME,
        endpoint=settings.azure_search_endpoint,
        api_key=settings.azure_search_api_key
    )
    crawler.create_or_update_index()
    yield crawler
    try:
        crawler.index_client.delete_index(TEST_INDEX_NAME)
    except Exception:
        pass


@pytest.fixture
def test_user_id():
    """Generate unique test user ID."""
    return f"test_user_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_session_id():
    """Generate unique test session ID."""
    return f"test_session_{uuid.uuid4().hex[:8]}"


class TestIndexLifecycle:
    """Test index creation and management."""

    def test_index_exists_after_creation(self, integration_crawler):
        """Index exists after creation."""
        assert integration_crawler.index_exists() is True

    def test_get_index_statistics(self, integration_crawler):
        """Can retrieve index statistics."""
        stats = integration_crawler.get_index_statistics()

        assert "index_name" in stats
        assert stats["index_name"] == TEST_INDEX_NAME
        assert "document_count" in stats

    def test_ensure_index_exists_idempotent(self, integration_crawler):
        """ensure_index_exists can be called multiple times."""
        integration_crawler.ensure_index_exists()
        integration_crawler.ensure_index_exists()
        assert integration_crawler.index_exists() is True


class TestEmbeddingGeneration:
    """Test embedding generation."""

    def test_generate_embedding_returns_1536_dims(self, integration_crawler):
        """Embedding has correct dimensions."""
        embedding = integration_crawler.generate_embedding("Test text for embedding")

        assert isinstance(embedding, list)
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

    def test_generate_embedding_truncates_long_text(self, integration_crawler):
        """Long text is truncated before embedding."""
        long_text = "x" * 50000
        embedding = integration_crawler.generate_embedding(long_text)

        assert len(embedding) == 1536


class TestFactIndexingAndRetrieval:
    """Test fact indexing and vector search retrieval."""

    @pytest.mark.asyncio
    async def test_index_fact_and_retrieve(self, integration_crawler, test_user_id):
        """Index a fact and retrieve it via search."""
        fact = Fact(
            user_id=test_user_id,
            key="HMLR",
            value="Hierarchical Memory with Linked Retrieval",
            category=FactCategory.ACRONYM,
            confidence=0.95,
            fact_id=1
        )

        result = await integration_crawler.index_fact(fact)
        assert result is True

        await asyncio.sleep(2)

        candidates = await integration_crawler.crawl(
            user_id=test_user_id,
            query="What does HMLR stand for?",
            top_k=5,
            min_score=0.3
        )

        assert len(candidates) >= 1
        assert any("HMLR" in c.content for c in candidates)

    @pytest.mark.asyncio
    async def test_semantic_search_ranking(self, integration_crawler, test_user_id):
        """Semantically similar queries rank higher."""
        facts = [
            Fact(user_id=test_user_id, key="Python", value="A programming language",
                 category=FactCategory.DEFINITION, confidence=0.9, fact_id=10),
            Fact(user_id=test_user_id, key="Azure", value="Microsoft cloud platform",
                 category=FactCategory.DEFINITION, confidence=0.9, fact_id=11),
            Fact(user_id=test_user_id, key="Cosmos DB", value="NoSQL database service",
                 category=FactCategory.DEFINITION, confidence=0.9, fact_id=12),
        ]

        for fact in facts:
            await integration_crawler.index_fact(fact)

        await asyncio.sleep(2)

        candidates = await integration_crawler.crawl(
            user_id=test_user_id,
            query="What programming languages are used in the project?",
            top_k=5,
            min_score=0.2
        )

        if len(candidates) >= 2:
            python_rank = next((i for i, c in enumerate(candidates) if "Python" in c.content), 999)
            azure_rank = next((i for i, c in enumerate(candidates) if "Azure" in c.content), 999)
            assert python_rank < azure_rank or python_rank == 999

    @pytest.mark.asyncio
    async def test_fact_deletion(self, integration_crawler, test_user_id):
        """Deleted facts are not searchable."""
        fact = Fact(
            user_id=test_user_id,
            key="ToDelete",
            value="This fact will be deleted",
            category=FactCategory.DEFINITION,
            confidence=0.9,
            fact_id=99
        )

        await integration_crawler.index_fact(fact)
        await asyncio.sleep(2)

        await integration_crawler.delete_fact(test_user_id, "99")
        await asyncio.sleep(2)

        candidates = await integration_crawler.crawl(
            user_id=test_user_id,
            query="ToDelete fact",
            top_k=10,
            min_score=0.1
        )

        assert not any("ToDelete" in c.content for c in candidates)


class TestSecretFactHandling:
    """Test that SECRET facts are handled securely."""

    @pytest.mark.asyncio
    async def test_secret_fact_value_not_searchable(self, integration_crawler, test_user_id):
        """SECRET fact value is not searchable, but key is indexed."""
        secret_fact = Fact(
            user_id=test_user_id,
            key="api_key_openai",
            value="sk-supersecretkey123456789",
            category=FactCategory.SECRET,
            confidence=1.0,
            fact_id=100
        )

        await integration_crawler.index_fact(secret_fact)
        await asyncio.sleep(2)

        value_search = await integration_crawler.crawl(
            user_id=test_user_id,
            query="sk-supersecretkey123456789",
            top_k=10,
            min_score=0.1
        )

        value_matches = [c for c in value_search if "sk-supersecret" in c.content]
        assert len(value_matches) == 0

        key_search = await integration_crawler.crawl(
            user_id=test_user_id,
            query="api_key_openai",
            top_k=10,
            min_score=0.1
        )

        key_matches = [c for c in key_search if "api_key_openai" in c.content]
        assert len(key_matches) >= 1

        for match in key_matches:
            assert "sk-supersecret" not in match.content
            assert "SECURE_VALUE_NOT_INDEXED" in match.content


class TestUserIsolation:
    """Test user isolation in search results."""

    @pytest.mark.asyncio
    async def test_cross_user_search_isolation(self, integration_crawler):
        """User A cannot search User B's memories."""
        user_a = f"user_a_{uuid.uuid4().hex[:8]}"
        user_b = f"user_b_{uuid.uuid4().hex[:8]}"

        fact_a = Fact(
            user_id=user_a,
            key="UserA_Secret",
            value="User A's private information",
            category=FactCategory.DEFINITION,
            confidence=0.9,
            fact_id=200
        )
        fact_b = Fact(
            user_id=user_b,
            key="UserB_Secret",
            value="User B's private information",
            category=FactCategory.DEFINITION,
            confidence=0.9,
            fact_id=201
        )

        await integration_crawler.index_fact(fact_a)
        await integration_crawler.index_fact(fact_b)
        await asyncio.sleep(2)

        results_for_a = await integration_crawler.crawl(
            user_id=user_a,
            query="private information",
            top_k=10,
            min_score=0.1
        )

        for result in results_for_a:
            assert result.user_id == user_a
            assert "UserB" not in result.content

    @pytest.mark.asyncio
    async def test_delete_user_memories_isolation(self, integration_crawler):
        """delete_user_memories only affects target user."""
        target_user = f"target_{uuid.uuid4().hex[:8]}"
        other_user = f"other_{uuid.uuid4().hex[:8]}"

        for i in range(3):
            await integration_crawler.index_fact(Fact(
                user_id=target_user, key=f"target_fact_{i}",
                value=f"Target fact {i}", category=FactCategory.DEFINITION,
                confidence=0.9, fact_id=300 + i
            ))
            await integration_crawler.index_fact(Fact(
                user_id=other_user, key=f"other_fact_{i}",
                value=f"Other fact {i}", category=FactCategory.DEFINITION,
                confidence=0.9, fact_id=400 + i
            ))

        await asyncio.sleep(2)

        deleted_count = await integration_crawler.delete_user_memories(target_user)
        assert deleted_count >= 3

        await asyncio.sleep(2)

        other_results = await integration_crawler.crawl(
            user_id=other_user,
            query="fact",
            top_k=10,
            min_score=0.1
        )

        assert len(other_results) >= 1


class TestBlockSummaryIndexing:
    """Test bridge block summary indexing."""

    @pytest.mark.asyncio
    async def test_index_block_summary_and_retrieve(self, integration_crawler, test_user_id, test_session_id):
        """Block summaries are indexed and searchable."""
        block = BridgeBlock(
            id=f"bb_{uuid.uuid4().hex[:8]}",
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Agent Architecture Design",
            summary="Discussed multi-agent system design with specialized agents",
            keywords=["agents", "architecture", "design"],
            open_loops=["Finalize agent communication protocol"],
            decisions_made=["Use event-driven architecture"],
            status="ACTIVE"
        )

        result = await integration_crawler.index_block_summary(block)
        assert result is True

        await asyncio.sleep(2)

        candidates = await integration_crawler.crawl(
            user_id=test_user_id,
            query="multi-agent architecture design",
            top_k=5,
            min_score=0.2,
            memory_type=MemoryType.BLOCK_SUMMARY
        )

        assert len(candidates) >= 1
        block_results = [c for c in candidates if c.memory_type == MemoryType.BLOCK_SUMMARY]
        assert len(block_results) >= 1

    @pytest.mark.asyncio
    async def test_block_update_reindexes(self, integration_crawler, test_user_id, test_session_id):
        """Updating a block re-indexes with new content."""
        block_id = f"bb_update_{uuid.uuid4().hex[:8]}"

        block_v1 = BridgeBlock(
            id=block_id,
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Initial Topic",
            summary="First version of summary",
            keywords=["initial"],
            status="ACTIVE"
        )
        await integration_crawler.index_block_summary(block_v1)
        await asyncio.sleep(2)

        block_v2 = BridgeBlock(
            id=block_id,
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Updated Topic About Machine Learning",
            summary="Discussing neural networks and deep learning approaches",
            keywords=["ML", "neural networks", "deep learning"],
            status="ACTIVE"
        )
        await integration_crawler.update_block_embedding(block_v2)
        await asyncio.sleep(2)

        candidates = await integration_crawler.crawl(
            user_id=test_user_id,
            query="neural networks deep learning",
            top_k=5,
            min_score=0.2
        )

        assert any("neural networks" in c.content.lower() or "deep learning" in c.content.lower()
                   for c in candidates)


class TestMemoryTypeFiltering:
    """Test filtering by memory type."""

    @pytest.mark.asyncio
    async def test_filter_by_fact_type(self, integration_crawler, test_user_id, test_session_id):
        """Can filter search to only facts."""
        fact = Fact(
            user_id=test_user_id, key="TypeTest_Fact",
            value="This is a fact", category=FactCategory.DEFINITION,
            confidence=0.9, fact_id=500
        )
        block = BridgeBlock(
            id=f"bb_type_{uuid.uuid4().hex[:8]}",
            session_id=test_session_id, user_id=test_user_id,
            topic_label="TypeTest Block", summary="This is a block summary",
            status="ACTIVE"
        )

        await integration_crawler.index_fact(fact)
        await integration_crawler.index_block_summary(block)
        await asyncio.sleep(2)

        fact_only = await integration_crawler.crawl(
            user_id=test_user_id,
            query="TypeTest",
            top_k=10,
            min_score=0.1,
            memory_type=MemoryType.FACT
        )

        for result in fact_only:
            assert result.memory_type == MemoryType.FACT

    @pytest.mark.asyncio
    async def test_filter_by_block_summary_type(self, integration_crawler, test_user_id, test_session_id):
        """Can filter search to only block summaries."""
        fact = Fact(
            user_id=test_user_id, key="TypeTest2_Fact",
            value="Another fact", category=FactCategory.DEFINITION,
            confidence=0.9, fact_id=501
        )
        block = BridgeBlock(
            id=f"bb_type2_{uuid.uuid4().hex[:8]}",
            session_id=test_session_id, user_id=test_user_id,
            topic_label="TypeTest2 Block", summary="Another block summary",
            status="ACTIVE"
        )

        await integration_crawler.index_fact(fact)
        await integration_crawler.index_block_summary(block)
        await asyncio.sleep(2)

        block_only = await integration_crawler.crawl(
            user_id=test_user_id,
            query="TypeTest2",
            top_k=10,
            min_score=0.1,
            memory_type=MemoryType.BLOCK_SUMMARY
        )

        for result in block_only:
            assert result.memory_type == MemoryType.BLOCK_SUMMARY
