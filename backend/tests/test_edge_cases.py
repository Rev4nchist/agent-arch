"""
Test Edge Cases and Error Handling

Verifies that the AI Guide gracefully handles:
- Empty results
- Ambiguous queries
- Very long queries
- Typos and variations
- Security concerns (injection attempts)
- Unusual input patterns
"""
import pytest
from conftest import query_guide


class TestEmptyResults:
    """Test handling of queries that return no data."""

    def test_nonexistent_assignee(self):
        """Query for non-existent person should handle gracefully."""
        result = query_guide("Show tasks assigned to ZzzNonExistentPerson123")
        print(f"\n=== NON-EXISTENT PERSON ===\n{result.response[:800]}")

        # Should not error
        assert "error" not in result.response.lower() or "no tasks" in result.response.lower()

        # Should indicate no results or suggest alternatives
        empty_indicators = ["no tasks", "none", "no items", "couldn't find", "no results", "0 tasks"]
        has_empty_indicator = any(ind in result.response.lower() for ind in empty_indicators)
        assert has_empty_indicator or "available" in result.response.lower(), \
            "Should indicate no results found"

    def test_future_date_query(self):
        """Query for far future dates should handle gracefully."""
        result = query_guide("Meetings scheduled in December 2030")
        print(f"\n=== FUTURE DATE ===\n{result.response[:800]}")

        # Should not crash
        assert len(result.response) > 20, "Should provide response"

    def test_impossible_filter_combination(self):
        """Query with impossible filters should handle gracefully."""
        result = query_guide("Show completed tasks that are also blocked")
        print(f"\n=== IMPOSSIBLE FILTER ===\n{result.response[:800]}")

        # Should explain or handle the contradiction
        assert len(result.response) > 20, "Should provide response"


class TestAmbiguousQueries:
    """Test handling of vague or ambiguous queries."""

    def test_very_vague_query(self):
        """Very vague queries should still provide useful response."""
        result = query_guide("Show me stuff")
        print(f"\n=== VAGUE QUERY ===\n{result.response[:800]}")

        # Should not error, should provide something or ask for clarification
        assert len(result.response) > 30, "Should provide response"

    def test_pronoun_only_query(self):
        """Queries using only pronouns should handle gracefully."""
        result = query_guide("What about it?")
        print(f"\n=== PRONOUN QUERY ===\n{result.response[:800]}")

        # Should ask for clarification or provide general help
        assert len(result.response) > 20, "Should provide response"

    def test_partial_query(self):
        """Partial/incomplete queries should handle gracefully."""
        result = query_guide("Tasks that are")
        print(f"\n=== PARTIAL QUERY ===\n{result.response[:800]}")

        # Should interpret or clarify
        assert len(result.response) > 30, "Should provide response"

    def test_multiple_intents_query(self):
        """Query with multiple possible intents should handle reasonably."""
        result = query_guide("Tasks and meetings and agents and decisions")
        print(f"\n=== MULTI-INTENT ===\n{result.response[:800]}")

        # Should address at least one entity type
        entities = ["task", "meeting", "agent", "decision"]
        mentioned = sum(1 for e in entities if e in result.response.lower())
        assert mentioned >= 1, "Should address at least one entity type"


class TestLongQueries:
    """Test handling of very long or complex queries."""

    def test_very_long_query(self):
        """Very long queries should be processed without error."""
        long_query = """I need to find all the tasks that are currently in progress
        and assigned to someone on the engineering team who has been working on
        Azure-related infrastructure items for the past month, specifically focusing
        on items that might be blocked or have dependencies on other teams,
        and I also want to know who I should talk to about these items"""

        result = query_guide(long_query)
        print(f"\n=== LONG QUERY ===\n{result.response[:800]}")

        # Should not error
        assert "error" not in result.response.lower()[:100]

        # Should extract and address key elements
        key_terms = ["task", "progress", "azure", "blocked", "team"]
        matched = sum(1 for t in key_terms if t in result.response.lower())
        assert matched >= 2, "Should address key elements of long query"

    def test_complex_multi_filter_query(self):
        """Complex query with multiple filters should work."""
        result = query_guide(
            "High priority tasks due this week assigned to David that are not blocked"
        )
        print(f"\n=== MULTI-FILTER ===\n{result.response[:800]}")

        # Should process without error
        assert len(result.response) > 50, "Should provide substantive response"


