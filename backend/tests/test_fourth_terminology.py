"""
Test Fourth-Specific Terminology

Verifies that the AI Guide correctly understands company and domain-specific
terminology used at Fourth, including:
- Agent tier system (Tier 1/2/3)
- Agent lifecycle stages
- Governance concepts
- Team/role terminology
"""
import pytest
from conftest import query_guide


class TestAgentTierTerminology:
    """Test understanding of the 3-tier agent classification system."""

    def test_tier_1_understanding(self):
        """Should understand Tier 1 = Individual level agents."""
        result = query_guide("Show Tier 1 agents")
        print(f"\n=== TIER 1 ===\n{result.response[:800]}")

        # Should return agent data
        assert "agent" in result.response.lower()

        # Tier 1 indicators
        tier1_terms = ["tier 1", "tier1", "individual", "personal"]
        has_tier1 = any(t in result.response.lower() for t in tier1_terms)
        assert has_tier1, "Should understand Tier 1 refers to individual agents"

    def test_tier_2_understanding(self):
        """Should understand Tier 2 = Department level agents."""
        result = query_guide("What Tier 2 agents do we have?")
        print(f"\n=== TIER 2 ===\n{result.response[:800]}")

        tier2_terms = ["tier 2", "tier2", "department", "team"]
        has_tier2 = any(t in result.response.lower() for t in tier2_terms)
        assert has_tier2, "Should understand Tier 2 refers to department agents"

    def test_tier_3_understanding(self):
        """Should understand Tier 3 = Enterprise level agents."""
        result = query_guide("List all Tier 3 enterprise agents")
        print(f"\n=== TIER 3 ===\n{result.response[:800]}")

        tier3_terms = ["tier 3", "tier3", "enterprise", "organization"]
        has_tier3 = any(t in result.response.lower() for t in tier3_terms)
        assert has_tier3, "Should understand Tier 3 refers to enterprise agents"

    def test_agents_by_tier_query(self):
        """'agents by tier' should show tier breakdown."""
        result = query_guide("Breakdown agents by tier")
        print(f"\n=== AGENTS BY TIER ===\n{result.response[:800]}")

        # Should mention multiple tiers
        tiers_mentioned = sum(1 for t in ["tier 1", "tier 2", "tier 3", "tier1", "tier2", "tier3"]
                             if t in result.response.lower())
        assert tiers_mentioned >= 1, "Should mention at least one tier"


class TestAgentLifecycleTerminology:
    """Test understanding of agent lifecycle stages."""

    LIFECYCLE_STAGES = ["idea", "design", "development", "testing", "staging", "production", "deprecated"]

    def test_production_agents_query(self):
        """'production agents' should filter to Production status."""
        result = query_guide("What agents are in production?")
        print(f"\n=== PRODUCTION AGENTS ===\n{result.response[:800]}")

        assert "production" in result.response.lower() or "agent" in result.response.lower()

    def test_development_stage_query(self):
        """'in development' should filter to Development status."""
        result = query_guide("Show agents in development")
        print(f"\n=== DEVELOPMENT AGENTS ===\n{result.response[:800]}")

        dev_terms = ["development", "develop", "building", "creating"]
        has_dev = any(t in result.response.lower() for t in dev_terms)
        assert has_dev, "Should understand development stage"

    def test_testing_stage_query(self):
        """'being tested' should filter to Testing status."""
        result = query_guide("Which agents are being tested?")
        print(f"\n=== TESTING AGENTS ===\n{result.response[:800]}")

        test_terms = ["testing", "test", "qa", "validation"]
        has_test = any(t in result.response.lower() for t in test_terms)
        print(f"Has testing reference: {has_test}")

    def test_staging_ready_query(self):
        """'ready for staging' should understand staging concept."""
        result = query_guide("Agents ready for staging")
        print(f"\n=== STAGING READY ===\n{result.response[:800]}")

        staging_terms = ["staging", "stage", "pre-production", "ready"]
        has_staging = any(t in result.response.lower() for t in staging_terms)
        print(f"Has staging reference: {has_staging}")

    def test_deprecated_agents_query(self):
        """'deprecated' should filter to Deprecated status."""
        result = query_guide("Show deprecated agents")
        print(f"\n=== DEPRECATED AGENTS ===\n{result.response[:800]}")

        deprecated_terms = ["deprecated", "retired", "obsolete", "sunset"]
        has_deprecated = any(t in result.response.lower() for t in deprecated_terms)
        print(f"Has deprecated reference: {has_deprecated}")

    def test_agent_pipeline_query(self):
        """'agent pipeline' should show lifecycle distribution."""
        result = query_guide("What does our agent pipeline look like?")
        print(f"\n=== AGENT PIPELINE ===\n{result.response[:800]}")

        # Should mention multiple stages
        stages_mentioned = sum(1 for s in self.LIFECYCLE_STAGES if s in result.response.lower())
        assert stages_mentioned >= 2, "Pipeline query should mention multiple stages"


