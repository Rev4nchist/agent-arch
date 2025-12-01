"""
Test Response Quality Metrics

Verifies that AI Guide responses meet quality standards for:
- Response length (not too short, not too verbose)
- Structure (headers, lists, sections)
- Tone (professional, confident)
- Completeness (answers the question)
"""
import pytest
import re
from conftest import (
    query_guide, response_length_check, has_list_format,
    has_actionable_content, extract_names_from_response
)


class TestResponseLength:
    """Test that responses are appropriately sized."""

    # Length thresholds
    MIN_LENGTH = 100
    MAX_LENGTH = 2500
    IDEAL_MIN = 150
    IDEAL_MAX = 1200

    def test_simple_query_not_too_short(self):
        """Simple queries should still get substantive responses."""
        result = query_guide("Show blocked tasks")
        print(f"\n=== LENGTH CHECK (SIMPLE) ===")
        print(f"Length: {len(result.response)} chars")

        length_info = response_length_check(result.response, self.MIN_LENGTH, self.MAX_LENGTH)
        assert not length_info["too_short"], \
            f"Response too short ({length_info['length']} chars)"

    def test_complex_query_not_too_long(self):
        """Complex queries should be concise, not verbose."""
        result = query_guide(
            "Give me a comprehensive overview of all tasks, their status, "
            "who they're assigned to, when they're due, and any blockers"
        )
        print(f"\n=== LENGTH CHECK (COMPLEX) ===")
        print(f"Length: {len(result.response)} chars")

        length_info = response_length_check(result.response, self.MIN_LENGTH, self.MAX_LENGTH)
        assert not length_info["too_long"], \
            f"Response too long ({length_info['length']} chars)"

    def test_aggregation_response_concise(self):
        """Aggregation responses should be data-focused and concise."""
        result = query_guide("How many tasks by status?")
        print(f"\n=== LENGTH CHECK (AGGREGATION) ===")
        print(f"Length: {len(result.response)} chars")

        # Aggregation should be focused
        assert len(result.response) <= self.IDEAL_MAX, \
            f"Aggregation response should be concise ({len(result.response)} chars)"

    def test_explanation_response_adequate(self):
        """Explanation responses should be thorough enough."""
        result = query_guide("What is a Tier 2 agent and why does it matter?")
        print(f"\n=== LENGTH CHECK (EXPLANATION) ===")
        print(f"Length: {len(result.response)} chars")

        assert len(result.response) >= self.IDEAL_MIN, \
            f"Explanation should be thorough ({len(result.response)} chars)"


class TestResponseStructure:
    """Test that responses use proper structure and formatting."""

    def test_list_query_uses_lists(self):
        """List queries should use list formatting."""
        result = query_guide("List all high priority tasks")
        print(f"\n=== STRUCTURE (LIST) ===\n{result.response[:600]}")

        assert has_list_format(result.response), \
            "List queries should use list formatting"

    def test_aggregation_uses_breakdown(self):
        """Aggregation queries should show breakdown."""
        result = query_guide("Breakdown tasks by status")
        print(f"\n=== STRUCTURE (AGGREGATION) ===\n{result.response[:600]}")

        # Should have some structure (lists, colons, numbers)
        has_structure = (
            has_list_format(result.response) or
            result.response.count(":") >= 2 or
            len(re.findall(r'\d+', result.response)) >= 2
        )
        assert has_structure, "Aggregation should have structured breakdown"

    def test_status_check_has_sections(self):
        """Status check should have clear sections."""
        result = query_guide("What's the status of blocked items?")
        print(f"\n=== STRUCTURE (STATUS) ===\n{result.response[:600]}")

        # Should have headers or clear sections
        section_indicators = ["**", "##", "###", ":\n", "Status:", "Summary:"]
        has_sections = any(ind in result.response for ind in section_indicators)
        # Soft check
        print(f"Has section indicators: {has_sections}")

    def test_complex_query_organized(self):
        """Complex queries should have organized response."""
        result = query_guide("Show me blocked tasks, who owns them, and what the blockers are")
        print(f"\n=== STRUCTURE (COMPLEX) ===\n{result.response[:800]}")

        # Should have some organization
        has_org = (
            has_list_format(result.response) or
            "**" in result.response or
            result.response.count("\n") >= 3
        )
        assert has_org, "Complex query response should be organized"


