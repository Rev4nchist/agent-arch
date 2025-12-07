"""
Unit tests for HMLR Suggestion Providers.
Tests MemorySuggestionProvider, StaticSuggestionProvider, IntentSuggestionProvider.
"""
import pytest
from src.hmlr.suggestion_models import (
    SuggestionSource,
    PersonalizedSuggestion,
    SuggestionData
)
from src.hmlr.suggestion_providers import (
    MemorySuggestionProvider,
    StaticSuggestionProvider,
    IntentSuggestionProvider,
    PAGE_STATIC_SUGGESTIONS
)


class TestStaticSuggestionProvider:
    @pytest.fixture
    def provider(self):
        return StaticSuggestionProvider()

    def test_dashboard_suggestions(self, provider):
        suggestions = provider.get_suggestions(page_type="dashboard")
        assert len(suggestions) == 4
        assert all(s.source == SuggestionSource.STATIC for s in suggestions)
        assert all(s.priority == 40 for s in suggestions)
        assert all(s.confidence == 1.0 for s in suggestions)

    def test_all_page_types_have_suggestions(self, provider):
        page_types = ["dashboard", "meetings", "tasks", "agents", "decisions",
                      "governance", "budget", "resources", "tech-radar", "architecture", "guide"]
        for page_type in page_types:
            suggestions = provider.get_suggestions(page_type=page_type)
            assert len(suggestions) >= 3, f"Page {page_type} should have at least 3 suggestions"

    def test_unknown_page_fallback(self, provider):
        suggestions = provider.get_suggestions(page_type="nonexistent")
        assert len(suggestions) == 4
        expected_texts = PAGE_STATIC_SUGGESTIONS["unknown"]
        assert all(s.text in expected_texts for s in suggestions)

    def test_metadata_includes_page_type(self, provider):
        suggestions = provider.get_suggestions(page_type="tasks")
        for s in suggestions:
            assert s.metadata["page_type"] == "tasks"


class TestMemorySuggestionProvider:
    @pytest.fixture
    def provider(self):
        return MemorySuggestionProvider()

    def test_empty_data_returns_empty(self, provider):
        data = SuggestionData()
        suggestions = provider.get_suggestions(data=data)
        assert suggestions == []

    def test_open_loops_highest_priority(self, provider):
        data = SuggestionData(
            open_loops=[
                {"text": "API integration guide", "topic": "backend", "priority": 100}
            ]
        )
        suggestions = provider.get_suggestions(data=data)
        assert len(suggestions) >= 1
        open_loop_suggestion = next(
            (s for s in suggestions if s.source == SuggestionSource.OPEN_LOOP), None
        )
        assert open_loop_suggestion is not None
        assert "Continue:" in open_loop_suggestion.text or "Resume:" in open_loop_suggestion.text

    def test_current_session_vs_cross_session(self, provider):
        data = SuggestionData(
            open_loops=[
                {"text": "Current task", "topic": "now", "priority": 100, "is_current_session": True},
                {"text": "Old task", "topic": "before", "priority": 90, "is_current_session": False}
            ]
        )
        suggestions = provider.get_suggestions(data=data)
        current = next((s for s in suggestions if "Current task" in s.text), None)
        old = next((s for s in suggestions if "Old task" in s.text), None)

        if current and old:
            assert current.confidence > old.confidence

    def test_common_queries_adapted_for_expertise(self, provider):
        beginner_data = SuggestionData(
            common_queries=["Deploy application"],
            expertise_level="beginner"
        )
        expert_data = SuggestionData(
            common_queries=["How do I deploy?"],
            expertise_level="expert"
        )

        beginner_suggestions = provider.get_suggestions(data=beginner_data)
        expert_suggestions = provider.get_suggestions(data=expert_data)

        if beginner_suggestions:
            assert any("Help me understand" in s.text for s in beginner_suggestions)
        if expert_suggestions:
            assert any("advanced" in s.text.lower() for s in expert_suggestions)

    def test_topic_interests_generate_explore_suggestions(self, provider):
        data = SuggestionData(
            topic_interests=["governance", "agents", "security"]
        )
        suggestions = provider.get_suggestions(data=data)
        explore_suggestions = [s for s in suggestions if s.source == SuggestionSource.TOPIC_INTEREST]
        assert len(explore_suggestions) >= 1
        assert any("Explore more about" in s.text for s in explore_suggestions)

    def test_entities_generate_update_suggestions(self, provider):
        data = SuggestionData(
            known_entities=[
                {"name": "Dashboard", "type": "project"},
                {"name": "AI Team", "type": "team"}
            ]
        )
        suggestions = provider.get_suggestions(data=data)
        entity_suggestions = [s for s in suggestions if s.source == SuggestionSource.ENTITY]
        assert len(entity_suggestions) >= 1
        assert any("Update on" in s.text or "Tell me about" in s.text for s in entity_suggestions)

    def test_context_facts_generate_explain_suggestions(self, provider):
        data = SuggestionData(
            relevant_facts=[
                {"key": "RAG", "category": "Acronym"},
                {"key": "HMLR", "category": "Definition"}
            ]
        )
        suggestions = provider.get_suggestions(data=data)
        context_suggestions = [s for s in suggestions if s.source == SuggestionSource.CONTEXT]
        assert len(context_suggestions) >= 1

    def test_max_open_loops_limit(self, provider):
        data = SuggestionData(
            open_loops=[
                {"text": f"Loop {i}", "topic": f"topic{i}", "priority": 100 - i}
                for i in range(10)
            ]
        )
        suggestions = provider.get_suggestions(data=data)
        open_loops = [s for s in suggestions if s.source == SuggestionSource.OPEN_LOOP]
        assert len(open_loops) <= 3

    def test_deduplication_of_common_queries(self, provider):
        data = SuggestionData(
            common_queries=["How do I deploy?", "how do i deploy?", "HOW DO I DEPLOY?"]
        )
        suggestions = provider.get_suggestions(data=data)
        common = [s for s in suggestions if s.source == SuggestionSource.COMMON_QUERY]
        assert len(common) <= 1


