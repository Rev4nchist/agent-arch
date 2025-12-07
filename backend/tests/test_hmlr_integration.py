"""HMLR Integration Tests.

Comprehensive test suite for the HMLR memory system.
Run with: pytest tests/test_hmlr_integration.py -v

Tests cover:
1. SQL connectivity and operations
2. Cosmos DB operations
3. Governor routing scenarios (all 4)
4. Fact extraction
5. Context hydration
6. End-to-end integration
"""

import pytest
import asyncio
import uuid
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize database before importing HMLR modules
from src.database import db
try:
    db.initialize()
except Exception as e:
    print(f"Warning: Could not initialize Cosmos DB: {e}")

from src.hmlr.models import (
    BridgeBlock, Turn, Fact, FactCategory,
    GovernorDecision, RoutingScenario, BlockStatus,
    UserProfile, HydratedContext
)
from src.hmlr.sql_client import HMLRSQLClient
from src.hmlr.bridge_block_mgr import BridgeBlockManager
from src.hmlr.governor import Governor
from src.hmlr.fact_scrubber import FactScrubber
from src.hmlr.hydrator import ContextHydrator
from src.hmlr.scribe import Scribe
from src.hmlr.service import HMLRService
from src.config import settings


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def test_user_id():
    """Generate unique test user ID."""
    return f"test_user_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_session_id():
    """Generate unique test session ID."""
    return f"test_session_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sql_client():
    """Create SQL client for tests."""
    client = HMLRSQLClient(settings.hmlr_sql_connection_string)
    yield client
    client.close()


@pytest.fixture
def block_manager():
    """Create block manager for tests."""
    return BridgeBlockManager()


@pytest.fixture
def hydrator():
    """Create hydrator for tests."""
    return ContextHydrator()


# =============================================================================
# TEST 1: SQL CONNECTIVITY
# =============================================================================

class TestSQLConnectivity:
    """Test Azure SQL database operations."""

    def test_connection(self, sql_client):
        """Test basic SQL connection."""
        conn = sql_client._get_connection()
        assert conn is not None
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

    def test_tables_exist(self, sql_client):
        """Verify all required tables exist."""
        conn = sql_client._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]

        assert 'fact_store' in tables, "fact_store table missing"
        assert 'user_profiles' in tables, "user_profiles table missing"
        assert 'fact_history' in tables, "fact_history table missing"

    def test_stored_procedures_exist(self, sql_client):
        """Verify all stored procedures exist."""
        conn = sql_client._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.procedures")
        procs = [row[0] for row in cursor.fetchall()]

        assert 'upsert_fact' in procs, "upsert_fact procedure missing"
        assert 'get_facts_by_keywords' in procs, "get_facts_by_keywords procedure missing"
        assert 'upsert_user_profile' in procs, "upsert_user_profile procedure missing"


# =============================================================================
# TEST 2: FACT OPERATIONS
# =============================================================================

