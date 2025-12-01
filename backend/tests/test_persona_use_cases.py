"""
AI Guide Persona Use Case Testing

Executes realistic persona-based test scenarios that mimic how actual users
would interact with the AI Guide. Each persona represents a distinct role
with specific goals, workflows, and question patterns.

Personas:
1. Project Manager (PM) - Status overviews, blockers, deadlines, workload
2. Engineering Lead - Technical details, agent status, integration health
3. Executive/Stakeholder - High-level summaries, KPIs, decision support
4. New Team Member - Onboarding info, context, learning resources
5. DevOps/Platform - Infrastructure status, deployments, resource health

Scoring:
- Relevance (1-5): Does it answer the actual question?
- Accuracy (1-5): Is the data correct?
- Actionability (1-5): Can user take action based on response?
"""

import httpx
import json
import time
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import re

BASE_URL = "http://localhost:8080"
API_KEY = "dev-test-key-123"

@dataclass
class TestResult:
    persona: str
    scenario: str
    query: str
    response: str
    response_time: float
    relevance_score: int = 0  # 1-5
    accuracy_score: int = 0   # 1-5
    actionability_score: int = 0  # 1-5
    notes: str = ""
    passed: bool = True

@dataclass
class PersonaTestSuite:
    persona: str
    scenario: str
    description: str
    queries: List[str]
    expectations: List[str]
    results: List[TestResult] = field(default_factory=list)