class TestIntentSuggestionProvider:
    @pytest.fixture
    def provider(self):
        return IntentSuggestionProvider()

    def test_task_query_intent(self, provider):
        suggestions = provider.get_suggestions(intent="task_query")
        assert len(suggestions) >= 1
        assert all(s.source == SuggestionSource.INTENT for s in suggestions)
        texts = [s.text.lower() for s in suggestions]
        assert any("task" in t for t in texts)

    def test_meeting_query_intent(self, provider):
        suggestions = provider.get_suggestions(intent="meeting_query")
        texts = [s.text.lower() for s in suggestions]
        assert any("meeting" in t or "action" in t for t in texts)

    def test_agent_query_intent(self, provider):
        suggestions = provider.get_suggestions(intent="agent_query")
        texts = [s.text.lower() for s in suggestions]
        assert any("agent" in t for t in texts)

    def test_platform_help_intent(self, provider):
        suggestions = provider.get_suggestions(intent="platform_help")
        texts = [s.text.lower() for s in suggestions]
        assert any("how" in t or "navigate" in t for t in texts)

    def test_unknown_intent_fallback(self, provider):
        suggestions = provider.get_suggestions(intent="unknown_intent_xyz")
        assert len(suggestions) >= 1
        assert "would you like to know" in suggestions[0].text.lower()

    def test_open_loop_injection_on_high_priority(self, provider):
        data = SuggestionData(
            open_loops=[{"text": "Continue API work", "topic": "api", "priority": 90}]
        )
        suggestions = provider.get_suggestions(intent="task_query", data=data)
        open_loop_found = any(s.source == SuggestionSource.OPEN_LOOP for s in suggestions)
        assert open_loop_found

    def test_no_open_loop_on_low_priority(self, provider):
        data = SuggestionData(
            open_loops=[{"text": "Old loop", "topic": "old", "priority": 50}]
        )
        suggestions = provider.get_suggestions(intent="task_query", data=data)
        open_loops = [s for s in suggestions if s.source == SuggestionSource.OPEN_LOOP]
        assert len(open_loops) == 0

    def test_response_text_not_currently_used(self, provider):
        suggestions1 = provider.get_suggestions(intent="task_query", response_text=None)
        suggestions2 = provider.get_suggestions(intent="task_query", response_text="Some response")
        assert len(suggestions1) == len(suggestions2)


class TestProviderIntegration:
    def test_all_providers_return_personalized_suggestions(self):
        memory = MemorySuggestionProvider()
        static = StaticSuggestionProvider()
        intent = IntentSuggestionProvider()

        data = SuggestionData(
            open_loops=[{"text": "Test", "topic": "test", "priority": 100}]
        )

        memory_results = memory.get_suggestions(data=data)
        static_results = static.get_suggestions(page_type="dashboard")
        intent_results = intent.get_suggestions(intent="task_query")

        all_results = memory_results + static_results + intent_results
        assert all(isinstance(s, PersonalizedSuggestion) for s in all_results)

    def test_priority_ordering_across_sources(self):
        memory = MemorySuggestionProvider()
        static = StaticSuggestionProvider()

        data = SuggestionData(
            open_loops=[{"text": "High priority loop", "topic": "urgent", "priority": 100}]
        )

        memory_results = memory.get_suggestions(data=data)
        static_results = static.get_suggestions(page_type="dashboard")

        if memory_results and static_results:
            highest_memory = max(s.priority for s in memory_results)
            highest_static = max(s.priority for s in static_results)
            assert highest_memory > highest_static
