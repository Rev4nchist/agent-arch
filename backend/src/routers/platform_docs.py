"""Platform documentation router for AI Guide context."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import uuid
import logging

from src.database import db
from src.models import (
    PlatformDoc,
    PlatformDocCreate,
    PlatformDocUpdate,
    PlatformDocCategory,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/platform-docs", tags=["platform-docs"])


@router.get("", response_model=List[PlatformDoc])
async def list_platform_docs(
    category: Optional[PlatformDocCategory] = None,
):
    """List all platform documentation, optionally filtered by category."""
    container = db.get_container("platform_docs")
    if not container:
        raise HTTPException(status_code=500, detail="Database not initialized")

    if category:
        query = "SELECT * FROM c WHERE c.category = @category ORDER BY c.title"
        params = [{"name": "@category", "value": category.value}]
    else:
        query = "SELECT * FROM c ORDER BY c.title"
        params = []

    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
    return [PlatformDoc(**item) for item in items]


@router.get("/search", response_model=List[PlatformDoc])
async def search_platform_docs(q: str, limit: int = 5):
    """Search platform docs by keyword matching."""
    container = db.get_container("platform_docs")
    if not container:
        raise HTTPException(status_code=500, detail="Database not initialized")

    query_lower = q.lower()
    query = """
        SELECT * FROM c
        WHERE ARRAY_CONTAINS(c.keywords, @keyword)
        OR CONTAINS(LOWER(c.title), @query)
        OR CONTAINS(LOWER(c.content), @query)
    """
    params = [
        {"name": "@keyword", "value": query_lower},
        {"name": "@query", "value": query_lower},
    ]

    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
    return [PlatformDoc(**item) for item in items[:limit]]


@router.get("/{doc_id}", response_model=PlatformDoc)
async def get_platform_doc(doc_id: str):
    """Get a specific platform document by ID."""
    container = db.get_container("platform_docs")
    if not container:
        raise HTTPException(status_code=500, detail="Database not initialized")

    query = "SELECT * FROM c WHERE c.id = @id"
    params = [{"name": "@id", "value": doc_id}]
    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    if not items:
        raise HTTPException(status_code=404, detail="Document not found")

    return PlatformDoc(**items[0])


@router.post("", response_model=PlatformDoc, status_code=201)
async def create_platform_doc(doc: PlatformDocCreate):
    """Create a new platform document."""
    container = db.get_container("platform_docs")
    if not container:
        raise HTTPException(status_code=500, detail="Database not initialized")

    doc_id = str(uuid.uuid4())
    now = datetime.utcnow()

    doc_data = {
        "id": doc_id,
        "category": doc.category.value,
        "title": doc.title,
        "content": doc.content,
        "keywords": doc.keywords,
        "related_features": doc.related_features,
        "updated_at": now.isoformat(),
    }

    container.create_item(body=doc_data)
    logger.info(f"Created platform doc: {doc.title}")

    return PlatformDoc(**doc_data)


@router.put("/{doc_id}", response_model=PlatformDoc)
async def update_platform_doc(doc_id: str, update: PlatformDocUpdate):
    """Update an existing platform document."""
    container = db.get_container("platform_docs")
    if not container:
        raise HTTPException(status_code=500, detail="Database not initialized")

    query = "SELECT * FROM c WHERE c.id = @id"
    params = [{"name": "@id", "value": doc_id}]
    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    if not items:
        raise HTTPException(status_code=404, detail="Document not found")

    existing = items[0]

    update_data = update.model_dump(exclude_unset=True)
    if "category" in update_data and update_data["category"]:
        update_data["category"] = update_data["category"].value

    for key, value in update_data.items():
        existing[key] = value

    existing["updated_at"] = datetime.utcnow().isoformat()

    container.upsert_item(body=existing)
    logger.info(f"Updated platform doc: {doc_id}")

    return PlatformDoc(**existing)


@router.delete("/{doc_id}", status_code=204)
async def delete_platform_doc(doc_id: str):
    """Delete a platform document."""
    container = db.get_container("platform_docs")
    if not container:
        raise HTTPException(status_code=500, detail="Database not initialized")

    query = "SELECT * FROM c WHERE c.id = @id"
    params = [{"name": "@id", "value": doc_id}]
    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    if not items:
        raise HTTPException(status_code=404, detail="Document not found")

    existing = items[0]
    container.delete_item(item=doc_id, partition_key=existing["category"])
    logger.info(f"Deleted platform doc: {doc_id}")


@router.post("/seed", status_code=201)
async def seed_platform_docs():
    """Seed initial platform documentation."""
    container = db.get_container("platform_docs")
    if not container:
        raise HTTPException(status_code=500, detail="Database not initialized")

    docs = _get_initial_docs()
    created_count = 0

    for doc in docs:
        doc_id = doc["id"]
        query = "SELECT c.id FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": doc_id}]
        existing = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

        if not existing:
            doc["updated_at"] = datetime.utcnow().isoformat()
            container.create_item(body=doc)
            created_count += 1
            logger.info(f"Seeded platform doc: {doc['title']}")

    return {"message": f"Seeded {created_count} platform documents", "total": len(docs)}


def _get_initial_docs() -> List[dict]:
    """Get initial platform documentation content."""
    return [
        {
            "id": "getting-started",
            "category": "workflow",
            "title": "Getting Started with the Platform",
            "content": """# Getting Started

