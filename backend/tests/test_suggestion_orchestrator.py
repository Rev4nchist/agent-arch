"""
Unit tests for HMLR Suggestion Orchestrator.
Tests ranking, diversity, fallback, and blending logic.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.hmlr.suggestion_models import (
    SuggestionSource,
    PersonalizedSuggestion,
    SuggestionData,
    SuggestionResponse
)
from src.hmlr.suggestion_orchestrator import SuggestionOrchestrator


class TestSuggestionOrchestratorInit:
    def test_init_without_hmlr_service(self):
        orchestrator = SuggestionOrchestrator(hmlr_service=None)
        assert orchestrator.memory_accessor is None
        assert orchestrator.memory_provider is not None
        assert orchestrator.static_provider is not None
        assert orchestrator.intent_provider is not None

    def test_init_with_mock_hmlr_service(self):
        mock_service = MagicMock()
        orchestrator = SuggestionOrchestrator(hmlr_service=mock_service)
        assert orchestrator.memory_accessor is not None


class TestDiversityLimits:
    def test_diversity_limits_defined(self):
        limits = SuggestionOrchestrator.DIVERSITY_LIMITS
        assert limits[SuggestionSource.OPEN_LOOP] == 2
        assert limits[SuggestionSource.COMMON_QUERY] == 2
        assert limits[SuggestionSource.STATIC] == 3
        assert limits[SuggestionSource.INTENT] == 2
        assert limits[SuggestionSource.ENTITY] == 1


class TestRankAndDiversify:
    @pytest.fixture
    def orchestrator(self):
        return SuggestionOrchestrator(hmlr_service=None)

    def test_empty_suggestions(self, orchestrator):
        result = orchestrator._rank_and_diversify([])
        assert result == []

    def test_respects_max_count(self, orchestrator):
        suggestions = [
            PersonalizedSuggestion(
                text=f"Suggestion {i}",
                source=SuggestionSource.STATIC,
                priority=50,
                confidence=0.8
            )
            for i in range(10)
        ]
        result = orchestrator._rank_and_diversify(suggestions, max_count=6)
        assert len(result) <= 6

    def test_sorts_by_priority_then_confidence(self, orchestrator):
        suggestions = [
            PersonalizedSuggestion(text="Low", source=SuggestionSource.STATIC, priority=40, confidence=0.5),
            PersonalizedSuggestion(text="High", source=SuggestionSource.OPEN_LOOP, priority=100, confidence=0.9),
            PersonalizedSuggestion(text="Medium", source=SuggestionSource.INTENT, priority=70, confidence=0.8),
        ]
        result = orchestrator._rank_and_diversify(suggestions)
        assert result[0].text == "High"
        assert result[1].text == "Medium"
        assert result[2].text == "Low"

    def test_respects_diversity_limits_per_source(self, orchestrator):
        suggestions = [
            PersonalizedSuggestion(
                text=f"Open loop {i}",
                source=SuggestionSource.OPEN_LOOP,
                priority=100 - i,
                confidence=0.9
            )
            for i in range(5)
        ]
        result = orchestrator._rank_and_diversify(suggestions)
        open_loops = [s for s in result if s.source == SuggestionSource.OPEN_LOOP]
        assert len(open_loops) <= 2

    def test_deduplicates_by_text(self, orchestrator):
        suggestions = [
            PersonalizedSuggestion(text="Same text", source=SuggestionSource.STATIC, priority=50, confidence=1.0),
            PersonalizedSuggestion(text="same text", source=SuggestionSource.INTENT, priority=60, confidence=0.8),
            PersonalizedSuggestion(text="SAME TEXT", source=SuggestionSource.OPEN_LOOP, priority=100, confidence=0.9),
        ]
        result = orchestrator._rank_and_diversify(suggestions)
        assert len(result) == 1
        assert result[0].priority == 100

    def test_fills_remaining_slots_after_diversity(self, orchestrator):
        suggestions = [
            PersonalizedSuggestion(text=f"Open {i}", source=SuggestionSource.OPEN_LOOP, priority=100, confidence=0.9)
            for i in range(5)
        ] + [
            PersonalizedSuggestion(text=f"Static {i}", source=SuggestionSource.STATIC, priority=40, confidence=1.0)
            for i in range(3)
        ]
        result = orchestrator._rank_and_diversify(suggestions, max_count=6)
        assert len(result) == 5
        open_loops = [s for s in result if s.source == SuggestionSource.OPEN_LOOP]
        statics = [s for s in result if s.source == SuggestionSource.STATIC]
        assert len(open_loops) == 2
        assert len(statics) == 3


class TestStaticFallback:
    @pytest.fixture
    def orchestrator(self):
        return SuggestionOrchestrator(hmlr_service=None)

    def test_fallback_returns_static_suggestions(self, orchestrator):
        response = orchestrator._static_fallback(page_type="dashboard", reason="no_user")
        assert response.is_personalized is False
        assert response.fallback_reason == "no_user"
        assert len(response.suggestions) <= 6

    def test_fallback_for_unknown_page(self, orchestrator):
        response = orchestrator._static_fallback(page_type="unknown_page", reason="test")
        assert len(response.suggestions) >= 1


class TestGetInitialSuggestions:
    @pytest.fixture
    def orchestrator(self):
        return SuggestionOrchestrator(hmlr_service=None)

    @pytest.mark.asyncio
    async def test_no_user_returns_static_fallback(self, orchestrator):
        response = await orchestrator.get_initial_suggestions(
            user_id=None,
            page_type="dashboard"
        )
        assert response.is_personalized is False
        assert response.fallback_reason == "no_user"

    @pytest.mark.asyncio
    async def test_hmlr_disabled_returns_static_fallback(self, orchestrator):
        with patch.object(orchestrator, '_is_hmlr_enabled', return_value=False):
            response = await orchestrator.get_initial_suggestions(
                user_id="user123",
                page_type="tasks"
            )
            assert response.is_personalized is False

    @pytest.mark.asyncio
    async def test_with_mock_memory_data(self):
        mock_service = MagicMock()
        orchestrator = SuggestionOrchestrator(hmlr_service=mock_service)

        mock_data = SuggestionData(
            open_loops=[{"text": "Continue API work", "topic": "api", "priority": 100}],
            common_queries=["How do I deploy?"],
            topic_interests=["governance"]
        )

        with patch.object(orchestrator, '_is_hmlr_enabled', return_value=True):
            with patch.object(orchestrator.memory_accessor, 'get_suggestion_data', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = mock_data
                response = await orchestrator.get_initial_suggestions(
                    user_id="user123",
                    page_type="dashboard"
                )
                assert response.is_personalized is True
                assert len(response.suggestions) >= 1


class TestGetFollowupSuggestions:
    @pytest.fixture
    def orchestrator(self):
        return SuggestionOrchestrator(hmlr_service=None)

    @pytest.mark.asyncio
    async def test_no_user_returns_intent_only(self, orchestrator):
        suggestions = await orchestrator.get_followup_suggestions(
            user_id=None,
            intent="task_query"
        )
        assert all(s.source == SuggestionSource.INTENT for s in suggestions)

    @pytest.mark.asyncio
    async def test_with_response_text(self, orchestrator):
        suggestions = await orchestrator.get_followup_suggestions(
            user_id=None,
            intent="meeting_query",
            response_text="Here are your upcoming meetings..."
        )
        assert len(suggestions) <= 6


class TestIsEmptyMemory:
    @pytest.fixture
    def orchestrator(self):
        return SuggestionOrchestrator(hmlr_service=None)

    def test_empty_data_detected(self, orchestrator):
        data = SuggestionData()
        assert orchestrator._is_empty_memory(data) is True

    def test_data_with_open_loops_not_empty(self, orchestrator):
        data = SuggestionData(
            open_loops=[{"text": "test", "topic": "test", "priority": 100}]
        )
        assert orchestrator._is_empty_memory(data) is False

    def test_data_with_common_queries_not_empty(self, orchestrator):
        data = SuggestionData(
            common_queries=["How do I deploy?"]
        )
        assert orchestrator._is_empty_memory(data) is False


class TestOrchestratorEdgeCases:
    @pytest.fixture
    def orchestrator(self):
        return SuggestionOrchestrator(hmlr_service=None)

    @pytest.mark.asyncio
    async def test_handles_memory_accessor_error(self):
        mock_service = MagicMock()
        orchestrator = SuggestionOrchestrator(hmlr_service=mock_service)

        with patch.object(orchestrator, '_is_hmlr_enabled', return_value=True):
            with patch.object(orchestrator.memory_accessor, 'get_suggestion_data', new_callable=AsyncMock) as mock_get:
                mock_get.side_effect = Exception("Database error")
                response = await orchestrator.get_initial_suggestions(
                    user_id="user123",
                    page_type="dashboard"
                )
                assert response.is_personalized is False
                assert "error" in response.fallback_reason

    def test_max_suggestions_constant(self, orchestrator):
        assert orchestrator.MAX_SUGGESTIONS == 6

    @pytest.mark.asyncio
    async def test_session_id_passed_to_memory_accessor(self):
        mock_service = MagicMock()
        orchestrator = SuggestionOrchestrator(hmlr_service=mock_service)

        with patch.object(orchestrator, '_is_hmlr_enabled', return_value=True):
            with patch.object(orchestrator.memory_accessor, 'get_suggestion_data', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = SuggestionData()

                await orchestrator.get_initial_suggestions(
                    user_id="user123",
                    page_type="dashboard",
                    session_id="session456"
                )

                mock_get.assert_called_once()
                call_kwargs = mock_get.call_args.kwargs
                assert call_kwargs.get("session_id") == "session456"
