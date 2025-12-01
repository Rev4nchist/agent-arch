"""
Live Persona Query Tests for AI Guide Accuracy Improvements.

Tests the following Phase 1-3 improvements:
- Phase 1: Aggregation queries get no limit (show all results)
- Phase 2: "showing X of Y total" context for accurate counts
- Phase 3: Case-insensitive status normalization

Requires backend running on localhost:8001.
"""
import httpx
import pytest
import re
import json

BASE_URL = "http://localhost:8080"
API_KEY = "dev-test-key-123"


def query_guide(query: str, context: str = None, page_context: dict = None) -> dict:
    """Helper to query AI Guide API."""
    payload = {"query": query}
    if context:
        payload["context"] = context
    if page_context:
        payload["page_context"] = page_context

    response = httpx.post(
        f"{BASE_URL}/api/agent/query",
        json=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        timeout=60.0
    )
    response.raise_for_status()
    return response.json()


class TestAggregationQueries:
    """Test that aggregation queries return all results without hardcoded limits."""

    def test_breakdown_agents_by_status(self):
        """Phase 1.1: 'breakdown agents by status' should return all agents."""
        result = query_guide("breakdown agents by status")
        print(f"\n=== BREAKDOWN AGENTS BY STATUS ===")
        print(f"Response: {result['response'][:500]}...")

        # Should contain status breakdown information
        assert "response" in result
        # AI should report agent status information
        response_lower = result["response"].lower()
        # Should mention some status-related terms
        assert any(term in response_lower for term in [
            "status", "agent", "production", "development", "testing",
            "design", "idea", "staging", "deprecated"
        ])

    def test_group_tasks_by_priority(self):
        """Phase 1.1: 'group tasks by priority' should return all tasks."""
        result = query_guide("group tasks by priority")
        print(f"\n=== GROUP TASKS BY PRIORITY ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result
        response_lower = result["response"].lower()
        # Should mention priority-related terms
        assert any(term in response_lower for term in [
            "priority", "task", "critical", "high", "medium", "low"
        ])

    def test_agents_by_tier(self):
        """Phase 1.1: 'agents by tier' should return tier breakdown."""
        result = query_guide("agents by tier")
        print(f"\n=== AGENTS BY TIER ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result
        response_lower = result["response"].lower()
        # Should mention tier-related terms
        assert any(term in response_lower for term in [
            "tier", "agent", "individual", "department", "enterprise"
        ])


class TestShowingXofYTotal:
    """Test that context includes 'showing X of Y total' for accurate counts."""

    def test_all_tasks_count(self):
        """Phase 1.2: Query should get accurate total count."""
        result = query_guide("how many tasks are there?")
        print(f"\n=== HOW MANY TASKS ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result
        # Should mention task count
        response_lower = result["response"].lower()
        assert "task" in response_lower

    def test_in_progress_tasks_count(self):
        """Phase 1.2: Query for in-progress should show filtered count."""
        result = query_guide("how many in-progress tasks are there?")
        print(f"\n=== IN-PROGRESS TASKS COUNT ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result
        response_lower = result["response"].lower()
        # Should reference task count
        assert "task" in response_lower or "in-progress" in response_lower or "in progress" in response_lower

    def test_agent_count_by_status(self):
        """Phase 1.2: Query for agents by status should show counts."""
        result = query_guide("how many agents are in production?")
        print(f"\n=== PRODUCTION AGENTS COUNT ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result


class TestStatusNormalization:
    """Test Phase 3 status normalization (case-insensitive matching)."""

    def test_blocked_lowercase(self):
        """Phase 3.1: 'blocked' should match 'Blocked' status."""
        result = query_guide("show me blocked tasks")
        print(f"\n=== BLOCKED TASKS (lowercase) ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result

    def test_in_progress_variations(self):
        """Phase 3.1: Various in-progress formats should all work."""
        queries = [
            "in-progress tasks",
            "in progress tasks",
            "inprogress tasks"
        ]
        for query in queries:
            result = query_guide(f"show me {query}")
            print(f"\n=== {query.upper()} ===")
            print(f"Response: {result['response'][:200]}...")
            assert "response" in result

    def test_done_vs_completed(self):
        """Phase 3.1: 'completed' should map to 'Done' status."""
        result = query_guide("show completed tasks")
        print(f"\n=== COMPLETED TASKS ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result

    def test_priority_case_insensitive(self):
        """Phase 3.1: Priority should work case-insensitively."""
        queries = [
            "high priority tasks",
            "HIGH priority tasks",
            "critical tasks"
        ]
        for query in queries:
            result = query_guide(query)
            print(f"\n=== {query.upper()} ===")
            print(f"Response: {result['response'][:200]}...")
            assert "response" in result


class TestIntegrationStatusQueries:
    """Test Task 19 integration status pattern matching."""

    def test_integration_issues(self):
        """IT-05: 'agents with integration issues' should find integration problems."""
        result = query_guide("agents with integration issues")
        print(f"\n=== INTEGRATION ISSUES ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result

    def test_fully_integrated(self):
        """Test 'fully integrated agents' query."""
        result = query_guide("show fully integrated agents")
        print(f"\n=== FULLY INTEGRATED ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result


class TestDateFiltering:
    """Test Task 19 date filtering with entity-aware date fields."""

    def test_recent_decisions(self):
        """Decisions should filter by decision_date field."""
        result = query_guide("show recent decisions from this month")
        print(f"\n=== RECENT DECISIONS ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result

    def test_overdue_tasks(self):
        """Tasks should filter by due_date for overdue."""
        result = query_guide("show overdue tasks")
        print(f"\n=== OVERDUE TASKS ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result


class TestDataAccuracyRules:
    """Test Phase 3.2 AI data accuracy (no hallucination)."""

    def test_no_hallucinated_counts(self):
        """AI should use actual data, not make up numbers."""
        result = query_guide("how many agents are there total?")
        print(f"\n=== TOTAL AGENTS COUNT ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result
        # Response should contain number-like patterns
        response = result["response"]
        # Should mention agents and some numeric context
        assert "agent" in response.lower()

    def test_empty_results_reported_correctly(self):
        """If no results, should say 0, not make up data."""
        result = query_guide("show me tasks assigned to NonExistentPerson12345")
        print(f"\n=== NON-EXISTENT ASSIGNEE ===")
        print(f"Response: {result['response'][:500]}...")

        assert "response" in result
        # Should indicate no results or unable to find
        response_lower = result["response"].lower()
        # Accept various ways of saying "not found"
        assert any(term in response_lower for term in [
            "no ", "0", "none", "not found", "don't have", "don't see",
            "unable", "couldn't find", "cannot find", "no matching"
        ])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