Welcome to the Fourth AI Architecture Platform! Here's how to get oriented:

## Dashboard
The Dashboard (/) shows an overview of:
- Recent meetings and upcoming schedule
- Task summary by status
- Agent portfolio statistics
- Recent decisions

## Key Workflows
1. **Track a Decision**: Go to Proposals & Decisions → Create Proposal → Get approval → Becomes Decision
2. **Manage Tasks**: Go to Tasks → Create or view tasks in list/kanban view
3. **Submit Feedback**: Go to Feedback Hub → Submit New → Fill form
4. **Find Documents**: Go to Resources Library → Search or browse by category

## Navigation
Use the sidebar on the left to navigate between sections. The current section is highlighted with a blue indicator.""",
            "keywords": ["start", "begin", "new", "help", "overview", "intro", "welcome", "onboarding"],
            "related_features": ["dashboard", "tasks", "feedback-hub"],
        },
        {
            "id": "dashboard-overview",
            "category": "feature",
            "title": "Dashboard",
            "content": """# Dashboard

The Dashboard is your home page and provides a quick overview of platform activity.

## What You'll See
- **Stats Cards**: Quick counts of meetings, tasks, agents, and decisions
- **Recent Meetings**: Latest scheduled and completed meetings
- **Task Summary**: Tasks grouped by status (Pending, In Progress, Done)
- **Agent Portfolio**: Overview of agents by tier and status

## Quick Actions
From the dashboard you can:
- Click any stat card to navigate to that section
- View recent activity across the platform
- Access the Fourth AI Guide for help

## Navigation
Click "Dashboard" in the sidebar or navigate to "/" to return here.""",
            "keywords": ["dashboard", "home", "overview", "stats", "summary", "main"],
            "related_features": ["meetings", "tasks", "agents"],
        },
        {
            "id": "proposals-decisions",
            "category": "feature",
            "title": "Proposals & Decisions",
            "content": """# Proposals & Decisions

This section manages the governance workflow from proposal to decision.

## Proposals Tab
Proposals are items under consideration. They go through these statuses:
- **Proposed**: Initial submission
- **Reviewing**: Under active discussion
- **Agreed**: Approved (becomes a Decision)
- **Deferred**: Postponed for later

## Creating a Proposal
1. Go to Proposals & Decisions in the sidebar
2. Click "Create Proposal" button
3. Fill in: Title, Description, Category, Proposer, Department
4. Optionally add rationale and impact assessment
5. Click Submit

