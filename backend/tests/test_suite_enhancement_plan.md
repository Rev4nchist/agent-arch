# AI Guide Test Suite Enhancement Plan

## Current Coverage Analysis

### What We Test Now (55 queries)
- Basic intent recognition
- Data retrieval accuracy
- Response relevance
- Actionability (names, dates, lists)

### Gaps Identified
1. **No template compliance testing** - Do responses follow the new structured formats?
2. **No contact extraction validation** - Are the right contacts surfaced?
3. **No historical/comparison testing** - Snapshot functionality untested
4. **No edge case coverage** - Empty results, errors, ambiguous queries
5. **No Fourth-specific terminology** - Industry/company terms
6. **No follow-up query patterns** - Real users ask clarifying questions
7. **No response length/quality testing** - Too verbose? Too terse?
8. **No negative testing** - Queries that SHOULD fail gracefully

---

## Recommended New Test Categories

### Category 1: Response Template Compliance Tests
**Purpose:** Verify AI follows structured response formats

```python
TEMPLATE_COMPLIANCE_TESTS = [
    # STATUS_CHECK should have: Summary → Top Items → Attention → Next Steps
    {
        "query": "What tasks are blocked?",
        "expected_sections": ["Status Summary", "Items Needing", "Next Steps"],
        "forbidden": ["I don't have enough information"]
    },
    # AGGREGATION should have: Headline → Breakdown → Insight → Recommendation
    {
        "query": "How many agents by status?",
        "expected_sections": ["total", "Breakdown", "Insight", "Recommendation"],
        "must_have_numbers": True
    },
    # OWNERSHIP should have: Direct answer → Contact → Team → How to reach
    {
        "query": "Who owns the AI Guide?",
        "expected_sections": ["owns", "contact", "reach"],
        "must_have_name": True
    },
]
```

### Category 2: Contact Extraction Accuracy Tests
**Purpose:** Verify contacts are correctly identified and prioritized

```python
CONTACT_EXTRACTION_TESTS = [
    {
        "query": "Show blocked tasks",
        "expected_contacts": ["assignee of blocked tasks"],
        "priority": "urgent contacts should appear first"
    },
    {
        "query": "Who's working on high priority items?",
        "verify": "contacts should match assigned_to field values"
    },
    {
        "query": "Tasks for the AI Search project",
        "verify": "owner_contact field should be included if available"
    },
]
```

### Category 3: Historical/Comparison Tests
**Purpose:** Validate snapshot and trend functionality

```python
COMPARISON_TESTS = [
    {
        "query": "Compare task status vs last week",
        "expected": ["Compared to", "+/-", "Trend"],
        "requires_snapshot": True
    },
    {
        "query": "How has agent count changed this month?",
        "expected": ["change", "previous", "current"],
        "intent": "COMPARISON"
    },
    {
        "query": "Show progress since yesterday",
        "expected": ["completed", "delta", "change"]
    },
]
```

### Category 4: Edge Cases & Error Handling
**Purpose:** Graceful handling of unusual inputs

```python
EDGE_CASE_TESTS = [
    # Empty results
    {"query": "Show tasks assigned to NonExistentPerson", "expected_behavior": "graceful empty state"},
    {"query": "Meetings in December 2030", "expected_behavior": "no data message"},

    # Ambiguous queries
    {"query": "Show me stuff", "expected_behavior": "clarification or reasonable guess"},
    {"query": "What about the thing?", "expected_behavior": "ask for clarification"},

    # Very long queries
    {"query": "I need to find all the tasks that are currently in progress and assigned to someone on the engineering team who has been working on Azure-related infrastructure items for the past month", "expected_behavior": "extract key filters"},

    # Typos and variations
    {"query": "sho me bloked taks", "expected_behavior": "understand intent despite typos"},
    {"query": "WHAT TASKS ARE BLOCKED???", "expected_behavior": "handle caps/punctuation"},

    # SQL injection attempts (security)
    {"query": "tasks'; DROP TABLE tasks; --", "expected_behavior": "safe handling, no error"},
]
```

### Category 5: Fourth-Specific Terminology
**Purpose:** Understand company/industry-specific terms

```python
FOURTH_TERMINOLOGY_TESTS = [
    # Tier system
    {"query": "Show Tier 2 agents", "expected": "department-level agents"},
    {"query": "What's in Tier 3?", "expected": "enterprise agents"},

    # Agent lifecycle
    {"query": "Agents ready for staging", "expected": "agents with status=Testing or Development"},
    {"query": "Production-ready agents", "expected": "agents that passed testing"},

    # Governance terms
    {"query": "Pending governance reviews", "expected": "tasks/decisions awaiting approval"},
    {"query": "Architecture decisions", "expected": "decisions with category=Architecture"},

    # Team roles (if applicable)
    {"query": "Platform team tasks", "expected": "infrastructure/devops tasks"},
]
```