def query_guide(query: str) -> tuple[str, float]:
    """Query the AI Guide and return response with timing."""
    start = time.time()
    try:
        response = httpx.post(
            f"{BASE_URL}/api/agent/query",
            json={"query": query},
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        response.raise_for_status()
        elapsed = time.time() - start
        return response.json().get("response", ""), elapsed
    except Exception as e:
        elapsed = time.time() - start
        return f"ERROR: {str(e)}", elapsed


def auto_score_response(query: str, response: str, expectation: str) -> tuple[int, int, int, str]:
    """
    Auto-score response based on heuristics.
    Returns (relevance, accuracy, actionability, notes)
    """
    response_lower = response.lower()
    query_lower = query.lower()
    notes = []

    # Relevance scoring
    relevance = 3  # Default moderate

    # Check if response mentions key terms from query
    query_keywords = set(re.findall(r'\b\w{4,}\b', query_lower))
    matched_keywords = sum(1 for kw in query_keywords if kw in response_lower)
    if matched_keywords >= len(query_keywords) * 0.5:
        relevance = 4
    if matched_keywords >= len(query_keywords) * 0.8:
        relevance = 5

    # Check for "I don't have" or "no information" responses
    if any(phrase in response_lower for phrase in ["i don't have", "no information", "cannot find", "not available"]):
        relevance = 2
        notes.append("Limited data available")

    # Check for error responses
    if "error" in response_lower or response.startswith("ERROR"):
        relevance = 1
        notes.append("Error in response")

    # Accuracy scoring - check for numeric data
    accuracy = 3  # Default moderate
    has_numbers = bool(re.search(r'\b\d+\b', response))
    has_specific_data = any(term in response_lower for term in ["task", "agent", "meeting", "decision", "pending", "completed"])

    if has_numbers and has_specific_data:
        accuracy = 4
        notes.append("Contains specific data")
    if "based on the current data" in response_lower:
        accuracy = 5
        notes.append("Grounded in actual data")

    # Actionability scoring
    actionability = 3  # Default moderate

    # Check for actionable elements
    has_names = bool(re.search(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', response))  # Names like "David Hayes"
    has_dates = bool(re.search(r'\d{4}-\d{2}-\d{2}', response))
    has_list = response.count('\n-') >= 2 or response.count('\n1.') >= 1
    has_status = any(status in response_lower for status in ["pending", "in-progress", "blocked", "completed", "done"])

    actionability_points = sum([has_names, has_dates, has_list, has_status])
    if actionability_points >= 3:
        actionability = 5
        notes.append("Highly actionable")
    elif actionability_points >= 2:
        actionability = 4
        notes.append("Actionable")
    elif actionability_points == 1:
        actionability = 3
    else:
        actionability = 2
        notes.append("Limited actionability")

    return relevance, accuracy, actionability, "; ".join(notes)


def run_test_suite(suite: PersonaTestSuite) -> PersonaTestSuite:
    """Run all queries in a test suite and collect results."""
    print(f"\n{'='*60}")
    print(f"PERSONA: {suite.persona}")
    print(f"SCENARIO: {suite.scenario}")
    print(f"{'='*60}")

    for i, (query, expectation) in enumerate(zip(suite.queries, suite.expectations)):
        print(f"\n[{i+1}/{len(suite.queries)}] Query: {query}")

        response, elapsed = query_guide(query)
        relevance, accuracy, actionability, notes = auto_score_response(query, response, expectation)

        result = TestResult(
            persona=suite.persona,
            scenario=suite.scenario,
            query=query,
            response=response[:500] + "..." if len(response) > 500 else response,
            response_time=elapsed,
            relevance_score=relevance,
            accuracy_score=accuracy,
            actionability_score=actionability,
            notes=notes,
            passed=(relevance + accuracy + actionability) / 3 >= 3.0
        )
        suite.results.append(result)

        avg_score = (relevance + accuracy + actionability) / 3
        status = "PASS" if result.passed else "FAIL"
        print(f"  Response time: {elapsed:.2f}s")
        print(f"  Scores: R={relevance} A={accuracy} Act={actionability} (Avg: {avg_score:.1f})")
        print(f"  Status: {status}")
        print(f"  Response preview: {response[:200]}...")

    return suite


# =============================================================================
# PERSONA TEST DEFINITIONS
# =============================================================================

PM_STANDUP = PersonaTestSuite(
    persona="Project Manager",
    scenario="Daily Standup Prep",
    description="PM preparing for daily standup needs quick status overview",
    queries=[
        "What's blocking the team today?",
        "Show me tasks due this week",
        "Who has the most work assigned?",
        "Any meetings scheduled today?",
        "What was completed yesterday?"
    ],
    expectations=[
        "List of blocked tasks with reasons",
        "Tasks with due dates in next 7 days",
        "Workload distribution by assignee",
        "Today's meetings with times",
        "Recently completed tasks"
    ]
)

PM_SPRINT = PersonaTestSuite(
    persona="Project Manager",
    scenario="Sprint Planning",
    description="PM planning upcoming sprint needs capacity and backlog info",
    queries=[
        "What high priority tasks are still pending?",
        "How many tasks did we complete last sprint?",
        "Show team capacity - who has bandwidth?",
        "What decisions are pending approval?",
        "Any tasks without assignees?"
    ],
    expectations=[
        "Prioritized backlog",
        "Completion metrics",
        "Tasks per person",
        "Awaiting decisions",
        "Unassigned work"
    ]
)

ENG_HEALTH = PersonaTestSuite(
    persona="Engineering Lead",
    scenario="Technical Health Check",
    description="Engineering Lead checking system and agent health",
    queries=[
        "What agents are in production?",
        "Any agents with integration issues?",
        "Show me agents in development",
        "What's the agent deployment timeline?",
        "Any critical technical tasks overdue?"
    ],
    expectations=[
        "Production agents with status",
        "Integration problems flagged",
        "Development pipeline",
        "Agents by stage",
        "Overdue high-priority items"
    ]
)

ENG_DECISIONS = PersonaTestSuite(
    persona="Engineering Lead",
    scenario="Architecture Decisions",
    description="Engineering Lead researching past architecture decisions",
    queries=[
        "What architecture decisions have been made?",
        "Why did we choose Azure OpenAI?",
        "Show recent technical decisions",
        "What proposals are pending technical review?",
        "Who made the CosmosDB decision?"
    ],
    expectations=[
        "Decision list",
        "Decision rationale",
        "Last 30 days decisions",
        "Awaiting decisions",
        "Decision owner/date"
    ]
)

EXEC_STATUS = PersonaTestSuite(
    persona="Executive",
    scenario="Weekly Status Report",
    description="Executive preparing for leadership meeting needs high-level metrics",
    queries=[
        "Give me a summary of project status",
        "What are the key risks or blockers?",
        "How many agents are operational vs planned?",
        "What decisions need my attention?",
        "Show progress this month"
    ],
    expectations=[
        "High-level overview",
        "Risk summary",
        "Pipeline metrics",
        "Pending approvals",
        "Monthly achievements"
    ]
)

EXEC_RESOURCES = PersonaTestSuite(
    persona="Executive",
    scenario="Resource Allocation",
    description="Executive reviewing resource utilization and team allocation",
    queries=[
        "How is the team workload distributed?",
        "What are the biggest initiatives?",
        "Any bottlenecks in delivery?",
        "Show me tasks by category",
        "What's the completion rate trend?"
    ],
    expectations=[
        "Work per person",
        "Major work streams",
        "Blockers/delays",
        "Work breakdown",
        "Productivity metrics"
    ]
)

NEW_ONBOARD = PersonaTestSuite(
    persona="New Team Member",
    scenario="Onboarding",
    description="New team member trying to understand the project and get oriented",
    queries=[
        "What is this project about?",
        "Who are the key people I should know?",
        "What are the main agents we're building?",
        "What should I focus on first?",
        "Where can I find documentation?"
    ],
    expectations=[
        "Project overview",
        "Team/stakeholders",
        "Agent overview",
        "Onboarding guidance",
        "Resource pointers"
    ]
)

NEW_TASKS = PersonaTestSuite(
    persona="New Team Member",
    scenario="Task Pickup",
    description="New team member looking for tasks to work on",
    queries=[
        "What tasks are available to pick up?",
        "Show me low priority tasks good for learning",
        "What did the team work on recently?",
        "Who should I ask about the AI Search task?",
        "What skills are needed for pending tasks?"
    ],
    expectations=[
        "Unassigned tasks",
        "Starter tasks",
        "Recent activity",
        "Task owner",
        "Requirements"
    ]
)

DEVOPS_DEPLOY = PersonaTestSuite(
    persona="DevOps",
    scenario="Deployment Status",
    description="DevOps engineer checking deployment pipeline and infrastructure",
    queries=[
        "What agents are ready for deployment?",
        "Any infrastructure tasks pending?",
        "Show me recent deployment decisions",
        "What's blocking production releases?",
        "Status of Azure resource setup?"
    ],
    expectations=[
        "Deployment-ready items",
        "Infra backlog",
        "Deployment-related decisions",
        "Release blockers",
        "Infrastructure status"
    ]
)

DEVOPS_INCIDENT = PersonaTestSuite(
    persona="DevOps",
    scenario="Incident Response",
    description="DevOps responding to a reported issue",
    queries=[
        "Any known issues with the AI Guide?",
        "Show me recent changes to the system",
        "What integrations might be affected?",
        "Who owns the backend service?",
        "Any related incidents or bugs?"
    ],
    expectations=[
        "Known problems",
        "Recent updates",
        "Integration list",
        "Ownership info",
        "Related issues"
    ]
)

COMPLEX_QUERIES = PersonaTestSuite(
    persona="Cross-Persona",
    scenario="Complex Multi-Part Queries",
    description="Test complex queries that combine multiple concerns",
    queries=[
        "Show blocked tasks and who owns them",
        "High priority tasks due this week assigned to David",
        "Compare agent count by status vs last month",
        "Tasks created from recent meetings",
        "Pending decisions that affect the architecture"
    ],
    expectations=[
        "Blocked + assignee",
        "Filtered list",
        "Comparison",
        "Meeting-task link",
        "Filtered decisions"
    ]
)


ALL_SUITES = [
    PM_STANDUP, PM_SPRINT,
    ENG_HEALTH, ENG_DECISIONS,
    EXEC_STATUS, EXEC_RESOURCES,
    NEW_ONBOARD, NEW_TASKS,
    DEVOPS_DEPLOY, DEVOPS_INCIDENT,
    COMPLEX_QUERIES
]


def generate_report(suites: List[PersonaTestSuite]) -> str:
    """Generate comprehensive markdown report from test results."""

    total_tests = sum(len(s.results) for s in suites)
    passed_tests = sum(1 for s in suites for r in s.results if r.passed)
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    all_results = [r for s in suites for r in s.results]
    avg_relevance = sum(r.relevance_score for r in all_results) / len(all_results) if all_results else 0
    avg_accuracy = sum(r.accuracy_score for r in all_results) / len(all_results) if all_results else 0
    avg_actionability = sum(r.actionability_score for r in all_results) / len(all_results) if all_results else 0
    avg_response_time = sum(r.response_time for r in all_results) / len(all_results) if all_results else 0

    report = f"""# AI Guide Persona Use Case Test Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Environment:** Docker Compose (localhost:8080)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | {total_tests} |
| **Passed** | {passed_tests} |
| **Failed** | {failed_tests} |
| **Pass Rate** | {pass_rate:.1f}% |
| **Avg Response Time** | {avg_response_time:.2f}s |

### Quality Scores (1-5 scale)

| Dimension | Score | Rating |
|-----------|-------|--------|
| **Relevance** | {avg_relevance:.2f} | {"*" * round(avg_relevance)} |
| **Accuracy** | {avg_accuracy:.2f} | {"*" * round(avg_accuracy)} |
| **Actionability** | {avg_actionability:.2f} | {"*" * round(avg_actionability)} |
| **Overall** | {(avg_relevance + avg_accuracy + avg_actionability) / 3:.2f} | {"*" * round((avg_relevance + avg_accuracy + avg_actionability) / 3)} |

---

## Results by Persona

"""

    # Group by persona
    personas = {}
    for suite in suites:
        if suite.persona not in personas:
            personas[suite.persona] = []
        personas[suite.persona].append(suite)

    for persona, persona_suites in personas.items():
        persona_results = [r for s in persona_suites for r in s.results]
        persona_passed = sum(1 for r in persona_results if r.passed)
        persona_total = len(persona_results)
        persona_rate = (persona_passed / persona_total * 100) if persona_total > 0 else 0

        p_relevance = sum(r.relevance_score for r in persona_results) / len(persona_results) if persona_results else 0
        p_accuracy = sum(r.accuracy_score for r in persona_results) / len(persona_results) if persona_results else 0
        p_actionability = sum(r.actionability_score for r in persona_results) / len(persona_results) if persona_results else 0

        report += f"""### {persona}

| Metric | Value |
|--------|-------|
| Tests | {persona_total} |
| Pass Rate | {persona_rate:.0f}% ({persona_passed}/{persona_total}) |
| Relevance | {p_relevance:.1f}/5 |
| Accuracy | {p_accuracy:.1f}/5 |
| Actionability | {p_actionability:.1f}/5 |

"""

        for suite in persona_suites:
            report += f"**Scenario: {suite.scenario}**\n\n"
            report += "| Query | R | A | Act | Time | Status |\n"
            report += "|-------|---|---|-----|------|--------|\n"

            for r in suite.results:
                status = "PASS" if r.passed else "FAIL"
                query_short = r.query[:40] + "..." if len(r.query) > 40 else r.query
                report += f"| {query_short} | {r.relevance_score} | {r.accuracy_score} | {r.actionability_score} | {r.response_time:.1f}s | {status} |\n"

            report += "\n"

    # Failure analysis
    failures = [r for r in all_results if not r.passed]
    if failures:
        report += """---

## Failure Analysis

"""
        for f in failures:
            report += f"""### FAILED: {f.query}
- **Persona:** {f.persona}
- **Scenario:** {f.scenario}
- **Scores:** Relevance={f.relevance_score}, Accuracy={f.accuracy_score}, Actionability={f.actionability_score}
- **Notes:** {f.notes}
- **Response:** {f.response[:300]}...

"""

    # Top performers
    top_results = sorted(all_results, key=lambda r: (r.relevance_score + r.accuracy_score + r.actionability_score) / 3, reverse=True)[:5]

    report += """---

## Top Performing Queries

| Query | Persona | Avg Score |
|-------|---------|-----------|
"""
    for r in top_results:
        avg = (r.relevance_score + r.accuracy_score + r.actionability_score) / 3
        query_short = r.query[:50] + "..." if len(r.query) > 50 else r.query
        report += f"| {query_short} | {r.persona} | {avg:.1f}/5 |\n"

    # Recommendations
    report += """
---

## Recommendations

"""

    # Analyze patterns
    low_relevance = [r for r in all_results if r.relevance_score <= 2]
    low_accuracy = [r for r in all_results if r.accuracy_score <= 2]
    low_actionability = [r for r in all_results if r.actionability_score <= 2]

    if low_relevance:
        report += f"### 1. Improve Query Understanding\n"
        report += f"{len(low_relevance)} queries had low relevance scores. Consider:\n"
        report += "- Expanding intent detection patterns\n"
        report += "- Adding more entity type recognition\n\n"

    if low_accuracy:
        report += f"### 2. Enhance Data Grounding\n"
        report += f"{len(low_accuracy)} queries had low accuracy scores. Consider:\n"
        report += "- Ensuring all responses cite data sources\n"
        report += "- Adding validation for numeric responses\n\n"

    if low_actionability:
        report += f"### 3. Increase Actionability\n"
        report += f"{len(low_actionability)} queries had low actionability scores. Consider:\n"
        report += "- Including assignee names in task responses\n"
        report += "- Adding due dates and status information\n"
        report += "- Formatting responses as actionable lists\n\n"

    if pass_rate >= 80:
        report += "### Overall Assessment: GOOD\n"
        report += "The AI Guide is performing well across most persona scenarios.\n"
    elif pass_rate >= 60:
        report += "### Overall Assessment: NEEDS IMPROVEMENT\n"
        report += "The AI Guide has room for improvement in several areas.\n"
    else:
        report += "### Overall Assessment: REQUIRES ATTENTION\n"
        report += "Significant improvements needed before production use.\n"

    return report


def main():
    """Run all persona tests and generate report."""
    print("=" * 70)
    print("AI GUIDE PERSONA USE CASE TESTING")
    print("=" * 70)
    print(f"Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total test suites: {len(ALL_SUITES)}")
    print(f"Total queries: {sum(len(s.queries) for s in ALL_SUITES)}")

    completed_suites = []
    for suite in ALL_SUITES:
        completed_suite = run_test_suite(suite)
        completed_suites.append(completed_suite)

    print("\n" + "=" * 70)
    print("GENERATING REPORT")
    print("=" * 70)

    report = generate_report(completed_suites)

    # Save report
    report_path = "AI_Guide_Persona_Test_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport saved to: {report_path}")

    # Print summary
    total = sum(len(s.results) for s in completed_suites)
    passed = sum(1 for s in completed_suites for r in s.results if r.passed)
    print(f"\nFINAL RESULTS: {passed}/{total} passed ({passed/total*100:.1f}%)")

    return completed_suites


if __name__ == "__main__":
    main()