## Categories
- Agent: New AI agent proposals
- Governance: Policy and process changes
- Technical: Architecture decisions
- Licensing: Tool and license requests
- AI Architect: Team-specific items

## Decisions Tab
Once a proposal is agreed, it becomes a Decision for permanent record. Decisions include:
- The original proposal details
- Decision date and decision maker
- Rationale for approval""",
            "keywords": ["proposal", "decision", "governance", "approve", "create", "submit", "vote"],
            "related_features": ["meetings", "tasks"],
        },
        {
            "id": "meetings-hub",
            "category": "feature",
            "title": "Meetings Hub",
            "content": """# Meetings Hub

Manage team meetings, transcripts, and action items.

## Meeting Types
- **Governance**: Policy and decision meetings
- **AI Architect**: Team sync meetings
- **Licensing**: License review meetings
- **Technical**: Architecture discussions
- **Review**: Code and design reviews

## Creating a Meeting
1. Go to Meetings Hub in the sidebar
2. Click "Schedule Meeting" button
3. Fill in: Title, Date/Time, Type, Facilitator
4. Add attendees and agenda
5. Click Schedule

## Meeting Features
- **Pre-work Checklist**: Add items attendees should complete before meeting
- **Transcript Upload**: Upload meeting transcripts for AI processing
- **AI Summary**: Get automatic meeting summaries from transcripts
- **Action Items**: Tasks extracted from transcripts
- **Decisions**: Decisions linked to meetings

## Processing Transcripts
1. Open a completed meeting
2. Click "Upload Transcript"
3. The AI will extract:
   - Meeting summary
   - Action items (converted to tasks)
   - Decisions made""",
            "keywords": ["meeting", "schedule", "transcript", "agenda", "action item", "summary", "calendar"],
            "related_features": ["tasks", "decisions"],
        },
        {
            "id": "tasks-overview",
            "category": "feature",
            "title": "Tasks",
            "content": """# Tasks

Track work items and assignments across the team.

## Views
- **List View**: Traditional list with filters
- **Kanban View**: Drag-and-drop board by status

## Task Statuses
- **Pending**: Not yet started
- **In-Progress**: Currently being worked on
- **Done**: Completed
- **Blocked**: Waiting on dependencies
- **Deferred**: Postponed

## Creating Tasks
1. Go to Tasks in the sidebar
2. Click "New Task" button
3. Fill in: Title, Description, Priority, Category
4. Optionally assign to someone and set due date
5. Click Create

## Task Categories
- Governance, Technical, Agent, Licensing, AI Architect

## Tabs: Architecture vs Feedback
- **Architecture Tasks**: Regular work items created directly or from meetings
- **Feedback Tasks**: Tasks converted from Feedback Hub submissions

## Priority Levels
- Critical (urgent, blocking issues)
- High (important, time-sensitive)
- Medium (normal priority)
- Low (nice to have)""",
            "keywords": ["task", "kanban", "assign", "priority", "status", "work", "todo", "create task"],
            "related_features": ["meetings", "feedback-hub", "agents"],
        },
        {
            "id": "agents-registry",
            "category": "feature",
            "title": "Agents",
            "content": """# Agents Registry

Track AI agents across the organization.

## Agent Tiers
- **Tier 1 - Individual**: Personal productivity agents
- **Tier 2 - Department**: Team-level agents
- **Tier 3 - Enterprise**: Organization-wide agents

## Agent Lifecycle
1. **Idea**: Initial concept
2. **Design**: Specification phase
3. **Development**: Being built
4. **Testing**: QA phase
5. **Staging**: Pre-production
6. **Production**: Live and active
7. **Deprecated**: No longer maintained

## Creating an Agent
1. Go to Agents in the sidebar
2. Click "Register Agent" button
3. Fill in: Name, Description, Tier, Owner
4. Add data sources and use case
5. Click Register