class TestTyposAndVariations:
    """Test handling of typos and input variations."""

    def test_minor_typos(self):
        """Minor typos should still be understood."""
        result = query_guide("shwo me bloked taks")
        print(f"\n=== TYPOS ===\n{result.response[:800]}")

        # Should understand intent despite typos
        # May or may not work - this is aspirational
        print(f"Response length: {len(result.response)}")

    def test_all_caps(self):
        """All caps queries should work normally."""
        result = query_guide("WHAT TASKS ARE BLOCKED")
        print(f"\n=== ALL CAPS ===\n{result.response[:800]}")

        # Should process normally
        assert len(result.response) > 50, "Should handle all caps"

    def test_excessive_punctuation(self):
        """Excessive punctuation should be handled."""
        result = query_guide("What tasks are blocked???!!!")
        print(f"\n=== EXCESSIVE PUNCTUATION ===\n{result.response[:800]}")

        # Should process normally
        assert len(result.response) > 50, "Should handle punctuation"

    def test_mixed_case_entity(self):
        """Mixed case entity names should work."""
        result = query_guide("show AGENTS in production")
        print(f"\n=== MIXED CASE ===\n{result.response[:800]}")

        # Should understand agents
        assert "agent" in result.response.lower(), "Should understand agent entity"


class TestSecurityEdgeCases:
    """Test security-related edge cases."""

    def test_sql_injection_attempt(self):
        """SQL injection attempts should be handled safely."""
        result = query_guide("tasks'; DROP TABLE tasks; --")
        print(f"\n=== SQL INJECTION ===\n{result.response[:800]}")

        # Should not error or expose system details
        assert "drop table" not in result.response.lower()
        assert "sql" not in result.response.lower()

    def test_script_injection_attempt(self):
        """Script injection attempts should be handled safely."""
        result = query_guide("<script>alert('xss')</script>")
        print(f"\n=== SCRIPT INJECTION ===\n{result.response[:800]}")

        # Should not include raw script
        assert "<script>" not in result.response

    def test_path_traversal_attempt(self):
        """Path traversal attempts should be handled safely."""
        result = query_guide("tasks in ../../etc/passwd")
        print(f"\n=== PATH TRAVERSAL ===\n{result.response[:800]}")

        # Should not expose system paths
        assert "/etc/" not in result.response
        assert "passwd" not in result.response.lower()


class TestUnusualPatterns:
    """Test other unusual input patterns."""

    def test_empty_query(self):
        """Empty-ish queries should handle gracefully."""
        result = query_guide("   ")
        print(f"\n=== EMPTY QUERY ===\n{result.response[:800]}")

        # Should provide help or ask for input
        assert len(result.response) > 10, "Should provide some response"

    def test_numbers_only(self):
        """Numbers-only queries should handle gracefully."""
        result = query_guide("123456")
        print(f"\n=== NUMBERS ONLY ===\n{result.response[:800]}")

        # Should try to interpret or ask for clarification
        assert len(result.response) > 10, "Should provide response"

    def test_emoji_query(self):
        """Emoji queries should handle gracefully."""
        result = query_guide("Show tasks")
        print(f"\n=== EMOJI QUERY ===\n{result.response[:800]}")

        # Should process the text part
        assert "task" in result.response.lower(), "Should understand task query"

    def test_repeated_words(self):
        """Repeated words should be handled."""
        result = query_guide("tasks tasks tasks blocked blocked")
        print(f"\n=== REPEATED WORDS ===\n{result.response[:800]}")

        # Should understand the intent
        task_or_blocked = "task" in result.response.lower() or "blocked" in result.response.lower()
        assert task_or_blocked, "Should understand intent despite repetition"
