"""
Shared fixtures and helpers for AI Guide test suite.
"""
import httpx
import pytest
import time
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

BASE_URL = "http://localhost:8080"
API_KEY = "dev-test-key-123"


@dataclass
class QueryResult:
    """Structured result from AI Guide query."""
    query: str
    response: str
    response_time: float
    intent: str
    confidence: str
    suggestions: List[Dict]
    sources: List[str]
    data_basis: Optional[Dict] = None
    raw: Dict = None


def query_guide(
    query: str,
    context: str = None,
    page_context: dict = None,
    timeout: float = 60.0
) -> QueryResult:
    """
    Query the AI Guide API and return structured result.

    Args:
        query: The natural language query
        context: Optional additional context
        page_context: Optional page context for filtering
        timeout: Request timeout in seconds

    Returns:
        QueryResult with response and metadata
    """
    payload = {"query": query}
    if context:
        payload["context"] = context
    if page_context:
        payload["page_context"] = page_context

    start = time.time()
    try:
        response = httpx.post(
            f"{BASE_URL}/api/agent/query",
            json=payload,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=timeout
        )
        response.raise_for_status()
        elapsed = time.time() - start
        data = response.json()

        return QueryResult(
            query=query,
            response=data.get("response", ""),
            response_time=elapsed,
            intent=data.get("intent", "unknown"),
            confidence=data.get("confidence", "unknown"),
            suggestions=data.get("suggestions", []),
            sources=data.get("sources", []),
            data_basis=data.get("data_basis"),
            raw=data
        )
    except Exception as e:
        elapsed = time.time() - start
        return QueryResult(
            query=query,
            response=f"ERROR: {str(e)}",
            response_time=elapsed,
            intent="error",
            confidence="none",
            suggestions=[],
            sources=[],
            raw={"error": str(e)}
        )


def check_sections_present(response: str, expected_sections: List[str]) -> Dict[str, bool]:
    """
    Check if expected sections are present in response.

    Args:
        response: The AI response text
        expected_sections: List of section keywords to look for

    Returns:
        Dict mapping section name to whether it was found
    """
    response_lower = response.lower()
    results = {}
    for section in expected_sections:
        # Check for section as header (with ** or :) or just as keyword
        patterns = [
            f"**{section.lower()}",
            f"{section.lower()}:",
            f"### {section.lower()}",
            f"## {section.lower()}",
            section.lower()
        ]
        results[section] = any(p in response_lower for p in patterns)
    return results


def extract_names_from_response(response: str) -> List[str]:
    """Extract person names from response (First Last pattern)."""
    # Match "First Last" patterns (capitalized words)
    pattern = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
    return list(set(re.findall(pattern, response)))


def extract_numbers_from_response(response: str) -> List[int]:
    """Extract numbers from response."""
    return [int(n) for n in re.findall(r'\b(\d+)\b', response)]


def has_list_format(response: str) -> bool:
    """Check if response contains list formatting."""
    return (
        response.count('\n-') >= 2 or
        response.count('\n*') >= 2 or
        response.count('\n1.') >= 1 or
        response.count('\n•') >= 2
    )