## Agent Details
Each agent record includes:
- Owner and department
- Data sources used
- Integration status
- Related tasks
- Deployment timeline""",
            "keywords": ["agent", "ai", "bot", "tier", "register", "lifecycle", "copilot"],
            "related_features": ["tasks", "proposals"],
        },
        {
            "id": "feedback-hub",
            "category": "feature",
            "title": "Feedback Hub",
            "content": """# Feedback Hub

Internal ticketing system for bugs, feature requests, and ideas.

## Submission Categories
- **Bug Report**: Something is broken
- **Feature Request**: Request new functionality
- **Improvement Idea**: Enhance existing features
- **Question**: Ask about how something works

## Submitting Feedback
1. Go to Feedback Hub in the sidebar
2. Click "Submit New" button
3. Select category and priority
4. Enter title and detailed description
5. Add optional tags
6. Click Submit

## Upvoting
Click the thumbs-up on any submission to upvote. Higher upvotes = higher visibility in admin triage.

## Priority Levels
- Critical, High, Medium, Low

## Admin Features (Feedback Admin page)
- View triage queue sorted by upvotes
- Assign submissions to team members
- Convert submissions to Tasks
- Decline submissions
- View statistics by category/status

## Workflow
1. User submits feedback
2. Admin reviews in triage queue
3. Admin assigns or converts to task
4. Task is completed
5. Submission marked as completed""",
            "keywords": ["feedback", "bug", "feature request", "idea", "submit", "upvote", "ticket"],
            "related_features": ["tasks", "feedback-admin"],
        },
        {
            "id": "feedback-admin",
            "category": "feature",
            "title": "Feedback Admin",
            "content": """# Feedback Admin

Manage and triage feedback submissions.

## Accessing Admin
1. Go to Feedback Hub
2. Click "Admin" button in the top right

## Triage Queue
Shows all submissions with status "Submitted", sorted by upvote count.

## Admin Actions
For each submission you can:
- **Assign**: Select a team member to handle it
- **Convert to Task**: Create a task from the submission (select category)
- **Decline**: Mark as declined if not actionable

## Statistics
The admin page shows:
- Total submissions
- Pending review count
- Completed count
- Declined count
- Breakdown by category and status

## Converting to Task
1. Find submission in queue
2. Click "Convert to Task..." dropdown
3. Select task category (Governance, Technical, etc.)
4. Task is created and linked to submission
5. Submission status updates automatically""",
            "keywords": ["admin", "triage", "assign", "convert", "manage", "review"],
            "related_features": ["feedback-hub", "tasks"],
        },
        {
            "id": "resources-library",
            "category": "feature",
            "title": "Resources Library",
            "content": """# Resources Library

Document storage and knowledge base.

## Resource Types
- **PDF**: PDF documents
- **Document**: Word docs, spreadsheets
- **Link**: External URLs
- **Video**: Video content
- **Image**: Images and diagrams

## Categories
Agent, Governance, Technical, Licensing, AI Architect, Architecture, Budget, Security

## Uploading Resources
1. Go to Resources Library in the sidebar
2. Click "Upload Resource" button
3. Select file or enter URL
4. Choose category and add tags
5. Add description
6. Click Upload

## Searching
- Use the search bar to find by title or description
- Filter by category using the dropdown
- Filter by type (PDF, Link, etc.)

## Features
- Preview text extraction for documents
- Thumbnail generation
- View count tracking
- Related resources linking""",
            "keywords": ["resource", "document", "upload", "library", "pdf", "link", "file", "knowledge"],
            "related_features": ["tech-radar"],
        },
        {
            "id": "tech-radar",
            "category": "feature",
            "title": "Tech Radar",
            "content": """# Tech Radar

Technology recommendations and adoption status.

