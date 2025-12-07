"""
Governor Routing Boundary Tests (P1)

Tests for Governor 4-scenario routing logic with boundary conditions:
- Similarity threshold at exactly 0.7
- All 4 routing scenarios
- Empty session states
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from src.hmlr.governor import Governor
from src.hmlr.models import BridgeBlock, RoutingScenario, Turn
from tests.conftest import create_test_block, create_test_turn


class TestSimilarityThreshold:
    """Tests for similarity threshold boundary (0.7)."""

    @pytest.fixture
    def governor(self):
        """Create Governor with mocked dependencies."""
        block_manager = MagicMock()
        sql_client = MagicMock()
        sql_client.search_facts = AsyncMock(return_value=[])
        gov = Governor(block_manager, sql_client)
        gov.similarity_threshold = 0.7
        return gov

    @pytest.mark.asyncio
    async def test_similarity_at_exactly_threshold_continues(self, governor):
        """Similarity at exactly 0.7 should result in CONTINUATION."""
        active_block = MagicMock(spec=BridgeBlock)
        active_block.id = "block-1"
        active_block.status = "ACTIVE"
        active_block.topic_label = "Test Topic"
        active_block.keywords = ["test", "keyword", "query"]
        active_block.turns = []

        with patch.object(governor, '_compute_topic_similarity', new_callable=AsyncMock) as mock_sim:
            mock_sim.return_value = 0.7

            decision = await governor._determine_scenario(
                query="test query",
                user_id="user-1",
                session_id="session-1",
                active_block=active_block,
                paused_blocks=[],
                facts=[],
                memories=[],
                topic_similarity=0.7,
                intent=None
            )

            assert decision.scenario == RoutingScenario.TOPIC_CONTINUATION
            assert decision.is_new_topic is False

    @pytest.mark.asyncio
    async def test_similarity_just_below_threshold_shifts(self, governor):
        """Similarity at 0.69 should result in TOPIC_SHIFT."""
        active_block = MagicMock(spec=BridgeBlock)
        active_block.id = "block-1"
        active_block.status = "ACTIVE"
        active_block.topic_label = "Test Topic"
        active_block.keywords = ["different", "topic"]
        active_block.turns = []

        with patch.object(governor, '_find_matching_paused', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None

            decision = await governor._determine_scenario(
                query="unrelated query",
                user_id="user-1",
                session_id="session-1",
                active_block=active_block,
                paused_blocks=[],
                facts=[],
                memories=[],
                topic_similarity=0.69,
                intent=None
            )

            assert decision.scenario == RoutingScenario.TOPIC_SHIFT
            assert decision.is_new_topic is True

    @pytest.mark.asyncio
    async def test_similarity_above_threshold_continues(self, governor):
        """Similarity above 0.7 should result in CONTINUATION."""
        active_block = MagicMock(spec=BridgeBlock)
        active_block.id = "block-1"
        active_block.status = "ACTIVE"
        active_block.topic_label = "Test Topic"

        decision = await governor._determine_scenario(
            query="very similar query",
            user_id="user-1",
            session_id="session-1",
            active_block=active_block,
            paused_blocks=[],
            facts=[],
            memories=[],
            topic_similarity=0.85,
            intent=None
        )

        assert decision.scenario == RoutingScenario.TOPIC_CONTINUATION


class TestRoutingScenarios:
    """Tests for all 4 routing scenarios."""

    @pytest.fixture
    def governor(self):
        """Create Governor with mocked dependencies."""
        block_manager = MagicMock()
        sql_client = MagicMock()
        sql_client.search_facts = AsyncMock(return_value=[])
        gov = Governor(block_manager, sql_client)
        gov.similarity_threshold = 0.7
        return gov

    @pytest.mark.asyncio
    async def test_scenario_1_continuation_active_block_similar(self, governor):
        """SCENARIO 1: Active block with high similarity continues."""
        active_block = MagicMock(spec=BridgeBlock)
        active_block.id = "active-1"
        active_block.status = "ACTIVE"
        active_block.topic_label = "Agent Development"

        decision = await governor._determine_scenario(
            query="How is agent development progressing?",
            user_id="user-1",
            session_id="session-1",
            active_block=active_block,
            paused_blocks=[],
            facts=[],
            memories=[],
            topic_similarity=0.8,
            intent="status_query"
        )

        assert decision.scenario == RoutingScenario.TOPIC_CONTINUATION
        assert decision.matched_block_id == "active-1"
        assert decision.is_new_topic is False
        assert decision.active_block == active_block

    @pytest.mark.asyncio
    async def test_scenario_2_resumption_paused_block_matches(self, governor):
        """SCENARIO 2: Paused block matches better than active."""
        paused_block = MagicMock(spec=BridgeBlock)
        paused_block.id = "paused-1"
        paused_block.status = "PAUSED"
        paused_block.topic_label = "Budget Discussion"
        paused_block.keywords = ["budget", "cost"]
        paused_block.turns = []

        with patch.object(governor, '_find_matching_paused', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = paused_block

            decision = await governor._determine_scenario(
                query="What about the budget?",
                user_id="user-1",
                session_id="session-1",
                active_block=None,
                paused_blocks=[paused_block],
                facts=[],
                memories=[],
                topic_similarity=0.0,
                intent="budget_query"
            )

            assert decision.scenario == RoutingScenario.TOPIC_RESUMPTION
            assert decision.matched_block_id == "paused-1"
            assert decision.is_new_topic is False

    @pytest.mark.asyncio
    async def test_scenario_3_new_topic_empty_session(self, governor):
        """SCENARIO 3: New topic when no blocks exist."""
        with patch.object(governor, '_find_matching_paused', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None

            decision = await governor._determine_scenario(
                query="Let's discuss deployment options",
                user_id="user-1",
                session_id="session-1",
                active_block=None,
                paused_blocks=[],
                facts=[],
                memories=[],
                topic_similarity=0.0,
                intent="planning"
            )

            assert decision.scenario == RoutingScenario.NEW_TOPIC_FIRST
            assert decision.matched_block_id is None
            assert decision.is_new_topic is True
            assert decision.active_block is None

    @pytest.mark.asyncio
    async def test_scenario_4_shift_low_similarity_creates_new(self, governor):
        """SCENARIO 4: Low similarity with active block creates new topic."""
        active_block = MagicMock(spec=BridgeBlock)
        active_block.id = "active-1"
        active_block.status = "ACTIVE"
        active_block.topic_label = "Agent Development"

        with patch.object(governor, '_find_matching_paused', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None

            decision = await governor._determine_scenario(
                query="What are the license costs?",
                user_id="user-1",
                session_id="session-1",
                active_block=active_block,
                paused_blocks=[],
                facts=[],
                memories=[],
                topic_similarity=0.2,
                intent="budget_query"
            )

            assert decision.scenario == RoutingScenario.TOPIC_SHIFT
            assert decision.is_new_topic is True
            assert decision.active_block == active_block


class TestEmptySessionStates:
    """Tests for empty and edge-case session states."""

    @pytest.fixture
    def governor(self):
        """Create Governor with mocked dependencies."""
        block_manager = MagicMock()
        block_manager.get_session_blocks = AsyncMock(return_value=[])
        sql_client = MagicMock()
        sql_client.search_facts = AsyncMock(return_value=[])
        return Governor(block_manager, sql_client)

    @pytest.mark.asyncio
    async def test_empty_session_no_blocks(self, governor):
        """Empty session should create new topic."""
        decision = await governor.route(
            user_id="user-1",
            session_id="empty-session",
            query="Hello, what can you help me with?"
        )

        assert decision.scenario == RoutingScenario.NEW_TOPIC_FIRST
        assert decision.is_new_topic is True

    @pytest.mark.asyncio
    async def test_session_all_blocks_paused_no_match(self, governor):
        """Session with only paused blocks that don't match."""
        paused_block = MagicMock(spec=BridgeBlock)
        paused_block.status = "PAUSED"
        paused_block.topic_label = "Old Topic"
        paused_block.keywords = ["old", "stuff"]
        paused_block.turns = []

        governor.block_manager.get_session_blocks = AsyncMock(return_value=[paused_block])

        decision = await governor.route(
            user_id="user-1",
            session_id="session-1",
            query="Completely different topic"
        )

        assert decision.scenario == RoutingScenario.NEW_TOPIC_FIRST
        assert decision.is_new_topic is True


