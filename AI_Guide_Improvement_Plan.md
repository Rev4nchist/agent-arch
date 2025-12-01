# AI Guide Improvement Plan
**Date:** 2025-11-26
**Analysis Depth:** ULTRATHINK
**Based On:** 55 Persona Use Case Tests (100% Pass Rate, Quality Issues Identified)

---

## Executive Summary

While all 55 tests passed functionally, quality scoring revealed **two key improvement areas**:

| Issue | Queries Affected | Impact |
|-------|------------------|--------|
| **Low Relevance** | 7 queries (12.7%) | Users not getting answers to their actual questions |
| **Low Actionability** | 17 queries (30.9%) | Responses lack practical next steps |

**Root Cause:** The AI Guide is *accurate* (4.87/5) but struggles with *understanding* (3.95/5) and *providing actionable guidance* (3.38/5).

---

## Part 1: Low Relevance Analysis

### 1.1 Affected Queries (Relevance Score <= 2)

| Query | Score | Persona | Root Cause |
|-------|-------|---------|------------|
| "What are the key risks or blockers?" | R=1 | Executive | "risks" not mapped to any entity/status |
| "What's blocking the team today?" | R=2 | PM | "blocking" detected but "today" filter fails |
| "What's the agent deployment timeline?" | R=2 | Eng Lead | "timeline" concept not in data model |
| "Any bottlenecks in delivery?" | R=2 | Executive | "bottlenecks" not mapped to blocked status |
| "Show me low priority tasks good for learning" | R=2 | New Member | "good for learning" - no complexity/learning tags |
| "Who owns the backend service?" | R=2 | DevOps | "owns" and "service" not linked to entities |
| "Compare agent count by status vs last month" | R=2 | Cross | Historical data not available |

### 1.2 Intent Detection Gaps

**Current Pattern Coverage in `main.py:732-798`:**

| Intent Type | Current Patterns | Missing Patterns |
|-------------|------------------|------------------|
| STATUS_CHECK | blocked, overdue, pending | **risks, bottlenecks, blockers** |
| AGGREGATION | count, breakdown, group | timeline view, trend analysis |
| COMPARISON | this week vs last week | **vs last month, historical** |
| ACTION_GUIDANCE | what should I work on | **good for learning, starter** |
| NEW: OWNERSHIP | (not implemented) | **who owns, responsible for** |

### 1.3 Data Model Gaps

```
MISSING FIELDS:
- tasks.complexity_level: "beginner" | "intermediate" | "advanced"
- tasks.learning_friendly: boolean
- agents.target_deployment_date: datetime (for timeline queries)
- services.owner: string (for ownership queries)
- Historical snapshots for trend comparison
```

---

## Part 2: Low Actionability Analysis

### 2.1 Affected Queries (Actionability Score <= 2)

**Pattern:** Responses provide *information* but not *next steps*.

| Query Category | Count | Missing Elements |
|----------------|-------|------------------|
| Agent Status Queries | 5 | Who to contact, next action |
| Decision Queries | 2 | Decision maker contact, rationale |
| Ownership Queries | 2 | Owner name, team, contact |
| Filter/Category Queries | 4 | How to drill down, what to focus on |
| Comparison Queries | 2 | What changed, why it matters |
| Deployment Queries | 2 | Deployment steps, prerequisites |

### 2.2 Scoring Logic Analysis

**Current actionability scoring (test_persona_use_cases.py:118-140):**

```python
# Checks for:
has_names     # Person names like "David Hayes"
has_dates     # Dates in YYYY-MM-DD format
has_list      # Bullet points or numbered lists
has_status    # Status words (pending, blocked, etc.)

# Score mapping:
0-1 points = Score 2 (Low)
2 points = Score 4 (Good)
3+ points = Score 5 (Excellent)
```

**Issue:** Responses often lack 2+ of these elements.

### 2.3 AI System Prompt Analysis

**Current system prompt (ai_client.py:218-231):**

```
CRITICAL DATA ACCURACY RULES:
1. ONLY use information explicitly provided in the context below...
2. When counting items, use ONLY the items shown...
3. The context shows "showing X of Y total"...
```

**Missing:** No instructions for actionability, next steps, or formatting.

---

## Part 3: Root Cause Summary

```
                    ACCURACY (4.87/5)
                         |
                    [STRONG]
                         |
    RELEVANCE (3.95/5) --+-- ACTIONABILITY (3.38/5)
           |                        |
      [GAPS IN]                [MISSING]
           |                        |
    - Intent patterns        - Next steps guidance
    - Entity detection       - Contact information
    - Date/time context      - Formatting instructions
    - Historical data        - Action suggestions
```

---

## Part 4: Improvement Recommendations

### Phase 1: Quick Wins (1-2 days)