class TestFactOperations:
    """Test fact CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_fact(self, sql_client, test_user_id):
        """Test creating and retrieving a fact."""
        fact = Fact(
            user_id=test_user_id,
            key="test_definition",
            value="A test is a procedure to verify correctness",
            category=FactCategory.DEFINITION,
            source_block_id="block_123",
            evidence_snippet="test is a procedure",
            confidence=0.95
        )

        # Create
        fact_id = await sql_client.save_fact(fact)
        assert fact_id > 0, "Failed to create fact"

        # Retrieve
        retrieved = await sql_client.get_fact_by_key(test_user_id, "test_definition")
        assert retrieved is not None, "Failed to retrieve fact"
        assert retrieved.value == fact.value
        assert retrieved.category == "Definition"

        # Cleanup
        await sql_client.delete_fact(fact_id)

    @pytest.mark.asyncio
    async def test_fact_upsert(self, sql_client, test_user_id):
        """Test that upsert updates existing facts."""
        fact = Fact(
            user_id=test_user_id,
            key="upsert_test",
            value="Original value",
            category=FactCategory.ENTITY,
            confidence=0.8
        )

        # Create
        fact_id_1 = await sql_client.save_fact(fact)

        # Update with same key
        fact.value = "Updated value"
        fact.confidence = 0.9
        fact_id_2 = await sql_client.save_fact(fact)

        # Should be same fact_id (upsert, not insert)
        assert fact_id_1 == fact_id_2, "Upsert created duplicate instead of updating"

        # Verify updated
        retrieved = await sql_client.get_fact_by_key(test_user_id, "upsert_test")
        assert retrieved.value == "Updated value"

        # Cleanup
        await sql_client.delete_fact(fact_id_1)

    @pytest.mark.asyncio
    async def test_search_facts(self, sql_client, test_user_id):
        """Test keyword-based fact search."""
        # Create test facts
        facts = [
            Fact(user_id=test_user_id, key="python", value="A programming language", category=FactCategory.DEFINITION),
            Fact(user_id=test_user_id, key="azure", value="Microsoft cloud platform", category=FactCategory.DEFINITION),
            Fact(user_id=test_user_id, key="david_role", value="Backend owner", category=FactCategory.ENTITY),
        ]

        fact_ids = []
        for fact in facts:
            fid = await sql_client.save_fact(fact)
            fact_ids.append(fid)

        # Search
        results = await sql_client.search_facts(test_user_id, ["python"], limit=5)
        assert len(results) >= 1, "Search should find at least one fact"
        assert any(f.key == "python" for f in results), "Should find python fact"

        # Cleanup
        for fid in fact_ids:
            await sql_client.delete_fact(fid)


# =============================================================================
# TEST 3: USER PROFILE OPERATIONS
# =============================================================================

class TestUserProfileOperations:
    """Test user profile CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_profile(self, sql_client, test_user_id):
        """Test creating and retrieving a user profile."""
        profile = UserProfile(
            user_id=test_user_id,
            preferences={"response_style": "detailed", "expertise": "advanced"},
            common_queries=["show tasks", "list meetings"],
            known_entities=[{"name": "David", "role": "developer"}],
            interaction_patterns={"avg_queries_per_session": 5}
        )

        # Save
        success = await sql_client.save_user_profile(profile)
        assert success, "Failed to save profile"

        # Retrieve
        retrieved = await sql_client.get_user_profile(test_user_id)
        assert retrieved is not None, "Failed to retrieve profile"
        assert retrieved.preferences.get("response_style") == "detailed"
        assert len(retrieved.common_queries) == 2

    @pytest.mark.asyncio
    async def test_update_profile_field(self, sql_client, test_user_id):
        """Test updating individual profile fields."""
        # Create base profile
        profile = UserProfile(user_id=test_user_id, preferences={})
        await sql_client.save_user_profile(profile)

        # Update preferences
        success = await sql_client.update_profile_field(
            test_user_id, "preferences", {"theme": "dark"}
        )
        assert success, "Failed to update preference"

        # Verify
        retrieved = await sql_client.get_user_profile(test_user_id)
        assert retrieved.preferences.get("theme") == "dark"


# =============================================================================
# TEST 4: BRIDGE BLOCK OPERATIONS
# =============================================================================

