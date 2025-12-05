# Agent-Arch ↔ MSFT Ecosystem Integration Architecture

## Overview

This document outlines the integration between the **Agent-Arch governance platform** and the **Microsoft AI ecosystem** (Azure AI Foundry, Agent Service, Fabric, etc.) to enable end-to-end agent lifecycle management.

---

## The Vision: 4-Phase Agent Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT-ARCH PLATFORM                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │   PHASE 1    │   │   PHASE 2    │   │   PHASE 3    │   │   PHASE 4    │ │
│  │   REQUEST    │ → │ COLLABORATE  │ → │    BUILD     │ → │   MONITOR    │ │
│  │              │   │              │   │              │   │              │ │
│  │ Staff/Dept   │   │ Back & Forth │   │ Azure AI     │   │ Usage Stats  │ │
│  │ submits idea │   │ Messaging    │   │ Foundry      │   │ from Azure   │ │
│  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
         │                   │                   │                   │
         ▼                   ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MICROSOFT ECOSYSTEM                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │   DevOps     │   │   Teams      │   │ AI Foundry   │   │   Monitor    │ │
│  │   Boards     │   │   Channels   │   │ Agent SDK    │   │   Fabric     │ │
│  │   (sync)     │   │   (notify)   │   │ (deploy)     │   │   (metrics)  │ │
│  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Agent Request System

### Current State (agent-arch)
- ✅ Agent creation form with tier, owner, department, use case
- ✅ Status: `Idea → Design → Development → Testing → Staging → Production`
- ✅ Owner assignment & contact info
- ⚠️ No structured intake workflow

### Enhanced Request Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        NEW AGENT REQUEST FORM                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  REQUESTER INFO                                                          │
│  ├── Name: [________________________]                                    │
│  ├── Department: [Dropdown ▼]                                            │
│  ├── Email: [________________________]                                   │
│  └── Teams Channel: [________________________]                           │
│                                                                          │
│  AGENT CONCEPT                                                           │
│  ├── Agent Name: [________________________]                              │
│  ├── Problem Statement: [                                        ]       │
│  │                      [________________________________________]       │
│  ├── Proposed Solution: [                                        ]       │
│  │                      [________________________________________]       │
│  └── Expected Tier: ○ Individual  ○ Department  ○ Enterprise             │
│                                                                          │
│  DATA & ACCESS                                                           │
│  ├── Data Sources Needed: □ Fourth IQ  □ SP Lists  □ D365  □ Other      │
│  ├── Who needs access? [________________________]                        │
│  └── Sensitive data? ○ Yes  ○ No  (triggers security review)            │
│                                                                          │
│  PRIORITY                                                                │
│  ├── Business Impact: ○ Critical  ○ High  ○ Medium  ○ Low               │
│  └── Urgency: [Target date picker]                                       │
│                                                                          │
│  [Submit Request]                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Model Enhancement

```python
# New fields for Agent model
class AgentRequest(BaseModel):
    # Existing fields...

    # New Request fields
    requester_id: str           # Who submitted
    requester_dept: str         # Department
    requester_email: str        # For notifications
    requester_teams_channel: Optional[str]  # Teams channel ID

    # Request details
    problem_statement: str      # What problem does this solve?
    proposed_solution: str      # How will the agent help?
    business_impact: Literal["critical", "high", "medium", "low"]
    target_date: Optional[datetime]

    # Approval workflow
    approval_status: Literal["pending_review", "in_discussion", "approved", "rejected", "deferred"]
    assigned_architect: Optional[str]  # AI Architect assigned
    review_notes: Optional[str]

    # Integration IDs
    devops_work_item_id: Optional[str]  # Azure DevOps sync
    teams_thread_id: Optional[str]       # Teams conversation
    foundry_agent_id: Optional[str]      # Once built
```

### API Endpoints to Add

```
POST   /api/agents/request              → Submit new agent request
GET    /api/agents/requests/queue       → Get pending requests
PATCH  /api/agents/{id}/assign          → Assign architect
PATCH  /api/agents/{id}/approve         → Approve for build
POST   /api/agents/{id}/start-discussion → Create Teams thread
```

---

## Phase 2: Communication & Collaboration

