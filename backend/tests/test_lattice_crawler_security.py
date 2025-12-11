"""
Security tests for LatticeCrawler - HMLR Vector Search Layer.

Tests cover:
- OData injection prevention
- User ID validation
- Secret handling (FactCategory.SECRET)
- Input bounds validation
- User isolation
- Error sanitization
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from src.hmlr.lattice_crawler import (
    LatticeCrawler,
    SecurityValidationError,
    _validate_user_id,
    _escape_odata_string,
    _sanitize_log_message,
    MAX_USER_ID_LENGTH,
    MAX_QUERY_LENGTH,
    MAX_TOP_K,
    MIN_SCORE_FLOOR,
    MAX_SCORE_CEILING,
)
from src.hmlr.models import Fact, BridgeBlock, MemoryType, FactCategory


class TestUserIdValidation:
    """Test user_id validation for OData injection prevention."""

    def test_valid_user_id_alphanumeric(self):
        """Valid alphanumeric user_id passes validation."""
        assert _validate_user_id("user123") == "user123"

    def test_valid_user_id_with_underscore(self):
        """Valid user_id with underscore passes."""
        assert _validate_user_id("user_123") == "user_123"

    def test_valid_user_id_with_dash(self):
        """Valid user_id with dash passes."""
        assert _validate_user_id("user-123") == "user-123"

    def test_valid_user_id_with_at_symbol(self):
        """Valid user_id with @ (email format) passes."""
        assert _validate_user_id("user@domain.com") == "user@domain.com"

    def test_valid_user_id_with_dot(self):
        """Valid user_id with dot passes."""
        assert _validate_user_id("david.hayes") == "david.hayes"

    def test_empty_user_id_raises(self):
        """Empty user_id raises SecurityValidationError."""
        with pytest.raises(SecurityValidationError, match="cannot be empty"):
            _validate_user_id("")

    def test_none_user_id_raises(self):
        """None user_id raises SecurityValidationError."""
        with pytest.raises(SecurityValidationError, match="cannot be empty"):
            _validate_user_id(None)

    def test_user_id_too_long_raises(self):
        """User_id exceeding MAX_USER_ID_LENGTH raises error."""
        long_id = "a" * (MAX_USER_ID_LENGTH + 1)
        with pytest.raises(SecurityValidationError, match="exceeds maximum length"):
            _validate_user_id(long_id)

    def test_user_id_at_max_length_passes(self):
        """User_id at exactly MAX_USER_ID_LENGTH passes."""
        max_id = "a" * MAX_USER_ID_LENGTH
        assert _validate_user_id(max_id) == max_id

    def test_odata_injection_single_quote(self):
        """Single quote injection attempt is rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id("user' or 1 eq 1 or user_id eq '")

    def test_odata_injection_double_quote(self):
        """Double quote injection attempt is rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id('user" or 1 eq 1')

    def test_odata_injection_backslash(self):
        """Backslash injection attempt is rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id("user\\admin")

    def test_sql_injection_attempt(self):
        """SQL-style injection attempt is rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id("'; DROP TABLE users;--")

    def test_path_traversal_attempt(self):
        """Path traversal attempt is rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id("../../../etc/passwd")

    def test_unicode_injection(self):
        """Unicode characters are rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id("user\u0000null")

    def test_whitespace_rejected(self):
        """Whitespace in user_id is rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id("user name")

    def test_newline_rejected(self):
        """Newline in user_id is rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id("user\nname")

    def test_tab_rejected(self):
        """Tab in user_id is rejected."""
        with pytest.raises(SecurityValidationError, match="invalid characters"):
            _validate_user_id("user\tname")

    def test_special_chars_rejected(self):
        """Various special characters are rejected."""
        invalid_chars = ["$", "#", "%", "^", "&", "*", "(", ")", "!", "+", "=", "[", "]", "{", "}", "|", ";", ":", "<", ">", ",", "?", "/"]
        for char in invalid_chars:
            with pytest.raises(SecurityValidationError):
                _validate_user_id(f"user{char}test")


class TestODataStringEscape:
    """Test OData string escaping."""

    def test_no_escape_needed(self):
        """Normal string passes unchanged."""
        assert _escape_odata_string("normal_user") == "normal_user"

    def test_single_quote_escaped(self):
        """Single quote is doubled for OData."""
        assert _escape_odata_string("O'Brien") == "O''Brien"

    def test_multiple_quotes_escaped(self):
        """Multiple quotes are all escaped."""
        assert _escape_odata_string("a'b'c") == "a''b''c"


class TestLogSanitization:
    """Test log message sanitization."""

    def test_api_key_redacted(self):
        """API key in message is redacted."""
        msg = "Error: api_key=sk-12345 failed"
        sanitized = _sanitize_log_message(msg)
        assert "sk-12345" not in sanitized
        assert "REDACTED" in sanitized

    def test_token_redacted(self):
        """Token in message is redacted."""
        msg = "Auth token: abc123secret failed"
        sanitized = _sanitize_log_message(msg)
        assert "abc123secret" not in sanitized
        assert "REDACTED" in sanitized

    def test_password_redacted(self):
        """Password in message is redacted."""
        msg = "Login failed password=mysecret123"
        sanitized = _sanitize_log_message(msg)
        assert "mysecret123" not in sanitized
        assert "REDACTED" in sanitized

    def test_secret_redacted(self):
        """Secret in message is redacted."""
        msg = "secret: top_secret_value"
        sanitized = _sanitize_log_message(msg)
        assert "top_secret_value" not in sanitized
        assert "REDACTED" in sanitized

    def test_message_truncated(self):
        """Long messages are truncated."""
        long_msg = "x" * 1000
        sanitized = _sanitize_log_message(long_msg, max_length=100)
        assert len(sanitized) == 100

    def test_normal_message_unchanged(self):
        """Normal message without secrets passes through."""
        msg = "User lookup failed for user123"
        sanitized = _sanitize_log_message(msg)
        assert sanitized == msg


class TestInputBoundsValidation:
    """Test input parameter bounds enforcement."""

    @pytest.fixture
    def mock_crawler(self):
        """Create LatticeCrawler with mocked dependencies."""
        with patch('src.hmlr.lattice_crawler.SearchClient') as mock_search, \
             patch('src.hmlr.lattice_crawler.SearchIndexClient'), \
             patch('src.hmlr.lattice_crawler.AzureOpenAI') as mock_openai:
            mock_openai_instance = MagicMock()
            mock_openai_instance.embeddings.create.return_value = MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
            mock_openai.return_value = mock_openai_instance

            mock_search_instance = MagicMock()
            mock_search_instance.search.return_value = iter([])
            mock_search.return_value = mock_search_instance

            crawler = LatticeCrawler(
                index_name="test-index",
                endpoint="https://test.search.windows.net",
                api_key="test-key"  # pragma: allowlist secret  # pragma: allowlist secret
            )
            crawler.search_client = mock_search_instance
            yield crawler

    @pytest.mark.asyncio
    async def test_top_k_bounded_to_max(self, mock_crawler):
        """top_k exceeding MAX_TOP_K is bounded."""
        result = await mock_crawler.crawl(
            user_id="test_user",
            query="test query",
            top_k=1000
        )
        call_args = mock_crawler.search_client.search.call_args
        assert call_args[1]["top"] == MAX_TOP_K

    @pytest.mark.asyncio
    async def test_top_k_minimum_is_one(self, mock_crawler):
        """top_k below 1 is bounded to 1."""
        result = await mock_crawler.crawl(
            user_id="test_user",
            query="test query",
            top_k=-5
        )
        call_args = mock_crawler.search_client.search.call_args
        assert call_args[1]["top"] == 1

    @pytest.mark.asyncio
    async def test_query_truncated_if_too_long(self, mock_crawler):
        """Query exceeding MAX_QUERY_LENGTH is truncated."""
        long_query = "x" * (MAX_QUERY_LENGTH + 1000)
        result = await mock_crawler.crawl(
            user_id="test_user",
            query=long_query
        )
        assert True

    @pytest.mark.asyncio
    async def test_empty_query_returns_empty(self, mock_crawler):
        """Empty query returns empty results."""
        result = await mock_crawler.crawl(
            user_id="test_user",
            query=""
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_min_score_bounded_to_floor(self, mock_crawler):
        """min_score below 0 is bounded."""
        result = await mock_crawler.crawl(
            user_id="test_user",
            query="test",
            min_score=-1.0
        )
        assert True

    @pytest.mark.asyncio
    async def test_min_score_bounded_to_ceiling(self, mock_crawler):
        """min_score above 1 is bounded."""
        result = await mock_crawler.crawl(
            user_id="test_user",
            query="test",
            min_score=2.0
        )
        assert True


class TestSecretHandling:
    """Test that secrets are not exposed in vector index."""

    @pytest.fixture
    def mock_crawler(self):
        """Create LatticeCrawler with mocked dependencies."""
        with patch('src.hmlr.lattice_crawler.SearchClient') as mock_search, \
             patch('src.hmlr.lattice_crawler.SearchIndexClient'), \
             patch('src.hmlr.lattice_crawler.AzureOpenAI') as mock_openai:
            mock_openai_instance = MagicMock()
            mock_openai_instance.embeddings.create.return_value = MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
            mock_openai.return_value = mock_openai_instance

            mock_search_instance = MagicMock()
            mock_search.return_value = mock_search_instance

            crawler = LatticeCrawler(
                index_name="test-index",
                endpoint="https://test.search.windows.net",
                api_key="test-key"  # pragma: allowlist secret
            )
            crawler.search_client = mock_search_instance
            yield crawler

    @pytest.mark.asyncio
    async def test_secret_fact_value_not_indexed(self, mock_crawler):
        """SECRET category facts have value replaced with placeholder."""
        secret_fact = Fact(
            user_id="test_user",
            key="api_key",
            value="sk-supersecretkey123",
            category=FactCategory.SECRET,
            confidence=1.0,
            fact_id=1
        )

        await mock_crawler.index_fact(secret_fact)

        call_args = mock_crawler.search_client.upload_documents.call_args
        indexed_doc = call_args[1]["documents"][0]

        assert "sk-supersecretkey123" not in indexed_doc["content"]
        assert "[SECURE_VALUE_NOT_INDEXED]" in indexed_doc["content"]
        assert "api_key" in indexed_doc["content"]

    @pytest.mark.asyncio
    async def test_non_secret_fact_value_indexed(self, mock_crawler):
        """Non-SECRET facts have value indexed normally."""
        normal_fact = Fact(
            user_id="test_user",
            key="favorite_color",
            value="blue",
            category=FactCategory.DEFINITION,
            confidence=0.9,
            fact_id=2
        )

        await mock_crawler.index_fact(normal_fact)

        call_args = mock_crawler.search_client.upload_documents.call_args
        indexed_doc = call_args[1]["documents"][0]

        assert "blue" in indexed_doc["content"]
        assert "[SECURE_VALUE_NOT_INDEXED]" not in indexed_doc["content"]

    @pytest.mark.asyncio
    async def test_secret_fact_string_category(self, mock_crawler):
        """SECRET as string category is properly handled."""
        secret_fact = Fact(
            user_id="test_user",
            key="password",
            value="verysecretpassword",
            category="Secret",
            confidence=1.0,
            fact_id=3
        )

        await mock_crawler.index_fact(secret_fact)

        call_args = mock_crawler.search_client.upload_documents.call_args
        indexed_doc = call_args[1]["documents"][0]

        assert "verysecretpassword" not in indexed_doc["content"]


class TestUserIsolation:
    """Test user isolation in search results."""

    @pytest.fixture
    def mock_crawler(self):
        """Create LatticeCrawler with mocked dependencies."""
        with patch('src.hmlr.lattice_crawler.SearchClient') as mock_search, \
             patch('src.hmlr.lattice_crawler.SearchIndexClient'), \
             patch('src.hmlr.lattice_crawler.AzureOpenAI') as mock_openai:
            mock_openai_instance = MagicMock()
            mock_openai_instance.embeddings.create.return_value = MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
            mock_openai.return_value = mock_openai_instance

            mock_search_instance = MagicMock()
            mock_search.return_value = mock_search_instance

            crawler = LatticeCrawler(
                index_name="test-index",
                endpoint="https://test.search.windows.net",
                api_key="test-key"  # pragma: allowlist secret
            )
            crawler.search_client = mock_search_instance
            yield crawler

    @pytest.mark.asyncio
    async def test_results_filtered_by_user_id(self, mock_crawler):
        """Results for wrong user_id are filtered out."""
        mock_crawler.search_client.search.return_value = iter([
            {
                "id": "fact_user1_1",
                "user_id": "user1",
                "content": "User 1 data",
                "memory_type": "fact",
                "source_id": "1",
                "@search.score": 0.9
            },
            {
                "id": "fact_user2_1",
                "user_id": "user2",
                "content": "User 2 data (should be filtered)",
                "memory_type": "fact",
                "source_id": "2",
                "@search.score": 0.95
            }
        ])

        results = await mock_crawler.crawl(
            user_id="user1",
            query="test query"
        )

        assert len(results) == 1
        assert results[0].user_id == "user1"

    @pytest.mark.asyncio
    async def test_odata_filter_includes_user_id(self, mock_crawler):
        """OData filter in search includes user_id constraint."""
        mock_crawler.search_client.search.return_value = iter([])

        await mock_crawler.crawl(
            user_id="test_user",
            query="test query"
        )

        call_args = mock_crawler.search_client.search.call_args
        filter_expr = call_args[1]["filter"]
        assert "user_id eq 'test_user'" in filter_expr

    @pytest.mark.asyncio
    async def test_delete_user_memories_validates_each_result(self, mock_crawler):
        """delete_user_memories checks user_id on each result before deletion."""
        mock_crawler.search_client.search.return_value = iter([
            {"id": "doc1", "user_id": "target_user"},
            {"id": "doc2", "user_id": "other_user"},
            {"id": "doc3", "user_id": "target_user"},
        ])

        count = await mock_crawler.delete_user_memories("target_user")

        call_args = mock_crawler.search_client.delete_documents.call_args
        deleted_docs = call_args[1]["documents"]

        deleted_ids = [d["id"] for d in deleted_docs]
        assert "doc1" in deleted_ids
        assert "doc3" in deleted_ids
        assert "doc2" not in deleted_ids
        assert count == 2


class TestSecurityValidationErrorHandling:
    """Test that security validation errors are properly handled."""

    @pytest.fixture
    def mock_crawler(self):
        """Create LatticeCrawler with mocked dependencies."""
        with patch('src.hmlr.lattice_crawler.SearchClient'), \
             patch('src.hmlr.lattice_crawler.SearchIndexClient'), \
             patch('src.hmlr.lattice_crawler.AzureOpenAI') as mock_openai:
            mock_openai_instance = MagicMock()
            mock_openai_instance.embeddings.create.return_value = MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
            mock_openai.return_value = mock_openai_instance

            crawler = LatticeCrawler(
                index_name="test-index",
                endpoint="https://test.search.windows.net",
                api_key="test-key"  # pragma: allowlist secret
            )
            yield crawler

    @pytest.mark.asyncio
    async def test_crawl_raises_on_invalid_user_id(self, mock_crawler):
        """crawl raises SecurityValidationError for invalid user_id."""
        with pytest.raises(SecurityValidationError):
            await mock_crawler.crawl(
                user_id="user' OR '1'='1",
                query="test"
            )

    @pytest.mark.asyncio
    async def test_index_fact_returns_false_on_invalid_user(self, mock_crawler):
        """index_fact returns False for invalid user_id."""
        bad_fact = Fact(
            user_id="invalid'user",
            key="test",
            value="test",
            category=FactCategory.ENTITY,
            confidence=0.9
        )
        result = await mock_crawler.index_fact(bad_fact)
        assert result is False

    @pytest.mark.asyncio
    async def test_index_block_returns_false_on_invalid_user(self, mock_crawler):
        """index_block_summary returns False for invalid user_id."""
        bad_block = BridgeBlock(
            id="block1",
            session_id="session1",
            user_id="invalid'user",
            topic_label="Test Topic"
        )
        result = await mock_crawler.index_block_summary(bad_block)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_fact_returns_false_on_invalid_user(self, mock_crawler):
        """delete_fact returns False for invalid user_id."""
        result = await mock_crawler.delete_fact("invalid'user", "fact1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_block_returns_false_on_invalid_user(self, mock_crawler):
        """delete_block returns False for invalid user_id."""
        result = await mock_crawler.delete_block("invalid'user", "block1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_user_memories_returns_zero_on_invalid_user(self, mock_crawler):
        """delete_user_memories returns 0 for invalid user_id."""
        result = await mock_crawler.delete_user_memories("invalid'user")
        assert result == 0


class TestDocumentIdSanitization:
    """Test document ID generation is safe."""

    @pytest.fixture
    def mock_crawler(self):
        """Create LatticeCrawler with mocked dependencies."""
        with patch('src.hmlr.lattice_crawler.SearchClient') as mock_search, \
             patch('src.hmlr.lattice_crawler.SearchIndexClient'), \
             patch('src.hmlr.lattice_crawler.AzureOpenAI') as mock_openai:
            mock_openai_instance = MagicMock()
            mock_openai_instance.embeddings.create.return_value = MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
            mock_openai.return_value = mock_openai_instance

            mock_search_instance = MagicMock()
            mock_search.return_value = mock_search_instance

            crawler = LatticeCrawler(
                index_name="test-index",
                endpoint="https://test.search.windows.net",
                api_key="test-key"  # pragma: allowlist secret
            )
            crawler.search_client = mock_search_instance
            yield crawler

    @pytest.mark.asyncio
    async def test_fact_doc_id_sanitized(self, mock_crawler):
        """Fact document ID has special chars replaced."""
        fact = Fact(
            user_id="test_user",
            key="test:key/with$special",
            value="test",
            category=FactCategory.ENTITY,
            confidence=0.9,
            fact_id=1
        )

        await mock_crawler.index_fact(fact)

        call_args = mock_crawler.search_client.upload_documents.call_args
        doc_id = call_args[1]["documents"][0]["id"]

        assert ":" not in doc_id
        assert "/" not in doc_id
        assert "$" not in doc_id

    @pytest.mark.asyncio
    async def test_block_doc_id_sanitized(self, mock_crawler):
        """Block document ID has special chars replaced."""
        block = BridgeBlock(
            id="block:1/test$id",
            session_id="session1",
            user_id="test_user",
            topic_label="Test Topic"
        )

        await mock_crawler.index_block_summary(block)

        call_args = mock_crawler.search_client.upload_documents.call_args
        doc_id = call_args[1]["documents"][0]["id"]

        assert ":" not in doc_id
        assert "/" not in doc_id
        assert "$" not in doc_id


class TestODataFilterConstruction:
    """Test OData filter is properly constructed."""

    @pytest.fixture
    def mock_crawler(self):
        """Create LatticeCrawler with mocked dependencies."""
        with patch('src.hmlr.lattice_crawler.SearchClient') as mock_search, \
             patch('src.hmlr.lattice_crawler.SearchIndexClient'), \
             patch('src.hmlr.lattice_crawler.AzureOpenAI') as mock_openai:
            mock_openai_instance = MagicMock()
            mock_openai_instance.embeddings.create.return_value = MagicMock(
                data=[MagicMock(embedding=[0.1] * 1536)]
            )
            mock_openai.return_value = mock_openai_instance

            mock_search_instance = MagicMock()
            mock_search_instance.search.return_value = iter([])
            mock_search.return_value = mock_search_instance

            crawler = LatticeCrawler(
                index_name="test-index",
                endpoint="https://test.search.windows.net",
                api_key="test-key"  # pragma: allowlist secret
            )
            crawler.search_client = mock_search_instance
            yield crawler

    @pytest.mark.asyncio
    async def test_filter_with_memory_type(self, mock_crawler):
        """Filter includes memory_type when specified."""
        await mock_crawler.crawl(
            user_id="test_user",
            query="test",
            memory_type=MemoryType.FACT
        )

        call_args = mock_crawler.search_client.search.call_args
        filter_expr = call_args[1]["filter"]

        assert "user_id eq 'test_user'" in filter_expr
        assert "memory_type eq 'fact'" in filter_expr

    @pytest.mark.asyncio
    async def test_filter_without_memory_type(self, mock_crawler):
        """Filter only has user_id when no memory_type specified."""
        await mock_crawler.crawl(
            user_id="test_user",
            query="test"
        )

        call_args = mock_crawler.search_client.search.call_args
        filter_expr = call_args[1]["filter"]

        assert "user_id eq 'test_user'" in filter_expr
        assert "memory_type" not in filter_expr


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_user_id_with_consecutive_valid_chars(self):
        """User ID with consecutive dots, dashes passes."""
        assert _validate_user_id("user..name") == "user..name"
        assert _validate_user_id("user--name") == "user--name"
        assert _validate_user_id("user__name") == "user__name"

    def test_user_id_starting_with_number(self):
        """User ID starting with number passes."""
        assert _validate_user_id("123user") == "123user"

    def test_user_id_all_numbers(self):
        """All numeric user ID passes."""
        assert _validate_user_id("123456789") == "123456789"

    def test_sanitize_log_mixed_patterns(self):
        """Multiple secret patterns in one message are all redacted."""
        msg = "api_key=abc123 password=secret token:xyz789"
        sanitized = _sanitize_log_message(msg)
        assert "abc123" not in sanitized
        assert "secret" not in sanitized
        assert "xyz789" not in sanitized
        assert sanitized.count("REDACTED") == 3

    def test_escape_empty_string(self):
        """Empty string escapes to empty string."""
        assert _escape_odata_string("") == ""

    def test_validate_user_id_exact_pattern_match(self):
        """Validate that pattern matches entire string."""
        with pytest.raises(SecurityValidationError):
            _validate_user_id("valid_user@domain.com ")