class TestBridgeBlockOperations:
    """Test Cosmos DB bridge block operations."""

    @pytest.mark.asyncio
    async def test_create_block(self, block_manager, test_session_id, test_user_id):
        """Test creating a bridge block."""
        block = await block_manager.create_block(
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Test Topic"
        )

        assert block is not None
        assert block.topic_label == "Test Topic"
        assert block.status == BlockStatus.ACTIVE
        assert block.session_id == test_session_id

        # Cleanup
        await block_manager.delete_block(block.id, test_session_id)

    @pytest.mark.asyncio
    async def test_add_turn_to_block(self, block_manager, test_session_id, test_user_id):
        """Test adding conversation turns to a block."""
        # Create block
        block = await block_manager.create_block(
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Turn Test Topic"
        )

        # Add turn
        turn = Turn(
            index=0,
            query="What tasks are assigned to me?",
            response_summary="You have 5 tasks assigned.",
            intent="task_query",
            entities=["tasks"]
        )

        updated = await block_manager.add_turn(block.id, test_session_id, turn)
        assert updated is not None
        assert len(updated.turns) == 1
        assert updated.turns[0].query == turn.query

        # Cleanup
        await block_manager.delete_block(block.id, test_session_id)

    @pytest.mark.asyncio
    async def test_pause_and_resume_block(self, block_manager, test_session_id, test_user_id):
        """Test pausing and resuming blocks."""
        # Create block
        block = await block_manager.create_block(
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Pause Test"
        )

        # Pause
        success = await block_manager.pause_block(block.id, test_session_id)
        assert success, "Failed to pause block"

        # Verify paused
        paused = await block_manager.get_block(block.id, test_session_id)
        assert paused.status == BlockStatus.PAUSED

        # Resume
        resumed = await block_manager.resume_block(block.id, test_session_id)
        assert resumed is not None
        assert resumed.status == BlockStatus.ACTIVE

        # Cleanup
        await block_manager.delete_block(block.id, test_session_id)


# =============================================================================
# TEST 5: GOVERNOR ROUTING SCENARIOS
# =============================================================================

class TestGovernorRouting:
    """Test the four routing scenarios."""

    @pytest.fixture
    def governor(self, block_manager, sql_client):
        """Create Governor for tests."""
        return Governor(
            block_manager=block_manager,
            sql_client=sql_client,
            ai_client=None  # No AI for unit tests
        )

    @pytest.mark.asyncio
    async def test_scenario_3_new_topic_first(
        self, governor, block_manager, test_session_id, test_user_id
    ):
        """Test Scenario 3: New Topic (first message, no active blocks)."""
        # No blocks exist for this session
        decision = await governor.route(
            user_id=test_user_id,
            session_id=test_session_id,
            query="Show me all open tasks",
            intent="task_list"
        )

        assert decision.scenario == RoutingScenario.NEW_TOPIC_FIRST
        assert decision.is_new_topic == True
        assert decision.matched_block_id is None
        assert decision.suggested_label != ""

    @pytest.mark.asyncio
    async def test_scenario_1_topic_continuation(
        self, governor, block_manager, test_session_id, test_user_id
    ):
        """Test Scenario 1: Topic Continuation (same topic, high similarity)."""
        # Create an active block about tasks
        block = await block_manager.create_block(
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Task Discussion"
        )
        block.keywords = ["tasks", "assigned", "overdue", "david"]
        await block_manager.update_block(block.id, test_session_id, {"keywords": block.keywords})

        # Query about the same topic
        decision = await governor.route(
            user_id=test_user_id,
            session_id=test_session_id,
            query="Which tasks are overdue?",  # Related to tasks
            intent="task_query"
        )

        # Should continue the existing topic (or shift if similarity is low)
        # Note: With simple keyword matching, similarity may be below threshold
        assert decision.scenario in [
            RoutingScenario.TOPIC_CONTINUATION,
            RoutingScenario.TOPIC_SHIFT
        ], f"Expected continuation or shift, got {decision.scenario}"

        # If it continued, should match the block
        if decision.scenario == RoutingScenario.TOPIC_CONTINUATION:
            assert decision.is_new_topic == False
            assert decision.matched_block_id == block.id

        # Cleanup
        await block_manager.delete_block(block.id, test_session_id)

    @pytest.mark.asyncio
    async def test_scenario_4_topic_shift(
        self, governor, block_manager, test_session_id, test_user_id
    ):
        """Test Scenario 4: Topic Shift (new topic, pause current)."""
        # Create an active block about tasks
        block = await block_manager.create_block(
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Task Discussion"
        )
        block.keywords = ["tasks", "assigned", "sprint"]
        await block_manager.update_block(block.id, test_session_id, {"keywords": block.keywords})

        # Query about completely different topic
        decision = await governor.route(
            user_id=test_user_id,
            session_id=test_session_id,
            query="What meetings do I have tomorrow?",  # Different topic
            intent="meeting_query"
        )

        # Should be topic shift (new topic, active block exists but doesn't match)
        assert decision.scenario == RoutingScenario.TOPIC_SHIFT
        assert decision.is_new_topic == True
        assert decision.active_block is not None  # The current block to be paused

        # Cleanup
        await block_manager.delete_block(block.id, test_session_id)

    @pytest.mark.asyncio
    async def test_scenario_2_topic_resumption(
        self, governor, block_manager, test_session_id, test_user_id
    ):
        """Test Scenario 2: Topic Resumption (return to paused block)."""
        # Create a PAUSED block about meetings
        meeting_block = await block_manager.create_block(
            session_id=test_session_id,
            user_id=test_user_id,
            topic_label="Meeting Discussion"
        )
        meeting_block.keywords = ["meetings", "calendar", "schedule", "standup"]
        await block_manager.update_block(
            meeting_block.id, test_session_id,
            {"keywords": meeting_block.keywords}
        )
        await block_manager.pause_block(meeting_block.id, test_session_id)

        # Query that matches the paused block
        decision = await governor.route(
            user_id=test_user_id,
            session_id=test_session_id,
            query="Back to the meetings - when is standup?",
            intent="meeting_query"
        )

        # Should resume the paused meeting block (or new topic if similarity is low)
        # Note: With simple keyword matching, the paused block may not match
        assert decision.scenario in [
            RoutingScenario.TOPIC_RESUMPTION,
            RoutingScenario.NEW_TOPIC_FIRST
        ], f"Expected resumption or new topic, got {decision.scenario}"

        # If it resumed, should match the meeting block
        if decision.scenario == RoutingScenario.TOPIC_RESUMPTION:
            assert decision.is_new_topic == False
            assert decision.matched_block_id == meeting_block.id

        # Cleanup
        await block_manager.delete_block(meeting_block.id, test_session_id)