### Option A: Built-in Messaging (Recommended for MVP)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENT: Ops Scheduling Assistant                   Status: In Discussion │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                    CONVERSATION THREAD                              ││
│  ├─────────────────────────────────────────────────────────────────────┤│
│  │ Sarah (Operations) - 2 days ago                                     ││
│  │ "We need an agent that can help managers schedule shifts faster.    ││
│  │  Currently takes 2 hours per week per manager."                     ││
│  │                                                                      ││
│  │ David (AI Architect) - 2 days ago                                   ││
│  │ "Great use case! A few questions:                                   ││
│  │  1. What data sources would it need? (schedules, availability)      ││
│  │  2. Should it auto-schedule or just suggest?"                       ││
│  │                                                                      ││
│  │ Sarah (Operations) - 1 day ago                                      ││
│  │ "It would need HotSchedules data. Suggestions first, managers       ││
│  │  approve. Also needs to respect labor law constraints."             ││
│  │                                                                      ││
│  │ David (AI Architect) - 1 day ago                                    ││
│  │ "Perfect. I've updated the spec. Looks like Tier 2 (Department).   ││
│  │  Ready for governance review? [Approve for Build]"                  ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ Type a message...                                    [@mention] [📎]││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  [Request More Info]  [Update Spec]  [Approve for Build]  [Defer]       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Model for Messages

```python
class AgentMessage(BaseModel):
    id: str
    agent_id: str               # Which agent request this belongs to
    author_id: str              # Who sent it
    author_name: str
    author_role: Literal["requester", "architect", "governance", "system"]
    content: str
    attachments: List[Attachment]  # File references
    mentions: List[str]         # @mentioned users
    created_at: datetime

    # Thread support
    reply_to: Optional[str]     # Parent message ID

    # Actions taken
    action_type: Optional[Literal["status_change", "spec_update", "approval", "question"]]

class AgentDiscussion(BaseModel):
    agent_id: str
    messages: List[AgentMessage]
    participants: List[str]     # All involved users
    last_activity: datetime
    unread_count: Dict[str, int]  # Per-user unread counts
```

### API Endpoints for Messaging

```
GET    /api/agents/{id}/messages              → Get conversation
POST   /api/agents/{id}/messages              → Send message
PATCH  /api/agents/{id}/messages/{msg_id}     → Edit message
DELETE /api/agents/{id}/messages/{msg_id}     → Delete message
POST   /api/agents/{id}/messages/{msg_id}/react  → Add reaction
GET    /api/agents/{id}/participants          → Get thread participants
POST   /api/agents/{id}/invite                → Invite user to discussion
```

### Option B: Teams Integration (Future Enhancement)

```python
# Integration with Microsoft Graph API
class TeamsIntegration:
    async def create_channel_for_agent(self, agent_id: str, agent_name: str):
        """Create Teams channel: #agent-{agent_name}"""

    async def post_to_channel(self, channel_id: str, message: str):
        """Post message to Teams channel"""

    async def sync_messages(self, channel_id: str, agent_id: str):
        """Sync Teams messages back to agent-arch"""

    async def notify_stakeholders(self, agent_id: str, event: str):
        """Send Teams notifications for status changes"""
```

---

## Phase 3: Build & Deploy in MSFT Ecosystem

### Connection Points

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT-ARCH → AZURE AI FOUNDRY                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  AGENT REQUEST (agent-arch)          AZURE AI FOUNDRY                   │
│  ┌──────────────────────┐            ┌──────────────────────┐           │
│  │ name: "Ops Scheduler"│  ────────► │ Project: ops-scheduler│          │
│  │ tier: Department     │            │ Hub: fourth-agents-hub│          │
│  │ data_sources: [...]  │            │                       │          │
│  │ use_case: "..."      │            │ Connections:          │          │
│  │                      │            │ - Fourth IQ (Fabric)  │          │
│  │ foundry_agent_id: ──────────────► │ - HotSchedules API    │          │
│  │   "ops-scheduler-prod"│            │                       │          │
│  └──────────────────────┘            │ Deployments:          │          │
│                                      │ - Agent endpoint      │          │
│                                      │ - Teams bot           │          │
│                                      └──────────────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Workflow Automation

```python
# When agent status changes to "Development"
@app.on_event("agent_status_change")
async def handle_agent_development(agent_id: str, new_status: str):
    if new_status == "Development":
        agent = await get_agent(agent_id)

        # 1. Create Azure AI Foundry Project
        foundry_project = await azure_foundry.create_project(
            name=agent.name.lower().replace(" ", "-"),
            hub="fourth-agents-hub",
            description=agent.description
        )

        # 2. Configure connections based on data_sources
        for source in agent.data_sources:
            await foundry_project.add_connection(
                get_connection_config(source)
            )

        # 3. Create initial agent scaffolding
        await foundry_project.create_agent_template(
            tier=agent.tier,
            use_case=agent.use_case
        )

        # 4. Update agent-arch with Foundry reference
        await update_agent(agent_id, {
            "foundry_project_id": foundry_project.id,
            "foundry_project_url": foundry_project.url
        })

        # 5. Create DevOps work items
        await devops.create_work_items_from_agent(agent)
```

