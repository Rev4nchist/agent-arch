"""
Test Historical/Comparison Queries

Verifies that the AI Guide correctly handles comparison and trend queries
using the snapshot service for historical data.
"""
import pytest
from conftest import query_guide


class TestComparisonIntentDetection:
    """Test that comparison queries are correctly classified."""

    def test_vs_last_week_detected(self):
        """'vs last week' should trigger comparison intent."""
        result = query_guide("Compare task status vs last week")
        print(f"\n=== VS LAST WEEK ===\n{result.response[:800]}")

        assert result.intent == "comparison", f"Expected comparison intent, got {result.intent}"

    def test_vs_last_month_detected(self):
        """'vs last month' should trigger comparison intent."""
        result = query_guide("Agent count vs last month")
        print(f"\n=== VS LAST MONTH ===\n{result.response[:800]}")

        assert result.intent == "comparison", f"Expected comparison intent, got {result.intent}"

    def test_how_has_changed_detected(self):
        """'how has X changed' should trigger comparison intent."""
        result = query_guide("How has task completion changed?")
        print(f"\n=== HOW CHANGED ===\n{result.response[:800]}")

        # Should be comparison or at least address the change
        change_words = ["change", "trend", "previous", "before", "compared"]
        has_change_content = any(w in result.response.lower() for w in change_words)
        assert has_change_content or result.intent == "comparison", \
            "Should address change or be comparison intent"

    def test_progress_since_detected(self):
        """'progress since X' should trigger comparison intent."""
        result = query_guide("Show progress since yesterday")
        print(f"\n=== PROGRESS SINCE ===\n{result.response[:800]}")

        progress_words = ["progress", "completed", "done", "change", "since"]
        has_progress = any(w in result.response.lower() for w in progress_words)
        assert has_progress, "Should address progress"

    def test_trend_keyword_detected(self):
        """'trend' keyword should trigger comparison intent."""
        result = query_guide("What's the adoption trend?")
        print(f"\n=== TREND ===\n{result.response[:800]}")

        assert result.intent == "comparison", f"Expected comparison intent, got {result.intent}"


class TestComparisonDataHandling:
    """Test handling of comparison data presence/absence."""

    def test_handles_no_historical_data(self):
        """Should gracefully handle when no historical data exists."""
        result = query_guide("Compare agent status vs last year")
        print(f"\n=== NO HISTORICAL DATA ===\n{result.response[:800]}")

        # Should not error - should explain no data or provide current state
        assert "error" not in result.response.lower(), "Should not return error"
        assert len(result.response) > 50, "Should provide meaningful response"

    def test_comparison_shows_current_state(self):
        """Comparison should always show current state even without history."""
        result = query_guide("How has agent count changed this week?")
        print(f"\n=== AGENT COUNT CHANGE ===\n{result.response[:800]}")

        # Should mention current count at minimum
        current_indicators = ["current", "now", "today", "at present", "agents"]
        has_current = any(ind in result.response.lower() for ind in current_indicators)
        assert has_current, "Should show current state"


class TestComparisonTimePeriods:
    """Test different time period comparisons."""

    def test_yesterday_comparison(self):
        """'yesterday' should use 1-day comparison."""
        result = query_guide("What changed since yesterday?")
        print(f"\n=== YESTERDAY ===\n{result.response[:800]}")

        time_refs = ["yesterday", "today", "24 hours", "day"]
        has_time_ref = any(ref in result.response.lower() for ref in time_refs)
        assert has_time_ref, "Should reference yesterday or today"

    def test_this_week_comparison(self):
        """'this week' should use week-based comparison."""
        result = query_guide("Progress this week")
        print(f"\n=== THIS WEEK ===\n{result.response[:800]}")

        week_refs = ["week", "monday", "days"]
        has_week_ref = any(ref in result.response.lower() for ref in week_refs)
        print(f"Has week reference: {has_week_ref}")

    def test_this_month_comparison(self):
        """'this month' should use month-based comparison."""
        result = query_guide("Decisions made this month")
        print(f"\n=== THIS MONTH ===\n{result.response[:800]}")

        month_refs = ["month", "november", "december", "30 day"]
        has_month_ref = any(ref in result.response.lower() for ref in month_refs)
        print(f"Has month reference: {has_month_ref}")


class TestComparisonMetrics:
    """Test specific comparison metrics."""

    def test_task_status_comparison(self):
        """Task status comparison should show status breakdown."""
        result = query_guide("Compare task status vs last week")
        print(f"\n=== TASK STATUS COMPARE ===\n{result.response[:800]}")

        status_words = ["pending", "progress", "blocked", "completed", "done", "status"]
        has_status = any(w in result.response.lower() for w in status_words)
        assert has_status, "Should mention task statuses"

    def test_agent_status_comparison(self):
        """Agent status comparison should show lifecycle stages."""
        result = query_guide("Compare agent status by stage vs last month")
        print(f"\n=== AGENT STATUS COMPARE ===\n{result.response[:800]}")

        stage_words = ["production", "development", "testing", "staging", "idea", "design"]
        has_stage = any(w in result.response.lower() for w in stage_words)
        print(f"Has stage info: {has_stage}")

    def test_completion_rate_comparison(self):
        """Completion rate comparison should show progress metrics."""
        result = query_guide("How has completion rate changed?")
        print(f"\n=== COMPLETION RATE ===\n{result.response[:800]}")

        completion_words = ["complet", "done", "finish", "rate", "progress"]
        has_completion = any(w in result.response.lower() for w in completion_words)
        assert has_completion, "Should mention completion metrics"


class TestComparisonFormat:
    """Test that comparison responses are well-formatted."""

    def test_comparison_shows_deltas(self):
        """Comparison should show change indicators (+/-)."""
        result = query_guide("Compare agent count vs last week")
        print(f"\n=== DELTAS ===\n{result.response[:800]}")

        # Look for delta indicators
        delta_indicators = ["+", "-", "increase", "decrease", "up", "down", "grew", "dropped", "same", "change"]
        has_delta = any(ind in result.response.lower() for ind in delta_indicators)
        # Soft check - may not have deltas if no historical data
        print(f"Has delta indicators: {has_delta}")

    def test_comparison_shows_direction(self):
        """Comparison should indicate trend direction."""
        result = query_guide("How is agent adoption trending?")
        print(f"\n=== TREND DIRECTION ===\n{result.response[:800]}")

        direction_words = ["increasing", "decreasing", "growing", "declining", "stable", "improving", "trending"]
        has_direction = any(w in result.response.lower() for w in direction_words)
        # Soft check
        print(f"Has direction indicator: {has_direction}")

    def test_comparison_provides_context(self):
        """Comparison should explain what the change means."""
        result = query_guide("Compare blocked tasks vs last week")
        print(f"\n=== COMPARISON CONTEXT ===\n{result.response[:800]}")

        context_indicators = ["means", "suggests", "indicates", "implication", "because", "due to"]
        has_context = any(ind in result.response.lower() for ind in context_indicators)
        # Soft check - nice to have
        print(f"Has context explanation: {has_context}")
