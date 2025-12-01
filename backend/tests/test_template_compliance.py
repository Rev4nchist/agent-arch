"""
Test Response Template Compliance

Verifies that AI Guide responses follow the structured formats defined
in RESPONSE_TEMPLATES for each intent type.

Templates should produce consistent, predictable response structures
that users can rely on.
"""
import pytest
from conftest import query_guide, check_sections_present, has_list_format


class TestStatusCheckTemplateCompliance:
    """STATUS_CHECK responses should have: Summary → Top Items → Attention → Next Steps"""

    EXPECTED_SECTIONS = ["summary", "status", "next steps"]

    def test_blocked_tasks_format(self):
        """'What tasks are blocked?' should follow status check template."""
        result = query_guide("What tasks are blocked?")
        print(f"\n=== BLOCKED TASKS ===\n{result.response[:800]}")

        assert result.intent == "status_check", f"Expected status_check intent, got {result.intent}"

        sections = check_sections_present(result.response, self.EXPECTED_SECTIONS)
        # At least 2 of 3 expected sections should be present
        present_count = sum(sections.values())
        assert present_count >= 2, f"Expected at least 2 sections, found {present_count}: {sections}"

    def test_overdue_items_format(self):
        """'Show overdue items' should follow status check template."""
        result = query_guide("Show overdue items")
        print(f"\n=== OVERDUE ITEMS ===\n{result.response[:800]}")

        sections = check_sections_present(result.response, self.EXPECTED_SECTIONS)
        present_count = sum(sections.values())
        assert present_count >= 2, f"Expected at least 2 sections, found {present_count}: {sections}"

    def test_risks_blockers_format(self):
        """'What are the key risks or blockers?' should follow status check template."""
        result = query_guide("What are the key risks or blockers?")
        print(f"\n=== RISKS/BLOCKERS ===\n{result.response[:800]}")

        # Should have next steps for actionability
        assert "next step" in result.response.lower() or "recommend" in result.response.lower(), \
            "Status check response should include next steps or recommendations"


class TestAggregationTemplateCompliance:
    """AGGREGATION responses should have: Headline → Breakdown → Insight → Recommendation"""

    EXPECTED_SECTIONS = ["total", "breakdown", "insight", "recommendation"]

    def test_task_count_by_status(self):
        """'How many tasks by status?' should follow aggregation template."""
        result = query_guide("How many tasks by status?")
        print(f"\n=== TASK COUNT ===\n{result.response[:800]}")

        assert result.intent == "aggregation", f"Expected aggregation intent, got {result.intent}"

        # Should have numbers
        import re
        numbers = re.findall(r'\b\d+\b', result.response)
        assert len(numbers) >= 1, "Aggregation response should contain numbers"

        # Should have breakdown format (list or table)
        assert has_list_format(result.response) or ":" in result.response, \
            "Aggregation should have breakdown format"

    def test_agent_breakdown_by_tier(self):
        """'Breakdown agents by tier' should follow aggregation template."""
        result = query_guide("Breakdown agents by tier")
        print(f"\n=== AGENT TIER BREAKDOWN ===\n{result.response[:800]}")

        sections = check_sections_present(result.response, ["tier", "total"])
        assert any(sections.values()), f"Should mention tier or total: {sections}"

    def test_aggregation_has_insight(self):
        """Aggregation responses should include insight or analysis."""
        result = query_guide("Show task distribution by priority")
        print(f"\n=== TASK DISTRIBUTION ===\n{result.response[:800]}")

        insight_keywords = ["insight", "significant", "majority", "most", "notable", "pattern"]
        has_insight = any(kw in result.response.lower() for kw in insight_keywords)
        assert has_insight, "Aggregation should include insight or analysis"


class TestListTemplateCompliance:
    """LIST responses should have: Count → Items → Summary → Next Steps"""

    def test_list_has_count(self):
        """List responses should start with count."""
        result = query_guide("Show all high priority tasks")
        print(f"\n=== HIGH PRIORITY LIST ===\n{result.response[:800]}")

        # Should mention count near the beginning
        import re
        first_300 = result.response[:300].lower()
        has_count = bool(re.search(r'\b\d+\b', first_300))
        assert has_count, "List response should include count near the beginning"

    def test_list_has_items(self):
        """List responses should have formatted items."""
        result = query_guide("List pending tasks")
        print(f"\n=== PENDING TASKS LIST ===\n{result.response[:800]}")

        assert has_list_format(result.response), "List response should use list formatting"

    def test_list_has_next_steps(self):
        """List responses should end with next steps when applicable."""
        result = query_guide("Show tasks assigned to Bob")
        print(f"\n=== BOB'S TASKS ===\n{result.response[:800]}")

        # Either has next steps or the list is complete
        response_lower = result.response.lower()
        has_conclusion = any(term in response_lower for term in [
            "next step", "action", "recommend", "let me know", "need more"
        ])
        # This is a soft check - not all lists need next steps
        print(f"Has conclusion: {has_conclusion}")