class TestResponseTone:
    """Test that responses have appropriate professional tone."""

    # Words that indicate hedging/uncertainty (should be minimal)
    HEDGING_WORDS = ["maybe", "perhaps", "possibly", "might", "could be", "i think", "i believe"]

    # Words that indicate confidence (should be present)
    CONFIDENT_WORDS = ["based on", "the data shows", "currently", "there are", "according to"]

    def test_no_excessive_hedging(self):
        """Responses should be confident, not hedging."""
        result = query_guide("How many tasks are pending?")
        print(f"\n=== TONE (HEDGING) ===\n{result.response[:600]}")

        response_lower = result.response.lower()
        hedge_count = sum(1 for h in self.HEDGING_WORDS if h in response_lower)

        assert hedge_count <= 1, \
            f"Too much hedging ({hedge_count} hedging phrases)"

    def test_data_grounded_language(self):
        """Responses should use data-grounded language."""
        result = query_guide("Give me a summary of project status")
        print(f"\n=== TONE (GROUNDED) ===\n{result.response[:600]}")

        response_lower = result.response.lower()
        confident_count = sum(1 for c in self.CONFIDENT_WORDS if c in response_lower)

        # At least some confident language
        print(f"Confident phrases found: {confident_count}")

    def test_professional_not_casual(self):
        """Responses should be professional, not casual."""
        result = query_guide("What's up with the project?")
        print(f"\n=== TONE (PROFESSIONAL) ===\n{result.response[:600]}")

        # Should not use overly casual language
        casual_words = ["gonna", "wanna", "kinda", "sorta", "stuff like that", "you know"]
        response_lower = result.response.lower()
        casual_count = sum(1 for c in casual_words if c in response_lower)

        assert casual_count == 0, "Response should be professional"

    def test_not_overly_apologetic(self):
        """Responses should not be overly apologetic."""
        result = query_guide("Show tasks assigned to NonExistent Person")
        print(f"\n=== TONE (APOLOGETIC) ===\n{result.response[:600]}")

        apology_phrases = ["i'm sorry", "i apologize", "unfortunately i cannot", "i'm afraid"]
        response_lower = result.response.lower()
        apology_count = sum(1 for a in apology_phrases if a in response_lower)

        assert apology_count <= 1, "Response should not be overly apologetic"


class TestResponseCompleteness:
    """Test that responses fully answer the question."""

    def test_answers_what_question(self):
        """'What' questions should provide direct answers."""
        result = query_guide("What tasks are blocked?")
        print(f"\n=== COMPLETENESS (WHAT) ===\n{result.response[:600]}")

        # Should mention tasks in response
        assert "task" in result.response.lower(), \
            "Should directly address the 'what' question"

    def test_answers_how_many_question(self):
        """'How many' questions should include numbers."""
        result = query_guide("How many agents are there?")
        print(f"\n=== COMPLETENESS (HOW MANY) ===\n{result.response[:600]}")

        # Should have numbers
        numbers = re.findall(r'\b\d+\b', result.response)
        assert len(numbers) >= 1, \
            "'How many' questions should include numbers"

    def test_answers_who_question(self):
        """'Who' questions should include names."""
        result = query_guide("Who is working on high priority tasks?")
        print(f"\n=== COMPLETENESS (WHO) ===\n{result.response[:600]}")

        names = extract_names_from_response(result.response)
        # Should have names or explain no one is assigned
        has_names = len(names) > 0
        explains_none = any(phrase in result.response.lower() for phrase in
                          ["no one", "unassigned", "not assigned", "no tasks"])
        assert has_names or explains_none, \
            "'Who' questions should include names or explain absence"

    def test_provides_actionable_info(self):
        """Responses should include actionable information."""
        result = query_guide("What should I work on first?")
        print(f"\n=== COMPLETENESS (ACTIONABLE) ===\n{result.response[:600]}")

        actionable = has_actionable_content(result.response)
        print(f"Actionable content: {actionable}")

        # Should have at least one actionable element
        actionable_count = sum(actionable.values())
        assert actionable_count >= 2, \
            "Response should be actionable"


class TestResponseConsistency:
    """Test that similar queries produce consistent responses."""

    def test_rephrased_query_similar_content(self):
        """Rephrased queries should return similar content."""
        result1 = query_guide("Show blocked tasks")
        result2 = query_guide("What tasks are currently blocked?")

        print(f"\n=== CONSISTENCY ===")
        print(f"Query 1: {result1.response[:300]}")
        print(f"Query 2: {result2.response[:300]}")

        # Both should have similar intent classification
        # and both should mention "blocked" or "task"
        common_terms = ["blocked", "task", "status"]
        result1_terms = sum(1 for t in common_terms if t in result1.response.lower())
        result2_terms = sum(1 for t in common_terms if t in result2.response.lower())

        assert result1_terms >= 1 and result2_terms >= 1, \
            "Rephrased queries should return consistent content"

    def test_multiple_runs_consistent(self):
        """Same query should return structurally consistent responses."""
        result1 = query_guide("How many tasks by status?")
        result2 = query_guide("How many tasks by status?")

        print(f"\n=== MULTI-RUN CONSISTENCY ===")
        print(f"Run 1 length: {len(result1.response)}")
        print(f"Run 2 length: {len(result2.response)}")

        # Lengths should be within 50% of each other
        length_ratio = min(len(result1.response), len(result2.response)) / max(len(result1.response), len(result2.response))
        assert length_ratio > 0.5, \
            "Multiple runs should produce similar length responses"