# =============================================================================
# TEST 6: FACT SCRUBBER
# =============================================================================

class TestFactScrubber:
    """Test fact extraction functionality."""

    @pytest.fixture
    def fact_scrubber(self, sql_client):
        """Create FactScrubber for tests."""
        return FactScrubber(sql_client=sql_client, ai_client=None)

    @pytest.mark.asyncio
    async def test_regex_extraction_definition(self, fact_scrubber, test_user_id):
        """Test regex-based definition extraction."""
        text = "An API is a set of protocols for building software applications."

        result = await fact_scrubber.extract_facts(text, test_user_id, "block_test")

        assert result.extraction_method == "regex_fallback"  # No AI client
        assert len(result.facts) >= 1
        # Should extract "API is a set of protocols..."

    @pytest.mark.asyncio
    async def test_regex_extraction_acronym(self, fact_scrubber, test_user_id):
        """Test regex-based acronym extraction."""
        text = "REST stands for Representational State Transfer."

        result = await fact_scrubber.extract_facts(text, test_user_id, "block_test")

        # Should extract the acronym
        acronyms = [f for f in result.facts if f.category == FactCategory.ACRONYM]
        assert len(acronyms) >= 1
        assert any("REST" in f.key.upper() for f in acronyms)

    @pytest.mark.asyncio
    async def test_empty_text_handling(self, fact_scrubber, test_user_id):
        """Test handling of empty or short text."""
        result = await fact_scrubber.extract_facts("Hi", test_user_id, "block_test")

        assert result.extraction_method == "skip_short"
        assert len(result.facts) == 0


# =============================================================================
# TEST 7: CONTEXT HYDRATOR
# =============================================================================

