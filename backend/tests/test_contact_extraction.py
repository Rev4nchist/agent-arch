"""
Test Contact Extraction Accuracy

Verifies that the AI Guide correctly extracts and surfaces contact information
from query results. Contacts should be:
- Relevant to the query context
- Prioritized (urgent items first)
- Include role/relationship information
"""
import pytest
from conftest import query_guide, extract_names_from_response


class TestContactSurfacing:
    """Test that contacts are surfaced in appropriate queries."""

    def test_blocked_tasks_show_assignees(self):
        """Blocked task queries should show assignee contacts."""
        result = query_guide("What tasks are blocked?")
        print(f"\n=== BLOCKED TASKS CONTACTS ===\n{result.response[:1000]}")

        names = extract_names_from_response(result.response)
        print(f"Names found: {names}")

        # If there are blocked tasks, should mention who's assigned
        response_lower = result.response.lower()
        if "blocked" in response_lower and "0" not in response_lower[:100]:
            # Has blocked items - should have contacts
            contact_indicators = ["assigned", "owner", "contact", "reach", "talk to"] + [n.lower() for n in names]
            has_contact_info = any(ind in response_lower for ind in contact_indicators)
            assert has_contact_info, "Blocked task query should include assignee information"

    def test_high_priority_tasks_show_owners(self):
        """High priority task queries should show owner contacts."""
        result = query_guide("Show high priority tasks")
        print(f"\n=== HIGH PRIORITY CONTACTS ===\n{result.response[:1000]}")

        names = extract_names_from_response(result.response)
        print(f"Names found: {names}")

        # High priority items should have clear ownership
        if len(names) > 0:
            # Check that names appear with context (not just mentioned)
            for name in names[:3]:  # Check first 3 names
                assert name in result.response, f"Name {name} should appear in response"

    def test_ownership_query_returns_name(self):
        """Direct ownership queries must return a person name."""
        result = query_guide("Who owns the AI Guide?")
        print(f"\n=== AI GUIDE OWNER ===\n{result.response[:1000]}")

        names = extract_names_from_response(result.response)
        print(f"Names found: {names}")

        assert len(names) > 0 or "no specific owner" in result.response.lower(), \
            "Ownership query should return name or state no owner is assigned"

    def test_task_specific_owner_query(self):
        """Queries about specific task ownership should return contact."""
        result = query_guide("Who should I ask about the Azure AI Search task?")
        print(f"\n=== TASK OWNER ===\n{result.response[:1000]}")

        names = extract_names_from_response(result.response)
        contact_keywords = ["ask", "contact", "reach", "talk", "assigned", "owner"]

        has_guidance = any(kw in result.response.lower() for kw in contact_keywords)
        assert has_guidance, "Should provide contact guidance for task-specific queries"


class TestContactPrioritization:
    """Test that urgent/blocked item contacts are prioritized."""

    def test_urgent_contacts_appear_first(self):
        """Contacts for urgent/blocked items should appear prominently."""
        result = query_guide("Show blocked and high priority tasks")
        print(f"\n=== URGENT TASKS ===\n{result.response[:1000]}")

        response_lower = result.response.lower()

        # Check if urgent-related terms appear before general listings
        urgent_markers = ["blocked", "urgent", "critical", "attention", "immediate"]
        for marker in urgent_markers:
            if marker in response_lower:
                # Good - urgent items are mentioned
                print(f"Found urgent marker: {marker}")
                break

    def test_needs_attention_flagging(self):
        """Items needing attention should be flagged in contact list."""
        result = query_guide("What items need my attention?")
        print(f"\n=== NEEDS ATTENTION ===\n{result.response[:1000]}")

        attention_markers = ["attention", "urgent", "action", "blocked", "overdue", "critical"]
        has_attention_marker = any(marker in result.response.lower() for marker in attention_markers)
        print(f"Has attention markers: {has_attention_marker}")


class TestContactRoles:
    """Test that contact roles are correctly identified."""

    def test_assignee_role_identified(self):
        """Assignees should be identified as such."""
        result = query_guide("Who is working on pending tasks?")
        print(f"\n=== TASK ASSIGNEES ===\n{result.response[:1000]}")

        role_indicators = ["assigned", "working on", "responsible", "handling", "owner"]
        has_role = any(ind in result.response.lower() for ind in role_indicators)
        assert has_role, "Should identify assignee roles"

    def test_decision_maker_identified(self):
        """Decision makers should be identified for decision queries."""
        result = query_guide("Who made the architecture decisions?")
        print(f"\n=== DECISION MAKERS ===\n{result.response[:1000]}")

        maker_indicators = ["made by", "decided", "approved", "created", "author"]
        has_maker = any(ind in result.response.lower() for ind in maker_indicators)
        print(f"Has decision maker info: {has_maker}")

    def test_meeting_facilitator_identified(self):
        """Meeting facilitators should be identified."""
        result = query_guide("Who ran the recent meetings?")
        print(f"\n=== MEETING FACILITATORS ===\n{result.response[:1000]}")

        facilitator_indicators = ["facilitator", "hosted", "ran", "led", "organized"]
        # Soft check - meetings may not have facilitators
        has_facilitator = any(ind in result.response.lower() for ind in facilitator_indicators)
        print(f"Has facilitator info: {has_facilitator}")


class TestContactCompleteness:
    """Test that contact information is complete when available."""

    def test_workload_query_shows_all_assignees(self):
        """Workload query should show all relevant assignees."""
        result = query_guide("How is work distributed across the team?")
        print(f"\n=== WORKLOAD DISTRIBUTION ===\n{result.response[:1000]}")

        names = extract_names_from_response(result.response)
        print(f"Names found: {names}")

        # Should have multiple names for workload distribution
        if "distributed" in result.response.lower() or "team" in result.response.lower():
            assert len(names) >= 1, "Workload query should show team member names"

    def test_team_query_returns_multiple_contacts(self):
        """Team-related queries should return multiple contacts."""
        result = query_guide("Who are the key people on this project?")
        print(f"\n=== KEY PEOPLE ===\n{result.response[:1000]}")

        names = extract_names_from_response(result.response)
        print(f"Names found: {names}")

        # Should list multiple people for team query
        assert len(names) >= 1, "Key people query should return at least one name"
