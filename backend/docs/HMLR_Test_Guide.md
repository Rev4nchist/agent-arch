# HMLR Memory System - Test Guide

## Overview

This guide provides step-by-step test scenarios to verify the HMLR memory system is working correctly and to showcase its capabilities.

**Prerequisites:**
- Backend running: `uvicorn src.main:app --reload`
- Azure SQL database provisioned and schema applied
- Test user ID and session ID ready

---

## Part 1: Automated Tests

### Running the Test Suite

```bash
cd C:\agent-arch\backend
pip install pytest pytest-asyncio
pytest tests/test_hmlr_integration.py -v
```

### Expected Results

| Test Category | Tests | Expected |
|--------------|-------|----------|
| SQL Connectivity | 3 | All pass |
| Fact Operations | 3 | All pass |
| User Profiles | 2 | All pass |
| Bridge Blocks | 3 | All pass |
| Governor Routing | 4 | All pass |
| Fact Scrubber | 3 | All pass |
| Context Hydrator | 2 | All pass |
| End-to-End | 2 | All pass |
| Edge Cases | 4 | All pass |
| Performance | 1 | < 500ms |

---

## Part 2: Manual API Tests

### Setup

Use these values for testing:
```
Base URL: http://localhost:8000
Test User ID: david.hayes
Test Session ID: test_session_001
```

### Test Tool

Use `curl`, Postman, or the frontend. All examples use curl.

---

## Test Scenario 1: New Topic (Scenario 3)

**Purpose:** Verify the system correctly identifies a fresh conversation.

### Request
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all open tasks assigned to David",
    "session_id": "scenario1_test",
    "user_id": "test_user_scenario1"
  }'
```

### Expected Behavior
- **Log output:** `HMLR: Added memory context (X tokens)`
- **Log output:** `HMLR: Stored turn in block (scenario=3)`
- Response should include task information

### Verify
```bash
# Check Cosmos DB for the new block
# The block should have:
# - status: ACTIVE
# - topic_label: Contains "Task" or similar
# - turns: 1 turn
```

---

## Test Scenario 2: Topic Continuation (Scenario 1)

**Purpose:** Verify follow-up questions stay in the same topic.

### Request 1 - Initial
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What tasks are assigned to the backend team?",
    "session_id": "scenario2_test",
    "user_id": "test_user_scenario2"
  }'
```

### Request 2 - Follow-up (SAME session_id)
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which of those are overdue?",
    "session_id": "scenario2_test",
    "user_id": "test_user_scenario2"
  }'
```

### Expected Behavior
- Request 1: `scenario=3` (new topic)
- Request 2: `scenario=1` (continuation) OR `scenario=4` if similarity is low
- The agent should understand "those" refers to the tasks from Request 1

### What to Look For
- The response should reference the previous context
- Only ONE block should exist with 2 turns

---

## Test Scenario 3: Topic Shift (Scenario 4)

**Purpose:** Verify switching to a completely different topic.

### Request 1 - Start with Tasks
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the sprint backlog",
    "session_id": "scenario3_test",
    "user_id": "test_user_scenario3"
  }'
```

### Request 2 - Shift to Meetings (SAME session_id)
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What meetings do I have this week?",
    "session_id": "scenario3_test",
    "user_id": "test_user_scenario3"
  }'
```

### Expected Behavior
- Request 1: `scenario=3` (new topic about tasks)
- Request 2: `scenario=4` (topic shift to meetings)
- The first block should be PAUSED
- A new block for meetings should be ACTIVE

### Verify
- Two blocks should exist in Cosmos DB
- First block: status=PAUSED, topic related to tasks
- Second block: status=ACTIVE, topic related to meetings

---

## Test Scenario 4: Topic Resumption (Scenario 2)

**Purpose:** Verify returning to a previously paused topic.

### Request 1 - Start Topic A
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Lets discuss the Q4 roadmap",
    "session_id": "scenario4_test",
    "user_id": "test_user_scenario4"
  }'
```