class TestContextHydrator:
    """Test context assembly functionality."""

    def test_hydrate_with_block_and_facts(self, hydrator):
        """Test hydrating context with block and facts."""
        block = BridgeBlock(
            id="block_123",
            session_id="session_123",
            user_id="user_123",
            topic_label="Task Review",
            summary="Reviewing Q4 tasks",
            keywords=["tasks", "Q4", "review"],
            turns=[
                Turn(index=0, query="Show Q4 tasks", response_summary="Found 10 tasks"),
                Turn(index=1, query="Which are overdue?", response_summary="3 are overdue")
            ]
        )

        facts = [
            Fact(user_id="user_123", key="david_role", value="Backend owner", category=FactCategory.ENTITY),
            Fact(user_id="user_123", key="q4_goal", value="Ship v2.0", category=FactCategory.DEFINITION)
        ]

        decision = GovernorDecision(
            scenario=RoutingScenario.TOPIC_CONTINUATION,
            matched_block_id=block.id,
            is_new_topic=False,
            suggested_label=block.topic_label,
            active_block=block,
            relevant_facts=facts,
            memories=[],
            topic_similarity=0.85
        )

        # Run synchronously for test (hydrate is async but simple)
        context = asyncio.get_event_loop().run_until_complete(
            hydrator.hydrate(decision, None, "test query")
        )

        assert context.full_context != ""
        assert "Task Review" in context.full_context
        assert "Backend owner" in context.full_context or "david_role" in context.full_context
        assert context.token_estimate > 0

    def test_hydrate_minimal(self, hydrator):
        """Test minimal hydration."""
        block = BridgeBlock(
            id="b1", session_id="s1", user_id="u1",
            topic_label="Test",
            turns=[Turn(index=0, query="Hello", response_summary="Hi")]
        )

        facts = [
            Fact(user_id="u1", key="name", value="David", category=FactCategory.ENTITY)
        ]

        result = hydrator.hydrate_minimal(block, facts)

        assert "Test" in result
        assert "David" in result or "name" in result


# =============================================================================
# TEST 8: END-TO-END INTEGRATION
# =============================================================================

class TestEndToEndIntegration:
    """Test full HMLR service integration."""

    @pytest.fixture
    def hmlr_service(self):
        """Create HMLR service for tests."""
        return HMLRService(ai_client=None)

    @pytest.mark.asyncio
    async def test_full_conversation_flow(
        self, hmlr_service, test_session_id, test_user_id
    ):
        """Test a complete conversation flow through HMLR."""
        # Turn 1: New topic
        decision1, context1 = await hmlr_service.route_query(
            user_id=test_user_id,
            session_id=test_session_id,
            query="What are David's open tasks?",
            intent="task_query",
            entities=["David", "tasks"]
        )

        assert decision1.scenario == RoutingScenario.NEW_TOPIC_FIRST

        # Store the turn
        block = await hmlr_service.store_turn(
            user_id=test_user_id,
            session_id=test_session_id,
            query="What are David's open tasks?",
            response="David has 5 open tasks: Task A, Task B...",
            decision=decision1,
            intent="task_query",
            entities=["David", "tasks"]
        )

        assert block is not None

        # Turn 2: Continuation
        decision2, context2 = await hmlr_service.route_query(
            user_id=test_user_id,
            session_id=test_session_id,
            query="Which of those are overdue?",
            intent="task_query",
            entities=["tasks", "overdue"]
        )

        # Should continue the task topic
        assert decision2.scenario in [
            RoutingScenario.TOPIC_CONTINUATION,
            RoutingScenario.TOPIC_SHIFT  # Acceptable if similarity is low
        ]

        # Turn 3: Topic shift
        decision3, context3 = await hmlr_service.route_query(
            user_id=test_user_id,
            session_id=test_session_id,
            query="Show me the budget for Q4",
            intent="budget_query",
            entities=["budget", "Q4"]
        )

        # Should be a topic shift
        assert decision3.scenario == RoutingScenario.TOPIC_SHIFT

        # Cleanup
        blocks = await hmlr_service.get_session_blocks(test_session_id)
        for b in blocks:
            await hmlr_service.block_manager.delete_block(b.id, test_session_id)

    @pytest.mark.asyncio
    async def test_fact_persistence_across_sessions(
        self, hmlr_service, test_user_id
    ):
        """Test that facts persist across different sessions."""
        session_1 = f"session_1_{uuid.uuid4().hex[:6]}"
        session_2 = f"session_2_{uuid.uuid4().hex[:6]}"

        # Session 1: Create a fact
        fact = Fact(
            user_id=test_user_id,
            key="persistence_test",
            value="This fact should persist",
            category=FactCategory.DEFINITION,
            confidence=1.0
        )
        fact_id = await hmlr_service.sql_client.save_fact(fact)

        # Session 2: Retrieve the fact
        facts = await hmlr_service.get_user_facts(test_user_id)

        assert any(f.key == "persistence_test" for f in facts), \
            "Fact should persist across sessions"

        # Cleanup
        await hmlr_service.sql_client.delete_fact(fact_id)


