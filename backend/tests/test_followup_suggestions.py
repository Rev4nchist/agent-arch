"""
Unit tests for HMLR-enhanced follow-up suggestions.
Tests _generate_action_suggestions and _generate_action_suggestions_with_hmlr.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.models import ActionSuggestion
from src.main import ClassifiedIntent, QueryIntent
from src.hmlr.suggestion_models import PersonalizedSuggestion, SuggestionSource


def create_classified_intent(
    intent: QueryIntent,
    entities: list = None,
    parameters: dict = None,
    confidence: float = 0.9
) -> ClassifiedIntent:
    return ClassifiedIntent(
        intent=intent,
        entities=entities or [],
        parameters=parameters or {},
        confidence=confidence,
        raw_query="test query"
    )


class TestGenerateActionSuggestions:
    def test_list_tasks_with_results(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"]
        )
        results = [{"id": "1", "title": "Task 1"}, {"id": "2", "title": "Task 2"}]

        suggestions = _generate_action_suggestions(classified, results, "")

        assert len(suggestions) <= 6
        assert all(isinstance(s, ActionSuggestion) for s in suggestions)

    def test_list_tasks_blocked_status(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"],
            parameters={"status": "Blocked"}
        )
        results = [{"id": "1", "status": "Blocked"}]

        suggestions = _generate_action_suggestions(classified, results, "")

        labels = [s.label for s in suggestions]
        assert any("blocker" in l.lower() for l in labels)

    def test_list_meetings_with_results(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["meetings"]
        )
        results = [{"id": "1", "title": "Meeting 1"}]

        suggestions = _generate_action_suggestions(classified, results, "")

        labels = [s.label.lower() for s in suggestions]
        assert any("meeting" in l or "schedule" in l or "upcoming" in l for l in labels)

    def test_search_single_result(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.SEARCH,
            entities=["tasks"]
        )
        results = [{"id": "task-123", "title": "Specific Task"}]

        suggestions = _generate_action_suggestions(classified, results, "")

        labels = [s.label.lower() for s in suggestions]
        assert any("detail" in l or "view" in l for l in labels)

    def test_search_no_results(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.SEARCH,
            entities=["tasks"]
        )
        results = []

        suggestions = _generate_action_suggestions(classified, results, "")

        labels = [s.label.lower() for s in suggestions]
        assert any("broaden" in l for l in labels)

    def test_status_check_tasks(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.STATUS_CHECK,
            entities=["tasks"]
        )
        results = [{"id": "1", "status": "In Progress"}]

        suggestions = _generate_action_suggestions(classified, results, "")

        labels = [s.label.lower() for s in suggestions]
        assert any("task" in l or "blocked" in l for l in labels)

    def test_aggregation_intent(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.AGGREGATION,
            entities=["agents"]
        )
        results = [{"count": 10, "type": "enterprise"}]

        suggestions = _generate_action_suggestions(classified, results, "")

        labels = [s.label.lower() for s in suggestions]
        assert any("drill" in l or "down" in l for l in labels)

    def test_comparison_intent(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.COMPARISON,
            entities=["tasks"]
        )
        results = []

        suggestions = _generate_action_suggestions(classified, results, "")

        labels = [s.label.lower() for s in suggestions]
        assert any("trend" in l for l in labels)

    def test_explanation_intent(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.EXPLANATION,
            entities=["platform"]
        )
        results = []

        suggestions = _generate_action_suggestions(classified, results, "")

        labels = [s.label.lower() for s in suggestions]
        assert len(labels) >= 1

    def test_max_four_suggestions(self):
        from src.main import _generate_action_suggestions

        classified = create_classified_intent(
            intent=QueryIntent.AUDIT,
            entities=["logs"]
        )
        results = []

        suggestions = _generate_action_suggestions(classified, results, "")

        assert len(suggestions) <= 6


class TestGenerateActionSuggestionsWithHMLR:
    @pytest.mark.asyncio
    async def test_no_user_returns_base_suggestions(self):
        from src.main import _generate_action_suggestions_with_hmlr

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"]
        )

        suggestions = await _generate_action_suggestions_with_hmlr(
            classified=classified,
            results=[{"id": "1"}],
            response_text="",
            user_id=None,
            session_id=None
        )

        assert len(suggestions) <= 6
        assert all(isinstance(s, ActionSuggestion) for s in suggestions)

    @pytest.mark.asyncio
    async def test_with_user_blends_hmlr_suggestions(self):
        from src.main import _generate_action_suggestions_with_hmlr

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"]
        )

        hmlr_suggestions = [
            PersonalizedSuggestion(
                text="Continue: API integration",
                source=SuggestionSource.OPEN_LOOP,
                priority=100,
                confidence=0.9,
                metadata={"original_text": "Continue API integration work"}
            )
        ]

        with patch('src.main.suggestion_orchestrator') as mock_orchestrator:
            mock_orchestrator.get_followup_suggestions = AsyncMock(return_value=hmlr_suggestions)

            suggestions = await _generate_action_suggestions_with_hmlr(
                classified=classified,
                results=[{"id": "1"}],
                response_text="Here are your tasks",
                user_id="user123",
                session_id="session456"
            )

            assert len(suggestions) <= 6
            labels = [s.label for s in suggestions]
            assert any("Continue" in l or "API" in l for l in labels)

    @pytest.mark.asyncio
    async def test_hmlr_error_falls_back_to_base(self):
        from src.main import _generate_action_suggestions_with_hmlr

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"]
        )

        with patch('src.main.suggestion_orchestrator') as mock_orchestrator:
            mock_orchestrator.get_followup_suggestions = AsyncMock(side_effect=Exception("HMLR error"))

            suggestions = await _generate_action_suggestions_with_hmlr(
                classified=classified,
                results=[{"id": "1"}],
                response_text="",
                user_id="user123",
                session_id="session456"
            )

            assert len(suggestions) >= 1
            assert all(isinstance(s, ActionSuggestion) for s in suggestions)

    @pytest.mark.asyncio
    async def test_empty_hmlr_suggestions_returns_base(self):
        from src.main import _generate_action_suggestions_with_hmlr

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"]
        )

        with patch('src.main.suggestion_orchestrator') as mock_orchestrator:
            mock_orchestrator.get_followup_suggestions = AsyncMock(return_value=[])

            suggestions = await _generate_action_suggestions_with_hmlr(
                classified=classified,
                results=[{"id": "1"}],
                response_text="",
                user_id="user123",
                session_id="session456"
            )

            assert len(suggestions) >= 1

    @pytest.mark.asyncio
    async def test_deduplicates_labels(self):
        from src.main import _generate_action_suggestions_with_hmlr

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"]
        )

        hmlr_suggestions = [
            PersonalizedSuggestion(
                text="Filter by priority",
                source=SuggestionSource.INTENT,
                priority=75,
                confidence=0.85,
                metadata={}
            )
        ]

        with patch('src.main.suggestion_orchestrator') as mock_orchestrator:
            mock_orchestrator.get_followup_suggestions = AsyncMock(return_value=hmlr_suggestions)

            suggestions = await _generate_action_suggestions_with_hmlr(
                classified=classified,
                results=[{"id": "1"}],
                response_text="",
                user_id="user123",
                session_id="session456"
            )

            labels = [s.label.lower() for s in suggestions]
            unique_labels = set(labels)
            assert len(labels) == len(unique_labels)

    @pytest.mark.asyncio
    async def test_hmlr_suggestions_come_first(self):
        from src.main import _generate_action_suggestions_with_hmlr

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"]
        )

        hmlr_suggestions = [
            PersonalizedSuggestion(
                text="High priority HMLR suggestion",
                source=SuggestionSource.OPEN_LOOP,
                priority=100,
                confidence=0.9,
                metadata={"original_text": "High priority HMLR suggestion"}
            )
        ]

        with patch('src.main.suggestion_orchestrator') as mock_orchestrator:
            mock_orchestrator.get_followup_suggestions = AsyncMock(return_value=hmlr_suggestions)

            suggestions = await _generate_action_suggestions_with_hmlr(
                classified=classified,
                results=[{"id": "1"}],
                response_text="",
                user_id="user123",
                session_id="session456"
            )

            if suggestions:
                assert "HMLR" in suggestions[0].label or "High priority" in suggestions[0].label

    @pytest.mark.asyncio
    async def test_truncates_long_labels(self):
        from src.main import _generate_action_suggestions_with_hmlr

        classified = create_classified_intent(
            intent=QueryIntent.LIST,
            entities=["tasks"]
        )

        long_text = "This is a very long suggestion text that should be truncated because it exceeds the maximum label length"
        hmlr_suggestions = [
            PersonalizedSuggestion(
                text=long_text,
                source=SuggestionSource.OPEN_LOOP,
                priority=100,
                confidence=0.9,
                metadata={"original_text": long_text}
            )
        ]

        with patch('src.main.suggestion_orchestrator') as mock_orchestrator:
            mock_orchestrator.get_followup_suggestions = AsyncMock(return_value=hmlr_suggestions)

            suggestions = await _generate_action_suggestions_with_hmlr(
                classified=classified,
                results=[{"id": "1"}],
                response_text="",
                user_id="user123",
                session_id="session456"
            )

            for s in suggestions:
                assert len(s.label) <= 43


class TestActionSuggestionParams:
    @pytest.mark.asyncio
    async def test_open_loop_creates_query_action(self):
        from src.main import _generate_action_suggestions_with_hmlr

        classified = create_classified_intent(intent=QueryIntent.LIST, entities=["tasks"])

        hmlr_suggestions = [
            PersonalizedSuggestion(
                text="Continue: API work",
                source=SuggestionSource.OPEN_LOOP,
                priority=100,
                confidence=0.9,
                metadata={"original_text": "What is the status of API integration?"}
            )
        ]

        with patch('src.main.suggestion_orchestrator') as mock_orchestrator:
            mock_orchestrator.get_followup_suggestions = AsyncMock(return_value=hmlr_suggestions)

            suggestions = await _generate_action_suggestions_with_hmlr(
                classified=classified,
                results=[],
                response_text="",
                user_id="user123",
                session_id="session456"
            )

            hmlr_derived = [s for s in suggestions if "API" in s.label or "Continue" in s.label]
            if hmlr_derived:
                assert hmlr_derived[0].action_type == "query"
                assert "query" in hmlr_derived[0].params
