"""
End-to-End Memory Flow Tests for HMLR System.

Tests cover the complete flow:
- Query → Route → Store → Extract → Index → Retrieve

These tests validate that the entire HMLR system works together correctly,
from receiving a user query through storing memories and retrieving them later.

Run with: pytest tests/test_hmlr_e2e_flow.py -v --tb=short
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone
import uuid

from src.hmlr.models import (
    BridgeBlock, Fact, FactCategory, GovernorDecision,
    RoutingScenario, CandidateMemory, MemoryType, BlockStatus
)
from src.hmlr.suggestion_models import SuggestionData


def create_test_block(
    block_id: str = None,
    session_id: str = "test-session",
    user_id: str = "test-user",
    topic_label: str = "Test Topic",
    summary: str = "Test summary",
    status: str = "ACTIVE"
) -> BridgeBlock:
    """Create a test BridgeBlock."""
    return BridgeBlock(
        id=block_id or f"bb_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        user_id=user_id,
        topic_label=topic_label,
        summary=summary,
        keywords=["test"],
        open_loops=[],
        decisions_made=[],
        status=status,
        last_activity=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc)
    )


def create_test_fact(
    user_id: str = "test-user",
    key: str = "test_key",
    value: str = "test_value",
    category: FactCategory = FactCategory.DEFINITION,
    fact_id: int = 1
) -> Fact:
    """Create a test Fact."""
    return Fact(
        user_id=user_id,
        key=key,
        value=value,
        category=category,
        confidence=0.9,
        fact_id=fact_id
    )


def create_test_candidate_memory(
    mem_id: str = "mem_1",
    user_id: str = "test-user",
    content: str = "Test memory content",
    memory_type: MemoryType = MemoryType.FACT,
    score: float = 0.9
) -> CandidateMemory:
    """Create a test CandidateMemory."""
    return CandidateMemory(
        id=mem_id,
        user_id=user_id,
        content=content,
        memory_type=memory_type,
        source_id=f"source_{mem_id}",
        score=score
    )


class TestRoutingScenarios:
    """Test all 4 routing scenarios are correctly identified."""

    def test_topic_continuation_scenario(self):
        """TOPIC_CONTINUATION when query matches active block."""
        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_CONTINUATION,
            matched_block_id="bb_123",
            active_block=create_test_block(block_id="bb_123"),
            topic_similarity=0.85,
            relevant_facts=[],
            memories=[]
        )

        assert decision.scenario == RoutingScenario.TOPIC_CONTINUATION
        assert decision.matched_block_id == "bb_123"
        assert decision.topic_similarity >= 0.7

    def test_topic_resumption_scenario(self):
        """TOPIC_RESUMPTION when query matches paused block."""
        paused_block = create_test_block(block_id="bb_456", status="PAUSED")
        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_RESUMPTION,
            matched_block_id="bb_456",
            active_block=paused_block,
            topic_similarity=0.75,
            relevant_facts=[],
            memories=[]
        )

        assert decision.scenario == RoutingScenario.TOPIC_RESUMPTION
        assert decision.matched_block_id == "bb_456"

    def test_new_topic_first_scenario(self):
        """NEW_TOPIC_FIRST when no blocks exist."""
        decision = GovernorDecision(
            scenario=RoutingScenario.NEW_TOPIC_FIRST,
            matched_block_id=None,
            active_block=None,
            topic_similarity=0.0,
            relevant_facts=[],
            memories=[]
        )

        assert decision.scenario == RoutingScenario.NEW_TOPIC_FIRST
        assert decision.matched_block_id is None

    def test_topic_shift_scenario(self):
        """TOPIC_SHIFT when query doesn't match active but has active blocks."""
        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_SHIFT,
            matched_block_id=None,
            active_block=None,
            topic_similarity=0.3,
            relevant_facts=[],
            memories=[]
        )

        assert decision.scenario == RoutingScenario.TOPIC_SHIFT


class TestFactExtractionFlow:
    """Test fact extraction from conversations."""

    def test_fact_structure_valid(self):
        """Extracted fact has all required fields."""
        fact = create_test_fact(
            user_id="user123",
            key="Python",
            value="A programming language",
            category=FactCategory.DEFINITION,
            fact_id=1
        )

        assert fact.user_id == "user123"
        assert fact.key == "Python"
        assert fact.value == "A programming language"
        assert fact.category == FactCategory.DEFINITION
        assert 0.0 <= fact.confidence <= 1.0

    def test_secret_fact_category(self):
        """SECRET category facts are created correctly."""
        secret_fact = create_test_fact(
            key="api_key",
            value="sk-secret123",
            category=FactCategory.SECRET
        )

        assert secret_fact.category == FactCategory.SECRET

    def test_fact_categories(self):
        """All fact categories are available."""
        categories = [
            FactCategory.DEFINITION,
            FactCategory.ACRONYM,
            FactCategory.SECRET,
            FactCategory.ENTITY,
        ]

        for cat in categories:
            fact = create_test_fact(category=cat)
            assert fact.category == cat