#### 1.1 Expand Intent Patterns

**File:** `backend/src/main.py` lines 732-798

**Add patterns for:**

```python
# STATUS_CHECK additions
r"\b(risks?|blockers?|bottlenecks?|impediments?)\b",
r"\bwhat('s| is| are).*\b(blocking|stuck|delayed)\b",

# New: OWNERSHIP intent
(QueryIntent.OWNERSHIP, [
    r"\b(who owns|owner of|responsible for|who manages)\b",
    r"\bwho.*\b(contact|ask about|handles)\b",
]),

# ACTION_GUIDANCE additions
r"\b(good for|suitable for|appropriate for)\s*(learning|beginners?|new)\b",
r"\b(starter|beginner|easy|simple)\s*(tasks?|work|items?)\b",

# COMPARISON additions
r"\bvs\.?\s*(last|previous)\s*(month|quarter|year)\b",
r"\b(historical|trend|over time)\b",
```

#### 1.2 Enhanced AI System Prompt

**File:** `backend/src/ai_client.py` lines 218-231

**Add actionability instructions:**

```python
system_prompt = """You are the Fourth AI Guide...

CRITICAL DATA ACCURACY RULES:
[existing rules...]

ACTIONABILITY GUIDELINES:
1. Always end responses with "Next Steps:" when applicable
2. Include WHO to contact for blocked/pending items
3. For task lists, highlight the TOP 1-3 most urgent items
4. When showing counts, explain WHAT THE USER SHOULD DO about them
5. Format responses with clear sections: Summary, Details, Next Steps
6. If items need attention, specify: "Action Required: [specific action]"

RESPONSE FORMAT:
- Use bullet points for lists
- Include dates in human-readable format (e.g., "Due: March 31, 2025")
- Show assignee names prominently
- End with actionable recommendations"""
```

#### 1.3 Add "Next Steps" to Response Generation

**File:** `backend/src/main.py` lines 1781-1786

**Enhance action suggestions:**

```python
# Current: suggestions = _generate_action_suggestions(...)

# Enhanced: Add to AI context
action_hints = f"\n[Suggested Actions for User]: {[s.label for s in suggestions[:3]]}"
full_context = f"{intent_context}\n{context}\n{action_hints}"
```

---

### Phase 2: Data Model Enhancements (3-5 days)

#### 2.1 Add Task Complexity Fields

**File:** `backend/src/models.py`

```python
class Task(BaseModel):
    # Existing fields...

    # New fields for learning/starter task queries
    complexity: Optional[str] = None  # "beginner", "intermediate", "advanced"
    learning_friendly: Optional[bool] = False
    skills_required: Optional[List[str]] = []
```

**Migration:** Add default values to existing tasks via CosmosDB update script.

#### 2.2 Add Agent Timeline Fields

```python
class Agent(BaseModel):
    # Existing fields...

    # New fields for timeline/deployment queries
    target_deployment_date: Optional[datetime] = None
    deployment_blockers: Optional[List[str]] = []
    next_milestone: Optional[str] = None
```

#### 2.3 Add Owner/Contact Fields

```python
# Add to relevant models
owner_name: Optional[str] = None
owner_contact: Optional[str] = None  # email or slack handle
team: Optional[str] = None
```

---

### Phase 3: Historical Data & Trends (5-7 days)

#### 3.1 Snapshot System

**New file:** `backend/src/snapshot_service.py`

```python
class SnapshotService:
    """Capture daily/weekly snapshots for trend analysis."""

    async def capture_daily_snapshot(self):
        """Store counts by status/priority for all entities."""
        snapshot = {
            "date": datetime.utcnow().isoformat(),
            "tasks": {
                "total": await self._count_tasks(),
                "by_status": await self._count_tasks_by_status(),
                "by_priority": await self._count_tasks_by_priority(),
            },
            "agents": {
                "total": await self._count_agents(),
                "by_status": await self._count_agents_by_status(),
            }
        }
        # Store in CosmosDB snapshots container
```

#### 3.2 Add COMPARISON Intent Handler

```python
# When intent == QueryIntent.COMPARISON:
if "last month" in query_lower or "previous month" in query_lower:
    current = await get_current_counts()
    previous = await get_snapshot(days_ago=30)
    context += format_comparison(current, previous)
```

---

### Phase 4: Response Quality Improvements (3-5 days)

#### 4.1 Response Templates by Intent

```python
RESPONSE_TEMPLATES = {
    QueryIntent.STATUS_CHECK: """
**Status Summary:**
{status_breakdown}

**Items Needing Attention:** {attention_items}

**Next Steps:**
- {next_step_1}
- {next_step_2}
""",
    QueryIntent.AGGREGATION: """
**{entity_type} Breakdown:**
{breakdown_table}

**Key Insight:** {insight}
**Recommendation:** {recommendation}
""",
}
```