### Azure Resource Mapping

| Agent-Arch Field | Azure AI Foundry Resource |
|-----------------|---------------------------|
| `name` | Project name |
| `tier` | Resource allocation tier |
| `data_sources` | Connections (Fabric, APIs, Cosmos) |
| `department` | Resource Group tag |
| `owner` | Project RBAC assignment |
| `status` | Deployment environment (Dev/Stage/Prod) |

### API Endpoints for MSFT Integration

```
POST   /api/agents/{id}/provision-foundry    → Create Foundry project
GET    /api/agents/{id}/foundry-status       → Get Foundry project status
POST   /api/agents/{id}/deploy               → Deploy agent to environment
GET    /api/agents/{id}/deployments          → List deployments
POST   /api/agents/{id}/sync-devops          → Sync with Azure DevOps
```

---

## Phase 4: Metrics & Reporting from Azure

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AZURE → AGENT-ARCH METRICS                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  AZURE AI FOUNDRY                    AGENT-ARCH DASHBOARD               │
│  ┌──────────────────────┐            ┌──────────────────────┐           │
│  │ Agent Metrics:       │            │ Agent: Ops Scheduler │           │
│  │ - Queries: 1,247     │  ────────► │                      │           │
│  │ - Tokens: 892K       │            │ Usage This Week:     │           │
│  │ - Avg latency: 2.1s  │            │ ████████░░ 1,247     │           │
│  │ - Success: 94.2%     │            │                      │           │
│  │ - Errors: 73         │            │ Cost: $127.45        │           │
│  └──────────────────────┘            │ Success: 94.2%       │           │
│                                      │ Avg Response: 2.1s   │           │
│  AZURE MONITOR                       │                      │           │
│  ┌──────────────────────┐            │ Top Users:           │           │
│  │ App Insights:        │  ────────► │ 1. Sarah M. (312)    │           │
│  │ - Request traces     │            │ 2. Mike R. (287)     │           │
│  │ - Error logs         │            │ 3. Lisa K. (198)     │           │
│  │ - User sessions      │            │                      │           │
│  └──────────────────────┘            │ [View Full Report]   │           │
│                                      └──────────────────────┘           │
│  MICROSOFT FABRIC                                                        │
│  ┌──────────────────────┐                                               │
│  │ Usage Analytics:     │                                               │
│  │ - Daily active users │  ────────► Real-time dashboards               │
│  │ - Query patterns     │            Power BI embedding                  │
│  │ - ROI calculations   │                                               │
│  └──────────────────────┘                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Metrics Data Model

```python
class AgentMetrics(BaseModel):
    agent_id: str
    period: Literal["hourly", "daily", "weekly", "monthly"]
    timestamp: datetime

    # Usage metrics
    total_queries: int
    unique_users: int
    total_tokens_input: int
    total_tokens_output: int

    # Performance metrics
    avg_latency_ms: float
    p95_latency_ms: float
    success_rate: float
    error_count: int

    # Cost metrics
    compute_cost_usd: float
    token_cost_usd: float
    total_cost_usd: float

    # User engagement
    top_users: List[Dict[str, Any]]  # user_id, query_count
    top_queries: List[str]           # Most common intents
    user_satisfaction: Optional[float]  # If feedback collected

class AgentHealthStatus(BaseModel):
    agent_id: str
    status: Literal["healthy", "degraded", "down", "unknown"]
    last_check: datetime

    # Component health
    model_endpoint: Literal["up", "down", "slow"]
    data_connections: Dict[str, Literal["connected", "error"]]

    # Alerts
    active_alerts: List[Alert]
    recent_incidents: List[Incident]
```

### Azure Integration Services

```python
class AzureMetricsService:
    async def fetch_agent_metrics(self, foundry_agent_id: str, period: str):
        """Fetch metrics from Azure AI Foundry"""
        # Call Azure Monitor API
        # Parse Application Insights data
        # Aggregate by period

    async def fetch_cost_data(self, resource_group: str, period: str):
        """Fetch cost data from Azure Cost Management"""

    async def fetch_health_status(self, foundry_agent_id: str):
        """Check agent health via Azure endpoints"""

    async def subscribe_to_alerts(self, agent_id: str, webhook_url: str):
        """Subscribe to Azure Monitor alerts"""
```