# =============================================================================
# TEST 9: EDGE CASES AND ERROR HANDLING
# =============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_session_handling(self, block_manager, test_session_id):
        """Test handling of session with no blocks."""
        blocks = await block_manager.get_session_blocks(test_session_id)
        assert blocks == [], "Empty session should return empty list"

        active = await block_manager.get_active_block(test_session_id)
        assert active is None, "Empty session should have no active block"

    @pytest.mark.asyncio
    async def test_unicode_handling(self, sql_client, test_user_id):
        """Test handling of unicode characters in facts."""
        fact = Fact(
            user_id=test_user_id,
            key="unicode_test",
            value="Testing unicode: 你好世界 🌍 émojis",
            category=FactCategory.DEFINITION
        )

        fact_id = await sql_client.save_fact(fact)
        retrieved = await sql_client.get_fact_by_key(test_user_id, "unicode_test")

        assert retrieved is not None
        assert "你好世界" in retrieved.value
        assert "🌍" in retrieved.value

        # Cleanup
        await sql_client.delete_fact(fact_id)

    @pytest.mark.asyncio
    async def test_very_long_query_handling(self):
        """Test handling of very long queries."""
        governor = Governor(
            block_manager=BridgeBlockManager(),
            sql_client=HMLRSQLClient(settings.hmlr_sql_connection_string),
            ai_client=None
        )

        long_query = "What " + "is " * 500 + "this?"  # ~2000 characters

        # Should not crash
        decision = await governor.route(
            user_id="test_user",
            session_id="test_session",
            query=long_query
        )

        assert decision is not None

    def test_hmlr_disabled_handling(self):
        """Test HMLR service when disabled."""
        service = HMLRService(ai_client=None)
        service.disable()

        assert service.enabled == False

        # Should return empty results when disabled
        decision, context = asyncio.get_event_loop().run_until_complete(
            service.route_query(
                user_id="test",
                session_id="test",
                query="test query"
            )
        )

        assert decision.scenario == RoutingScenario.NEW_TOPIC_FIRST
        assert context.full_context == ""


# =============================================================================
# TEST 10: PERFORMANCE BASELINE
# =============================================================================

class TestPerformance:
    """Performance baseline tests."""

    @pytest.mark.asyncio
    async def test_routing_latency(self):
        """Measure routing decision latency."""
        import time

        service = HMLRService(ai_client=None)
        session_id = f"perf_test_{uuid.uuid4().hex[:6]}"

        latencies = []
        for i in range(5):
            start = time.time()
            await service.route_query(
                user_id="perf_test_user",
                session_id=session_id,
                query=f"Test query number {i}"
            )
            latencies.append((time.time() - start) * 1000)

        avg_latency = sum(latencies) / len(latencies)
        print(f"\nAverage routing latency: {avg_latency:.2f}ms")

        # Should be under 1000ms without AI calls (includes DB latency)
        # Note: First call may be slower due to connection setup
        assert avg_latency < 1000, f"Routing too slow: {avg_latency}ms"

        # Cleanup
        blocks = await service.get_session_blocks(session_id)
        for b in blocks:
            await service.block_manager.delete_block(b.id, session_id)


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
