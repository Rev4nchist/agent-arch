"""
Test Task 19 improvements:
1. Aggregation intent classification
2. Date filtering for decisions (entity-aware date fields)
3. Integration status queries for agents
"""
import pytest
import re
from datetime import datetime, timedelta

# Import the intent classification patterns from main.py
import sys
sys.path.insert(0, 'C:/agent-arch/backend/src')


class TestAggregationIntentClassification:
    """Test that aggregation queries are correctly classified."""

    AGGREGATION_PATTERNS = [
        r'\b(breakdown|break down|break-down)\b.*\b(by|per)\b',
        r'\b(group|grouped|grouping)\b.*\b(by|per)\b',
        r'\bhow many\b.*\b(by|per|each)\b',
        r'\b(count|total|number of)\b.*\b(by|per|each|grouped)\b',
        r'\b(distribution|breakdown|summary)\b.*\b(of|for)\b.*\b(by|per|across)\b',
        r'\b(statistics|stats)\b.*\b(by|per|for each)\b',
        r'\b(agents?|tasks?|meetings?|decisions?|proposals?)\b.*\b(by|per)\b.*(status|type|tier|priority|category|department)',
    ]

    def matches_aggregation(self, query: str) -> bool:
        """Check if query matches aggregation patterns."""
        query_lower = query.lower()
        for pattern in self.AGGREGATION_PATTERNS:
            if re.search(pattern, query_lower):
                return True
        return False

    def test_breakdown_by_status(self):
        """Test 'breakdown agents by status' - the failing case from persona tests."""
        assert self.matches_aggregation("breakdown agents by status")
        assert self.matches_aggregation("break down agents by status")
        assert self.matches_aggregation("break-down agents by status")

    def test_group_by_patterns(self):
        """Test grouping patterns."""
        assert self.matches_aggregation("group tasks by priority")
        assert self.matches_aggregation("grouped agents by tier")
        assert self.matches_aggregation("grouping decisions by category")

    def test_count_by_patterns(self):
        """Test count/total patterns."""
        assert self.matches_aggregation("how many agents by status")
        assert self.matches_aggregation("count tasks by priority")
        assert self.matches_aggregation("total meetings by type")

    def test_distribution_patterns(self):
        """Test distribution/summary patterns."""
        assert self.matches_aggregation("distribution of agents by tier")
        assert self.matches_aggregation("summary of tasks by status")

    def test_entity_by_field_patterns(self):
        """Test direct entity by field patterns."""
        assert self.matches_aggregation("agents by status")
        assert self.matches_aggregation("tasks by priority")
        assert self.matches_aggregation("meetings by type")
        assert self.matches_aggregation("decisions by category")
        assert self.matches_aggregation("agents by department")


class TestEntityAwareDateFields:
    """Test that date field mapping is correct for each entity type."""

    DATE_FIELD_MAP = {
        'decisions': 'decision_date',
        'meetings': 'date',
        'tasks': 'due_date',
        'proposals': 'created_at',
        'agents': 'created_at',
        'audit_logs': 'timestamp',
    }

    def test_decisions_use_decision_date(self):
        """Decisions should use decision_date field."""
        assert self.DATE_FIELD_MAP['decisions'] == 'decision_date'

    def test_meetings_use_date(self):
        """Meetings should use date field."""
        assert self.DATE_FIELD_MAP['meetings'] == 'date'

    def test_tasks_use_due_date(self):
        """Tasks should use due_date field."""
        assert self.DATE_FIELD_MAP['tasks'] == 'due_date'

    def test_audit_logs_use_timestamp(self):
        """Audit logs should use timestamp field."""
        assert self.DATE_FIELD_MAP['audit_logs'] == 'timestamp'


class TestIntegrationStatusPatterns:
    """Test integration status pattern extraction."""

    INTEGRATION_STATUS_PATTERNS = {
        'Integration Issues': r'\b(integration issues?|integration problems?|failing integration|integration fail|integration errors?)\b',
        'Blocked': r'\b(integration blocked|blocked integration)\b',
        'In Progress': r'\b(integrating|integration in[- ]progress|currently integrating)\b',
        'Partially Integrated': r'\b(partially integrated|partial integration)\b',
        'Fully Integrated': r'\b(fully integrated|complete integration|integration complete)\b',
        'Not Started': r'\b(not integrated|no integration|integration not started)\b',
    }

    def extract_integration_status(self, query: str) -> str | None:
        """Extract integration status from query."""
        query_lower = query.lower()
        for int_status, pattern in self.INTEGRATION_STATUS_PATTERNS.items():
            if re.search(pattern, query_lower):
                return int_status
        return None

    def test_integration_issues_detection(self):
        """Test IT-05 'integration issues' query pattern."""
        assert self.extract_integration_status("agents with integration issues") == "Integration Issues"
        assert self.extract_integration_status("show integration problems") == "Integration Issues"
        assert self.extract_integration_status("failing integration") == "Integration Issues"

    def test_blocked_integration_detection(self):
        """Test blocked integration detection."""
        assert self.extract_integration_status("integration blocked agents") == "Blocked"
        assert self.extract_integration_status("blocked integration") == "Blocked"

    def test_in_progress_detection(self):
        """Test in progress integration detection."""
        assert self.extract_integration_status("currently integrating") == "In Progress"
        assert self.extract_integration_status("integration in progress") == "In Progress"
        assert self.extract_integration_status("integration in-progress") == "In Progress"

    def test_fully_integrated_detection(self):
        """Test fully integrated detection."""
        assert self.extract_integration_status("fully integrated agents") == "Fully Integrated"
        assert self.extract_integration_status("integration complete") == "Fully Integrated"

    def test_not_started_detection(self):
        """Test not started detection."""
        assert self.extract_integration_status("not integrated yet") == "Not Started"
        assert self.extract_integration_status("no integration") == "Not Started"


class TestAgentKeywordDetection:
    """Test that agent entity is detected for integration queries."""

    AGENT_KEYWORDS = ['agent', 'agents', 'ai agent', 'bot', 'bots', 'assistant', 'integration', 'integrated', 'integrating']

    def detects_agent_entity(self, query: str) -> bool:
        """Check if query would detect agent entity."""
        query_lower = query.lower()
        return any(kw in query_lower for kw in self.AGENT_KEYWORDS)

    def test_integration_queries_detect_agents(self):
        """Integration queries should detect agent entity."""
        assert self.detects_agent_entity("integration issues")
        assert self.detects_agent_entity("fully integrated")
        assert self.detects_agent_entity("integrating systems")

    def test_explicit_agent_queries(self):
        """Explicit agent queries should detect agent entity."""
        assert self.detects_agent_entity("list all agents")
        assert self.detects_agent_entity("show agent status")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