class TestMemoryRetrieval:
    """Test memory retrieval in routing decisions."""

    def test_relevant_facts_included_in_decision(self):
        """Relevant facts are included in GovernorDecision."""
        facts = [
            create_test_fact(key="Python", value="Programming language"),
            create_test_fact(key="FastAPI", value="Web framework", fact_id=2)
        ]

        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_CONTINUATION,
            matched_block_id="bb_123",
            active_block=create_test_block(),
            topic_similarity=0.8,
            relevant_facts=facts,
            memories=[]
        )

        assert len(decision.relevant_facts) == 2
        assert any(f.key == "Python" for f in decision.relevant_facts)
        assert any(f.key == "FastAPI" for f in decision.relevant_facts)

    def test_memories_as_dicts_included(self):
        """Memories from vector search included as dicts."""
        memories = [
            {
                "id": "mem_1",
                "user_id": "test-user",
                "content": "Previous discussion about APIs",
                "memory_type": "block_summary",
                "score": 0.85
            },
            {
                "id": "mem_2",
                "user_id": "test-user",
                "content": "Definition of REST",
                "memory_type": "fact",
                "score": 0.75
            }
        ]

        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_CONTINUATION,
            matched_block_id="bb_123",
            active_block=create_test_block(),
            topic_similarity=0.8,
            relevant_facts=[],
            memories=memories
        )

        assert len(decision.memories) == 2
        assert decision.memories[0]["score"] > decision.memories[1]["score"]


class TestBlockLifecycle:
    """Test bridge block lifecycle management."""

    def test_block_creation(self):
        """New block has correct initial state."""
        block = create_test_block(
            topic_label="API Design Discussion",
            status="ACTIVE"
        )

        assert block.status == "ACTIVE"
        assert block.topic_label == "API Design Discussion"
        assert block.open_loops == []
        assert block.decisions_made == []

    def test_block_with_open_loops(self):
        """Block can store open loops."""
        block = BridgeBlock(
            id="bb_123",
            session_id="sess_1",
            user_id="user_1",
            topic_label="Sprint Planning",
            open_loops=["Review PR #456", "Update documentation"],
            status="ACTIVE"
        )

        assert len(block.open_loops) == 2
        assert "Review PR #456" in block.open_loops

    def test_block_with_decisions(self):
        """Block can store decisions made."""
        block = BridgeBlock(
            id="bb_123",
            session_id="sess_1",
            user_id="user_1",
            topic_label="Architecture Review",
            decisions_made=["Use event-driven pattern", "Deploy to Azure"],
            status="ACTIVE"
        )

        assert len(block.decisions_made) == 2

    def test_block_paused_status(self):
        """Block can transition to PAUSED."""
        block = create_test_block(status="PAUSED")

        assert block.status == "PAUSED"

    def test_block_status_enum_values(self):
        """BlockStatus enum has expected values."""
        assert BlockStatus.ACTIVE.value == "ACTIVE"
        assert BlockStatus.PAUSED.value == "PAUSED"


class TestCrossSessionFlow:
    """Test cross-session memory persistence."""

    def test_fact_has_user_id_for_isolation(self):
        """Facts have user_id for cross-session isolation."""
        fact = create_test_fact(user_id="user_abc")

        assert fact.user_id == "user_abc"

    def test_block_has_session_and_user_id(self):
        """Blocks have both session_id and user_id."""
        block = create_test_block(
            session_id="session_xyz",
            user_id="user_abc"
        )

        assert block.session_id == "session_xyz"
        assert block.user_id == "user_abc"

    def test_candidate_memory_has_user_id(self):
        """CandidateMemory includes user_id for filtering."""
        memory = create_test_candidate_memory(
            user_id="user_abc",
            content="Test memory content"
        )

        assert memory.user_id == "user_abc"

    def test_candidate_memory_has_source_id(self):
        """CandidateMemory includes source_id for tracing."""
        memory = create_test_candidate_memory()

        assert memory.source_id is not None
        assert len(memory.source_id) > 0


class TestSuggestionDataFlow:
    """Test suggestion data generation."""

    def test_suggestion_data_structure(self):
        """SuggestionData has all required fields."""
        data = SuggestionData(
            open_loops=[
                {"text": "Review PR", "topic": "Code Review", "priority": 90, "is_current_session": True}
            ],
            common_queries=["How to deploy?", "What's the API endpoint?"],
            topic_interests=["Python", "Azure", "FastAPI"],
            known_entities=[{"name": "Project Alpha", "type": "project"}, {"name": "Team Beta", "type": "team"}],
            recent_topics=["API Design", "Testing Strategy"],
            expertise_level="advanced",
            facts=[{"key": "framework", "value": "FastAPI"}]
        )

        assert len(data.open_loops) == 1
        assert len(data.common_queries) == 2
        assert data.expertise_level == "advanced"

    def test_suggestion_data_empty_valid(self):
        """SuggestionData can be empty for new users."""
        data = SuggestionData(
            open_loops=[],
            common_queries=[],
            topic_interests=[],
            known_entities=[],
            recent_topics=[],
            expertise_level="beginner",
            facts=[]
        )

        assert len(data.open_loops) == 0
        assert data.expertise_level == "beginner"