## Categories
- **Adopt**: Proven, recommended for wide use
- **Trial**: Worth exploring, limited production use
- **Assess**: Worth investigating, not production ready
- **Hold**: Proceed with caution or phase out

## Viewing the Radar
The radar visualization shows tools positioned by category. Click any item to see details.

## Item Details
Each tool/technology includes:
- Current recommendation category
- Description of the tool
- Status notes
- Link to documentation

## Adding Items
1. Go to Tech Radar in the sidebar
2. Click "Add Tool" button
3. Enter tool name, category, description
4. Add recommendation and docs link
5. Click Add

## Use Cases
- Standardize technology choices
- Guide new project decisions
- Track technology lifecycle""",
            "keywords": ["tech radar", "technology", "adopt", "trial", "assess", "hold", "tool", "recommendation"],
            "related_features": ["resources"],
        },
        {
            "id": "audit-trail",
            "category": "feature",
            "title": "Audit Trail",
            "content": """# Audit Trail

Activity tracking and compliance logging.

## What's Tracked
- **View**: When items are viewed
- **Create**: New items created
- **Update**: Changes to existing items
- **Delete**: Items removed
- **Query**: AI Guide queries

## Audit Log Details
Each entry includes:
- User who performed action
- Action type
- Entity affected (task, meeting, etc.)
- Timestamp
- IP address
- Details of changes

## Filtering
Filter audit logs by:
- User
- Entity type (task, agent, meeting, etc.)
- Action type
- Date range

## Use Cases
- Compliance reporting
- Track who changed what
- Debug issues
- Activity monitoring""",
            "keywords": ["audit", "log", "track", "activity", "compliance", "history", "changes"],
            "related_features": [],
        },
        {
            "id": "fourth-ai-guide",
            "category": "feature",
            "title": "Fourth AI Guide",
            "content": """# Fourth AI Guide

Your AI assistant for the platform.

## What It Can Do
- Answer questions about platform features
- Explain how to perform tasks
- Provide navigation guidance
- Query platform data (tasks, agents, meetings)
- Suggest next steps

## How to Use
1. Click "Fourth AI Guide" in the sidebar
2. Type your question in the chat input
3. Press Enter or click Send
4. Read the response with sources and suggestions

## Example Questions
- "How do I create a task?"
- "Where can I see all decisions?"
- "What's the process for approving an agent?"
- "Show me my assigned tasks"
- "What meetings are scheduled this week?"

## Tips
- Be specific in your questions
- The Guide can reference platform documentation
- Click suggestion chips for follow-up questions
- Sources are shown for documentation references""",
            "keywords": ["guide", "ai", "help", "assistant", "chat", "question", "how to"],
            "related_features": [],
        },
        {
            "id": "navigation-guide",
            "category": "navigation",
            "title": "Platform Navigation",
            "content": """# Platform Navigation

## Sidebar Menu
The sidebar on the left contains all main sections:
- **Dashboard** (/) - Home overview
- **Proposals & Decisions** (/decisions) - Governance workflow
- **Meetings Hub** (/meetings) - Meeting management
- **Tasks** (/tasks) - Work item tracking
- **Agents** (/agents) - AI agent registry
- **Governance** (/governance) - Policies and procedures
- **Budget & Licensing** (/budget) - Financial tracking
- **Resources Library** (/resources) - Document storage
- **Tech Radar** (/tech-radar) - Technology recommendations
- **Architecture Lab** (/architecture) - Design patterns
- **Feedback Hub** (/feedback) - Internal ticketing
- **Audit Trail** (/audit) - Activity logs
- **Fourth AI Guide** (/guide) - AI assistant

## Active Section Indicator
The current section is highlighted with a blue left border.

## Quick Tips
- Click any section name to navigate
- Use browser back/forward to move between pages
- Most sections have create/add buttons in top right""",
            "keywords": ["navigate", "menu", "sidebar", "where", "find", "go to", "location"],
            "related_features": [],
        },
        {
            "id": "workflow-proposal-to-decision",
            "category": "workflow",
            "title": "Proposal to Decision Workflow",
            "content": """# Proposal to Decision Workflow