### Request 2 - Switch to Topic B
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quick question - whats the budget status?",
    "session_id": "scenario4_test",
    "user_id": "test_user_scenario4"
  }'
```

### Request 3 - Return to Topic A
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Back to the roadmap - what are the December milestones?",
    "session_id": "scenario4_test",
    "user_id": "test_user_scenario4"
  }'
```

### Expected Behavior
- Request 1: `scenario=3` (new topic - roadmap)
- Request 2: `scenario=4` (shift to budget)
- Request 3: `scenario=2` (resume roadmap topic)

### What to Look For
- The agent should have context about "the roadmap" from Request 1
- The roadmap block should become ACTIVE again

---

## Test Scenario 5: Fact Extraction and Persistence

**Purpose:** Verify facts are extracted and remembered across sessions.

### Request 1 - Teach a Fact (Session A)
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Just FYI, Sarah is now the owner of the API Gateway service",
    "session_id": "fact_test_session_1",
    "user_id": "fact_test_user"
  }'
```

### Wait 5 seconds for background extraction

### Request 2 - Recall the Fact (Session B - DIFFERENT session)
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who owns the API Gateway?",
    "session_id": "fact_test_session_2",
    "user_id": "fact_test_user"
  }'
```

### Expected Behavior
- The agent should mention Sarah in the response
- The fact should be visible in Azure SQL `fact_store` table

### Verify in SQL
```sql
SELECT * FROM fact_store WHERE user_id = 'fact_test_user';
-- Should see a fact about Sarah and API Gateway
```

---

## Test Scenario 6: Acronym Learning

**Purpose:** Verify acronym extraction works.

### Request
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Remember that HMLR stands for Hierarchical Memory Lookup and Routing",
    "session_id": "acronym_test",
    "user_id": "acronym_test_user"
  }'
```

### Verify in SQL
```sql
SELECT * FROM fact_store
WHERE user_id = 'acronym_test_user' AND category = 'Acronym';
-- Should see HMLR = Hierarchical Memory Lookup and Routing
```

---

## Test Scenario 7: Context Enrichment

**Purpose:** Verify the hydrator provides useful context to the AI.

### Request 1 - Establish Context
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to review tasks. David has 5 tasks, Sarah has 3.",
    "session_id": "context_test",
    "user_id": "context_test_user"
  }'
```

### Request 2 - Ask About Context
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many tasks does David have?",
    "session_id": "context_test",
    "user_id": "context_test_user"
  }'
```

### Expected Behavior
- The agent should answer "5 tasks" using conversation context
- The log should show `HMLR: Added memory context`

---

## Test Scenario 8: Multi-User Isolation

**Purpose:** Verify facts are isolated per user.

### Request 1 - User A teaches a fact
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "My favorite color is blue",
    "session_id": "isolation_test",
    "user_id": "user_alice"
  }'
```

### Request 2 - User B asks about it
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Alices favorite color?",
    "session_id": "isolation_test",
    "user_id": "user_bob"
  }'
```

### Expected Behavior
- User B should NOT be able to access User A's facts
- The agent should not know Alice's favorite color (from Bob's perspective)

---

## Test Scenario 9: Graceful Degradation

**Purpose:** Verify the system handles errors gracefully.

### Temporarily Disable HMLR
```python
# In Python console or add to test endpoint
from src.main import hmlr_service
hmlr_service.disable()
```

### Request
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me tasks",
    "session_id": "degradation_test",
    "user_id": "degradation_user"
  }'
```

### Expected Behavior
- The request should still work
- No HMLR logs should appear
- Response should be normal (just without memory context)

### Re-enable HMLR
```python
hmlr_service.enable()
```

---

## Part 3: Showcase Demonstrations

### Demo 1: "The Smart Assistant"

**Story:** Show how the agent learns and remembers over time.

