"""
Cross-Session Memory Tests (P1)

Tests for cross-session memory retrieval and recency decay:
- Open loop retrieval across sessions
- Priority sorting
- Recency decay calculations
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, timezone

from src.hmlr.memory_accessor import HMLRMemoryAccessor
from tests.conftest import create_test_block


class TestOpenLoopRetrieval:
    """Tests for cross-session open loop retrieval."""

    @pytest.fixture
    def mock_hmlr_service(self):
        """Create mock HMLR service."""
        hmlr = MagicMock()
        hmlr.get_user_profile = AsyncMock(return_value=MagicMock(
            common_queries=[],
            known_entities=[],
            interaction_patterns={},
            preferences={}
        ))
        hmlr.get_user_facts = AsyncMock(return_value=[])
        hmlr.get_session_blocks = AsyncMock(return_value=[])
        hmlr.block_manager = MagicMock()
        hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return hmlr

    @pytest.mark.asyncio
    async def test_cross_session_open_loops_retrieved(self, mock_hmlr_service):
        """Open loops from other sessions should be retrieved."""
        now = datetime.now(timezone.utc)

        cross_session_block = MagicMock()
        cross_session_block.id = "block-other-session"
        cross_session_block.session_id = "other-session"
        cross_session_block.topic_label = "Cross Session Topic"
        cross_session_block.open_loops = ["Cross-session pending item"]
        cross_session_block.last_activity = now - timedelta(hours=12)

        mock_hmlr_service.block_manager.get_user_blocks_with_open_loops = AsyncMock(
            return_value=[cross_session_block]
        )

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="current-session",
                include_cross_session=True
            )

            assert len(data.open_loops) >= 1
            cross_loops = [l for l in data.open_loops if not l.get("is_current_session", True)]
            assert len(cross_loops) >= 1

    @pytest.mark.asyncio
    async def test_open_loops_sorted_by_priority(self, mock_hmlr_service):
        """Open loops should be sorted by priority (highest first)."""
        now = datetime.now(timezone.utc)

        recent_block = MagicMock()
        recent_block.id = "block-recent"
        recent_block.session_id = "session-recent"
        recent_block.topic_label = "Recent Topic"
        recent_block.open_loops = ["Recent pending"]
        recent_block.last_activity = now - timedelta(hours=1)

        old_block = MagicMock()
        old_block.id = "block-old"
        old_block.session_id = "session-old"
        old_block.topic_label = "Old Topic"
        old_block.open_loops = ["Old pending"]
        old_block.last_activity = now - timedelta(hours=48)

        mock_hmlr_service.block_manager.get_user_blocks_with_open_loops = AsyncMock(
            return_value=[old_block, recent_block]
        )

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="current-session",
                include_cross_session=True
            )

            if len(data.open_loops) >= 2:
                assert data.open_loops[0]["priority"] >= data.open_loops[1]["priority"]

    @pytest.mark.asyncio
    async def test_open_loops_max_limit_5(self, mock_hmlr_service):
        """Maximum 5 open loops should be returned."""
        now = datetime.now(timezone.utc)

        blocks = []
        for i in range(10):
            block = MagicMock()
            block.id = f"block-{i}"
            block.session_id = f"session-{i}"
            block.topic_label = f"Topic {i}"
            block.open_loops = [f"Pending item {i}"]
            block.last_activity = now - timedelta(hours=i)
            blocks.append(block)

        mock_hmlr_service.block_manager.get_user_blocks_with_open_loops = AsyncMock(
            return_value=blocks
        )

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="current-session",
                include_cross_session=True
            )

            assert len(data.open_loops) <= 5

    @pytest.mark.asyncio
    async def test_open_loops_exclude_720h_old(self, mock_hmlr_service):
        """Open loops older than 720 hours (30 days) should be excluded."""
        now = datetime.now(timezone.utc)

        old_block = MagicMock()
        old_block.id = "block-very-old"
        old_block.session_id = "session-old"
        old_block.topic_label = "Very Old Topic"
        old_block.open_loops = ["Ancient pending item"]
        old_block.last_activity = now - timedelta(hours=800)

        mock_hmlr_service.block_manager.get_user_blocks_with_open_loops = AsyncMock(
            return_value=[old_block]
        )

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="current-session",
                include_cross_session=True
            )

            assert len(data.open_loops) == 0


class TestRecencyDecay:
    """Tests for recency decay priority calculations."""

    def test_recency_priority_1_hour_ago(self):
        """1 hour ago cross-session: base 80, decay ~0.5, priority ~80."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor.__new__(HMLRMemoryAccessor)
        priority = accessor._calculate_recency_priority(1.0, is_current_session=False)

        assert priority == 80

    def test_recency_priority_24_hours_ago(self):
        """24 hours ago: base 80, decay 12, priority 68."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor.__new__(HMLRMemoryAccessor)
        priority = accessor._calculate_recency_priority(24.0, is_current_session=False)

        assert priority == 68

    def test_recency_priority_48_hours_ago(self):
        """48 hours ago: base 80, decay = 12 + (24*0.3) = 19.2, priority ~61."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor.__new__(HMLRMemoryAccessor)
        priority = accessor._calculate_recency_priority(48.0, is_current_session=False)

        assert priority == 61

    def test_recency_priority_very_old_capped_at_40(self):
        """Very old items should have minimum priority of 40."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor.__new__(HMLRMemoryAccessor)
        priority = accessor._calculate_recency_priority(500.0, is_current_session=False)

        assert priority == 40

    def test_current_session_base_100_not_80(self):
        """Current session items should have base priority of 100."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor.__new__(HMLRMemoryAccessor)
        priority = accessor._calculate_recency_priority(1.0, is_current_session=True)

        assert priority == 100

    def test_current_session_decays_slower_than_cross(self):
        """Current session with same age should have higher priority."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor.__new__(HMLRMemoryAccessor)

        current_priority = accessor._calculate_recency_priority(12.0, is_current_session=True)
        cross_priority = accessor._calculate_recency_priority(12.0, is_current_session=False)

        assert current_priority > cross_priority


class TestExpertiseDetection:
    """Tests for expertise level detection from interaction patterns."""

    @pytest.fixture
    def mock_hmlr_service(self):
        """Create mock HMLR service."""
        hmlr = MagicMock()
        hmlr.get_user_facts = AsyncMock(return_value=[])
        hmlr.get_session_blocks = AsyncMock(return_value=[])
        hmlr.block_manager = MagicMock()
        hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return hmlr

    @pytest.mark.asyncio
    async def test_expert_level_detected(self, mock_hmlr_service):
        """User with 100+ queries and 60%+ technical should be expert."""
        mock_profile = MagicMock()
        mock_profile.common_queries = []
        mock_profile.known_entities = []
        mock_profile.preferences = {}
        mock_profile.interaction_patterns = {
            "total_queries": 150,
            "technical_queries": 120
        }

        mock_hmlr_service.get_user_profile = AsyncMock(return_value=mock_profile)

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="expert-user",
                session_id="session-1"
            )

            assert data.expertise_level == "expert"

    @pytest.mark.asyncio
    async def test_beginner_level_for_few_queries(self, mock_hmlr_service):
        """User with few queries should be beginner."""
        mock_profile = MagicMock()
        mock_profile.common_queries = []
        mock_profile.known_entities = []
        mock_profile.preferences = {}
        mock_profile.interaction_patterns = {
            "total_queries": 5,
            "technical_queries": 2
        }

        mock_hmlr_service.get_user_profile = AsyncMock(return_value=mock_profile)

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="new-user",
                session_id="session-1"
            )

            assert data.expertise_level == "beginner"
