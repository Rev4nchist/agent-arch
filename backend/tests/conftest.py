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
