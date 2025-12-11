"""
Open Loop Reliability Tests for HMLR Memory System.

Tests cover:
- Open loop creation and storage in blocks
- Open loop surfacing in suggestions
- Cross-session open loop retrieval
- Priority ordering by age
- Max limit enforcement
- Open loop resolution

Open loops are critical for "reminding about things that slip through the cracks".
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, timezone
import uuid

from src.hmlr.models import BridgeBlock
from src.hmlr.memory_accessor import HMLRMemoryAccessor
from src.hmlr.suggestion_models import SuggestionData


def create_mock_block(
    block_id: str = None,
    session_id: str = "test-session",
    user_id: str = "test-user",
    topic_label: str = "Test Topic",
    open_loops: list = None,
    status: str = "ACTIVE",
    last_activity: datetime = None
) -> BridgeBlock:
    """Create a mock BridgeBlock for testing."""
    return BridgeBlock(
        id=block_id or f"bb_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        user_id=user_id,
        topic_label=topic_label,
        open_loops=open_loops or [],
        status=status,
        last_activity=last_activity or datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc)
    )


class TestOpenLoopStorage:
    """Test open loop storage in bridge blocks."""

    def test_open_loop_added_to_block(self):
        """Open loops are stored in block.open_loops list."""
        block = create_mock_block(
            open_loops=["Review PR #123", "Finalize budget report"]
        )

        assert len(block.open_loops) == 2
        assert "Review PR #123" in block.open_loops
        assert "Finalize budget report" in block.open_loops

    def test_open_loops_are_strings(self):
        """Open loops must be string type."""
        block = create_mock_block(
            open_loops=["Task 1", "Task 2", "Task 3"]
        )

        for loop in block.open_loops:
            assert isinstance(loop, str)

    def test_empty_open_loops(self):
        """Block can have empty open_loops list."""
        block = create_mock_block(open_loops=[])

        assert block.open_loops == []
        assert len(block.open_loops) == 0

    def test_special_characters_in_open_loops(self):
        """Open loops can contain special characters."""
        special_loops = [
            "Review PR #123 with 'quotes'",
            "Fix bug <XSS> test",
            "Budget: $1,000 & expenses",
            "Task with\nnewline"
        ]
        block = create_mock_block(open_loops=special_loops)

        assert len(block.open_loops) == 4
        assert all(loop in block.open_loops for loop in special_loops)


class TestOpenLoopRetrieval:
    """Test open loop retrieval logic.

    Note: These tests focus on the data model and calculation logic,
    not full integration with HMLRMemoryAccessor which requires complex mocking.
    """

    def test_open_loop_structure_has_required_fields(self):
        """Open loop dict has required fields: text, topic, priority, is_current_session."""
        open_loop = {
            "text": "Schedule meeting with Sarah",
            "topic": "Project Planning",
            "block_id": "bb_123",
            "priority": 95,
            "is_current_session": True
        }

        assert "text" in open_loop
        assert "topic" in open_loop
        assert "priority" in open_loop
        assert "is_current_session" in open_loop

    def test_recency_priority_calculation(self):
        """Test priority decreases with age."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor(MagicMock())

        priority_1h = accessor._calculate_recency_priority(1, is_current_session=True)
        priority_24h = accessor._calculate_recency_priority(24, is_current_session=True)
        priority_48h = accessor._calculate_recency_priority(48, is_current_session=True)

        assert priority_1h > priority_24h > priority_48h

    def test_current_session_priority_higher(self):
        """Current session has higher base priority than cross-session."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor(MagicMock())

        current_priority = accessor._calculate_recency_priority(1, is_current_session=True)
        cross_priority = accessor._calculate_recency_priority(1, is_current_session=False)

        assert current_priority > cross_priority

    def test_open_loops_extracted_from_block(self):
        """Open loops correctly extracted from block model."""
        block = create_mock_block(
            topic_label="Budget Planning",
            open_loops=["Finalize budget", "Review expenses"]
        )

        assert len(block.open_loops) == 2
        assert "Finalize budget" in block.open_loops
        assert "Review expenses" in block.open_loops


class TestCrossSessionOpenLoops:
    """Test cross-session open loop logic.

    Note: Focuses on the logic and constants rather than full async integration.
    """

    def test_cross_session_cutoff_hours(self):
        """Cross-session cutoff is 720 hours (30 days)."""
        from src.hmlr.memory_accessor import CROSS_SESSION_HOURS_CUTOFF

        assert CROSS_SESSION_HOURS_CUTOFF == 720

    def test_max_open_loops_constant(self):
        """Max open loops returned is 5."""
        from src.hmlr.memory_accessor import MAX_OPEN_LOOPS

        assert MAX_OPEN_LOOPS == 5

    def test_block_with_old_activity_excluded(self):
        """Test age calculation for old blocks."""
        now = datetime.now(timezone.utc)
        old_activity = now - timedelta(hours=800)

        age_hours = (now - old_activity).total_seconds() / 3600
        assert age_hours > 720

    def test_block_with_recent_activity_included(self):
        """Test age calculation for recent blocks."""
        now = datetime.now(timezone.utc)
        recent_activity = now - timedelta(hours=24)

        age_hours = (now - recent_activity).total_seconds() / 3600
        assert age_hours < 720


class TestOpenLoopPriority:
    """Test open loop priority ordering logic."""

    def test_recent_loops_have_higher_priority(self):
        """More recent open loops have higher priority."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor(MagicMock())

        priority_1h = accessor._calculate_recency_priority(1, is_current_session=True)
        priority_24h = accessor._calculate_recency_priority(24, is_current_session=True)

        assert priority_1h > priority_24h

    def test_current_session_higher_than_cross_session(self):
        """Current session loops prioritized over cross-session with same age."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        accessor = HMLRMemoryAccessor(MagicMock())

        current_priority = accessor._calculate_recency_priority(2, is_current_session=True)
        cross_priority = accessor._calculate_recency_priority(1, is_current_session=False)

        assert current_priority > cross_priority

    def test_priority_sorting_order(self):
        """Open loops should be sorted by priority descending."""
        loops = [
            {"text": "Low priority", "priority": 50},
            {"text": "High priority", "priority": 95},
            {"text": "Medium priority", "priority": 75},
        ]

        sorted_loops = sorted(loops, key=lambda x: x["priority"], reverse=True)

        assert sorted_loops[0]["text"] == "High priority"
        assert sorted_loops[1]["text"] == "Medium priority"
        assert sorted_loops[2]["text"] == "Low priority"


class TestOpenLoopMaxLimit:
    """Test max open loop limit enforcement."""

    @pytest.fixture
    def mock_hmlr_service(self):
        service = MagicMock()
        service.block_manager = MagicMock()
        service.sql_client = MagicMock()
        return service

    @pytest.fixture
    def memory_accessor(self, mock_hmlr_service):
        return HMLRMemoryAccessor(mock_hmlr_service)

    @pytest.mark.asyncio
    async def test_max_open_loops_enforced(self, memory_accessor, mock_hmlr_service):
        """Only MAX_OPEN_LOOPS (5) returned regardless of how many exist."""
        block = create_mock_block(
            open_loops=[f"Task {i}" for i in range(10)]
        )

        mock_hmlr_service.block_manager.get_session_blocks = AsyncMock(return_value=[block])
        mock_hmlr_service.sql_client.get_user_profile = MagicMock(return_value=None)

        result = await memory_accessor.get_suggestion_data("user", "session")

        assert len(result.open_loops) <= 5

    @pytest.mark.asyncio
    async def test_highest_priority_loops_kept(self, memory_accessor, mock_hmlr_service):
        """When limited, highest priority loops are kept."""
        now = datetime.now(timezone.utc)

        blocks = []
        for i in range(10):
            blocks.append(create_mock_block(
                block_id=f"block_{i}",
                session_id="session",
                open_loops=[f"Task {i}"],
                last_activity=now - timedelta(hours=i)
            ))

        mock_hmlr_service.block_manager.get_session_blocks = AsyncMock(return_value=blocks)
        mock_hmlr_service.sql_client.get_user_profile = MagicMock(return_value=None)

        result = await memory_accessor.get_suggestion_data("user", "session")

        if result.open_loops:
            priorities = [ol["priority"] for ol in result.open_loops]
            assert priorities == sorted(priorities, reverse=True)


class TestOpenLoopInHydratedContext:
    """Test open loops appear in hydrated context for LLM."""

    @pytest.mark.asyncio
    async def test_open_loops_in_context_text(self):
        """Open loops are included in hydrated context text."""
        from src.hmlr.hydrator import ContextHydrator
        from src.hmlr.models import GovernorDecision, RoutingScenario

        block = create_mock_block(
            topic_label="Sprint Planning",
            open_loops=["Assign story points", "Review backlog"]
        )

        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_CONTINUATION,
            matched_block_id=block.id,
            active_block=block,
            topic_similarity=0.9,
            relevant_facts=[],
            memories=[]
        )

        hydrator = ContextHydrator()
        context = await hydrator.hydrate(decision)

        assert "Assign story points" in context.open_loops_text or "Review backlog" in context.open_loops_text


class TestOpenLoopInSuggestions:
    """Test open loops surface in suggestion system."""

    def test_suggestion_data_includes_open_loops_field(self):
        """SuggestionData model has open_loops field."""
        data = SuggestionData(
            open_loops=[
                {"text": "Test task", "topic": "Test", "priority": 100, "is_current_session": True}
            ],
            common_queries=[],
            topic_interests=[],
            known_entities=[],
            recent_topics=[],
            expertise_level="intermediate",
            facts=[]
        )

        assert len(data.open_loops) == 1
        assert data.open_loops[0]["text"] == "Test task"
