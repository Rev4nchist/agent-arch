# HMLR Technical Implementation Guide

## Overview

This document provides technical details for developers working with the HMLR (Hierarchical Memory Lookup & Routing) memory system integrated into the Azure Agent framework.

**Version:** 1.0
**Last Updated:** December 2024

---

## Table of Contents

1. [Architecture](#architecture)
2. [Components](#components)
3. [Data Models](#data-models)
4. [Database Schema](#database-schema)
5. [API Integration](#api-integration)
6. [Configuration](#configuration)
7. [Code Examples](#code-examples)
8. [Performance Tuning](#performance-tuning)
9. [Troubleshooting](#troubleshooting)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Azure Agent Framework                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────────────────────────────────────┐   │
│  │   FastAPI    │    │              HMLR Service                     │   │
│  │   Endpoint   │───►│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│  │              │    │  │ Governor │  │ Hydrator │  │  Scribe  │   │   │
│  │ /api/agent/  │    │  │ (Router) │  │(Context) │  │(Learner) │   │   │
│  │    query     │    │  └────┬─────┘  └────┬─────┘  └────┬─────┘   │   │
│  └──────────────┘    │       │             │             │          │   │
│                      │  ┌────▼─────────────▼─────────────▼────┐     │   │
│                      │  │         Bridge Block Manager         │     │   │
│                      │  │            Fact Scrubber             │     │   │
│                      │  └────┬─────────────────────────┬──────┘     │   │
│                      └───────┼─────────────────────────┼────────────┘   │
│                              │                         │                 │
├──────────────────────────────┼─────────────────────────┼─────────────────┤
│                              ▼                         ▼                 │
│  ┌───────────────────────────────────┐  ┌───────────────────────────┐   │
│  │         Azure Cosmos DB           │  │       Azure SQL           │   │
│  │                                   │  │                           │   │
│  │  Container: bridge_blocks         │  │  Tables:                  │   │
│  │  Partition: /session_id           │  │  - fact_store             │   │
│  │                                   │  │  - user_profiles          │   │
│  │  Stores: Topic-based conversation │  │  - fact_history           │   │
│  │  blocks (per-session)             │  │                           │   │
│  └───────────────────────────────────┘  │  Stores: Persistent facts │   │
│                                         │  and user preferences     │   │
│                                         │  (per-user, forever)      │   │
│                                         └───────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Request                                                              Response
   │                                                                    ▲
   ▼                                                                    │
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. ROUTING PHASE                                                         │
│    ┌─────────┐     ┌─────────────────────────────────────────────────┐  │
│    │ Request │────►│ Governor.route()                                │  │
│    └─────────┘     │   - asyncio.gather():                           │  │
│                    │     1. get_session_blocks() [Cosmos]            │  │
│                    │     2. lookup_facts() [SQL]                     │  │
│                    │     3. retrieve_memories() [future: AI Search]  │  │
│                    │   - compute_topic_similarity()                  │  │
│                    │   - determine_scenario() → 1, 2, 3, or 4        │  │
│                    └─────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────┤
│ 2. CONTEXT PHASE                                                         │
│    ┌──────────────┐    ┌─────────────────────────────────────────────┐  │
│    │ Governor     │───►│ Hydrator.hydrate()                          │  │
│    │ Decision     │    │   - build_block_summary()                   │  │
│    └──────────────┘    │   - build_block_history()                   │  │
│                        │   - build_facts_text()                      │  │
│                        │   - build_preferences_text()                │  │
│                        │   - assemble_full_context()                 │  │
│                        └─────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────┤
│ 3. AI QUERY PHASE                                                        │
│    ┌──────────────┐    ┌─────────────────────────────────────────────┐  │
│    │ Hydrated     │───►│ ai_client.query_agent()                     │  │
│    │ Context      │    │   - context = hmlr_context + live_context   │  │
│    └──────────────┘    │   - Generates response with full context    │  │
│                        └─────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────┤
│ 4. STORAGE PHASE (Background)                                            │
│    ┌──────────────┐    ┌─────────────────────────────────────────────┐  │
│    │ AI Response  │───►│ hmlr_service.store_turn()                   │  │
│    └──────────────┘    │   - Create/update BridgeBlock [Cosmos]      │  │
│                        │   - Background: fact_scrubber.extract()     │  │
│                        │   - Background: scribe.process_turn()       │  │
│                        └─────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. HMLRService (`service.py`)

**Purpose:** Main orchestrator that coordinates all HMLR components.

```python
class HMLRService:
    def __init__(self, ai_client=None, sql_connection_string=None):
        self.sql_client = HMLRSQLClient(...)
        self.block_manager = BridgeBlockManager()
        self.governor = Governor(...)
        self.fact_scrubber = FactScrubber(...)
        self.hydrator = ContextHydrator()
        self.scribe = Scribe(...)

    async def route_query(user_id, session_id, query, intent, entities):
        """Main entry point - returns (GovernorDecision, HydratedContext)"""

    async def store_turn(user_id, session_id, query, response, decision, ...):
        """Store conversation turn and trigger background processing"""
```

**Key Methods:**
| Method | Purpose |
|--------|---------|
| `route_query()` | Get routing decision and hydrated context |
| `store_turn()` | Store turn, trigger fact extraction |
| `get_user_facts()` | Retrieve all facts for a user |
| `get_user_profile()` | Get user profile |
| `end_session()` | Clean up when session ends |

---

### 2. Governor (`governor.py`)

**Purpose:** Routes conversations using 4 scenarios based on topic similarity.

```python
class Governor:
    async def route(user_id, session_id, query, intent, entities) -> GovernorDecision:
        # Parallel execution (key HMLR pattern)
        blocks, facts, memories = await asyncio.gather(
            self._get_session_blocks(session_id),
            self._lookup_facts(user_id, query),
            self._retrieve_memories(user_id, query)
        )

        # Determine scenario
        if not active_block:
            if matching_paused:
                return SCENARIO_2  # Resumption
            return SCENARIO_3  # New Topic First

        if topic_similarity >= threshold:
            return SCENARIO_1  # Continuation

        if matching_paused:
            return SCENARIO_2  # Resumption

        return SCENARIO_4  # Topic Shift
```

**Routing Scenarios:**

| Scenario | Condition | Action |
|----------|-----------|--------|
| 1 - Continuation | Active block + high similarity | Continue in same block |
| 2 - Resumption | Paused block matches query | Resume paused block |
| 3 - New Topic First | No active blocks | Create new block |
| 4 - Topic Shift | Active block + low similarity | Pause current, create new |

**Similarity Calculation:**
```python
def _compute_topic_similarity(query, block) -> float:
    # Keyword overlap + topic label match + recent turn context
    # Returns 0.0 - 1.0
    # Threshold: 0.7 (configurable)
```

---

### 3. BridgeBlockManager (`bridge_block_mgr.py`)

**Purpose:** CRUD operations for Bridge Blocks in Cosmos DB.

```python
class BridgeBlockManager:
    CONTAINER_NAME = "bridge_blocks"

    async def create_block(session_id, user_id, topic_label, first_turn=None)
    async def get_session_blocks(session_id) -> List[BridgeBlock]
    async def get_active_block(session_id) -> Optional[BridgeBlock]
    async def add_turn(block_id, session_id, turn)
    async def pause_block(block_id, session_id)
    async def resume_block(block_id, session_id)
```

**Block Lifecycle:**
```
CREATE (ACTIVE) ──► ADD_TURNS ──► PAUSE ──► RESUME ──► ...
                                    │
                                    └──► DELETE (session end)
```

---

### 4. FactScrubber (`fact_scrubber.py`)

**Purpose:** Extracts hard facts from conversations using LLM or regex fallback.

```python
class FactScrubber:
    EXTRACTION_PROMPT = """Extract ONLY hard facts...
    CATEGORIES: Definition, Acronym, Secret, Entity
    Return JSON: {"facts": [...]}
    """

    async def extract_and_save(user_id, block_id, text) -> List[Fact]:
        # 1. Extract facts (LLM or regex)
        # 2. Save to Azure SQL
        # 3. Return saved facts
```

**Extraction Patterns (Regex Fallback):**
| Category | Patterns |
|----------|----------|
| Definition | `X is Y`, `X means Y`, `X: Y` |
| Acronym | `X stands for Y`, `X (Y)` |
| Entity | Named entities with relationships |
| Secret | `api_key:`, `password:`, `token:` |

---

### 5. ContextHydrator (`hydrator.py`)

**Purpose:** Assembles context for LLM prompts from multiple sources.

```python
class ContextHydrator:
    async def hydrate(decision, profile, query) -> HydratedContext:
        return HydratedContext(
            block_summary=self._build_block_summary(block),
            block_history=self._build_block_history(block),
            relevant_facts_text=self._build_facts_text(facts),
            user_preferences_text=self._build_preferences_text(profile),
            open_loops_text=self._build_open_loops_text(block),
            full_context=assembled_context,
            token_estimate=len(context) * 0.25
        )
```

**Context Assembly Order:**
1. Scenario label (e.g., "Continuing conversation on same topic")
2. Block summary (topic, keywords, decisions)
3. User preferences
4. Relevant facts
5. Open loops
6. Recent conversation history

---

### 6. Scribe (`scribe.py`)

**Purpose:** Background agent that learns user preferences over time.

```python
class Scribe:
    async def process_turn(user_id, block, turn) -> Optional[ScribeUpdate]:
        # Extract patterns from turn
        updates = {}
        updates["common_queries"] = self._extract_query_pattern(turn.query)
        updates["known_entities"] = self._extract_entities(turn)
        updates["interaction_patterns"] = self._analyze_interaction_pattern(turn)

        # Save to profile
        for field, value in updates.items():
            await self.sql_client.update_profile_field(user_id, field, value)
```

**What Scribe Learns:**
| Field | What It Tracks |
|-------|----------------|
| `common_queries` | Frequently asked query patterns |
| `known_entities` | People, services, projects mentioned |
| `interaction_patterns` | Query style, expertise level |
| `preferences` | Response preferences, topic interests |

---

### 7. SQLClient (`sql_client.py`)

**Purpose:** Azure SQL operations for facts and user profiles.

```python
class HMLRSQLClient:
    async def save_fact(fact: Fact) -> int  # Returns fact_id
    async def get_facts_by_user(user_id, limit) -> List[Fact]
    async def search_facts(user_id, keywords, limit) -> List[Fact]
    async def get_fact_by_key(user_id, key) -> Optional[Fact]
    async def delete_fact(fact_id) -> bool

    async def get_user_profile(user_id) -> Optional[UserProfile]
    async def save_user_profile(profile) -> bool
    async def update_profile_field(user_id, field, value) -> bool
```

---

## Data Models

### BridgeBlock

```python
class BridgeBlock(BaseModel):
    id: str                          # "bb_20241206_143022_abc123"
    session_id: str                  # Partition key for Cosmos
    user_id: str
    topic_label: str                 # "Task Discussion"
    summary: str = ""                # AI-generated summary
    keywords: List[str] = []         # For similarity matching
    turns: List[Turn] = []           # Conversation history
    open_loops: List[str] = []       # Unresolved items
    decisions_made: List[str] = []   # Recorded decisions
    status: BlockStatus              # ACTIVE or PAUSED
    created_at: datetime
    last_activity: datetime
```

### Turn

```python
class Turn(BaseModel):
    index: int
    query: str
    response_summary: str            # Truncated for storage
    intent: Optional[str]
    entities: List[str] = []
    timestamp: datetime
```

### Fact

```python
class Fact(BaseModel):
    fact_id: Optional[int]           # SQL identity
    user_id: str
    key: str                         # "david_role", "API", etc.
    value: str                       # The fact content
    category: FactCategory           # Definition|Acronym|Secret|Entity
    source_block_id: Optional[str]   # Provenance
    source_chunk_id: Optional[str]
    evidence_snippet: Optional[str]  # Context around fact
    confidence: float = 1.0          # 0.0 - 1.0
    verified: bool = False
    created_at: Optional[datetime]
```

### GovernorDecision

```python
class GovernorDecision(BaseModel):
    scenario: RoutingScenario        # 1, 2, 3, or 4
    matched_block_id: Optional[str]
    is_new_topic: bool
    suggested_label: str
    active_block: Optional[BridgeBlock]
    relevant_facts: List[Fact]
    memories: List[Dict]
    topic_similarity: float
```

### HydratedContext

```python
class HydratedContext(BaseModel):
    block_summary: str = ""
    block_history: str = ""
    relevant_facts_text: str = ""
    user_preferences_text: str = ""
    open_loops_text: str = ""
    full_context: str = ""
    token_estimate: int = 0
```

---

## Database Schema

### Azure SQL Tables

#### fact_store
```sql
CREATE TABLE fact_store (
    fact_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id NVARCHAR(255) NOT NULL,
    [key] NVARCHAR(255) NOT NULL,        -- Note: [key] is reserved word
    value NVARCHAR(MAX) NOT NULL,
    category NVARCHAR(50) NOT NULL,
    source_block_id NVARCHAR(255),
    source_chunk_id NVARCHAR(255),
    evidence_snippet NVARCHAR(MAX),
    confidence FLOAT DEFAULT 1.0,
    verified BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Indexes
CREATE INDEX IX_fact_key ON fact_store([key]);
CREATE INDEX IX_fact_user ON fact_store(user_id);
CREATE INDEX IX_fact_category ON fact_store(category);
```

#### user_profiles
```sql
CREATE TABLE user_profiles (
    profile_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id NVARCHAR(255) UNIQUE NOT NULL,
    preferences NVARCHAR(MAX),           -- JSON
    common_queries NVARCHAR(MAX),        -- JSON array
    known_entities NVARCHAR(MAX),        -- JSON array
    interaction_patterns NVARCHAR(MAX),  -- JSON
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    last_updated DATETIME2 DEFAULT GETUTCDATE()
);
```

#### fact_history
```sql
CREATE TABLE fact_history (
    history_id INT IDENTITY(1,1) PRIMARY KEY,
    fact_id INT NOT NULL,
    user_id NVARCHAR(255) NOT NULL,
    old_value NVARCHAR(MAX),
    new_value NVARCHAR(MAX),
    change_reason NVARCHAR(255),
    changed_at DATETIME2 DEFAULT GETUTCDATE(),
    FOREIGN KEY (fact_id) REFERENCES fact_store(fact_id) ON DELETE CASCADE
);
```

### Stored Procedures

#### upsert_fact
```sql
CREATE PROCEDURE upsert_fact
    @user_id NVARCHAR(255),
    @fact_key NVARCHAR(255),    -- Note: renamed from @key
    @value NVARCHAR(MAX),
    @category NVARCHAR(50),
    @source_block_id NVARCHAR(255) = NULL,
    @source_chunk_id NVARCHAR(255) = NULL,
    @evidence_snippet NVARCHAR(MAX) = NULL,
    @confidence FLOAT = 1.0
AS
BEGIN
    -- Insert or update fact
    -- Archives old value to fact_history on update
END
```

### Cosmos DB Container

**Container:** `bridge_blocks`
**Partition Key:** `/session_id`

```json
{
    "id": "bb_20241206_143022_abc123",
    "session_id": "session_xyz",
    "user_id": "david.hayes",
    "topic_label": "Q4 Task Review",
    "summary": "Reviewing overdue tasks for Q4",
    "keywords": ["tasks", "Q4", "overdue", "review"],
    "turns": [
        {
            "index": 0,
            "query": "Show me overdue Q4 tasks",
            "response_summary": "Found 5 overdue tasks...",
            "intent": "task_query",
            "entities": ["tasks", "Q4"],
            "timestamp": "2024-12-06T14:30:22Z"
        }
    ],
    "open_loops": ["Need to assign Task #123"],
    "decisions_made": ["Prioritize API Gateway work"],
    "status": "ACTIVE",
    "created_at": "2024-12-06T14:30:22Z",
    "last_activity": "2024-12-06T14:35:10Z"
}
```

---

## API Integration

### Query Endpoint Integration

**File:** `main.py`
**Endpoint:** `POST /api/agent/query`

```python
@app.post("/api/agent/query")
async def query_agent(request: AgentQueryRequest):
    # ... existing code ...

    # HMLR Integration Point 1: Route and get context
    hmlr_decision = None
    user_id = request.user_id or "anonymous"
    if settings.hmlr_enabled and session_id != "default":
        hmlr_decision, hmlr_hydrated = await hmlr_service.route_query(
            user_id=user_id,
            session_id=session_id,
            query=request.query,
            intent=classified.intent.value,
            entities=classified.entities
        )
        if hmlr_hydrated.full_context:
            context = f"{hmlr_hydrated.full_context}\n\n{context}"

    # ... AI query ...

    # HMLR Integration Point 2: Store turn
    if settings.hmlr_enabled and hmlr_decision:
        await hmlr_service.store_turn(
            user_id=user_id,
            session_id=session_id,
            query=request.query,
            response=result.get('response', ''),
            decision=hmlr_decision,
            intent=classified.intent.value,
            entities=classified.entities
        )
```

### Request Model

```python
class AgentQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    page_context: Optional[PageContext] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None      # Required for HMLR
```

---

## Configuration

### Environment Variables

```bash
# .env file

# HMLR Azure SQL Connection
HMLR_SQL_CONNECTION_STRING=Driver={SQL Server};Server=tcp:agent-arch-sql.database.windows.net,1433;Database=hmlr-db;Uid=sqladmin;Pwd=YourPassword;Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;
```

### Application Settings

**File:** `config.py`

```python
class Settings(BaseSettings):
    # HMLR Configuration
    hmlr_enabled: bool = True
    hmlr_sql_connection_string: str = ""
    hmlr_max_blocks_per_session: int = 10
    hmlr_block_inactive_minutes: int = 15
    hmlr_fact_extraction_enabled: bool = True
    hmlr_profile_update_enabled: bool = True
    hmlr_topic_similarity_threshold: float = 0.7
```

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `hmlr_enabled` | `True` | Enable/disable HMLR globally |
| `hmlr_topic_similarity_threshold` | `0.7` | Minimum similarity for topic continuation |
| `hmlr_max_blocks_per_session` | `10` | Max topic blocks per session |
| `hmlr_fact_extraction_enabled` | `True` | Enable background fact extraction |
| `hmlr_profile_update_enabled` | `True` | Enable profile learning |

---

## Code Examples

### Example 1: Basic Query with Memory

```python
from src.hmlr import HMLRService

# Initialize
hmlr = HMLRService(ai_client=my_ai_client)

# Route a query
decision, context = await hmlr.route_query(
    user_id="david.hayes",
    session_id="session_123",
    query="What tasks are assigned to me?",
    intent="task_query",
    entities=["tasks", "david"]
)

print(f"Scenario: {decision.scenario}")  # 1, 2, 3, or 4
print(f"Context tokens: {context.token_estimate}")
print(f"Memory context:\n{context.full_context}")
```

### Example 2: Storing a Turn

```python
# After AI generates response
block = await hmlr.store_turn(
    user_id="david.hayes",
    session_id="session_123",
    query="What tasks are assigned to me?",
    response="You have 5 tasks: Task A, Task B...",
    decision=decision,
    intent="task_query",
    entities=["tasks", "david"]
)

print(f"Stored in block: {block.id}")
print(f"Block now has {len(block.turns)} turns")
```

### Example 3: Manual Fact Creation

```python
from src.hmlr.models import Fact, FactCategory

# Create a fact directly
fact = Fact(
    user_id="david.hayes",
    key="sarah_role",
    value="Sarah owns the API Gateway service",
    category=FactCategory.ENTITY,
    confidence=1.0
)

fact_id = await hmlr.sql_client.save_fact(fact)
print(f"Saved fact with ID: {fact_id}")

# Search for facts
facts = await hmlr.sql_client.search_facts(
    user_id="david.hayes",
    keywords=["sarah", "API"],
    limit=5
)
```

### Example 4: Profile Management

```python
# Get or create profile
profile = await hmlr.get_user_profile("david.hayes")

# Update preference
await hmlr.scribe.update_preference(
    user_id="david.hayes",
    key="response_style",
    value="detailed"
)

# Add known entity
await hmlr.scribe.add_known_entity(
    user_id="david.hayes",
    name="Sarah",
    role="API Gateway Owner",
    context="Backend team"
)
```

---

## Performance Tuning

### Latency Breakdown

| Operation | Typical Latency | Notes |
|-----------|-----------------|-------|
| Governor routing | 100-300ms | Parallel DB calls |
| Context hydration | 10-50ms | In-memory assembly |
| Fact extraction | 200-500ms | Background, async |
| Profile update | 50-100ms | Background, async |
| **Total overhead** | **150-400ms** | Added to query time |

### Optimization Tips

1. **Use session_id consistently**
   - Same session = faster routing (blocks cached)
   - New session = cold start overhead

2. **Provide intent and entities**
   - Helps Governor make faster decisions
   - Improves fact search relevance

3. **Tune similarity threshold**
   - Higher (0.8+) = more topic shifts, less context
   - Lower (0.5-) = more continuations, richer context

4. **Limit fact extraction**
   - Set `hmlr_fact_extraction_enabled=False` for speed-critical paths
   - Enable for conversational flows

### Connection Pooling

The SQL client maintains a single connection. For high-concurrency:

```python
# Consider connection pooling for production
# Current implementation:
class HMLRSQLClient:
    def _get_connection(self):
        if self._connection is None or self._connection.closed:
            self._connection = pyodbc.connect(self.connection_string)
        return self._connection
```

---

## Troubleshooting

### Common Issues

#### 1. "HMLR logs not appearing"

**Check:**
- `settings.hmlr_enabled` is `True`
- `session_id` is provided and not "default"
- `user_id` is provided

**Debug:**
```python
print(f"HMLR enabled: {settings.hmlr_enabled}")
print(f"Session ID: {request.session_id}")
print(f"User ID: {request.user_id}")
```

#### 2. "Facts not being saved"

**Check:**
- SQL connection string is valid
- `fact_store` table exists
- `upsert_fact` stored procedure exists

**Debug:**
```sql
-- Check table
SELECT COUNT(*) FROM fact_store;

-- Test stored procedure
EXEC upsert_fact @user_id='test', @fact_key='test', @value='test', @category='Entity';
```

#### 3. "Bridge blocks not created"

**Check:**
- Cosmos DB is initialized
- `bridge_blocks` container exists
- Partition key is `/session_id`

**Debug:**
```python
from src.database import db
db.initialize()
container = db.get_container("bridge_blocks")
print(f"Container: {container}")
```

#### 4. "Topic continuation not working"

**Cause:** Similarity below threshold (0.7)

**Fix:**
- Add more keywords to blocks
- Lower `hmlr_topic_similarity_threshold`
- Check keyword extraction in Governor

#### 5. "Performance degradation"

**Check:**
- Azure SQL connection latency
- Cosmos DB RU consumption
- Network latency to Azure

**Monitor:**
```python
import time

start = time.time()
decision, context = await hmlr.route_query(...)
print(f"Routing took: {(time.time() - start) * 1000:.0f}ms")
```

### Logging

Enable detailed logging:

```python
import logging

logging.getLogger("src.hmlr").setLevel(logging.DEBUG)
logging.getLogger("src.hmlr.governor").setLevel(logging.DEBUG)
logging.getLogger("src.hmlr.fact_scrubber").setLevel(logging.DEBUG)
```

### Health Check

```python
async def check_hmlr_health():
    """Verify HMLR components are working."""
    results = {}

    # SQL
    try:
        from src.hmlr.sql_client import HMLRSQLClient
        client = HMLRSQLClient(settings.hmlr_sql_connection_string)
        conn = client._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        results["sql"] = "OK"
        client.close()
    except Exception as e:
        results["sql"] = f"ERROR: {e}"

    # Cosmos
    try:
        from src.hmlr.bridge_block_mgr import BridgeBlockManager
        mgr = BridgeBlockManager()
        blocks = await mgr.get_session_blocks("health_check")
        results["cosmos"] = "OK"
    except Exception as e:
        results["cosmos"] = f"ERROR: {e}"

    return results
```

---

## File Structure

```
backend/src/hmlr/
├── __init__.py           # Module exports
├── models.py             # Pydantic data models
├── service.py            # HMLRService orchestrator
├── governor.py           # Routing logic (4 scenarios)
├── bridge_block_mgr.py   # Cosmos DB operations
├── fact_scrubber.py      # Fact extraction
├── hydrator.py           # Context assembly
├── scribe.py             # Profile learning
└── sql_client.py         # Azure SQL operations

backend/scripts/
├── hmlr_azure_sql_schema.sql   # SQL schema script
└── run_hmlr_schema.py          # Python schema runner

backend/tests/
└── test_hmlr_integration.py    # 27 integration tests

backend/docs/
├── HMLR_Memory_System_Overview.md   # Non-technical guide
├── HMLR_Technical_Guide.md          # This document
└── HMLR_Test_Guide.md               # Test scenarios
```

---

## References

- Original HMLR concept: [Sean-V-Dev/HMLR-Agentic-AI-Memory-System](https://github.com/Sean-V-Dev/HMLR-Agentic-AI-Memory-System)
- Azure Cosmos DB: [Documentation](https://docs.microsoft.com/azure/cosmos-db/)
- Azure SQL: [Documentation](https://docs.microsoft.com/azure/azure-sql/)

---

*Last Updated: December 2024*
