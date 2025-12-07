"""
Suggestion System Edge Case Tests (P2)

Tests for suggestion system edge cases:
- Source diversity limits
- Fallback behavior
- Page type suggestions
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from src.hmlr.suggestion_orchestrator import SuggestionOrchestrator
from src.hmlr.suggestion_providers import (
    MemorySuggestionProvider,
    StaticSuggestionProvider,
    IntentSuggestionProvider
)
from src.hmlr.suggestion_models import SuggestionData, SuggestionSource


class TestSourceDiversityLimits:
    """Tests for suggestion source diversity limits."""

    def test_max_2_open_loop_suggestions(self):
        """Memory provider should limit open loop suggestions to 3."""
        provider = MemorySuggestionProvider()

        data = SuggestionData(
            open_loops=[
                {"text": "Loop 1", "topic": "Topic 1", "priority": 90, "is_current_session": True},
                {"text": "Loop 2", "topic": "Topic 2", "priority": 85, "is_current_session": True},
                {"text": "Loop 3", "topic": "Topic 3", "priority": 80, "is_current_session": True},
                {"text": "Loop 4", "topic": "Topic 4", "priority": 75, "is_current_session": True},
                {"text": "Loop 5", "topic": "Topic 5", "priority": 70, "is_current_session": True},
            ]
        )

        suggestions = provider.get_suggestions(data=data, page_type="dashboard")

        open_loop_suggestions = [s for s in suggestions if s.source == SuggestionSource.OPEN_LOOP]
        assert len(open_loop_suggestions) <= 3

    def test_max_3_common_query_suggestions(self):
        """Memory provider should limit common query suggestions to 3."""
        provider = MemorySuggestionProvider()

        data = SuggestionData(
            common_queries=[
                "Query 1",
                "Query 2",
                "Query 3",
                "Query 4",
                "Query 5",
            ],
            expertise_level="intermediate"
        )

        suggestions = provider.get_suggestions(data=data, page_type="dashboard")

        common_query_suggestions = [s for s in suggestions if s.source == SuggestionSource.COMMON_QUERY]
        assert len(common_query_suggestions) <= 3

    def test_max_2_entity_suggestions(self):
        """Memory provider should limit entity suggestions to 2."""
        provider = MemorySuggestionProvider()

        data = SuggestionData(
            known_entities=[
                {"name": "Entity 1", "type": "project"},
                {"name": "Entity 2", "type": "project"},
                {"name": "Entity 3", "type": "project"},
                {"name": "Entity 4", "type": "project"},
            ]
        )

        suggestions = provider.get_suggestions(data=data, page_type="dashboard")

        entity_suggestions = [s for s in suggestions if s.source == SuggestionSource.ENTITY]
        assert len(entity_suggestions) <= 2

    def test_max_3_topic_interest_suggestions(self):
        """Memory provider should limit topic interest suggestions to 3."""
        provider = MemorySuggestionProvider()

        data = SuggestionData(
            topic_interests=["topic1", "topic2", "topic3", "topic4", "topic5"]
        )

        suggestions = provider.get_suggestions(data=data, page_type="dashboard")

        topic_suggestions = [s for s in suggestions if s.source == SuggestionSource.TOPIC_INTEREST]
        assert len(topic_suggestions) <= 3


class TestFallbackBehavior:
    """Tests for fallback when HMLR is unavailable."""

    @pytest.mark.asyncio
    async def test_fallback_when_hmlr_disabled(self):
        """Should return static suggestions when HMLR is disabled."""
        with patch('src.hmlr.suggestion_orchestrator.settings') as mock_settings:
            mock_settings.hmlr_enabled = False

            orchestrator = SuggestionOrchestrator(hmlr_service=None)

            response = await orchestrator.get_initial_suggestions(
                user_id="test-user",
                page_type="dashboard"
            )

            assert response.is_personalized is False
            assert response.fallback_reason is not None
            assert len(response.suggestions) > 0

    @pytest.mark.asyncio
    async def test_fallback_when_memory_empty(self):
        """Should fallback when memory returns empty data."""
        mock_hmlr = MagicMock()

        with patch('src.hmlr.suggestion_orchestrator.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            orchestrator = SuggestionOrchestrator(hmlr_service=mock_hmlr)

            with patch.object(orchestrator, 'memory_accessor') as mock_accessor:
                mock_accessor.get_suggestion_data = AsyncMock(
                    return_value=SuggestionData()
                )

                response = await orchestrator.get_initial_suggestions(
                    user_id="test-user",
                    page_type="dashboard"
                )

                assert len(response.suggestions) > 0

    @pytest.mark.asyncio
    async def test_fallback_reason_populated(self):
        """Fallback reason should be populated when falling back."""
        with patch('src.hmlr.suggestion_orchestrator.settings') as mock_settings:
            mock_settings.hmlr_enabled = False

            orchestrator = SuggestionOrchestrator(hmlr_service=None)

            response = await orchestrator.get_initial_suggestions(
                user_id="test-user",
                page_type="dashboard"
            )

            assert response.fallback_reason is not None
            assert "no_user" in response.fallback_reason.lower() or "error" in response.fallback_reason.lower()


class TestPageTypeSuggestions:
    """Tests for page-type specific static suggestions."""

    def test_dashboard_suggestions(self):
        """Dashboard should have relevant static suggestions."""
        provider = StaticSuggestionProvider()

        suggestions = provider.get_suggestions(page_type="dashboard")

        assert len(suggestions) > 0
        texts = [s.text.lower() for s in suggestions]
        assert any("task" in t or "meeting" in t or "agent" in t or "help" in t for t in texts)

    def test_meetings_suggestions(self):
        """Meetings page should have meeting-related suggestions."""
        provider = StaticSuggestionProvider()

        suggestions = provider.get_suggestions(page_type="meetings")

        assert len(suggestions) > 0
        texts = [s.text.lower() for s in suggestions]
        assert any("meeting" in t or "topic" in t or "action" in t for t in texts)

    def test_tasks_suggestions(self):
        """Tasks page should have task-related suggestions."""
        provider = StaticSuggestionProvider()

        suggestions = provider.get_suggestions(page_type="tasks")

        assert len(suggestions) > 0
        texts = [s.text.lower() for s in suggestions]
        assert any("task" in t or "priority" in t or "blocked" in t for t in texts)

    def test_unknown_page_fallback(self):
        """Unknown page type should return default suggestions."""
        provider = StaticSuggestionProvider()

        suggestions = provider.get_suggestions(page_type="nonexistent-page")

        assert len(suggestions) > 0


class TestSuggestionRanking:
    """Tests for suggestion ranking and diversification."""

    @pytest.mark.asyncio
    async def test_suggestions_sorted_by_priority(self):
        """Suggestions should be sorted by priority (high to low)."""
        mock_hmlr = MagicMock()

        with patch('src.hmlr.suggestion_orchestrator.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            orchestrator = SuggestionOrchestrator(hmlr_service=mock_hmlr)

            with patch.object(orchestrator, 'memory_accessor') as mock_accessor:
                mock_accessor.get_suggestion_data = AsyncMock(return_value=SuggestionData(
                    open_loops=[
                        {"text": "Important pending", "topic": "Topic", "priority": 95, "is_current_session": True}
                    ],
                    common_queries=["What tasks are blocked?"],
                    topic_interests=["governance"],
                    known_entities=[{"name": "AI Guide", "type": "project"}],
                    expertise_level="expert"
                ))

                response = await orchestrator.get_initial_suggestions(
                    user_id="test-user",
                    page_type="dashboard"
                )

                priorities = [s.priority for s in response.suggestions]
                assert priorities == sorted(priorities, reverse=True)

    @pytest.mark.asyncio
    async def test_max_suggestions_limited(self):
        """Total suggestions should be limited to reasonable count."""
        mock_hmlr = MagicMock()

        with patch('src.hmlr.suggestion_orchestrator.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            orchestrator = SuggestionOrchestrator(hmlr_service=mock_hmlr)

            with patch.object(orchestrator, 'memory_accessor') as mock_accessor:
                mock_accessor.get_suggestion_data = AsyncMock(return_value=SuggestionData(
                    open_loops=[
                        {"text": "Pending 1", "topic": "Topic", "priority": 95, "is_current_session": True},
                        {"text": "Pending 2", "topic": "Topic", "priority": 90, "is_current_session": True}
                    ],
                    common_queries=["Query 1", "Query 2"],
                    topic_interests=["topic1", "topic2"],
                    known_entities=[{"name": "Entity", "type": "project"}],
                    expertise_level="expert"
                ))

                response = await orchestrator.get_initial_suggestions(
                    user_id="test-user",
                    page_type="dashboard"
                )

                assert len(response.suggestions) <= 8
