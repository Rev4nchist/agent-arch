"""
HMLR Error Handling Tests (P2)

Tests for graceful error handling:
- Feature flag behavior
- Connection failures
- Data validation
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from src.hmlr.memory_accessor import HMLRMemoryAccessor
from src.hmlr.suggestion_models import SuggestionData


class TestFeatureFlags:
    """Tests for HMLR feature flag behavior."""

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
    async def test_hmlr_disabled_returns_empty_data(self, mock_hmlr_service):
        """When HMLR is disabled, should return empty suggestion data."""
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = False

            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)
            assert len(data.open_loops) == 0
            assert len(data.common_queries) == 0

    @pytest.mark.asyncio
    async def test_fact_extraction_disabled_skips_extraction(self, mock_hmlr_service):
        """When fact extraction is disabled, should skip fact extraction."""
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            mock_settings.hmlr_fact_extraction_enabled = False

            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)

    @pytest.mark.asyncio
    async def test_profile_updates_disabled_returns_data(self, mock_hmlr_service):
        """When profile updates disabled, should still return data."""
        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True
            mock_settings.hmlr_profile_update_enabled = False

            accessor = HMLRMemoryAccessor(mock_hmlr_service)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)


class TestConnectionFailures:
    """Tests for graceful handling of connection failures."""

    @pytest.mark.asyncio
    async def test_cosmos_connection_failure_graceful(self):
        """Cosmos connection failure should return empty data, not crash."""
        mock_hmlr = MagicMock()
        mock_hmlr.get_user_profile = AsyncMock(side_effect=Exception("Connection refused"))
        mock_hmlr.get_user_facts = AsyncMock(return_value=[])
        mock_hmlr.get_session_blocks = AsyncMock(return_value=[])
        mock_hmlr.block_manager = MagicMock()
        mock_hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            accessor = HMLRMemoryAccessor(mock_hmlr)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)

    @pytest.mark.asyncio
    async def test_sql_connection_failure_graceful(self):
        """SQL connection failure should return empty data, not crash."""
        mock_hmlr = MagicMock()
        mock_hmlr.get_user_profile = AsyncMock(return_value=MagicMock(
            common_queries=[],
            known_entities=[],
            interaction_patterns={},
            preferences={}
        ))
        mock_hmlr.get_user_facts = AsyncMock(side_effect=Exception("SQL connection failed"))
        mock_hmlr.get_session_blocks = AsyncMock(return_value=[])
        mock_hmlr.block_manager = MagicMock()
        mock_hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            accessor = HMLRMemoryAccessor(mock_hmlr)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)

    @pytest.mark.asyncio
    async def test_block_manager_failure_graceful(self):
        """Block manager failure should return empty data, not crash."""
        mock_hmlr = MagicMock()
        mock_hmlr.get_user_profile = AsyncMock(return_value=MagicMock(
            common_queries=[],
            known_entities=[],
            interaction_patterns={},
            preferences={}
        ))
        mock_hmlr.get_user_facts = AsyncMock(return_value=[])
        mock_hmlr.get_session_blocks = AsyncMock(side_effect=Exception("Block manager error"))
        mock_hmlr.block_manager = MagicMock()
        mock_hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            accessor = HMLRMemoryAccessor(mock_hmlr)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)


class TestDataValidation:
    """Tests for data validation and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_profile_data_handled(self):
        """Invalid profile data should be handled gracefully."""
        mock_hmlr = MagicMock()
        mock_hmlr.get_user_profile = AsyncMock(return_value=None)
        mock_hmlr.get_user_facts = AsyncMock(return_value=[])
        mock_hmlr.get_session_blocks = AsyncMock(return_value=[])
        mock_hmlr.block_manager = MagicMock()
        mock_hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            accessor = HMLRMemoryAccessor(mock_hmlr)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)

    @pytest.mark.asyncio
    async def test_empty_query_handling(self):
        """Empty query should not crash governor routing."""
        from src.hmlr.governor import Governor

        mock_block_manager = MagicMock()
        mock_block_manager.get_session_blocks = AsyncMock(return_value=[])
        mock_sql_client = MagicMock()
        mock_sql_client.search_facts = AsyncMock(return_value=[])

        governor = Governor(mock_block_manager, mock_sql_client)

        decision = await governor.route(
            user_id="test-user",
            session_id="test-session",
            query=""
        )

        assert decision is not None
        assert decision.is_new_topic is True

    @pytest.mark.asyncio
    async def test_very_long_query_2000_chars(self):
        """Very long query (2000+ chars) should be handled."""
        from src.hmlr.governor import Governor

        mock_block_manager = MagicMock()
        mock_block_manager.get_session_blocks = AsyncMock(return_value=[])
        mock_sql_client = MagicMock()
        mock_sql_client.search_facts = AsyncMock(return_value=[])

        governor = Governor(mock_block_manager, mock_sql_client)

        long_query = "What is the status of " + "a" * 2000

        decision = await governor.route(
            user_id="test-user",
            session_id="test-session",
            query=long_query
        )

        assert decision is not None


class TestNullSafetyHandling:
    """Tests for null/None safety in HMLR components."""

    @pytest.mark.asyncio
    async def test_null_user_id_handled(self):
        """Null user_id should be handled gracefully."""
        mock_hmlr = MagicMock()
        mock_hmlr.get_user_profile = AsyncMock(return_value=None)
        mock_hmlr.get_user_facts = AsyncMock(return_value=[])
        mock_hmlr.get_session_blocks = AsyncMock(return_value=[])
        mock_hmlr.block_manager = MagicMock()
        mock_hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            accessor = HMLRMemoryAccessor(mock_hmlr)

            data = await accessor.get_suggestion_data(
                user_id=None,
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)

    @pytest.mark.asyncio
    async def test_null_session_blocks_handled(self):
        """Null session blocks should be handled gracefully."""
        mock_hmlr = MagicMock()
        mock_hmlr.get_user_profile = AsyncMock(return_value=MagicMock(
            common_queries=[],
            known_entities=[],
            interaction_patterns={},
            preferences={}
        ))
        mock_hmlr.get_user_facts = AsyncMock(return_value=[])
        mock_hmlr.get_session_blocks = AsyncMock(return_value=None)
        mock_hmlr.block_manager = MagicMock()
        mock_hmlr.block_manager.get_user_blocks_with_open_loops = AsyncMock(return_value=[])

        with patch('src.hmlr.memory_accessor.settings') as mock_settings:
            mock_settings.hmlr_enabled = True

            accessor = HMLRMemoryAccessor(mock_hmlr)

            data = await accessor.get_suggestion_data(
                user_id="test-user",
                session_id="test-session"
            )

            assert isinstance(data, SuggestionData)
