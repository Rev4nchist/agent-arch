# Plan: AI Guide Platform Awareness

## Objective
Enhance the Fourth AI Guide to answer questions about the platform itself - its features, operations, navigation, and how to accomplish tasks. The guide should serve as an onboarding assistant for new team members.

---

## Current State Analysis

| Component | Status | Notes |
|-----------|--------|-------|
| Guide Endpoint | ✓ Exists | `POST /api/agent/query` |
| AI Model | ✓ Configured | Azure AI Foundry Model Router |
| Guide UI | ✓ Exists | `/guide` page with chat interface |
| Context Injection | ✗ Manual only | No auto-retrieval |
| Platform Docs | ✗ Missing | No documentation storage |
| Source Attribution | ✗ Empty | `sources: []` always |

---

## Implementation Plan

### Phase 1: Platform Documentation Storage

**Goal:** Create structured documentation that the AI can reference.

#### 1.1 Create Platform Documentation Container
```python
# New Cosmos DB container: "platform_docs"
# Partition key: /category

PlatformDoc:
  id: str
  category: str  # "navigation", "feature", "workflow", "faq"
  title: str
  content: str   # Markdown content
  keywords: List[str]  # For search matching
  related_features: List[str]  # Links to other docs
  updated_at: datetime
```

#### 1.2 Seed Documentation Content
Create documentation for each platform section:

| Section | Topics to Document |
|---------|-------------------|
| **Dashboard** | Overview, stats cards, quick actions |
| **Proposals & Decisions** | Creating proposals, decision workflow, tabs |
| **Meetings Hub** | Scheduling, transcripts, action items |
| **Tasks** | Creating tasks, kanban view, filters, Architecture vs Feedback tabs |
| **Agents** | Agent registry, tiers, lifecycle stages |
| **Feedback Hub** | Submitting feedback, admin triage, convert to task |
| **Resources Library** | Uploading documents, categories, search |
| **Tech Radar** | Tool categories, recommendations |
| **Audit Trail** | Activity tracking, filters |
| **Fourth AI Guide** | How to use the guide itself |

#### 1.3 Documentation Schema Example
```json
{
  "id": "feedback-hub-overview",
  "category": "feature",
  "title": "Feedback Hub",
  "content": "The Feedback Hub allows team members to submit bug reports, feature requests, improvement ideas, and questions...",
  "keywords": ["feedback", "bug", "feature request", "submit", "idea"],
  "related_features": ["tasks", "feedback-admin"],
  "updated_at": "2025-12-03T00:00:00Z"
}
```

---

### Phase 2: Context Retrieval System

**Goal:** Automatically fetch relevant documentation based on user query.

#### 2.1 Query Classification
Detect query intent to determine what context to fetch:

```python
class QueryIntent(Enum):
    PLATFORM_HELP = "platform_help"      # "How do I create a task?"
    DATA_QUERY = "data_query"            # "What tasks are assigned to me?"
    NAVIGATION = "navigation"            # "Where can I find decisions?"
    GENERAL = "general"                  # General AI architecture questions
```

#### 2.2 Context Aggregation Service
```python
# backend/src/context_service.py

class ContextService:
    async def get_context_for_query(self, query: str, intent: QueryIntent) -> ContextResult:
        """Gather relevant context based on query intent."""

        context_parts = []
        sources = []

        if intent == QueryIntent.PLATFORM_HELP:
            # Search platform docs by keywords
            docs = await self.search_platform_docs(query)
            context_parts.append(self.format_docs(docs))
            sources.extend([d.title for d in docs])

        elif intent == QueryIntent.DATA_QUERY:
            # Fetch relevant data from Cosmos DB
            data = await self.fetch_relevant_data(query)
            context_parts.append(self.format_data(data))

        elif intent == QueryIntent.NAVIGATION:
            # Provide navigation structure
            nav = await self.get_navigation_context()
            context_parts.append(nav)

        return ContextResult(
            context="\n\n".join(context_parts),
            sources=sources
        )
```

#### 2.3 Keyword-Based Document Search
```python
async def search_platform_docs(self, query: str) -> List[PlatformDoc]:
    """Search platform docs by keyword matching."""

    # Extract keywords from query
    query_lower = query.lower()

    # Query Cosmos DB for matching docs
    docs = container.query_items(
        query="""
            SELECT * FROM c
            WHERE ARRAY_CONTAINS(c.keywords, @keyword)
            OR CONTAINS(LOWER(c.title), @query)
            OR CONTAINS(LOWER(c.content), @query)
        """,
        parameters=[
            {"name": "@keyword", "value": extracted_keyword},
            {"name": "@query", "value": query_lower}
        ]
    )

    return list(docs)[:5]  # Top 5 matches
```

---

### Phase 3: Enhanced System Prompt

**Goal:** Give the AI proper instructions for platform assistance.

