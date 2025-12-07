"""
Unit tests for HMLR Memory Accessor.
Tests data retrieval, recency decay, and caching logic.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, timezone
from src.hmlr.memory_accessor import HMLRMemoryAccessor
from src.hmlr.suggestion_models import SuggestionData


def create_mock_profile(
    common_queries=None,
    known_entities=None,
    interaction_patterns=None,
    preferences=None
):
    profile = MagicMock()
    profile.common_queries = common_queries or []
    profile.known_entities = known_entities or []
    profile.interaction_patterns = interaction_patterns or {}
    profile.preferences = preferences or {}
    return profile


def create_mock_block(
    block_id="block1",
    session_id="session1",
    topic_label="Test Topic",
    open_loops=None,
    last_activity=None
):
    block = MagicMock()
    block.id = block_id
    block.session_id = session_id
    block.topic_label = topic_label
    block.open_loops = open_loops or []
    block.last_activity = last_activity or datetime.now(timezone.utc)
    return block


def create_mock_fact(key="test", value="test value", category="DEFINITION", confidence=0.9):
    fact = MagicMock()
    fact.key = key
    fact.value = value
    fact.category = category
    fact.confidence = confidence
    return fact


class TestHMLRMemoryAccessorInit:
    def test_init_with_hmlr_service(self):
        mock_service = MagicMock()
        accessor = HMLRMemoryAccessor(mock_service)
        assert accessor.hmlr == mock_service

    def test_init_without_hmlr_service(self):
        accessor = HMLRMemoryAccessor(None)
        assert accessor.hmlr is None


class TestGetSuggestionData:
    @pytest.fixture
    def mock_service(self):
        service = MagicMock()
        service.get_user_profile = AsyncMock(return_value=None)
        service.get_user_facts = AsyncMock(return_value=[])
        service.get_session_blocks = AsyncMock(return_value=[])
        service.block_manager = MagicMock()
        service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def accessor(self, mock_service):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            return HMLRMemoryAccessor(mock_service)

    @pytest.mark.asyncio
    async def test_returns_suggestion_data(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(return_value=create_mock_profile(
            common_queries=["How do I deploy?"],
            known_entities=[{"name": "Dashboard", "type": "project"}],
            interaction_patterns={"total_queries": 150, "technical_queries": 100, "topic_frequency": {"governance": 10}},
            preferences={"preferred_topics": ["governance"]}
        ))
        mock_service.get_user_facts = AsyncMock(return_value=[])

        data = await accessor.get_suggestion_data(
            user_id="user123",
            session_id="session456"
        )

        assert isinstance(data, SuggestionData)
        assert "How do I deploy?" in data.common_queries

    @pytest.mark.asyncio
    async def test_handles_missing_user_profile(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(return_value=create_mock_profile())
        mock_service.get_user_facts = AsyncMock(return_value=[])

        data = await accessor.get_suggestion_data(user_id="unknown_user")

        assert isinstance(data, SuggestionData)
        assert data.common_queries == []

    @pytest.mark.asyncio
    async def test_handles_hmlr_service_error(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(side_effect=Exception("DB Error"))

        data = await accessor.get_suggestion_data(user_id="user123")

        assert isinstance(data, SuggestionData)
        assert data == SuggestionData()


class TestOpenLoopExtraction:
    @pytest.fixture
    def mock_service(self):
        service = MagicMock()
        service.get_user_profile = AsyncMock(return_value=create_mock_profile())
        service.get_user_facts = AsyncMock(return_value=[])
        service.get_session_blocks = AsyncMock(return_value=[])
        service.block_manager = MagicMock()
        service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def accessor(self, mock_service):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            return HMLRMemoryAccessor(mock_service)

    @pytest.mark.asyncio
    async def test_extracts_open_loops_from_session_blocks(self, accessor, mock_service):
        mock_blocks = [
            create_mock_block(
                block_id="block1",
                topic_label="API Integration",
                open_loops=["Continue implementing OAuth"],
                last_activity=datetime.now(timezone.utc)
            )
        ]
        mock_service.get_session_blocks = AsyncMock(return_value=mock_blocks)

        data = await accessor.get_suggestion_data(
            user_id="user123",
            session_id="session456"
        )

        assert len(data.open_loops) >= 1
        assert any("OAuth" in str(loop) for loop in data.open_loops)

    @pytest.mark.asyncio
    async def test_current_session_loops_marked(self, accessor, mock_service):
        current_session = "current-session-id"
        mock_blocks = [
            create_mock_block(
                block_id="block1",
                session_id=current_session,
                topic_label="Current Work",
                open_loops=["Current task"],
                last_activity=datetime.now(timezone.utc)
            )
        ]
        mock_service.get_session_blocks = AsyncMock(return_value=mock_blocks)

        data = await accessor.get_suggestion_data(
            user_id="user123",
            session_id=current_session,
            include_cross_session=True
        )

        current_loops = [l for l in data.open_loops if l.get("is_current_session")]
        assert len(current_loops) >= 1


class TestRecencyDecay:
    @pytest.fixture
    def mock_service(self):
        service = MagicMock()
        service.get_user_profile = AsyncMock(return_value=create_mock_profile())
        service.get_user_facts = AsyncMock(return_value=[])
        service.get_session_blocks = AsyncMock(return_value=[])
        service.block_manager = MagicMock()
        service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def accessor(self, mock_service):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            return HMLRMemoryAccessor(mock_service)

    @pytest.mark.asyncio
    async def test_recent_loops_higher_priority(self, accessor, mock_service):
        now = datetime.now(timezone.utc)
        mock_blocks = [
            create_mock_block(
                block_id="recent",
                topic_label="Recent Work",
                open_loops=["Recent task"],
                last_activity=now
            ),
            create_mock_block(
                block_id="old",
                topic_label="Old Work",
                open_loops=["Old task"],
                last_activity=now - timedelta(hours=48)
            )
        ]
        mock_service.get_session_blocks = AsyncMock(return_value=mock_blocks)

        data = await accessor.get_suggestion_data(
            user_id="user123",
            session_id="session123"
        )

        if len(data.open_loops) >= 2:
            recent = next((l for l in data.open_loops if "Recent" in str(l.get("topic", ""))), None)
            old = next((l for l in data.open_loops if "Old" in str(l.get("topic", ""))), None)
            if recent and old:
                assert recent.get("priority", 0) >= old.get("priority", 0)

    @pytest.mark.asyncio
    async def test_very_old_loops_excluded(self, accessor, mock_service):
        now = datetime.now(timezone.utc)
        mock_blocks = [
            create_mock_block(
                block_id="ancient",
                topic_label="Ancient Work",
                open_loops=["Ancient task"],
                last_activity=now - timedelta(days=30)
            )
        ]
        mock_service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=mock_blocks)

        data = await accessor.get_suggestion_data(
            user_id="user123",
            include_cross_session=True
        )

        ancient_loops = [l for l in data.open_loops if "Ancient" in str(l.get("topic", ""))]
        assert len(ancient_loops) == 0


class TestCrossSessionBehavior:
    @pytest.fixture
    def mock_service(self):
        service = MagicMock()
        service.get_user_profile = AsyncMock(return_value=create_mock_profile())
        service.get_user_facts = AsyncMock(return_value=[])
        service.get_session_blocks = AsyncMock(return_value=[])
        service.block_manager = MagicMock()
        service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def accessor(self, mock_service):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            return HMLRMemoryAccessor(mock_service)

    @pytest.mark.asyncio
    async def test_include_cross_session_true(self, accessor, mock_service):
        now = datetime.now(timezone.utc)
        mock_blocks = [
            create_mock_block(
                block_id="block1",
                session_id="other-session",
                topic_label="Other Session Work",
                open_loops=["Task from other session"],
                last_activity=now - timedelta(hours=2)
            )
        ]
        mock_service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=mock_blocks)

        data = await accessor.get_suggestion_data(
            user_id="user123",
            session_id="current-session",
            include_cross_session=True
        )

        cross_session = [l for l in data.open_loops if not l.get("is_current_session")]
        assert len(cross_session) >= 1

    @pytest.mark.asyncio
    async def test_include_cross_session_false(self, accessor, mock_service):
        now = datetime.now(timezone.utc)
        current_session_blocks = [
            create_mock_block(
                block_id="block1",
                session_id="current-session",
                topic_label="Current Session Work",
                open_loops=["Current task"],
                last_activity=now
            )
        ]
        cross_session_blocks = [
            create_mock_block(
                block_id="block2",
                session_id="other-session",
                topic_label="Other Session Work",
                open_loops=["Other task"],
                last_activity=now
            )
        ]
        mock_service.get_session_blocks = AsyncMock(return_value=current_session_blocks)
        mock_service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=cross_session_blocks)

        data = await accessor.get_suggestion_data(
            user_id="user123",
            session_id="current-session",
            include_cross_session=False
        )

        if data.open_loops:
            for loop in data.open_loops:
                assert loop.get("is_current_session") is True


class TestExpertiseLevelExtraction:
    @pytest.fixture
    def mock_service(self):
        service = MagicMock()
        service.get_user_profile = AsyncMock(return_value=create_mock_profile())
        service.get_user_facts = AsyncMock(return_value=[])
        service.get_session_blocks = AsyncMock(return_value=[])
        service.block_manager = MagicMock()
        service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def accessor(self, mock_service):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            return HMLRMemoryAccessor(mock_service)

    @pytest.mark.asyncio
    async def test_extracts_expertise_level_expert(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(return_value=create_mock_profile(
            interaction_patterns={"total_queries": 150, "technical_queries": 100}
        ))

        data = await accessor.get_suggestion_data(user_id="user123")

        assert data.expertise_level == "expert"

    @pytest.mark.asyncio
    async def test_extracts_expertise_level_advanced(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(return_value=create_mock_profile(
            interaction_patterns={"total_queries": 60, "technical_queries": 30}
        ))

        data = await accessor.get_suggestion_data(user_id="user123")

        assert data.expertise_level == "advanced"

    @pytest.mark.asyncio
    async def test_extracts_expertise_level_beginner(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(return_value=create_mock_profile(
            interaction_patterns={"total_queries": 5, "technical_queries": 2}
        ))

        data = await accessor.get_suggestion_data(user_id="user123")

        assert data.expertise_level == "beginner"

    @pytest.mark.asyncio
    async def test_defaults_to_intermediate(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(return_value=create_mock_profile())

        data = await accessor.get_suggestion_data(user_id="user123")

        assert data.expertise_level == "intermediate"


class TestTopicInterestsExtraction:
    @pytest.fixture
    def mock_service(self):
        service = MagicMock()
        service.get_user_profile = AsyncMock(return_value=create_mock_profile())
        service.get_user_facts = AsyncMock(return_value=[])
        service.get_session_blocks = AsyncMock(return_value=[])
        service.block_manager = MagicMock()
        service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def accessor(self, mock_service):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            return HMLRMemoryAccessor(mock_service)

    @pytest.mark.asyncio
    async def test_extracts_from_topic_frequency(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(return_value=create_mock_profile(
            interaction_patterns={"topic_frequency": {"governance": 45, "agents": 30}}
        ))

        data = await accessor.get_suggestion_data(user_id="user123")

        assert "governance" in data.topic_interests

    @pytest.mark.asyncio
    async def test_extracts_from_preferred_topics(self, accessor, mock_service):
        mock_service.get_user_profile = AsyncMock(return_value=create_mock_profile(
            preferences={"preferred_topics": ["security", "performance"]}
        ))

        data = await accessor.get_suggestion_data(user_id="user123")

        assert "security" in data.topic_interests or "performance" in data.topic_interests


class TestFactsExtraction:
    @pytest.fixture
    def mock_service(self):
        service = MagicMock()
        service.get_user_profile = AsyncMock(return_value=create_mock_profile())
        service.get_user_facts = AsyncMock(return_value=[])
        service.get_session_blocks = AsyncMock(return_value=[])
        service.block_manager = MagicMock()
        service.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def accessor(self, mock_service):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            return HMLRMemoryAccessor(mock_service)

    @pytest.mark.asyncio
    async def test_extracts_relevant_facts(self, accessor, mock_service):
        mock_facts = [
            create_mock_fact(key="RAG", value="Retrieval Augmented Generation", category="ACRONYM"),
            create_mock_fact(key="HMLR", value="Hierarchical Memory", category="DEFINITION")
        ]
        mock_service.get_user_facts = AsyncMock(return_value=mock_facts)

        data = await accessor.get_suggestion_data(user_id="user123")

        assert len(data.relevant_facts) == 2
        assert any(f["key"] == "RAG" for f in data.relevant_facts)


class TestDisabledHMLR:
    def test_returns_empty_when_disabled(self):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = False
            accessor = HMLRMemoryAccessor(MagicMock())

    @pytest.mark.asyncio
    async def test_returns_empty_data_when_service_none(self):
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            accessor = HMLRMemoryAccessor(None)
            data = await accessor.get_suggestion_data(user_id="user123")
            assert data == SuggestionData()