### Category 6: Multi-Turn Conversation Patterns
**Purpose:** Test realistic follow-up patterns (even without session memory)

```python
FOLLOW_UP_PATTERNS = [
    # Drill-down pattern
    {"sequence": [
        "How many tasks by status?",
        "Show me the blocked ones",
        "Who owns those?"
    ]},

    # Refinement pattern
    {"sequence": [
        "Show all agents",
        "Just the ones in production",
        "Which have integration issues?"
    ]},

    # Context switch
    {"sequence": [
        "Tasks due this week",
        "What meetings do I have?",
        "Back to tasks - any high priority?"
    ]},
]
```

### Category 7: Response Quality Metrics
**Purpose:** Measure response characteristics beyond accuracy

```python
QUALITY_METRICS = {
    "response_length": {
        "min_chars": 100,  # Not too short
        "max_chars": 2000,  # Not too verbose
        "ideal_range": (200, 800)
    },
    "structure": {
        "has_sections": True,  # Uses headers/sections
        "has_lists": True,  # Uses bullet/numbered lists
        "has_next_steps": True  # Ends with actions
    },
    "tone": {
        "professional": True,
        "no_hedging": ["I think", "maybe", "possibly"],
        "confident": ["Based on", "The data shows", "Currently"]
    }
}
```

### Category 8: Persona-Specific Depth Tests
**Purpose:** Deeper testing for each persona's critical needs

```python
# Executive needs quick summaries
EXEC_DEPTH_TESTS = [
    {"query": "Give me a 30-second summary", "max_length": 500},
    {"query": "Top 3 risks right now", "expected_count": 3},
    {"query": "Red/yellow/green status", "expected": "RAG status indicators"},
]

# PM needs accurate counts
PM_DEPTH_TESTS = [
    {"query": "Exact count of tasks by status", "verify_against_db": True},
    {"query": "Who has overdue items?", "verify_due_dates": True},
    {"query": "Sprint velocity", "expected": "completion rate metrics"},
]

# New member needs context
NEWBIE_DEPTH_TESTS = [
    {"query": "Explain the agent lifecycle", "expected": "beginner-friendly explanation"},
    {"query": "Who do I talk to about X?", "must_have_name": True},
    {"query": "Good first task", "expected": "low complexity, well-documented"},
]
```

---

## Implementation Priority

### Phase 1: Quick Wins (1-2 hours)
1. Add template compliance checks to existing tests
2. Add contact extraction validation
3. Add edge case tests for empty results

### Phase 2: Core Expansion (2-4 hours)
4. Fourth terminology tests
5. Comparison/historical tests
6. Response quality metrics

### Phase 3: Advanced (4-8 hours)
7. Follow-up pattern simulation
8. Database verification tests
9. Performance benchmarks

---

## New Test File Structure

```
backend/tests/
├── test_persona_use_cases.py      # Existing: 55 core queries
├── test_persona_live_queries.py   # Existing: Aggregation tests
├── test_task19_improvements.py    # Existing: Pattern tests
│
├── test_template_compliance.py    # NEW: Response format validation
├── test_contact_extraction.py     # NEW: Contact surfacing accuracy
├── test_comparison_queries.py     # NEW: Historical/trend tests
├── test_edge_cases.py             # NEW: Error handling, ambiguity
├── test_fourth_terminology.py     # NEW: Company-specific terms
├── test_response_quality.py       # NEW: Length, structure, tone
└── conftest.py                    # Shared fixtures, helpers
```

---

## Success Metrics for Production

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Pass Rate | ~85% | 95%+ | (passed/total) |
| Avg Relevance | 4.13 | 4.5+ | 1-5 scale |
| Avg Accuracy | 4.58 | 4.7+ | 1-5 scale |
| Avg Actionability | 4.51 | 4.7+ | 1-5 scale |
| Template Compliance | N/A | 90%+ | Sections present |
| Contact Accuracy | N/A | 85%+ | Correct contacts surfaced |
| Edge Case Handling | N/A | 100% | No crashes/errors |
| Avg Response Time | ~3s | <5s | Seconds |

---

## Recommended Next Steps

1. **Create test fixtures** with known data states
2. **Add database verification** to compare AI counts vs actual counts
3. **Implement smoke tests** for CI/CD pipeline
4. **Create user feedback loop** to capture real queries that fail