#### 3.1 New System Prompt Structure
```python
PLATFORM_SYSTEM_PROMPT = """You are the Fourth AI Guide, the intelligent assistant for the Fourth AI Architecture Platform.

## Your Role
Help team members navigate and use the platform effectively. You can:
- Explain platform features and how to use them
- Guide users through workflows and processes
- Answer questions about platform data (meetings, tasks, agents, etc.)
- Suggest next steps and related features

## Platform Overview
The Fourth AI Architecture Platform helps the AI Architect Team manage:
- **Proposals & Decisions**: Track governance decisions and proposals
- **Meetings Hub**: Schedule meetings, process transcripts, track action items
- **Tasks**: Manage work items in list or kanban view
- **Agents**: Registry of AI agents across the organization
- **Feedback Hub**: Internal ticketing for bugs, features, and ideas
- **Resources Library**: Document storage and knowledge base
- **Tech Radar**: Technology adoption recommendations
- **Audit Trail**: Activity tracking and compliance

## Response Guidelines
1. Be concise but thorough
2. Include specific navigation paths (e.g., "Go to Tasks → Click 'New Task'")
3. Mention related features when relevant
4. If you reference documentation, cite the source
5. Suggest next steps or actions the user can take
6. If you don't know something, say so clearly

## Context
The following platform documentation is relevant to this query:

{context}
"""
```

#### 3.2 Response Format Guidelines
```python
RESPONSE_FORMAT_PROMPT = """
When answering platform questions, structure your response as:

1. **Direct Answer**: Answer the question concisely
2. **How To** (if applicable): Step-by-step instructions
3. **Tips**: Any helpful tips or shortcuts
4. **Related**: Mention related features or next steps

Keep responses focused and actionable.
"""
```

---

### Phase 4: Backend Implementation

#### 4.1 New Files to Create
```
backend/src/
├── context_service.py      # Context retrieval logic
├── platform_docs.py        # Documentation CRUD operations
└── routers/
    └── platform_docs.py    # API endpoints for docs management
```

#### 4.2 Update ai_client.py
```python
async def query_agent(
    self,
    query: str,
    context: Optional[str] = None,
    page_context: Optional[PageContext] = None
) -> AgentQueryResponse:
    """Enhanced query with automatic context retrieval."""

    # Classify intent
    intent = self.classify_intent(query)

    # Get relevant context
    context_service = ContextService()
    context_result = await context_service.get_context_for_query(query, intent)

    # Merge with any provided context
    full_context = context_result.context
    if context:
        full_context = f"{context}\n\n{full_context}"

    # Build enhanced prompt
    system_prompt = PLATFORM_SYSTEM_PROMPT.format(context=full_context)

    # Query AI
    response = self.client.complete(
        messages=[
            SystemMessage(content=system_prompt),
            UserMessage(content=query),
        ],
        model=settings.model_router_deployment,
        temperature=0.7,
        max_tokens=1500,
    )

    return AgentQueryResponse(
        response=response.choices[0].message.content,
        sources=context_result.sources,
        intent=intent.value
    )
```

#### 4.3 Update Request/Response Models
```python
class PageContext(BaseModel):
    """Context about user's current location in the app."""
    current_page: Optional[str] = None
    selected_ids: List[str] = []
    active_filters: dict = {}

class AgentQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    page_context: Optional[PageContext] = None  # NEW

class AgentQueryResponse(BaseModel):
    response: str
    sources: List[str] = []
    intent: Optional[str] = None  # NEW
    suggestions: List[str] = []   # NEW - follow-up suggestions
```

---

### Phase 5: Frontend Enhancements

#### 5.1 Update Guide Chat Component
```typescript
// Send page context with queries
const handleSendMessage = async () => {
  const response = await api.guide.query({
    query: inputMessage,
    page_context: {
      current_page: pathname,
      selected_ids: selectedItems,
      active_filters: currentFilters,
    }
  });

  // Display response with sources
  addMessage({
    role: 'assistant',
    content: response.response,
    sources: response.sources,
    suggestions: response.suggestions,
  });
};
```

#### 5.2 Display Sources in Responses
```tsx
{message.sources?.length > 0 && (
  <div className="mt-2 text-xs text-gray-500">
    <span className="font-medium">Sources:</span>
    {message.sources.map((source, i) => (
      <span key={i} className="ml-1 text-blue-600">{source}</span>
    ))}
  </div>
)}
```

#### 5.3 Quick Action Suggestions
```tsx
{message.suggestions?.length > 0 && (
  <div className="mt-3 flex flex-wrap gap-2">
    {message.suggestions.map((suggestion, i) => (
      <button
        key={i}
        onClick={() => setInputMessage(suggestion)}
        className="text-xs px-2 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
      >
        {suggestion}
      </button>
    ))}
  </div>
)}
```

---

### Phase 6: Documentation Seeding

#### 6.1 Initial Documentation Set
Create comprehensive docs for each feature:

```python
INITIAL_DOCS = [
    {
        "id": "getting-started",
        "category": "workflow",
        "title": "Getting Started with the Platform",
        "content": """
# Getting Started

Welcome to the Fourth AI Architecture Platform! Here's how to get oriented:

## Dashboard
The Dashboard (/dashboard) shows an overview of:
- Recent meetings and upcoming schedule
- Task summary by status
- Agent portfolio statistics
- Recent decisions

## Key Workflows
1. **Track a Decision**: Go to Proposals & Decisions → Create Proposal → Get approval → Becomes Decision
2. **Manage Tasks**: Go to Tasks → Create or view tasks in list/kanban view
3. **Submit Feedback**: Go to Feedback Hub → Submit New → Fill form
4. **Find Documents**: Go to Resources Library → Search or browse by category
        """,
        "keywords": ["start", "begin", "new", "help", "overview", "intro"]
    },
    # ... more docs
]
```

#### 6.2 Documentation Management API
```python
# POST /api/platform-docs - Create doc
# GET /api/platform-docs - List docs
# GET /api/platform-docs/{id} - Get doc
# PUT /api/platform-docs/{id} - Update doc
# DELETE /api/platform-docs/{id} - Delete doc
```

---

## Implementation Order

### Sprint 1: Foundation (Backend)
1. [ ] Create `platform_docs` Cosmos DB container
2. [ ] Create PlatformDoc model in models.py
3. [ ] Create platform_docs router with CRUD endpoints
4. [ ] Seed initial documentation (~20 docs covering all features)
5. [ ] Create ContextService with keyword search

### Sprint 2: AI Enhancement (Backend)
6. [ ] Update AgentQueryRequest/Response models
7. [ ] Implement intent classification
8. [ ] Update ai_client.py with new system prompt
9. [ ] Integrate ContextService into query flow
10. [ ] Add source tracking to responses

### Sprint 3: Frontend Integration
11. [ ] Update api.ts with new request/response types
12. [ ] Update Guide chat to send page_context
13. [ ] Display sources in chat messages
14. [ ] Add suggestion chips for follow-up questions
15. [ ] Test end-to-end flow

### Sprint 4: Polish & Documentation
16. [ ] Add more documentation content
17. [ ] Fine-tune keyword matching
18. [ ] Add "Was this helpful?" feedback
19. [ ] Performance optimization
20. [ ] User testing and iteration

---

## Example Interactions

### Example 1: Feature Question
**User:** "How do I submit a bug report?"

**AI Response:**
> To submit a bug report, follow these steps:
>
> 1. Go to **Feedback Hub** in the sidebar
> 2. Click **Submit New** button (top right)
> 3. Select **Bug Report** as the category
> 4. Fill in the title, description, and priority
> 5. Add relevant tags and click **Submit**
>
> **Tip:** Be as specific as possible in the description - include steps to reproduce the bug.
>
> **Related:** After submission, admins can convert your bug report to a Task for tracking.
>
> *Sources: Feedback Hub, Submit Feedback*

### Example 2: Navigation Question
**User:** "Where can I see all the decisions we've made?"

**AI Response:**
> You can view all decisions in **Proposals & Decisions** (click it in the sidebar).
>
> On that page:
> - Use the **Decisions** tab to see approved decisions
> - Use the **Proposals** tab to see items still under review
> - Filter by category, status, or date using the dropdowns
>
> **Tip:** Click any decision to see its full details, rationale, and linked meeting.
>
> *Sources: Proposals & Decisions*

### Example 3: Workflow Question
**User:** "What's the process for getting a new AI agent approved?"

**AI Response:**
> The agent approval workflow involves several steps:
>
> 1. **Submit Proposal**: Go to Proposals & Decisions → Create Proposal
>    - Select "Agent" category
>    - Describe the agent, use case, and tier level
>
> 2. **Review**: Proposal goes to "Reviewing" status
>    - Discussed in Governance meetings
>    - Stakeholders provide feedback
>
> 3. **Decision**: Once approved, becomes a formal Decision
>    - Agent is added to the Agent registry
>    - Related tasks are created
>
> 4. **Track Progress**: Monitor in Agents page
>    - Status moves through: Idea → Design → Development → Testing → Production
>
> *Sources: Proposals & Decisions, Agents*

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Query response time | < 3 seconds |
| Relevant context retrieval | > 80% accuracy |
| User satisfaction | > 4/5 rating |
| Documentation coverage | All features documented |
| Source attribution | 100% of platform queries cite sources |

---

## Technical Notes

### Database Changes
- New container: `platform_docs` (partition: `/category`)
- No changes to existing containers

### API Changes
- Enhanced `/api/agent/query` request/response
- New `/api/platform-docs` CRUD endpoints

### Performance Considerations
- Cache frequently accessed docs
- Limit context to top 5 relevant docs
- Use keyword indexing for fast search

### Future Enhancements
- Semantic search with Azure AI Search embeddings
- Multi-turn conversation memory
- Personalized responses based on user role
- Integration with meeting transcripts for contextual answers