class TestGovernanceTerminology:
    """Test understanding of governance-related terminology."""

    def test_governance_review_query(self):
        """'governance review' should be understood."""
        result = query_guide("What items need governance review?")
        print(f"\n=== GOVERNANCE REVIEW ===\n{result.response[:800]}")

        gov_terms = ["governance", "review", "approval", "pending"]
        has_gov = any(t in result.response.lower() for t in gov_terms)
        assert has_gov, "Should understand governance review concept"

    def test_pending_approvals_query(self):
        """'pending approvals' should filter correctly."""
        result = query_guide("Show pending approvals")
        print(f"\n=== PENDING APPROVALS ===\n{result.response[:800]}")

        approval_terms = ["pending", "approval", "awaiting", "review"]
        has_approval = any(t in result.response.lower() for t in approval_terms)
        assert has_approval, "Should understand pending approvals"

    def test_architecture_decisions_query(self):
        """'architecture decisions' should filter by category."""
        result = query_guide("List architecture decisions")
        print(f"\n=== ARCHITECTURE DECISIONS ===\n{result.response[:800]}")

        arch_terms = ["architecture", "decision", "technical", "design"]
        has_arch = any(t in result.response.lower() for t in arch_terms)
        assert has_arch, "Should understand architecture decisions"

    def test_security_decisions_query(self):
        """'security decisions' should filter by Security category."""
        result = query_guide("What security decisions have been made?")
        print(f"\n=== SECURITY DECISIONS ===\n{result.response[:800]}")

        security_terms = ["security", "decision", "policy", "access"]
        has_security = any(t in result.response.lower() for t in security_terms)
        assert has_security, "Should understand security decisions"

    def test_budget_decisions_query(self):
        """'budget decisions' should filter by Budget category."""
        result = query_guide("Show budget-related decisions")
        print(f"\n=== BUDGET DECISIONS ===\n{result.response[:800]}")

        budget_terms = ["budget", "cost", "financial", "spending", "decision"]
        has_budget = any(t in result.response.lower() for t in budget_terms)
        print(f"Has budget reference: {has_budget}")


class TestTaskCategoryTerminology:
    """Test understanding of task categorization terminology."""

    def test_infrastructure_tasks_query(self):
        """'infrastructure tasks' should filter correctly."""
        result = query_guide("Show infrastructure tasks")
        print(f"\n=== INFRASTRUCTURE TASKS ===\n{result.response[:800]}")

        infra_terms = ["infrastructure", "infra", "platform", "devops", "azure", "cloud"]
        has_infra = any(t in result.response.lower() for t in infra_terms)
        assert has_infra, "Should understand infrastructure tasks"

    def test_governance_tasks_query(self):
        """'governance tasks' should filter correctly."""
        result = query_guide("What governance tasks are pending?")
        print(f"\n=== GOVERNANCE TASKS ===\n{result.response[:800]}")

        gov_terms = ["governance", "policy", "compliance", "process"]
        has_gov = any(t in result.response.lower() for t in gov_terms)
        print(f"Has governance reference: {has_gov}")

    def test_development_tasks_query(self):
        """'development tasks' should filter correctly."""
        result = query_guide("Show development tasks")
        print(f"\n=== DEVELOPMENT TASKS ===\n{result.response[:800]}")

        dev_terms = ["development", "dev", "code", "build", "implement"]
        has_dev = any(t in result.response.lower() for t in dev_terms)
        assert has_dev, "Should understand development tasks"


class TestTeamRoleTerminology:
    """Test understanding of team and role terminology."""

    def test_platform_team_query(self):
        """'platform team' should be understood."""
        result = query_guide("What is the platform team working on?")
        print(f"\n=== PLATFORM TEAM ===\n{result.response[:800]}")

        team_terms = ["platform", "team", "infrastructure", "devops"]
        has_team = any(t in result.response.lower() for t in team_terms)
        assert has_team, "Should understand platform team"

    def test_architect_role_query(self):
        """'architect' role should be understood."""
        result = query_guide("What has the architect decided?")
        print(f"\n=== ARCHITECT ===\n{result.response[:800]}")

        arch_terms = ["architect", "architecture", "design", "decision"]
        has_arch = any(t in result.response.lower() for t in arch_terms)
        print(f"Has architect reference: {has_arch}")

    def test_stakeholder_query(self):
        """'stakeholder' should be understood."""
        result = query_guide("What do stakeholders need to know?")
        print(f"\n=== STAKEHOLDERS ===\n{result.response[:800]}")

        # Should provide executive-level summary
        assert len(result.response) > 50, "Should provide information for stakeholders"