#### 4.2 Contact Information Enhancement

```python
def _enhance_with_contacts(response: str, items: List[dict]) -> str:
    """Add contact info for blocked/pending items."""
    contacts = set()
    for item in items:
        if item.get('assigned_to'):
            contacts.add(item['assigned_to'])
        if item.get('owner_name'):
            contacts.add(item['owner_name'])

    if contacts:
        response += f"\n\n**Key Contacts:** {', '.join(contacts)}"
    return response
```

---

## Part 5: Implementation Priority

| Priority | Item | Impact | Effort | Files Affected |
|----------|------|--------|--------|----------------|
| **P0** | Expand intent patterns | High | Low | main.py |
| **P0** | Enhanced system prompt | High | Low | ai_client.py |
| **P1** | Add "Next Steps" formatting | High | Low | ai_client.py |
| **P1** | Add complexity fields | Medium | Medium | models.py, migration |
| **P2** | Add ownership fields | Medium | Medium | models.py |
| **P2** | Response templates | Medium | Medium | main.py |
| **P3** | Historical snapshots | Medium | High | new service |
| **P3** | Comparison handlers | Medium | High | main.py |

---

## Part 6: Success Metrics

### Target Scores (Post-Implementation)

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Relevance | 3.95 | 4.5+ | +14% |
| Accuracy | 4.87 | 4.9+ | +1% (maintain) |
| Actionability | 3.38 | 4.2+ | +24% |
| Overall | 4.07 | 4.5+ | +11% |

### Validation Criteria

1. Re-run all 55 persona tests after each phase
2. **Phase 1 Success:** 0 queries with R<=2, <10 queries with Act<=2
3. **Phase 2 Success:** Learning/timeline queries score R>=4
4. **Phase 3 Success:** Comparison queries score R>=4, Act>=3

---

## Part 7: Specific Query Fixes

### Query: "What are the key risks or blockers?" (R=1)

**Current Behavior:** Query doesn't match STATUS_CHECK patterns, defaults to LIST
**Fix:** Add "risks" and "blockers" to STATUS_CHECK patterns
**Expected Result:** Returns blocked tasks with context

### Query: "Show me low priority tasks good for learning" (R=2)

**Current Behavior:** Matches "low priority" but "good for learning" is ignored
**Fix 1:** Add intent pattern for learning-friendly tasks
**Fix 2:** Add `complexity` and `learning_friendly` fields to Task model
**Expected Result:** Returns beginner-appropriate tasks

### Query: "Who owns the backend service?" (R=2)

**Current Behavior:** "owns" doesn't trigger any intent, no ownership data
**Fix 1:** Add OWNERSHIP intent with patterns
**Fix 2:** Add `owner_name`, `owner_contact` to Agent/Task models
**Expected Result:** Returns owner with contact info

### Query: "Compare agent count by status vs last month" (R=2)

**Current Behavior:** COMPARISON intent triggered but no historical data
**Fix:** Implement snapshot service and historical queries
**Expected Result:** Shows current vs previous month with delta

---

## Appendix A: Files to Modify

```
backend/src/main.py
  - Lines 732-798: Intent patterns (_classify_intent)
  - Lines 1242-1349: Query builder (_build_cosmos_query)
  - Lines 1691-1792: Query endpoint (query_agent)

backend/src/ai_client.py
  - Lines 218-231: System prompt (query_agent method)

backend/src/models.py
  - Task model: Add complexity, learning_friendly, skills_required
  - Agent model: Add target_deployment_date, deployment_blockers
  - All models: Add owner_name, owner_contact, team

NEW FILES:
  - backend/src/snapshot_service.py
  - backend/migrations/add_complexity_fields.py
```

---

## Appendix B: Test Query Mapping

| Low-Scoring Query | Fix Phase | Expected Improvement |
|-------------------|-----------|----------------------|
| Key risks or blockers | Phase 1 | R: 1->4, Act: 5->5 |
| Blocking team today | Phase 1 | R: 2->4, Act: 3->4 |
| Agent deployment timeline | Phase 2 | R: 2->4, Act: 2->4 |
| Bottlenecks in delivery | Phase 1 | R: 2->4, Act: 3->4 |
| Low priority learning tasks | Phase 2 | R: 2->4, Act: 2->4 |
| Who owns backend service | Phase 2 | R: 2->4, Act: 2->5 |
| Compare vs last month | Phase 3 | R: 2->4, Act: 2->4 |

---

**Report Generated:** 2025-11-26
**Analysis Method:** Deep code review, pattern analysis, data model inspection
**Confidence Level:** High (based on actual test data and code analysis)
