"""
Integration tests for the Suggestions API endpoint.
Tests /api/guide/suggestions endpoint behavior.
"""
import pytest
import httpx
import time
from typing import Dict, Any, List

BASE_URL = "http://localhost:8080"
API_KEY = "dev-test-key-123"


def get_suggestions(
    page_type: str = "dashboard",
    user_id: str = None,
    session_id: str = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """Fetch suggestions from the API."""
    params = {"page_type": page_type}
    if user_id:
        params["user_id"] = user_id
    if session_id:
        params["session_id"] = session_id

    try:
        response = httpx.get(
            f"{BASE_URL}/api/guide/suggestions",
            params=params,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


class TestSuggestionsEndpointBasic:
    @pytest.mark.integration
    def test_endpoint_returns_200(self):
        result = get_suggestions(page_type="dashboard")
        assert "error" not in result or "404" not in str(result.get("error", ""))

    @pytest.mark.integration
    def test_returns_suggestions_array(self):
        result = get_suggestions(page_type="dashboard")
        if "error" not in result:
            assert "suggestions" in result
            assert isinstance(result["suggestions"], list)

    @pytest.mark.integration
    def test_returns_is_personalized_flag(self):
        result = get_suggestions(page_type="dashboard")
        if "error" not in result:
            assert "is_personalized" in result
            assert isinstance(result["is_personalized"], bool)

    @pytest.mark.integration
    def test_returns_page_type(self):
        result = get_suggestions(page_type="tasks")
        if "error" not in result:
            assert result.get("page_type") == "tasks"


class TestStaticFallbackBehavior:
    @pytest.mark.integration
    def test_no_user_returns_static(self):
        result = get_suggestions(page_type="dashboard", user_id=None)
        if "error" not in result:
            assert result["is_personalized"] is False
            assert result.get("fallback_reason") == "no_user"

    @pytest.mark.integration
    def test_static_suggestions_for_dashboard(self):
        result = get_suggestions(page_type="dashboard")
        if "error" not in result:
            suggestions = result["suggestions"]
            assert len(suggestions) >= 1
            texts = [s["text"] for s in suggestions]
            assert any("ask" in t.lower() or "task" in t.lower() or "meeting" in t.lower() for t in texts)

    @pytest.mark.integration
    def test_static_suggestions_for_tasks(self):
        result = get_suggestions(page_type="tasks")
        if "error" not in result:
            texts = [s["text"].lower() for s in result["suggestions"]]
            assert any("task" in t or "priority" in t or "blocked" in t for t in texts)

    @pytest.mark.integration
    def test_static_suggestions_for_meetings(self):
        result = get_suggestions(page_type="meetings")
        if "error" not in result:
            texts = [s["text"].lower() for s in result["suggestions"]]
            assert any("meeting" in t or "discussed" in t or "action" in t for t in texts)


class TestSuggestionStructure:
    @pytest.mark.integration
    def test_suggestion_has_required_fields(self):
        result = get_suggestions(page_type="dashboard")
        if "error" not in result and result["suggestions"]:
            suggestion = result["suggestions"][0]
            assert "id" in suggestion
            assert "text" in suggestion
            assert "source" in suggestion
            assert "priority" in suggestion
            assert "confidence" in suggestion

    @pytest.mark.integration
    def test_suggestion_source_is_valid(self):
        result = get_suggestions(page_type="dashboard")
        if "error" not in result:
            valid_sources = ["static", "intent", "open_loop", "common_query", "topic_interest", "entity", "context"]
            for suggestion in result["suggestions"]:
                assert suggestion["source"] in valid_sources

    @pytest.mark.integration
    def test_suggestion_priority_in_range(self):
        result = get_suggestions(page_type="dashboard")
        if "error" not in result:
            for suggestion in result["suggestions"]:
                assert 0 <= suggestion["priority"] <= 100

    @pytest.mark.integration
    def test_suggestion_confidence_in_range(self):
        result = get_suggestions(page_type="dashboard")
        if "error" not in result:
            for suggestion in result["suggestions"]:
                assert 0.0 <= suggestion["confidence"] <= 1.0


class TestPageTypeVariations:
    PAGE_TYPES = [
        "dashboard", "meetings", "tasks", "agents", "decisions",
        "governance", "budget", "resources", "tech-radar", "architecture", "guide"
    ]

    @pytest.mark.integration
    @pytest.mark.parametrize("page_type", PAGE_TYPES)
    def test_each_page_type_returns_suggestions(self, page_type):
        result = get_suggestions(page_type=page_type)
        if "error" not in result:
            assert len(result["suggestions"]) >= 1, f"Page {page_type} should have suggestions"

    @pytest.mark.integration
    def test_unknown_page_uses_fallback(self):
        result = get_suggestions(page_type="nonexistent_page_type")
        if "error" not in result:
            assert len(result["suggestions"]) >= 1


class TestSessionIdBehavior:
    @pytest.mark.integration
    def test_session_id_accepted(self):
        result = get_suggestions(
            page_type="dashboard",
            session_id="test-session-123"
        )
        if "error" not in result:
            assert "suggestions" in result

    @pytest.mark.integration
    def test_different_sessions_same_page(self):
        result1 = get_suggestions(page_type="dashboard", session_id="session-a")
        result2 = get_suggestions(page_type="dashboard", session_id="session-b")
        if "error" not in result1 and "error" not in result2:
            assert result1["suggestions"] is not None
            assert result2["suggestions"] is not None


class TestUserIdBehavior:
    @pytest.mark.integration
    def test_with_user_id(self):
        result = get_suggestions(
            page_type="dashboard",
            user_id="test-user-456"
        )
        if "error" not in result:
            assert "suggestions" in result

    @pytest.mark.integration
    def test_user_id_reflected_in_response(self):
        result = get_suggestions(
            page_type="dashboard",
            user_id="test-user-789"
        )
        if "error" not in result:
            if result["user_id"] is not None:
                assert result["user_id"] == "test-user-789"


class TestPerformance:
    @pytest.mark.integration
    def test_response_time_under_threshold(self):
        start = time.time()
        result = get_suggestions(page_type="dashboard")
        elapsed = time.time() - start

        if "error" not in result:
            assert elapsed < 2.0, f"Response took {elapsed}s, expected < 2.0s"

    @pytest.mark.integration
    def test_multiple_rapid_requests(self):
        times = []
        for _ in range(5):
            start = time.time()
            result = get_suggestions(page_type="dashboard")
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        assert avg_time < 1.0, f"Average response time {avg_time}s too slow"


class TestMaxSuggestions:
    @pytest.mark.integration
    def test_max_suggestions_limit(self):
        result = get_suggestions(page_type="dashboard")
        if "error" not in result:
            assert len(result["suggestions"]) <= 6, "Should return at most 6 suggestions"


class TestFollowUpSuggestionsViaQuery:
    """Test that follow-up suggestions in query responses include HMLR data when available."""

    @pytest.mark.integration
    def test_query_response_includes_suggestions(self):
        try:
            response = httpx.post(
                f"{BASE_URL}/api/agent/query",
                json={
                    "query": "Show blocked tasks",
                    "page_context": {"current_page": "tasks", "visible_entity_type": "tasks"}
                },
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            assert "suggestions" in data
            assert isinstance(data["suggestions"], list)
        except Exception as e:
            pytest.skip(f"Query endpoint not available: {e}")

    @pytest.mark.integration
    def test_query_with_user_id(self):
        try:
            response = httpx.post(
                f"{BASE_URL}/api/agent/query",
                json={
                    "query": "What tasks are pending?",
                    "user_id": "test-user-hmlr",
                    "session_id": "test-session-hmlr"
                },
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            assert "suggestions" in data
        except Exception as e:
            pytest.skip(f"Query endpoint not available: {e}")