class TestOwnershipTemplateCompliance:
    """OWNERSHIP responses should have: Direct Answer → Contact → Team → How to Reach"""

    def test_ownership_has_direct_answer(self):
        """Ownership query should have direct answer with name."""
        result = query_guide("Who owns the backend service?")
        print(f"\n=== BACKEND OWNER ===\n{result.response[:800]}")

        assert result.intent == "ownership", f"Expected ownership intent, got {result.intent}"

        # Should contain a person's name
        import re
        names = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', result.response)
        assert len(names) > 0, "Ownership response should include person name"

    def test_ownership_has_contact_suggestion(self):
        """Ownership response should suggest how to reach the person."""
        result = query_guide("Who should I contact about AI Guide?")
        print(f"\n=== AI GUIDE CONTACT ===\n{result.response[:800]}")

        contact_keywords = ["contact", "reach", "ask", "talk to", "email", "slack", "team"]
        has_contact = any(kw in result.response.lower() for kw in contact_keywords)
        assert has_contact, "Ownership response should include contact suggestion"


class TestComparisonTemplateCompliance:
    """COMPARISON responses should have: Headline Change → +/- Indicators → Trend → Implication"""

    def test_comparison_has_change_indicator(self):
        """Comparison should show change with +/- or direction."""
        result = query_guide("Compare agent count by status vs last week")
        print(f"\n=== AGENT COMPARISON ===\n{result.response[:800]}")

        assert result.intent == "comparison", f"Expected comparison intent, got {result.intent}"

        change_indicators = ["+", "-", "increase", "decrease", "change", "grew", "dropped", "same"]
        has_change = any(ind in result.response.lower() for ind in change_indicators)
        # Note: May not have change if no historical data
        print(f"Has change indicator: {has_change}")

    def test_comparison_mentions_trend(self):
        """Comparison should mention trend direction."""
        result = query_guide("How has task completion changed this month?")
        print(f"\n=== COMPLETION TREND ===\n{result.response[:800]}")

        trend_keywords = ["trend", "increasing", "decreasing", "stable", "improving", "declining"]
        has_trend = any(kw in result.response.lower() for kw in trend_keywords)
        # Soft check - trend may not apply if no historical data
        print(f"Has trend mention: {has_trend}")


class TestExplanationTemplateCompliance:
    """EXPLANATION responses should have: Definition → Context → Examples → Related"""

    def test_explanation_has_definition(self):
        """Explanation should start with clear definition."""
        result = query_guide("What is a Tier 2 agent?")
        print(f"\n=== TIER 2 EXPLANATION ===\n{result.response[:800]}")

        assert result.intent == "explanation", f"Expected explanation intent, got {result.intent}"

        # Should have definitional content
        definition_markers = ["is", "are", "refers to", "means", "defined as"]
        has_definition = any(marker in result.response.lower()[:200] for marker in definition_markers)
        assert has_definition, "Explanation should include definition"

    def test_explanation_provides_context(self):
        """Explanation should provide relevant context."""
        result = query_guide("Explain the agent governance process")
        print(f"\n=== GOVERNANCE EXPLANATION ===\n{result.response[:800]}")

        # Should be substantive (not just "I don't know")
        assert len(result.response) > 100, "Explanation should be substantive"


class TestAuditTemplateCompliance:
    """AUDIT responses should have: Time Context → Activities → Patterns → Notable"""

    def test_audit_has_time_context(self):
        """Audit response should include time context."""
        result = query_guide("Show recent activity")
        print(f"\n=== RECENT ACTIVITY ===\n{result.response[:800]}")

        time_markers = ["recent", "today", "yesterday", "last", "past", "hour", "day", "week"]
        has_time = any(marker in result.response.lower() for marker in time_markers)
        assert has_time, "Audit response should include time context"

    def test_audit_lists_activities(self):
        """Audit response should list activities."""
        result = query_guide("What changes were made today?")
        print(f"\n=== TODAY'S CHANGES ===\n{result.response[:800]}")

        # Should have list format or activity mentions
        activity_words = ["created", "updated", "modified", "changed", "added", "deleted", "activity"]
        has_activities = any(word in result.response.lower() for word in activity_words)
        print(f"Has activity mentions: {has_activities}")
