"""
Unit tests for HMLR Suggestion Models.
Tests data structures, validation, and serialization.
"""
import pytest
from src.hmlr.suggestion_models import (
    SuggestionSource,
    PersonalizedSuggestion,
    SuggestionData,
    SuggestionResponse
)


class TestSuggestionSource:
    def test_all_sources_defined(self):
        expected = ["static", "intent", "open_loop", "common_query", "topic_interest", "entity", "context"]
        for source in expected:
            assert SuggestionSource(source) is not None

    def test_source_values(self):
        assert SuggestionSource.STATIC.value == "static"
        assert SuggestionSource.OPEN_LOOP.value == "open_loop"
        assert SuggestionSource.INTENT.value == "intent"


class TestPersonalizedSuggestion:
    def test_create_minimal(self):
        s = PersonalizedSuggestion(
            text="Test suggestion",
            source=SuggestionSource.STATIC,
            priority=50,
            confidence=0.8
        )
        assert s.text == "Test suggestion"
        assert s.source == SuggestionSource.STATIC
        assert s.priority == 50
        assert s.confidence == 0.8
        assert s.metadata is None

    def test_create_with_metadata(self):
        s = PersonalizedSuggestion(
            text="Continue task",
            source=SuggestionSource.OPEN_LOOP,
            priority=100,
            confidence=0.9,
            metadata={"block_id": "123", "topic": "API integration"}
        )
        assert s.metadata["block_id"] == "123"
        assert s.metadata["topic"] == "API integration"

    def test_id_generation(self):
        s1 = PersonalizedSuggestion(
            text="Test",
            source=SuggestionSource.STATIC,
            priority=50,
            confidence=1.0
        )
        s2 = PersonalizedSuggestion(
            text="Test",
            source=SuggestionSource.STATIC,
            priority=50,
            confidence=1.0
        )
        assert s1.id != s2.id

    def test_serialization(self):
        s = PersonalizedSuggestion(
            text="Test",
            source=SuggestionSource.INTENT,
            priority=75,
            confidence=0.85,
            metadata={"intent": "task_query"}
        )
        d = s.model_dump()
        assert d["text"] == "Test"
        assert d["source"] == "intent"
        assert d["priority"] == 75
        assert d["confidence"] == 0.85

    def test_priority_range(self):
        high = PersonalizedSuggestion(
            text="High priority",
            source=SuggestionSource.OPEN_LOOP,
            priority=100,
            confidence=0.9
        )
        low = PersonalizedSuggestion(
            text="Low priority",
            source=SuggestionSource.STATIC,
            priority=40,
            confidence=1.0
        )
        assert high.priority > low.priority


class TestSuggestionData:
    def test_empty_data(self):
        data = SuggestionData()
        assert data.open_loops == []
        assert data.common_queries == []
        assert data.topic_interests == []
        assert data.known_entities == []
        assert data.relevant_facts == []
        assert data.expertise_level == "intermediate"

    def test_populated_data(self):
        data = SuggestionData(
            open_loops=[{"text": "API integration", "topic": "backend", "priority": 95}],
            common_queries=["How do I deploy?", "Show blocked tasks"],
            topic_interests=["governance", "agents"],
            known_entities=[{"name": "Dashboard", "type": "project"}],
            relevant_facts=[{"key": "RAG", "category": "Acronym"}],
            expertise_level="expert"
        )
        assert len(data.open_loops) == 1
        assert len(data.common_queries) == 2
        assert data.expertise_level == "expert"


class TestSuggestionResponse:
    def test_minimal_response(self):
        r = SuggestionResponse(
            suggestions=[],
            is_personalized=False,
            page_type="dashboard"
        )
        assert r.suggestions == []
        assert r.is_personalized is False
        assert r.user_id is None
        assert r.fallback_reason is None

    def test_personalized_response(self):
        suggestions = [
            PersonalizedSuggestion(
                text="Continue: API work",
                source=SuggestionSource.OPEN_LOOP,
                priority=100,
                confidence=0.9
            )
        ]
        r = SuggestionResponse(
            suggestions=suggestions,
            is_personalized=True,
            user_id="user123",
            page_type="tasks"
        )
        assert r.is_personalized is True
        assert r.user_id == "user123"
        assert len(r.suggestions) == 1

    def test_fallback_response(self):
        r = SuggestionResponse(
            suggestions=[],
            is_personalized=False,
            fallback_reason="empty_memory",
            page_type="dashboard"
        )
        assert r.fallback_reason == "empty_memory"

    def test_serialization(self):
        r = SuggestionResponse(
            suggestions=[
                PersonalizedSuggestion(
                    text="Test",
                    source=SuggestionSource.STATIC,
                    priority=40,
                    confidence=1.0
                )
            ],
            is_personalized=False,
            page_type="dashboard"
        )
        d = r.model_dump()
        assert "suggestions" in d
        assert "is_personalized" in d
        assert d["page_type"] == "dashboard"