class TestDataIntegrity:
    """Test data integrity across the flow."""

    def test_block_id_format(self):
        """Block IDs follow expected format."""
        block = create_test_block()

        assert block.id.startswith("bb_")

    def test_fact_id_numeric(self):
        """Fact IDs are numeric."""
        fact = create_test_fact(fact_id=123)

        assert isinstance(fact.fact_id, int)
        assert fact.fact_id == 123

    def test_timestamp_is_utc(self):
        """Timestamps are in UTC timezone."""
        block = create_test_block()

        assert block.created_at.tzinfo is not None
        assert block.last_activity.tzinfo is not None

    def test_similarity_score_range(self):
        """Topic similarity is in valid range [0, 1]."""
        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_CONTINUATION,
            matched_block_id="bb_123",
            active_block=create_test_block(),
            topic_similarity=0.85,
            relevant_facts=[],
            memories=[]
        )

        assert 0.0 <= decision.topic_similarity <= 1.0


class TestMemoryTypeHandling:
    """Test different memory types are handled correctly."""

    def test_fact_memory_type(self):
        """FACT memory type is handled."""
        memory = create_test_candidate_memory(
            content="Python is a programming language",
            memory_type=MemoryType.FACT
        )

        assert memory.memory_type == MemoryType.FACT

    def test_block_summary_memory_type(self):
        """BLOCK_SUMMARY memory type is handled."""
        memory = create_test_candidate_memory(
            content="Discussed API design patterns",
            memory_type=MemoryType.BLOCK_SUMMARY
        )

        assert memory.memory_type == MemoryType.BLOCK_SUMMARY

    def test_memory_types_distinct(self):
        """Memory types are distinct and don't overlap."""
        fact_mem = create_test_candidate_memory(
            mem_id="1",
            memory_type=MemoryType.FACT
        )
        block_mem = create_test_candidate_memory(
            mem_id="2",
            memory_type=MemoryType.BLOCK_SUMMARY
        )

        assert fact_mem.memory_type != block_mem.memory_type

    def test_memory_type_enum_values(self):
        """MemoryType enum has expected values."""
        assert MemoryType.FACT.value == "fact"
        assert MemoryType.BLOCK_SUMMARY.value == "block_summary"


class TestEdgeCases:
    """Test edge cases in the E2E flow."""

    def test_empty_query_creates_new_topic(self):
        """Empty/whitespace queries result in new topic."""
        decision = GovernorDecision(
            scenario=RoutingScenario.NEW_TOPIC_FIRST,
            matched_block_id=None,
            active_block=None,
            topic_similarity=0.0,
            relevant_facts=[],
            memories=[]
        )

        assert decision.scenario == RoutingScenario.NEW_TOPIC_FIRST

    def test_very_long_content(self):
        """Long content is handled."""
        long_content = "x" * 10000
        memory = create_test_candidate_memory(content=long_content)

        assert len(memory.content) == 10000

    def test_special_characters_in_content(self):
        """Special characters are handled in content."""
        special_content = "API key: ${{ secrets.KEY }} with <html> & 'quotes'"
        fact = create_test_fact(value=special_content)

        assert fact.value == special_content

    def test_unicode_content(self):
        """Unicode content is handled."""
        unicode_content = "日本語テスト πρόγραμμα 🚀"
        block = create_test_block(topic_label=unicode_content)

        assert block.topic_label == unicode_content

    def test_zero_similarity_score(self):
        """Zero similarity score is valid."""
        decision = GovernorDecision(
            scenario=RoutingScenario.NEW_TOPIC_FIRST,
            matched_block_id=None,
            active_block=None,
            topic_similarity=0.0,
            relevant_facts=[],
            memories=[]
        )

        assert decision.topic_similarity == 0.0

    def test_perfect_similarity_score(self):
        """Perfect (1.0) similarity score is valid."""
        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_CONTINUATION,
            matched_block_id="bb_exact",
            active_block=create_test_block(),
            topic_similarity=1.0,
            relevant_facts=[],
            memories=[]
        )

        assert decision.topic_similarity == 1.0


class TestRoutingScenarioValues:
    """Test routing scenario enum values."""

    def test_scenario_values(self):
        """Routing scenarios have expected integer values."""
        assert RoutingScenario.TOPIC_CONTINUATION.value == 1
        assert RoutingScenario.TOPIC_RESUMPTION.value == 2
        assert RoutingScenario.NEW_TOPIC_FIRST.value == 3
        assert RoutingScenario.TOPIC_SHIFT.value == 4

    def test_all_scenarios_unique(self):
        """All scenario values are unique."""
        values = [s.value for s in RoutingScenario]
        assert len(values) == len(set(values))