```
Session 1:
User: "I'm David, I lead the platform team"
Agent: "Nice to meet you, David!"

User: "Sarah reports to me and handles API development"
Agent: "Got it, Sarah handles APIs under your leadership."

--- Later that day (new session) ---

Session 2:
User: "Who handles API development?"
Agent: "Sarah handles API development. She reports to you, David."
       ^^ Agent remembered from earlier!
```

### Demo 2: "The Context Keeper"

**Story:** Show how the agent maintains conversation flow.

```
User: "Let's talk about the Q4 roadmap"
Agent: [Discusses Q4 roadmap]

User: "What are the key milestones?"
Agent: [Lists Q4 milestones - knows we're still talking about Q4]

User: "Quick question - when's the next standup?"
Agent: "Tomorrow at 10am. Want to continue with the Q4 roadmap?"
       ^^ Agent offers to return to original topic

User: "Yes, where were we?"
Agent: "We were discussing Q4 milestones. You asked about..."
       ^^ Agent seamlessly resumes
```

### Demo 3: "The Learning Agent"

**Story:** Show preference learning over time.

```
Week 1:
User: "Give me a detailed breakdown of tasks"
Agent: [Provides detailed breakdown]

Week 2:
User: "Show tasks"
Agent: [Provides detailed breakdown automatically]
       ^^ Learned user prefers detailed responses

Week 3:
User: "Just give me a quick summary"
Agent: [Provides brief summary]
       ^^ Adapts to explicit request
```

---

## Part 4: Troubleshooting Tests

### Issue: No HMLR Logs Appearing

**Check:**
1. Is `HMLR_ENABLED=true` in config?
2. Is `session_id` provided in request? (not "default")
3. Is `user_id` provided?

**Test:**
```bash
curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test",
    "session_id": "debug_test",
    "user_id": "debug_user"
  }'
```

### Issue: Facts Not Being Saved

**Check SQL directly:**
```sql
SELECT TOP 10 * FROM fact_store ORDER BY created_at DESC;
```

**Check stored procedure:**
```sql
EXEC upsert_fact
  @user_id='test',
  @fact_key='test_key',
  @value='test_value',
  @category='Entity',
  @source_block_id=NULL,
  @source_chunk_id=NULL,
  @evidence_snippet='test',
  @confidence=1.0;

SELECT * FROM fact_store WHERE user_id='test';
```

### Issue: Blocks Not Being Created

**Check Cosmos DB:**
```
Container: bridge_blocks
Query: SELECT * FROM c WHERE c.session_id = "your_session_id"
```

---

## Part 5: Performance Benchmarks

### Baseline Latency Test

```python
import requests
import time

url = "http://localhost:8000/api/agent/query"
payload = {
    "query": "Show me tasks",
    "session_id": "perf_test",
    "user_id": "perf_user"
}

latencies = []
for i in range(10):
    start = time.time()
    requests.post(url, json=payload)
    latencies.append((time.time() - start) * 1000)

print(f"Average: {sum(latencies)/len(latencies):.0f}ms")
print(f"Min: {min(latencies):.0f}ms")
print(f"Max: {max(latencies):.0f}ms")
```

### Expected Performance

| Operation | Expected Latency |
|-----------|-----------------|
| HMLR Routing | < 200ms |
| Full Query (with AI) | < 3000ms |
| Fact Extraction (background) | < 500ms |

---

## Summary Checklist

Before declaring HMLR ready for production, verify:

- [ ] All automated tests pass
- [ ] Scenario 1 (Continuation) works
- [ ] Scenario 2 (Resumption) works
- [ ] Scenario 3 (New Topic) works
- [ ] Scenario 4 (Topic Shift) works
- [ ] Facts persist across sessions
- [ ] Multi-user isolation works
- [ ] Performance meets benchmarks
- [ ] Graceful degradation works
- [ ] No SQL injection vulnerabilities
- [ ] Unicode characters handled correctly

---

*Last Updated: December 2024*