### API Endpoints for Metrics

```
GET    /api/agents/{id}/metrics              → Get agent metrics
GET    /api/agents/{id}/metrics/realtime     → WebSocket for real-time
GET    /api/agents/{id}/health               → Health status
GET    /api/agents/{id}/cost                 → Cost breakdown
GET    /api/agents/{id}/users                → User activity
GET    /api/dashboard/overview               → All agents overview
POST   /api/agents/{id}/alerts/subscribe     → Subscribe to alerts
```

### Agent Detail Page Enhancement

```
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENT: Ops Scheduling Assistant                     [Production] 🟢     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  QUERIES/WEEK   │  │   COST/MONTH    │  │  SUCCESS RATE   │          │
│  │     1,247       │  │    $127.45      │  │     94.2%       │          │
│  │    ▲ +12%       │  │    ▲ +8%        │  │    ▲ +2.1%      │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                          │
│  [Overview] [Messages] [Metrics] [Deployments] [Settings]                │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  USAGE TREND (Last 30 Days)                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │     ╭──╮                                                    ╭──╮    ││
│  │    ╭╯  ╰╮   ╭──╮                                    ╭──╮   ╭╯  ╯    ││
│  │  ──╯    ╰───╯  ╰────────────────────────────────────╯  ╰───╯        ││
│  │  Oct 1                                                   Oct 30     ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  TOP USERS                          TOP QUERIES                          │
│  ┌───────────────────────┐         ┌───────────────────────┐            │
│  │ 1. Sarah M.    312    │         │ "Schedule next week"  │            │
│  │ 2. Mike R.     287    │         │ "Show conflicts"      │            │
│  │ 3. Lisa K.     198    │         │ "Optimize coverage"   │            │
│  │ 4. John D.     156    │         │ "Labor compliance"    │            │
│  │ 5. Amy S.      142    │         │ "Swap shifts"         │            │
│  └───────────────────────┘         └───────────────────────┘            │
│                                                                          │
│  AZURE RESOURCES                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 🟢 AI Foundry Project    │ 🟢 Model Endpoint    │ 🟢 Data Connections││
│  │ ops-scheduler-prod       │ gpt-4o-mini          │ Fabric, HotSched   ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  [Open in Azure Portal]  [View Logs]  [Download Report]                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Roadmap

### Phase 1: Agent Request System (2-3 weeks)
- [ ] Enhance Agent model with request fields
- [ ] Create intake form UI
- [ ] Add approval workflow endpoints
- [ ] Add requester notifications

### Phase 2: Communication System (2-3 weeks)
- [ ] Create AgentMessage model & Cosmos container
- [ ] Build messaging API endpoints
- [ ] Create conversation thread UI component
- [ ] Add @mention support & notifications
- [ ] (Optional) Teams webhook integration

### Phase 3: MSFT Ecosystem Connection (3-4 weeks)
- [ ] Azure AI Foundry API integration
- [ ] Auto-provisioning workflow
- [ ] DevOps work item sync
- [ ] Deployment status tracking
- [ ] Store Foundry resource IDs

### Phase 4: Metrics & Reporting (3-4 weeks)
- [ ] Azure Monitor integration
- [ ] Metrics data model & storage
- [ ] Real-time metrics API
- [ ] Agent detail dashboard
- [ ] Cost tracking & alerts

---

## Technical Requirements

### Azure Services Needed
| Service | Purpose |
|---------|---------|
| Azure AI Foundry | Agent development & deployment |
| Azure Monitor | Metrics & logging |
| Application Insights | Request tracing |
| Azure Cost Management | Cost tracking |
| Microsoft Graph | Teams integration |
| Azure DevOps | Work item tracking |
| Microsoft Fabric | Analytics & reporting |

### Authentication
- **Entra ID** for user authentication
- **Managed Identity** for Azure service-to-service
- **On-Behalf-Of** for user context in agent calls

### API Keys/Connections
- Azure AI Foundry Management API
- Azure Monitor Query API
- Microsoft Graph API (Teams)
- Azure DevOps REST API
- Azure Cost Management API

---

## Next Steps

1. **Validate architecture** with MSFT team in working session
2. **Prioritize phases** based on Fourth's immediate needs
3. **Start Phase 1** (request system) as it's self-contained
4. **MSFT session focus**: Confirm API access patterns & authentication

---

*Document: Agent-Arch ↔ MSFT Integration Architecture*
*Version: 1.0*
*Date: December 2024*