def has_actionable_content(response: str) -> Dict[str, bool]:
    """Check for actionable content markers."""
    response_lower = response.lower()
    return {
        "has_names": len(extract_names_from_response(response)) > 0,
        "has_numbers": len(extract_numbers_from_response(response)) > 0,
        "has_list": has_list_format(response),
        "has_next_steps": any(term in response_lower for term in [
            "next steps", "next step", "action", "recommend", "should", "consider"
        ]),
        "has_dates": bool(re.search(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}', response)),
        "has_status": any(status in response_lower for status in [
            "pending", "in-progress", "in progress", "blocked", "completed", "done"
        ])
    }


def response_length_check(response: str, min_len: int = 100, max_len: int = 2000) -> Dict[str, Any]:
    """Check response length is within acceptable bounds."""
    length = len(response)
    return {
        "length": length,
        "too_short": length < min_len,
        "too_long": length > max_len,
        "in_range": min_len <= length <= max_len
    }


@pytest.fixture
def guide_client():
    """Fixture providing query_guide function."""
    return query_guide


@pytest.fixture
def sample_queries():
    """Fixture providing sample queries by category."""
    return {
        "status": [
            "What tasks are blocked?",
            "Show overdue items",
            "Any pending approvals?"
        ],
        "aggregation": [
            "How many tasks by status?",
            "Breakdown agents by tier",
            "Count meetings this month"
        ],
        "list": [
            "Show all agents",
            "List high priority tasks",
            "Show recent meetings"
        ],
        "ownership": [
            "Who owns the backend?",
            "Who's responsible for AI Guide?",
            "Who should I contact about infrastructure?"
        ],
        "comparison": [
            "Compare status vs last week",
            "How has agent count changed?",
            "Progress since yesterday"
        ]
    }


# =============================================================================
# HMLR Test Fixtures and Factories
# =============================================================================

from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, timezone
import uuid


def create_test_block(
    block_id: str = None,
    session_id: str = "test-session",
    user_id: str = "test-user",
    topic_label: str = "Test Topic",
    status: str = "ACTIVE",
    open_loops: List[str] = None,
    turns: List[Dict] = None,
    decisions_made: List[str] = None,
    keywords: List[str] = None,
    summary: str = None,
    created_at: datetime = None,
    last_activity: datetime = None
) -> Dict[str, Any]:
    """Factory for creating test BridgeBlock data."""
    now = datetime.now(timezone.utc)
    return {
        "id": block_id or f"bb_test_{uuid.uuid4().hex[:8]}",
        "session_id": session_id,
        "user_id": user_id,
        "topic_label": topic_label,
        "status": status,
        "open_loops": open_loops or [],
        "turns": turns or [],
        "decisions_made": decisions_made or [],
        "keywords": keywords or [],
        "summary": summary or "",
        "created_at": (created_at or now).isoformat(),
        "last_activity": (last_activity or now).isoformat()
    }


def create_test_fact(
    user_id: str = "test-user",
    key: str = "test_key",
    value: str = "test_value",
    category: str = "Definition",
    confidence: float = 0.9,
    verified: bool = True,
    fact_id: int = None
) -> Dict[str, Any]:
    """Factory for creating test Fact data."""
    return {
        "fact_id": fact_id or 1,
        "user_id": user_id,
        "key": key,
        "value": value,
        "category": category,
        "confidence": confidence,
        "verified": verified,
        "created_at": datetime.now(timezone.utc).isoformat()
    }


def create_test_profile(
    user_id: str = "test-user",
    preferences: Dict = None,
    common_queries: List[str] = None,
    known_entities: List[Dict] = None,
    interaction_patterns: Dict = None
) -> Dict[str, Any]:
    """Factory for creating test UserProfile data."""
    return {
        "user_id": user_id,
        "preferences": preferences or {"response_style": "concise"},
        "common_queries": common_queries or [],
        "known_entities": known_entities or [],
        "interaction_patterns": interaction_patterns or {
            "total_queries": 50,
            "technical_queries": 30
        }
    }


def create_test_turn(
    index: int = 0,
    query: str = "Test query",
    response_summary: str = "Test response",
    intent: str = None,
    entities: List[str] = None
) -> Dict[str, Any]:
    """Factory for creating test Turn data."""
    return {
        "index": index,
        "query": query,
        "response_summary": response_summary,
        "intent": intent,
        "entities": entities or [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def mock_cosmos_container():
    """Mock Cosmos DB container for HMLR tests."""
    container = MagicMock()
    container.create_item = MagicMock()
    container.read_item = MagicMock()
    container.replace_item = MagicMock()
    container.delete_item = MagicMock()
    container.upsert_item = MagicMock()
    container.query_items = MagicMock(return_value=iter([]))
    return container


@pytest.fixture
def mock_database(mock_cosmos_container):
    """Mock database with containers for HMLR tests."""
    db = MagicMock()
    db.get_container = MagicMock(return_value=mock_cosmos_container)
    db.initialize = MagicMock()
    db.containers = {
        "bridge_blocks": mock_cosmos_container,
        "user_profiles": mock_cosmos_container,
        "user_facts": mock_cosmos_container
    }
    return db


@pytest.fixture
def mock_sql_client():
    """Mock SQL client for HMLR tests."""
    client = MagicMock()
    client.save_fact = MagicMock(return_value=1)
    client.get_facts_by_user = MagicMock(return_value=[])
    client.search_facts = MagicMock(return_value=[])
    client.get_fact_by_key = MagicMock(return_value=None)
    client.delete_fact = MagicMock(return_value=True)
    client.get_user_profile = MagicMock(return_value=None)
    client.save_user_profile = MagicMock(return_value=True)
    client.update_profile_field = MagicMock(return_value=True)
    client.close = MagicMock()
    return client


@pytest.fixture
def mock_ai_client():
    """Mock AI client for LLM operations in HMLR tests."""
    client = AsyncMock()
    client.complete = AsyncMock(return_value={"content": '{"facts": []}'})
    return client


@pytest.fixture
def sample_blocks():
    """Sample blocks with various states for testing."""
    now = datetime.now(timezone.utc)
    return [
        create_test_block(
            block_id="bb_active_1",
            session_id="session-1",
            topic_label="Active Topic",
            status="ACTIVE",
            open_loops=["Pending item 1", "Pending item 2"],
            last_activity=now
        ),
        create_test_block(
            block_id="bb_paused_1",
            session_id="session-1",
            topic_label="Paused Topic",
            status="PAUSED",
            open_loops=["Old pending item"],
            last_activity=now - timedelta(hours=2)
        ),
        create_test_block(
            block_id="bb_paused_2",
            session_id="session-2",
            topic_label="Cross-Session Topic",
            status="PAUSED",
            open_loops=["Cross-session pending"],
            last_activity=now - timedelta(days=1)
        )
    ]


@pytest.fixture
def sample_profile():
    """Sample user profile for testing."""
    return create_test_profile(
        user_id="david.hayes",
        common_queries=[
            "What tasks are blocked?",
            "Show agent development status"
        ],
        known_entities=[
            {"name": "AI Guide", "type": "project"},
            {"name": "HMLR", "type": "system"}
        ],
        interaction_patterns={
            "total_queries": 150,
            "technical_queries": 120,
            "topics_by_frequency": {
                "agent development": 45,
                "governance": 30
            }
        }
    )


@pytest.fixture
def sample_facts():
    """Sample facts for testing."""
    return [
        create_test_fact(
            key="HMLR",
            value="Hierarchical Memory Lookup and Routing",
            category="Acronym"
        ),
        create_test_fact(
            key="Tech Stack",
            value="Next.js, FastAPI, CosmosDB",
            category="Definition"
        )
    ]


@pytest.fixture
def hmlr_test_user_id():
    """Standard test user ID for HMLR tests."""
    return f"test-user-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def hmlr_test_session_id():
    """Standard test session ID for HMLR tests."""
    return f"test-session-{uuid.uuid4().hex[:8]}"