This workflow tracks items from initial proposal through to formal decision.

## Step 1: Create Proposal
1. Go to Proposals & Decisions
2. Click "Create Proposal"
3. Fill in details and submit
4. Status: Proposed

## Step 2: Review Process
1. Proposal discussed in governance meeting
2. Stakeholders provide feedback
3. Update status to "Reviewing"

## Step 3: Decision
If approved:
1. Update proposal status to "Agreed"
2. Create formal Decision record
3. Link to original proposal
4. Link to meeting where decided

If not approved:
- Status → "Deferred" (revisit later)
- Or decline with rationale

## Step 4: Implementation
1. Create related tasks from the decision
2. Track progress in Tasks section
3. Link tasks to the decision

## Best Practices
- Include clear rationale in proposals
- Document impact assessment
- Link to relevant meetings
- Create actionable tasks after approval""",
            "keywords": ["workflow", "process", "proposal", "decision", "approve", "governance"],
            "related_features": ["proposals-decisions", "meetings", "tasks"],
        },
        {
            "id": "workflow-feedback-to-task",
            "category": "workflow",
            "title": "Feedback to Task Workflow",
            "content": """# Feedback to Task Workflow

Convert user feedback into actionable tasks.

## Step 1: User Submits Feedback
1. User goes to Feedback Hub
2. Clicks "Submit New"
3. Fills in category, title, description, priority
4. Submits feedback

## Step 2: Community Input
1. Other team members can upvote
2. Higher upvotes = higher priority in triage
3. Comments can be added for discussion

## Step 3: Admin Triage
1. Admin reviews triage queue (sorted by upvotes)
2. Options:
   - Assign to team member
   - Convert to task
   - Decline if not actionable

## Step 4: Convert to Task
1. Click "Convert to Task" dropdown
2. Select task category
3. Task is created with:
   - Title from feedback
   - Description from feedback
   - Link back to original submission
4. Appears in "Feedback Tasks" tab in Tasks section

## Step 5: Complete
1. Work on task as normal
2. Mark task as Done
3. Feedback submission auto-updates to Completed""",
            "keywords": ["feedback", "task", "convert", "workflow", "triage", "submit"],
            "related_features": ["feedback-hub", "tasks", "feedback-admin"],
        },
        {
            "id": "workflow-agent-approval",
            "category": "workflow",
            "title": "Agent Approval Workflow",
            "content": """# Agent Approval Workflow

Process for getting a new AI agent approved and registered.

## Step 1: Initial Proposal
1. Go to Proposals & Decisions
2. Create proposal with category "Agent"
3. Include:
   - Agent name and description
   - Proposed tier (Individual/Department/Enterprise)
   - Use case and business justification
   - Data sources required
   - Owner and department

## Step 2: Governance Review
1. Proposal reviewed in Governance meeting
2. Assess:
   - Business value
   - Data requirements
   - Security considerations
   - Resource needs
3. Status updated to "Reviewing"

## Step 3: Decision
If approved:
1. Proposal status → "Agreed"
2. Create Decision record
3. Proceed to registration

## Step 4: Agent Registration
1. Go to Agents section
2. Click "Register Agent"
3. Fill in approved details
4. Status starts as "Idea"

## Step 5: Lifecycle Progression
Track agent through stages:
Idea → Design → Development → Testing → Staging → Production

Create tasks at each stage to track work.

## Key Considerations
- Tier 3 (Enterprise) requires executive approval
- Data privacy review for sensitive data sources
- Integration assessment for existing systems""",
            "keywords": ["agent", "approval", "workflow", "register", "governance", "tier"],
            "related_features": ["proposals-decisions", "agents", "meetings"],
        },
    ]