class TestTopicSimilarityComputation:
    """Tests for topic similarity computation."""

    @pytest.fixture
    def governor(self):
        """Create Governor with mocked dependencies."""
        block_manager = MagicMock()
        sql_client = MagicMock()
        return Governor(block_manager, sql_client)

    @pytest.mark.asyncio
    async def test_empty_keywords_returns_low_similarity(self, governor):
        """Block with no keywords should return low similarity."""
        block = MagicMock(spec=BridgeBlock)
        block.keywords = []
        block.topic_label = ""
        block.turns = []

        similarity = await governor._compute_topic_similarity("test query", block)

        assert similarity == 0.3

    @pytest.mark.asyncio
    async def test_topic_label_match_boosts_similarity(self, governor):
        """Topic label appearing in query should boost similarity."""
        block = MagicMock(spec=BridgeBlock)
        block.keywords = ["development"]
        block.topic_label = "Agent Development"
        block.turns = []

        similarity = await governor._compute_topic_similarity(
            "Tell me about agent development progress",
            block
        )

        assert similarity >= 0.5

    @pytest.mark.asyncio
    async def test_keyword_overlap_increases_similarity(self, governor):
        """More keyword overlap should increase similarity."""
        block = MagicMock(spec=BridgeBlock)
        block.keywords = ["deployment", "pipeline", "ci", "cd"]
        block.topic_label = "CI/CD Pipeline"
        block.turns = []

        similarity = await governor._compute_topic_similarity(
            "How is the deployment pipeline configured?",
            block
        )

        assert similarity > 0.3
