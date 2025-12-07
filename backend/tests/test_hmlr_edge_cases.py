"""
HMLR Edge Case Tests (P0)

Tests for edge cases discovered during manual testing:
- Container initialization issues
- Data format mismatches
- Missing container handling
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from tests.conftest import create_test_block, create_test_profile, create_test_fact


class TestContainerInitialization:
    """Tests for lazy container initialization in BridgeBlockManager."""

    def test_lazy_container_initialization(self, mock_database):
        """Container should be lazily initialized on first access."""
        with patch('src.hmlr.bridge_block_mgr.db', mock_database):
            from src.hmlr.bridge_block_mgr import BridgeBlockManager

            manager = BridgeBlockManager()
            assert manager._container is None

            _ = manager.container

            mock_database.get_container.assert_called_once_with("bridge_blocks")
            assert manager._container is not None

    def test_container_reuse_after_init(self, mock_database):
        """Container should be reused after initialization."""
        with patch('src.hmlr.bridge_block_mgr.db', mock_database):
            from src.hmlr.bridge_block_mgr import BridgeBlockManager

            manager = BridgeBlockManager()

            container1 = manager.container
            container2 = manager.container

            mock_database.get_container.assert_called_once()
            assert container1 is container2

    def test_container_access_before_db_init_returns_none(self, mock_database):
        """Container access when db returns None should handle gracefully."""
        mock_database.get_container.return_value = None

        with patch('src.hmlr.bridge_block_mgr.db', mock_database):
            from src.hmlr.bridge_block_mgr import BridgeBlockManager

            manager = BridgeBlockManager()
            container = manager.container

            assert container is None


class TestOpenLoopDataFormat:
    """Tests for open_loops data format (must be strings, not dicts)."""

    def test_open_loops_as_strings(self):
        """Open loops should be stored as strings."""
        block = create_test_block(
            open_loops=["Pending task 1", "Pending task 2"]
        )

        assert isinstance(block["open_loops"], list)
        assert all(isinstance(loop, str) for loop in block["open_loops"])

    def test_open_loops_empty_list(self):
        """Empty open loops should be an empty list."""
        block = create_test_block(open_loops=[])

        assert block["open_loops"] == []

    def test_open_loops_with_special_characters(self):
        """Open loops should handle special characters."""
        special_loops = [
            "Task with 'quotes'",
            'Task with "double quotes"',
            "Task with emoji",
            "Task with <html> tags",
            "Task with & ampersand"
        ]
        block = create_test_block(open_loops=special_loops)

        assert block["open_loops"] == special_loops

    @pytest.mark.asyncio
    async def test_open_loops_format_in_memory_accessor(self):
        """Memory accessor should correctly process string open loops."""
        from src.hmlr.memory_accessor import HMLRMemoryAccessor

        mock_hmlr = MagicMock()
        mock_hmlr.get_user_profile = AsyncMock(return_value=MagicMock(
            common_queries=[],
            known_entities=[],
            interaction_patterns={},
            preferences={}
        ))
        mock_hmlr.get_user_facts = AsyncMock(return_value=[])

        mock_block = MagicMock()
        mock_block.id = "test-block"
        mock_block.session_id = "test-session"
        mock_block.topic_label = "Test Topic"
        mock_block.open_loops = ["String loop 1", "String loop 2"]
        mock_block.last_activity = datetime.now(timezone.utc)

        mock_hmlr.get_session_blocks = AsyncMock(return_value=[mock_block])
        mock_hmlr.block_manager = MagicMock()
        mock_hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            accessor = HMLRMemoryAccessor(mock_hmlr)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert len(data.open_loops) == 2
            for loop in data.open_loops:
                assert "text" in loop
                assert isinstance(loop["text"], str)


class TestMissingContainers:
    """Tests for handling missing containers."""

    def test_user_profiles_container_in_database_init(self):
        """user_profiles container should be defined in database init."""
        from src.database import Database

        db = Database.__new__(Database)
        db.client = MagicMock()
        db.database = None
        db.containers = {}

        mock_db = MagicMock()
        mock_container = MagicMock()
        mock_db.create_container_if_not_exists.return_value = mock_container
        db.client.create_database_if_not_exists.return_value = mock_db

        db.initialize()

        container_names = [call[1]['id'] for call in mock_db.create_container_if_not_exists.call_args_list]
        assert "user_profiles" in container_names

    def test_user_facts_container_in_database_init(self):
        """user_facts container should be defined in database init."""
        from src.database import Database

        db = Database.__new__(Database)
        db.client = MagicMock()
        db.database = None
        db.containers = {}

        mock_db = MagicMock()
        mock_container = MagicMock()
        mock_db.create_container_if_not_exists.return_value = mock_container
        db.client.create_database_if_not_exists.return_value = mock_db

        db.initialize()

        container_names = [call[1]['id'] for call in mock_db.create_container_if_not_exists.call_args_list]
        assert "user_facts" in container_names

    def test_bridge_blocks_container_in_database_init(self):
        """bridge_blocks container should be defined in database init."""
        from src.database import Database

        db = Database.__new__(Database)
        db.client = MagicMock()
        db.database = None
        db.containers = {}

        mock_db = MagicMock()
        mock_container = MagicMock()
        mock_db.create_container_if_not_exists.return_value = mock_container
        db.client.create_database_if_not_exists.return_value = mock_db

        db.initialize()

        container_names = [call[1]['id'] for call in mock_db.create_container_if_not_exists.call_args_list]
        assert "bridge_blocks" in container_names
