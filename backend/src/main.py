"""Main FastAPI application."""
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from src.config import settings
from src.database import db
from src.ai_client import ai_client
from src.routers import transcripts, azure_resources, resources, audit, submissions, platform_docs, access, budget, memories, feature_updates
from src.context_service import context_service
from src.audit_middleware import AuditMiddleware
from src.search_service import initialize_search_index, get_search_service
from src.hmlr import HMLRService, SuggestionOrchestrator, SuggestionResponse
from src.models import (
    Meeting,
    Task,
    Agent,
    Proposal,
    ProposalUpdate,
    Decision,
    Resource,
    TechRadarItem,
    CodePattern,
    TranscriptProcessRequest,
    TranscriptProcessResponse,
    AgentQueryRequest,
    AgentQueryResponse,
    PageContext,
    ActionSuggestion,
    DataBasis,
)
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel as PydanticBaseModel
import uuid
import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def index_document_async(doc_id: str, doc_type: str, obj: any):
    """
    Asynchronously index a document to Azure AI Search.
    Called after create/update operations.
    """
    try:
        search_service = get_search_service()

        # Extract content based on document type
        content = ""
        title = ""
        metadata = {}
        status = None
        priority = None
        category = None

        if doc_type == "meeting":
            content = obj.transcript or obj.transcript_text or ""
            title = obj.title or "Meeting"
            metadata = {
                "date": str(obj.date) if obj.date else None,
                "facilitator": obj.facilitator,
                "participants": obj.participants or [],
            }
            status = obj.status.value if hasattr(obj.status, 'value') else str(obj.status)

        elif doc_type == "task":
            content_parts = [obj.description or ""]
            if obj.acceptance_criteria:
                content_parts.append(f"Acceptance Criteria: {obj.acceptance_criteria}")
            content = " ".join(content_parts)
            title = obj.title or "Task"
            metadata = {
                "assigned_to": obj.assigned_to,
                "due_date": str(obj.due_date) if obj.due_date else None,
                "estimated_hours": obj.estimated_hours,
                "tags": obj.tags or [],
            }
            status = obj.status.value if hasattr(obj.status, 'value') else str(obj.status)
            priority = obj.priority.value if hasattr(obj.priority, 'value') else str(obj.priority)

        elif doc_type == "agent":
            content_parts = [obj.description or ""]
            if obj.capabilities:
                content_parts.append(f"Capabilities: {', '.join(obj.capabilities)}")
            if obj.use_cases:
                content_parts.append(f"Use Cases: {', '.join(obj.use_cases)}")
            content = " ".join(content_parts)
            title = obj.name or "Agent"
            metadata = {
                "tier": obj.tier.value if hasattr(obj.tier, 'value') else str(obj.tier) if obj.tier else None,
                "development_status": obj.development_status.value if hasattr(obj.development_status, 'value') else str(obj.development_status) if obj.development_status else None,
                "tools": obj.tools or [],
                "repositories": obj.repositories or [],
            }
            status = obj.development_status.value if hasattr(obj.development_status, 'value') else str(obj.development_status) if obj.development_status else None
            category = obj.tier.value if hasattr(obj.tier, 'value') else str(obj.tier) if obj.tier else None

        elif doc_type == "governance":
            content_parts = [obj.description or ""]
            if hasattr(obj, 'rationale') and obj.rationale:
                content_parts.append(f"Rationale: {obj.rationale}")
            if hasattr(obj, 'impact') and obj.impact:
                content_parts.append(f"Impact: {obj.impact}")
            content = " ".join(content_parts)
            title = obj.title or "Governance Item"
            status = "Approved"
            category = "decision" if doc_type.startswith("decision") else "proposal"

        # Skip if no content
        if not content or not content.strip():
            logger.warning(f"Skipping index for {doc_type} {doc_id} - no content")
            return

        # Upload to search index
        search_service.upload_document(
            doc_id=doc_id,
            content=content,
            doc_type=doc_type,
            title=title,
            metadata=metadata,
            status=status,
            priority=priority,
            category=category,
        )
        logger.info(f"Indexed {doc_type} {doc_id} to search")

    except Exception as e:
        logger.error(f"Error indexing {doc_type} {doc_id}: {str(e)}")
        # Don't fail the request if indexing fails


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    logger.info("Initializing database...")
    db.initialize()

    logger.info("Initializing search index...")
    try:
        initialize_search_index()
        logger.info("Search index initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search index: {e}")
        logger.warning("Application will continue without search functionality")

    logger.info("Application started")
    yield
    # Shutdown
    logger.info("Application shutdown")


app = FastAPI(
    title="MSFT Agent Architecture Guide API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
logger.info(f"Configuring CORS with origins: {settings.cors_origins_list}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,  # Changed to False - we use Bearer tokens, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add audit middleware (logs all API actions)
app.add_middleware(AuditMiddleware)

# Register routers
app.include_router(transcripts.router)
app.include_router(azure_resources.router)
app.include_router(resources.router)
app.include_router(audit.router)
app.include_router(submissions.router)
app.include_router(platform_docs.router)
app.include_router(access.router)
app.include_router(budget.router)
app.include_router(memories.router)
app.include_router(feature_updates.router)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.environment}


# Meetings endpoints
@app.get("/api/meetings", response_model=List[Meeting])
async def get_meetings():
    """Get all meetings."""
    try:
        container = db.get_container("meetings")
        items = list(container.read_all_items())
        return [Meeting(**item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching meetings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meetings/{meeting_id}", response_model=Meeting)
async def get_meeting(meeting_id: str):
    """Get meeting by ID."""
    try:
        container = db.get_container("meetings")
        item = container.read_item(item=meeting_id, partition_key=meeting_id)
        return Meeting(**item)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Meeting not found")


@app.post("/api/meetings", response_model=Meeting)
async def create_meeting(meeting: Meeting):
    """Create new meeting."""
    try:
        if not meeting.id:
            meeting.id = str(uuid.uuid4())
        meeting.created_at = datetime.utcnow()
        meeting.updated_at = datetime.utcnow()

        container = db.get_container("meetings")
        container.create_item(body=meeting.model_dump(mode='json'))

        # Index to search
        index_document_async(meeting.id, "meeting", meeting)

        return jsonable_encoder(meeting)
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/meetings/{meeting_id}", response_model=Meeting)
async def update_meeting(meeting_id: str, meeting: Meeting):
    """Update meeting. Auto-sets status to Completed when transcript is added."""
    try:
        meeting.id = meeting_id
        meeting.updated_at = datetime.utcnow()

        # Auto-transition to Completed when transcript is added
        if (meeting.transcript or meeting.transcript_text or meeting.transcript_url):
            from src.models import MeetingStatus
            if meeting.status != MeetingStatus.CANCELLED:
                meeting.status = MeetingStatus.COMPLETED
                logger.info(f"Meeting {meeting_id} auto-transitioned to Completed (transcript added)")

        container = db.get_container("meetings")
        container.upsert_item(body=meeting.model_dump(mode='json'))

        # Index to search
        index_document_async(meeting.id, "meeting", meeting)

        return jsonable_encoder(meeting)
    except Exception as e:
        logger.error(f"Error updating meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/meetings/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """Delete meeting."""
    try:
        container = db.get_container("meetings")
        container.delete_item(item=meeting_id, partition_key=meeting_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Meeting not found")


# Tasks endpoints
@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    """Get all tasks."""
    try:
        container = db.get_container("tasks")
        items = list(container.read_all_items())
        return [Task(**item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get task by ID."""
    try:
        container = db.get_container("tasks")
        item = container.read_item(item=task_id, partition_key=task_id)
        return Task(**item)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Task not found")


@app.post("/api/tasks", response_model=Task)
async def create_task(task: Task):
    """Create new task."""
    try:
        if not task.id:
            task.id = str(uuid.uuid4())
        task.created_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        container = db.get_container("tasks")
        container.create_item(body=task.model_dump(mode='json'))

        # Index to search
        index_document_async(task.id, "task", task)

        return jsonable_encoder(task)
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task: Task):
    """Update task."""
    try:
        task.id = task_id
        task.updated_at = datetime.utcnow()

        container = db.get_container("tasks")
        container.upsert_item(body=task.model_dump(mode='json'))

        # Index to search
        index_document_async(task.id, "task", task)

        return jsonable_encoder(task)
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete task."""
    try:
        container = db.get_container("tasks")
        container.delete_item(item=task_id, partition_key=task_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Task not found")


# Agents endpoints
@app.get("/api/agents", response_model=List[Agent])
async def get_agents():
    """Get all agents."""
    try:
        container = db.get_container("agents")
        items = list(container.read_all_items())
        return [Agent(**item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get agent by ID."""
    try:
        container = db.get_container("agents")
        item = container.read_item(item=agent_id, partition_key=agent_id)
        return Agent(**item)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Agent not found")


@app.post("/api/agents", response_model=Agent)
async def create_agent(agent: Agent):
    """Create new agent."""
    try:
        if not agent.id:
            agent.id = str(uuid.uuid4())
        agent.created_at = datetime.utcnow()
        agent.updated_at = datetime.utcnow()

        container = db.get_container("agents")
        container.create_item(body=agent.model_dump(mode='json'))

        # Index to search
        index_document_async(agent.id, "agent", agent)

        return jsonable_encoder(agent)
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/agents/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent: Agent):
    """Update agent."""
    try:
        agent.id = agent_id
        agent.updated_at = datetime.utcnow()

        container = db.get_container("agents")
        container.upsert_item(body=agent.model_dump(mode='json'))

        # Index to search
        index_document_async(agent.id, "agent", agent)

        return jsonable_encoder(agent)
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete agent."""
    try:
        container = db.get_container("agents")
        container.delete_item(item=agent_id, partition_key=agent_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Agent not found")




# Proposals endpoints
@app.get("/api/proposals", response_model=List[Proposal])
async def get_proposals():
    """Get all proposals."""
    try:
        container = db.get_container("proposals")
        items = list(container.read_all_items())
        return [Proposal(**item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching proposals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/proposals/{proposal_id}", response_model=Proposal)
async def get_proposal(proposal_id: str):
    """Get proposal by ID."""
    try:
        container = db.get_container("proposals")
        item = container.read_item(item=proposal_id, partition_key=proposal_id)
        return Proposal(**item)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Proposal not found")


@app.post("/api/proposals", response_model=Proposal)
async def create_proposal(proposal: Proposal):
    """Create new proposal."""
    try:
        if not proposal.id:
            proposal.id = str(uuid.uuid4())
        proposal.created_at = datetime.utcnow()
        proposal.updated_at = datetime.utcnow()

        container = db.get_container("proposals")
        container.create_item(body=proposal.model_dump(mode='json'))

        # Index to search
        index_document_async(proposal.id, "governance", proposal)

        return jsonable_encoder(proposal)
    except Exception as e:
        logger.error(f"Error creating proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/proposals/{proposal_id}", response_model=Proposal)
async def update_proposal(proposal_id: str, update_data: ProposalUpdate):
    """Update proposal (partial update)."""
    try:
        container = db.get_container("proposals")
        existing = container.read_item(item=proposal_id, partition_key=proposal_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                existing[key] = value
        existing["updated_at"] = datetime.utcnow().isoformat()

        container.upsert_item(body=existing)

        proposal = Proposal(**existing)
        index_document_async(proposal.id, "governance", proposal)

        return jsonable_encoder(proposal)
    except Exception as e:
        logger.error(f"Error updating proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/proposals/{proposal_id}")
async def delete_proposal(proposal_id: str):
    """Delete proposal."""
    try:
        container = db.get_container("proposals")
        container.delete_item(item=proposal_id, partition_key=proposal_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Proposal not found")


# Decisions endpoints
@app.get("/api/decisions", response_model=List[Decision])
async def get_decisions():
    """Get all decisions."""
    try:
        container = db.get_container("decisions")
        items = list(container.read_all_items())
        return [Decision(**item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching decisions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/decisions", response_model=Decision)
async def create_decision(decision: Decision):
    """Create new decision."""
    try:
        if not decision.id:
            decision.id = str(uuid.uuid4())
        decision.created_at = datetime.utcnow()

        container = db.get_container("decisions")
        container.create_item(body=decision.model_dump(mode='json'))

        # Index to search
        index_document_async(decision.id, "governance", decision)

        return jsonable_encoder(decision)
    except Exception as e:
        logger.error(f"Error creating decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))






@app.get("/api/decisions/{decision_id}", response_model=Decision)
async def get_decision(decision_id: str):
    """Get a single decision by ID."""
    try:
        container = db.get_container("decisions")
        item = container.read_item(item=decision_id, partition_key=decision_id)
        return Decision(**item)
    except Exception as e:
        if "NotFound" in str(e):
            raise HTTPException(status_code=404, detail="Decision not found")
        logger.error(f"Error fetching decision {decision_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/decisions/{decision_id}", response_model=Decision)
async def update_decision(decision_id: str, data: dict):
    """Update an existing decision."""
    try:
        container = db.get_container("decisions")
        existing = container.read_item(item=decision_id, partition_key=decision_id)

        # Update fields
        for key, value in data.items():
            if key not in ['id', 'created_at'] and value is not None:
                existing[key] = value
        existing['updated_at'] = datetime.utcnow().isoformat()

        container.replace_item(item=decision_id, body=existing)
        return Decision(**existing)
    except Exception as e:
        if "NotFound" in str(e):
            raise HTTPException(status_code=404, detail="Decision not found")
        logger.error(f"Error updating decision {decision_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/decisions/{decision_id}")
async def delete_decision(decision_id: str):
    """Delete a decision."""
    try:
        container = db.get_container("decisions")
        container.delete_item(item=decision_id, partition_key=decision_id)
        return {"message": "Decision deleted"}
    except Exception as e:
        if "NotFound" in str(e):
            raise HTTPException(status_code=404, detail="Decision not found")
        logger.error(f"Error deleting decision {decision_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/decisions/from-proposal", response_model=Decision)
async def create_decision_from_proposal(data: dict):
    """Create decision from approved proposal."""
    try:
        proposal_id = data.get("proposal_id")
        if not proposal_id:
            raise HTTPException(status_code=400, detail="proposal_id is required")

        # Get proposal
        proposals_container = db.get_container("proposals")
        try:
            proposal_item = proposals_container.read_item(item=proposal_id, partition_key=proposal_id)
            proposal = Proposal(**proposal_item)
        except Exception:
            raise HTTPException(status_code=404, detail="Proposal not found")

        # Create decision from proposal
        decision = Decision(
            id=str(uuid.uuid4()),
            title=data.get("title", proposal.title),
            description=data.get("description", proposal.description),
            category=data.get("category", "Governance"),
            decision_date=datetime.utcnow(),
            decision_maker=data.get("decision_maker", proposal.proposer),
            rationale=data.get("rationale", proposal.rationale),
            impact=data.get("impact", proposal.impact),
            proposal_id=proposal_id,
        )
        decision.created_at = datetime.utcnow()

        container = db.get_container("decisions")
        container.create_item(body=decision.model_dump(mode='json'))

        # Index to search
        index_document_async(decision.id, "governance", decision)

        return jsonable_encoder(decision)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating decision from proposal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Tech Radar endpoints
@app.get("/api/tech-radar", response_model=List[TechRadarItem])
async def get_tech_radar_items():
    """Get all tech radar items."""
    try:
        container = db.get_container("tech_radar_items")
        items = list(container.read_all_items())
        return [TechRadarItem(**item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching tech radar items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tech-radar", response_model=TechRadarItem)
async def create_tech_radar_item(item: TechRadarItem):
    """Create new tech radar item."""
    try:
        if not item.id:
            item.id = str(uuid.uuid4())
        item.last_updated = datetime.utcnow()

        container = db.get_container("tech_radar_items")
        container.create_item(body=item.model_dump(mode='json'))
        return jsonable_encoder(item)
    except Exception as e:
        logger.error(f"Error creating tech radar item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/tech-radar/{item_id}", response_model=TechRadarItem)
async def update_tech_radar_item(item_id: str, item: TechRadarItem):
    """Update tech radar item."""
    try:
        item.id = item_id
        item.last_updated = datetime.utcnow()

        container = db.get_container("tech_radar_items")
        container.upsert_item(body=item.model_dump(mode='json'))
        return jsonable_encoder(item)
    except Exception as e:
        logger.error(f"Error updating tech radar item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Code Patterns endpoints
@app.get("/api/code-patterns", response_model=List[CodePattern])
async def get_code_patterns():
    """Get all code patterns."""
    try:
        container = db.get_container("code_patterns")
        items = list(container.read_all_items())
        return [CodePattern(**item) for item in items]
    except Exception as e:
        logger.error(f"Error fetching code patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/code-patterns", response_model=CodePattern)
async def create_code_pattern(pattern: CodePattern):
    """Create new code pattern."""
    try:
        if not pattern.id:
            pattern.id = str(uuid.uuid4())
        pattern.created_at = datetime.utcnow()

        container = db.get_container("code_patterns")
        container.create_item(body=pattern.model_dump(mode='json'))
        return jsonable_encoder(pattern)
    except Exception as e:
        logger.error(f"Error creating code pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# AI endpoints
@app.post("/api/transcripts/process", response_model=TranscriptProcessResponse)
async def process_transcript(request: TranscriptProcessRequest):
    """Process transcript to extract action items and decisions."""
    try:
        result = await ai_client.process_transcript(request.transcript_text)

        # Create Task and Decision objects
        tasks = []
        for item in result.get("action_items", []):
            task = Task(
                id=str(uuid.uuid4()),
                title=item.get("title", ""),
                description=item.get("description"),
                assigned_to=item.get("assigned_to"),
                due_date=item.get("due_date"),
                priority=item.get("priority", "Medium"),
                created_from_meeting=request.meeting_id,
            )
            tasks.append(task)

        decisions = []
        for item in result.get("decisions", []):
            decision = Decision(
                id=str(uuid.uuid4()),
                title=item.get("title", ""),
                description=item.get("description", ""),
                decision_date=datetime.utcnow(),
                decision_maker=item.get("decision_maker", ""),
                category=item.get("category", "Governance"),
                rationale=item.get("rationale"),
                meeting=request.meeting_id,
            )
            decisions.append(decision)

        return TranscriptProcessResponse(
            action_items=tasks,
            decisions=decisions,
        )
    except Exception as e:
        logger.error(f"Error processing transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# =============================================================================
# CONVERSATION MEMORY SYSTEM (Phase 5.2)
# =============================================================================

@dataclass
class ConversationTurn:
    """A single turn in conversation history."""
    query: str
    response: str
    intent: str
    entities: List[str]
    extracted_context: Dict[str, Any]  # assignee, status, etc.
    timestamp: datetime


class ConversationMemory:
    """
    Session-based conversation memory for multi-turn context.
    Stores last N turns and extracted entities for follow-up questions.
    """

    def __init__(self, max_turns: int = 5, ttl_minutes: int = 30):
        self.sessions: Dict[str, List[ConversationTurn]] = {}
        self.session_timestamps: Dict[str, datetime] = {}
        self.max_turns = max_turns
        self.ttl_minutes = ttl_minutes

    def _cleanup_expired(self):
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired = [
            sid for sid, ts in self.session_timestamps.items()
            if (now - ts).total_seconds() > self.ttl_minutes * 60
        ]
        for sid in expired:
            del self.sessions[sid]
            del self.session_timestamps[sid]

    def add_turn(
        self,
        session_id: str,
        query: str,
        response: str,
        intent: str,
        entities: List[str],
        extracted_context: Dict[str, Any]
    ):
        """Add a conversation turn to session memory."""
        self._cleanup_expired()

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        turn = ConversationTurn(
            query=query,
            response=response,
            intent=intent,
            entities=entities,
            extracted_context=extracted_context,
            timestamp=datetime.utcnow()
        )

        self.sessions[session_id].append(turn)
        self.session_timestamps[session_id] = datetime.utcnow()

        # Keep only last N turns
        if len(self.sessions[session_id]) > self.max_turns:
            self.sessions[session_id] = self.sessions[session_id][-self.max_turns:]

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get accumulated context from session history.
        Returns merged context from all turns (latest values win).
        """
        self._cleanup_expired()

        if session_id not in self.sessions:
            return {}

        merged_context = {}
        for turn in self.sessions[session_id]:
            merged_context.update(turn.extracted_context)

        return merged_context

    def get_last_entities(self, session_id: str) -> List[str]:
        """Get entities from the last turn for pronoun resolution."""
        if session_id not in self.sessions or not self.sessions[session_id]:
            return []
        return self.sessions[session_id][-1].entities

    def get_history_summary(self, session_id: str) -> str:
        """Get a brief summary of conversation history for AI context."""
        if session_id not in self.sessions:
            return ""

        turns = self.sessions[session_id]
        if not turns:
            return ""

        summary_parts = ["[Previous conversation context]"]
        for turn in turns[-3:]:  # Last 3 turns
            summary_parts.append(f"User asked: {turn.query[:100]}")
            if turn.extracted_context:
                ctx_items = [f"{k}={v}" for k, v in turn.extracted_context.items()]
                summary_parts.append(f"  Context: {', '.join(ctx_items)}")

        return "\n".join(summary_parts)

    def clear_session(self, session_id: str):
        """Clear a specific session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_timestamps:
            del self.session_timestamps[session_id]


# Global conversation memory instance
conversation_memory = ConversationMemory()

# Global HMLR memory service instance
hmlr_service = HMLRService(ai_client=ai_client)

# Global suggestion orchestrator (uses HMLR for personalization)
suggestion_orchestrator = SuggestionOrchestrator(hmlr_service=hmlr_service)


def _resolve_pronouns(query: str, session_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Resolve pronouns like 'them', 'those', 'it' using conversation context.
    Returns modified query and any additional context to apply.
    """
    query_lower = query.lower()
    additional_context = {}

    # Get context from previous turns
    session_context = conversation_memory.get_context(session_id)
    last_entities = conversation_memory.get_last_entities(session_id)

    if not session_context:
        return query, additional_context

    # Pronoun patterns that reference previous results
    pronoun_patterns = [
        (r'\b(those|these|them)\b', 'plural_reference'),
        (r'\b(it|that|this)\b', 'singular_reference'),
        (r'\b(his|her|their)\b', 'possessive_reference'),
        (r'\bwho\s+(owns?|is responsible)\b', 'ownership_followup'),
    ]

    for pattern, ref_type in pronoun_patterns:
        if re.search(pattern, query_lower):
            # Carry forward relevant context
            if 'assignee' in session_context:
                additional_context['assignee'] = session_context['assignee']
            if 'status' in session_context:
                additional_context['status'] = session_context['status']
            if 'priority' in session_context:
                additional_context['priority'] = session_context['priority']
            if last_entities:
                additional_context['inferred_entities'] = last_entities
            break

    # Handle specific follow-up patterns
    if re.search(r'\bwhich (are|is) (overdue|blocked|pending)\b', query_lower):
        # "Which are overdue?" after "Show David's tasks"
        if 'assignee' in session_context:
            additional_context['assignee'] = session_context['assignee']

    if re.search(r'\bshow me more\b|\bmore details?\b|\btell me more\b', query_lower):
        # Carry forward all context for drill-down
        additional_context.update(session_context)

    return query, additional_context


# =============================================================================
# INTENT CLASSIFICATION SYSTEM (Task 16.1)
# =============================================================================

class QueryIntent(str, Enum):
    """Types of user query intents for the AI Guide."""
    STATUS_CHECK = "status_check"      # "What's blocked?", "Show overdue tasks"
    AGGREGATION = "aggregation"        # "How many tasks?", "Count by status"
    SEARCH = "search"                  # "Find tasks about API", "Search for meetings with John"
    COMPARISON = "comparison"          # "Compare this week vs last week"
    ACTION_GUIDANCE = "action_guidance" # "What should I work on?", "What's most urgent?"
    EXPLANATION = "explanation"        # "What is Tier 2 governance?", "Explain agent tiers"
    LIST = "list"                      # "Show all tasks", "List meetings"
    DETAIL = "detail"                  # "Tell me about task X", "Details on meeting Y"
    AUDIT = "audit"                    # "Who modified task X?", "Show recent activity", "Audit trail"
    OWNERSHIP = "ownership"            # "Who owns X?", "Who's responsible for Y?"


@dataclass
class ClassifiedIntent:
    """Result of intent classification with extracted parameters."""
    intent: QueryIntent
    entities: List[str]           # ['tasks', 'meetings', 'agents', etc.]
    parameters: Dict[str, Any]    # Extracted filters and values
    confidence: str               # 'high', 'medium', 'low'
    raw_query: str


def _classify_intent(query: str) -> ClassifiedIntent:
    """
    Classify the user's query intent and extract relevant parameters.
    Returns intent type, target entities, and extracted filter parameters.
    """
    query_lower = query.lower().strip()
    parameters: Dict[str, Any] = {}
    confidence = "medium"

    # Intent detection patterns - checked in order (more specific patterns first)
    # Using a list of tuples to ensure ordering is preserved
    intent_pattern_list = [
        # AUDIT - asking about activity history, who did what, changes (check first - most specific)
        (QueryIntent.AUDIT, [
            r"\b(who|what user)\b.*\b(changed|modified|created|deleted|updated|edited)\b",
            r"\b(audit|activity|change)\s*(log|trail|history)\b",
            r"\b(recent|latest)\s*(activity|changes|actions|modifications)\b",
            r"\bshow\s*(me\s*)?(the\s*)?(activity|audit|changes)\b",
            r"\bwhat\s*(happened|changed|was\s*(done|modified))\b",
            r"\bhistory\s*(of|for)\b",
            r"\btrack(ing)?\s*(changes|modifications|activity)\b",
        ]),
        # STATUS_CHECK - asking about specific statuses (most specific - check first)
        (QueryIntent.STATUS_CHECK, [
            r"\b(blocked|overdue|pending|completed|done|in[- ]progress)\b",
            r"\bstatus\b.*\b(of|for|on)\b",
            r"\bwhat.*status\b",
            r"\bwhich.*(are|is)\s+(blocked|pending|overdue|done)\b",
            # Phase 1.1: Add risks/blockers/bottlenecks patterns
            r"\b(risks?|blockers?|bottlenecks?|impediments?)\b",
            r"\bwhat('s| is| are).*\b(blocking|stuck|delayed|holding up)\b",
        ]),
        # AGGREGATION - counting or grouping (check patterns carefully for "breakdown X by Y")
        (QueryIntent.AGGREGATION, [
            r"\b(how many|count|total|number of|sum|average)\b",
            r"\b(breakdown|break down|distribution|summary|group|grouped)\b.*\b(by|of)\b",
            r"\bgive me (a |the )?(count|number|total|breakdown|summary)\b",
            r"\b(tasks?|meetings?|agents?|decisions?|proposals?)\b.*\b(by status|by priority|by assignee|by category|by tier|by type)\b",
            r"\b(by status|by priority|by tier|by category)\b.*\b(breakdown|summary|distribution)\b",
            r"\b(status|priority|tier)\s+(breakdown|distribution|summary)\b",
        ]),
        # COMPARISON - comparing time periods or entities
        (QueryIntent.COMPARISON, [
            r"\b(compare|comparison|versus|vs\.?|difference between)\b",
            r"\b(this week|last week|this month|last month)\b.*\b(vs\.?|versus|compared to|and)\b",
            r"\bmore than\b.*\b(last|previous)\b",
            # Phase 1.4: Historical/trend comparison patterns
            r"\bvs\.?\s*(last|previous)\s*(month|quarter|year|week)\b",
            r"\b(historical|trend|over time|progress)\b",
            r"\b(how has|what changed|growth|decline)\b",
        ]),
        # ACTION_GUIDANCE - asking for recommendations
        (QueryIntent.ACTION_GUIDANCE, [
            r"\b(what should|what can|what do|where should)\b.*\b(i|we)\b.*\b(work on|focus|start|do|prioritize)\b",
            r"\b(most urgent|highest priority|most important|next|recommend)\b",
            r"\bwhat('s| is| are) (next|the priority|important)\b",
            r"\bhelp me (decide|prioritize|choose)\b",
            r"\bsugg(est|estion)\b",
            # Phase 1.3: Learning/starter task patterns
            r"\b(good for|suitable for|appropriate for)\s*(learning|beginners?|new|onboarding)\b",
            r"\b(starter|beginner|easy|simple|introductory)\s*(tasks?|work|items?)\b",
            r"\bfirst\s*(task|issue|thing|item)\s*(to|for)\b",
        ]),
        # EXPLANATION - asking for definitions or explanations
        (QueryIntent.EXPLANATION, [
            r"\b(what is|what are|what does|explain|define|describe|tell me about)\b.*\b(tier|governance|policy|rule|process)\b",
            r"\bhow does\b.*\bwork\b",
            r"\bwhat('s| is) (a |the )?(tier|governance|budget|approval)\b",
            r"\bexplain\b",
        ]),
        # SEARCH - looking for specific items
        (QueryIntent.SEARCH, [
            r"\b(find|search|look for|locate|where is|looking for)\b",
            r"\b(contain|containing|about|related to|regarding|with)\b.*\b(keyword|word|term)\b",
            r"\bany.*(mention|about|related)\b",
        ]),
        # OWNERSHIP - asking about who owns/is responsible for something (Phase 1.2)
        (QueryIntent.OWNERSHIP, [
            r"\b(who owns|owner of|responsible for|who manages)\b",
            r"\bwho.*\b(contact|ask about|handles|maintains)\b",
            r"\b(ownership|responsible|in charge of)\b",
        ]),
        # DETAIL - asking about specific items
        (QueryIntent.DETAIL, [
            r"\b(details?|more info|tell me (more )?about|information (on|about))\b",
            r"\bwhat('s| is) (the |)(task|meeting|agent|decision)\b.*\b(id|called|named)\b",
            r"\bshow me\b.*\b(the |)(task|meeting|agent)\b",
        ]),
        # LIST - general listing (default for many queries - check last)
        (QueryIntent.LIST, [
            r"\b(show|list|display|get|give me)\b.*\b(all|my|the|our)\b",
            r"\bwhat (tasks?|meetings?|agents?|decisions?)\b",
            r"\b(all|my|our|the)\b.*\b(tasks?|meetings?|agents?)\b",
        ]),
    ]

    # Detect intent by matching patterns (order preserved via list)
    detected_intent = QueryIntent.LIST  # Default
    for intent, patterns in intent_pattern_list:
        for pattern in patterns:
            if re.search(pattern, query_lower):
                detected_intent = intent
                confidence = "high"
                break
        if confidence == "high":
            break

    # Extract status filters
    status_patterns = {
        'blocked': r'\b(blocked|stuck|stalled)\b',
        'pending': r'\b(pending|waiting|not started|todo)\b',
        'in-progress': r'\b(in[- ]progress|working on|active|ongoing)\b',
        'completed': r'\b(completed|done|finished|closed)\b',
        'overdue': r'\b(overdue|past due|late|missed deadline)\b',
    }
    for status, pattern in status_patterns.items():
        if re.search(pattern, query_lower):
            parameters['status'] = status
            break

    # Extract priority filters
    priority_patterns = {
        'high': r'\b(high priority|urgent|critical|important|asap)\b',
        'medium': r'\b(medium priority|normal priority|moderate)\b',
        'low': r'\b(low priority|minor|not urgent)\b',
    }
    for priority, pattern in priority_patterns.items():
        if re.search(pattern, query_lower):
            parameters['priority'] = priority
            break

    # Extract integration status filters (for agents)
    integration_status_patterns = {
        'Integration Issues': r'\b(integration issues?|integration problems?|failing integration|integration fail|integration errors?)\b',
        'Blocked': r'\b(integration blocked|blocked integration)\b',
        'In Progress': r'\b(integrating|integration in[- ]progress|currently integrating)\b',
        'Partially Integrated': r'\b(partially integrated|partial integration)\b',
        'Fully Integrated': r'\b(fully integrated|complete integration|integration complete)\b',
        'Not Started': r'\b(not integrated|no integration|integration not started)\b',
    }
    for int_status, pattern in integration_status_patterns.items():
        if re.search(pattern, query_lower):
            parameters['integration_status'] = int_status
            break

    # Extract assignee mentions (simple name extraction)
    assignee_match = re.search(r"\b(assigned to|for|belonging to|owned by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", query)
    if assignee_match:
        parameters['assignee'] = assignee_match.group(2)

    # Extract date/time references
    date_refs = _extract_date_references(query_lower)
    if date_refs:
        parameters.update(date_refs)

    # Extract search terms (for SEARCH intent)
    if detected_intent == QueryIntent.SEARCH:
        search_match = re.search(r'(?:find|search|look for|about|containing|related to)\s+["\']?([^"\']+)["\']?', query_lower)
        if search_match:
            parameters['search_term'] = search_match.group(1).strip()

    # Phase 2.4: Extract learning/complexity indicators
    learning_patterns = [
        r'\b(good for|suitable for|appropriate for)\s*(learning|beginners?|new|onboarding)\b',
        r'\b(starter|beginner|easy|simple|introductory)\s*(tasks?|work|items?)\b',
        r'\bfirst\s*(task|issue|thing|item)\s*(to|for)\b',
        r'\b(learning|onboarding|beginner)\b',
    ]
    for pattern in learning_patterns:
        if re.search(pattern, query_lower):
            parameters['learning_friendly'] = True
            parameters['complexity'] = 'beginner'
            break

    # Phase 2.4: Extract ownership/owner queries
    owner_match = re.search(r'\bwho\s+(owns?|manages?|is responsible for|handles?|maintains?)\s+(the\s+)?(.+?)(\?|$)', query_lower)
    if owner_match:
        # Extract what they're asking about (e.g., "backend service")
        parameters['ownership_subject'] = owner_match.group(3).strip()

    # Phase 2.4: Extract timeline-related flags for agents
    timeline_patterns = [
        r'\b(deployment|deploy)\s+(timeline|schedule|plan)\b',
        r'\btimeline\b.*\bagent',
        r'\bwhen\b.*\b(deploy|launch|release)\b',
    ]
    for pattern in timeline_patterns:
        if re.search(pattern, query_lower):
            parameters['show_timeline'] = True
            break

    # Detect target entities
    entities = _detect_query_entities(query)

    return ClassifiedIntent(
        intent=detected_intent,
        entities=entities,
        parameters=parameters,
        confidence=confidence,
        raw_query=query
    )


def _apply_page_context(
    classified: ClassifiedIntent,
    page_context: Optional[PageContext]
) -> ClassifiedIntent:
    """
    Enhance classified intent with page context from the frontend.
    - If user is on a specific page, infer entity type
    - If items are selected, focus query on those items
    - Apply any active filters from the frontend
    """
    if not page_context:
        return classified

    PAGE_TO_ENTITY = {
        'tasks': ['tasks'],
        'meetings': ['meetings'],
        'agents': ['agents'],
        'proposals': ['proposals'],
        'decisions': ['decisions'],
        'resources': ['resources'],
        'dashboard': ['tasks', 'meetings', 'agents'],
    }

    entities = classified.entities
    params = classified.parameters.copy()

    if page_context.current_page and not entities:
        page_key = page_context.current_page.lower().replace('/', '').strip()
        if page_key in PAGE_TO_ENTITY:
            entities = PAGE_TO_ENTITY[page_key]

    if page_context.visible_entity_type and not entities:
        entities = [page_context.visible_entity_type]

    if page_context.selected_ids:
        params['selected_ids'] = page_context.selected_ids

    if page_context.active_filters:
        for key, value in page_context.active_filters.items():
            if key not in params and value is not None:
                params[key] = value

    return ClassifiedIntent(
        intent=classified.intent,
        entities=entities if entities else classified.entities,
        parameters=params,
        confidence=classified.confidence,
        raw_query=classified.raw_query
    )


def _generate_action_suggestions(
    classified: ClassifiedIntent,
    results: List[Dict[str, Any]],
    response_text: str
) -> List[ActionSuggestion]:
    """
    Generate contextual follow-up action suggestions based on query results.
    Returns suggestions for actions the user might want to take next.
    """
    suggestions = []
    intent = classified.intent
    entities = classified.entities
    params = classified.parameters
    result_count = len(results)

    if intent == QueryIntent.LIST:
        if result_count > 0:
            if 'tasks' in entities:
                suggestions.append(ActionSuggestion(
                    label="Show high priority",
                    action_type="query",
                    params={"query": "show high priority tasks"}
                ))
                suggestions.append(ActionSuggestion(
                    label="Show blocked",
                    action_type="query",
                    params={"query": "show blocked tasks"}
                ))
                suggestions.append(ActionSuggestion(
                    label="Tasks due soon",
                    action_type="query",
                    params={"query": "tasks due this week"}
                ))
                suggestions.append(ActionSuggestion(
                    label="Go to Tasks",
                    action_type="navigate",
                    params={"page": "tasks"}
                ))
            elif 'meetings' in entities:
                suggestions.append(ActionSuggestion(
                    label="Show upcoming",
                    action_type="query",
                    params={"query": "upcoming meetings this week"}
                ))
                suggestions.append(ActionSuggestion(
                    label="Recent summaries",
                    action_type="query",
                    params={"query": "recent meeting summaries"}
                ))
                suggestions.append(ActionSuggestion(
                    label="Go to Meetings",
                    action_type="navigate",
                    params={"page": "meetings"}
                ))
            elif 'agents' in entities:
                suggestions.append(ActionSuggestion(
                    label="Active agents",
                    action_type="query",
                    params={"query": "show active agents"}
                ))
                suggestions.append(ActionSuggestion(
                    label="Agents by tier",
                    action_type="query",
                    params={"query": "show agents by tier"}
                ))
                suggestions.append(ActionSuggestion(
                    label="Go to Agents",
                    action_type="navigate",
                    params={"page": "agents"}
                ))
            elif 'proposals' in entities:
                suggestions.append(ActionSuggestion(
                    label="Show pending",
                    action_type="query",
                    params={"query": "show pending proposals"}
                ))
                suggestions.append(ActionSuggestion(
                    label="Go to Proposals",
                    action_type="navigate",
                    params={"page": "proposals"}
                ))
            else:
                suggestions.append(ActionSuggestion(
                    label="List tasks",
                    action_type="view",
                    params={"entity": "tasks"}
                ))
                suggestions.append(ActionSuggestion(
                    label="List meetings",
                    action_type="view",
                    params={"entity": "meetings"}
                ))
                suggestions.append(ActionSuggestion(
                    label="List agents",
                    action_type="view",
                    params={"entity": "agents"}
                ))
        else:
            if 'tasks' in entities:
                suggestions.append(ActionSuggestion(
                    label="Create task",
                    action_type="create",
                    params={"entity": "task"}
                ))
            elif 'meetings' in entities:
                suggestions.append(ActionSuggestion(
                    label="Schedule meeting",
                    action_type="create",
                    params={"entity": "meeting"}
                ))

    elif intent == QueryIntent.SEARCH:
        if result_count == 0:
            suggestions.append(ActionSuggestion(
                label="Broaden search",
                action_type="query",
                params={"query": "show all items"}
            ))
        elif result_count == 1 and results:
            item = results[0]
            suggestions.append(ActionSuggestion(
                label="View details",
                action_type="navigate",
                params={"id": item.get('id'), "entity": entities[0] if entities else 'item'}
            ))

    elif intent == QueryIntent.STATUS_CHECK:
        if 'tasks' in entities:
            suggestions.append(ActionSuggestion(
                label="List all tasks",
                action_type="view",
                params={"entity": "tasks"}
            ))
            suggestions.append(ActionSuggestion(
                label="Show blocked",
                action_type="query",
                params={"query": "show blocked tasks"}
            ))

    elif intent == QueryIntent.AGGREGATION:
        if entities:
            entity = entities[0]
            suggestions.append(ActionSuggestion(
                label=f"Drill down",
                action_type="query",
                params={"query": f"list {entity} by category"}
            ))

    elif intent == QueryIntent.COMPARISON:
        suggestions.append(ActionSuggestion(
            label="Show trends",
            action_type="query",
            params={"query": "show trends over time"}
        ))

    elif intent == QueryIntent.EXPLANATION:
        suggestions.append(ActionSuggestion(
            label="List tasks",
            action_type="view",
            params={"entity": "tasks"}
        ))
        suggestions.append(ActionSuggestion(
            label="List meetings",
            action_type="view",
            params={"entity": "meetings"}
        ))
        suggestions.append(ActionSuggestion(
            label="List agents",
            action_type="view",
            params={"entity": "agents"}
        ))

    elif intent == QueryIntent.AUDIT:
        suggestions.append(ActionSuggestion(
            label="View audit log",
            action_type="navigate",
            params={"page": "audit"}
        ))
        suggestions.append(ActionSuggestion(
            label="Today's activity",
            action_type="query",
            params={"query": "show activity from today"}
        ))
        suggestions.append(ActionSuggestion(
            label="Filter by user",
            action_type="filter",
            params={"entity": "audit_logs", "field": "user_id"}
        ))

    return suggestions[:6]


def _get_page_context_suggestions(page_type: str) -> List[ActionSuggestion]:
    """Generate suggestions relevant to the current page."""
    PAGE_SUGGESTIONS = {
        'tasks': [
            ActionSuggestion(label="High priority tasks", action_type="query",
                           params={"query": "show high priority tasks"}),
            ActionSuggestion(label="Blocked tasks", action_type="query",
                           params={"query": "show blocked tasks"}),
        ],
        'meetings': [
            ActionSuggestion(label="Upcoming meetings", action_type="query",
                           params={"query": "upcoming meetings this week"}),
            ActionSuggestion(label="Recent summaries", action_type="query",
                           params={"query": "recent meeting summaries"}),
        ],
        'agents': [
            ActionSuggestion(label="Active agents", action_type="query",
                           params={"query": "show active agents"}),
            ActionSuggestion(label="Development agents", action_type="query",
                           params={"query": "agents in development"}),
        ],
        'decisions': [
            ActionSuggestion(label="Pending proposals", action_type="query",
                           params={"query": "show pending proposals"}),
            ActionSuggestion(label="Recent decisions", action_type="query",
                           params={"query": "recent architecture decisions"}),
        ],
        'governance': [
            ActionSuggestion(label="Key policies", action_type="query",
                           params={"query": "what are the key governance policies"}),
            ActionSuggestion(label="Compliance status", action_type="query",
                           params={"query": "show compliance requirements"}),
        ],
        'budget': [
            ActionSuggestion(label="Budget overview", action_type="query",
                           params={"query": "current budget allocation"}),
            ActionSuggestion(label="Active licenses", action_type="query",
                           params={"query": "show active licenses"}),
        ],
    }
    return PAGE_SUGGESTIONS.get(page_type, [])


async def _generate_action_suggestions_with_hmlr(
    classified: ClassifiedIntent,
    results: List[Dict[str, Any]],
    response_text: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    page_type: Optional[str] = None
) -> List[ActionSuggestion]:
    """
    Generate follow-up suggestions with HMLR personalization.
    Blends intent-based suggestions with memory-driven personalization.
    Falls back to static suggestions if HMLR unavailable.
    """
    base_suggestions = _generate_action_suggestions(classified, results, response_text)

    # Add page-context suggestions (max 2)
    if page_type:
        page_suggestions = _get_page_context_suggestions(page_type)
        base_suggestions = base_suggestions + page_suggestions[:2]

    if not user_id or suggestion_orchestrator is None:
        return base_suggestions[:6]

    try:
        hmlr_suggestions = await suggestion_orchestrator.get_followup_suggestions(
            user_id=user_id,
            intent=classified.intent.value,
            response_text=response_text[:500] if response_text else None,
            session_id=session_id
        )

        logger.info(f"HMLR: user_id={user_id}, session_id={session_id}, page_type={page_type}")
        logger.info(f"HMLR: Got {len(hmlr_suggestions)} suggestions from orchestrator")
        for s in hmlr_suggestions:
            source = s.source if isinstance(s.source, str) else s.source.value
            logger.info(f"  HMLR suggestion: source={source}, text={s.text[:50]}...")

        if not hmlr_suggestions:
            return base_suggestions[:6]

        converted = []
        for ps in hmlr_suggestions[:2]:
            source = ps.source if isinstance(ps.source, str) else ps.source.value
            if source == "open_loop":
                action_type = "open_loop"
                params = {
                    "query": ps.metadata.get("original_text", ps.text),
                    "topic": ps.metadata.get("topic", ""),
                    "block_id": ps.metadata.get("block_id", "")
                }
            elif source == "intent":
                action_type = "query"
                params = {"query": ps.text}
            else:
                action_type = "query"
                params = {"query": ps.text}

            converted.append(ActionSuggestion(
                label=ps.text[:40] + "..." if len(ps.text) > 40 else ps.text,
                action_type=action_type,
                params=params
            ))

        combined = converted + base_suggestions
        seen = set()
        unique = []
        for s in combined:
            key = s.label.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(s)

        return unique[:8]

    except Exception as e:
        logger.warning(f"HMLR followup suggestions failed, using base: {e}")
        return base_suggestions[:6]


# =============================================================================
# Response Templates by Intent (Phase 4.1)
# =============================================================================
RESPONSE_TEMPLATES = {
    QueryIntent.STATUS_CHECK: """
**Response Format for Status Check:**
1. Start with a clear status summary count (e.g., "Found X items with status Y")
2. List the TOP 3 most important/urgent items with:
   - Title and current status
   - Who's assigned (if applicable)
   - Days overdue or blocked duration (if relevant)
3. Include **Items Needing Immediate Attention** section if any are critical/urgent
4. End with **Next Steps:** listing 1-3 actionable recommendations
""",

    QueryIntent.AGGREGATION: """
**Response Format for Aggregation/Count:**
1. Start with the headline number clearly (e.g., "There are X total tasks")
2. Show breakdown using a simple table or bullet list:
   - Category: Count (percentage if useful)
3. Highlight the most significant finding (e.g., "Most tasks are In Progress (45%)")
4. Include **Key Insight:** explaining what the numbers mean
5. End with **Recommendation:** based on the data pattern
""",

    QueryIntent.LIST: """
**Response Format for List:**
1. Start with count: "Here are X items matching your request"
2. List items with key details on each line:
   - Title | Status | Assigned To | Due Date
3. If >5 items, summarize: "Showing top 5 of X total. Let me know if you want more."
4. Highlight any items that need attention (blocked, overdue, high priority)
5. End with **Next Steps:** if any items need action
""",

    QueryIntent.ACTION_GUIDANCE: """
**Response Format for Action Guidance:**
1. Start with direct recommendation: "I recommend starting with..."
2. List 1-3 suggested items with rationale for each:
   - Task name: Why this is a good choice (complexity, learning opportunity, impact)
3. Include **Who to Contact:** if help might be needed
4. End with **Getting Started:** with specific first step
""",

    QueryIntent.OWNERSHIP: """
**Response Format for Ownership Query:**
1. Answer the ownership question directly: "[Person] owns/is responsible for [thing]"
2. Include contact details if available
3. Mention team affiliation if relevant
4. List any related owners (backup contacts, team members)
5. End with **To reach them:** with communication suggestion
""",

    QueryIntent.COMPARISON: """
**Response Format for Comparison:**
1. Start with headline comparison: "Compared to [period], [key change]"
2. Show changes using +/- indicators:
   - Metric: Current (change from previous)
3. Highlight significant changes (>20% or notable shifts)
4. Include **Trend:** indicating direction (improving/declining/stable)
5. End with **Implication:** explaining what this means for the team
""",

    QueryIntent.EXPLANATION: """
**Response Format for Explanation:**
1. Start with a clear, concise definition (1-2 sentences)
2. Explain why it matters in this context
3. Provide concrete examples from the data if relevant
4. List key points or rules (if applicable)
5. End with **Related:** linking to related concepts if helpful
""",

    QueryIntent.AUDIT: """
**Response Format for Audit/Activity:**
1. Start with time context: "In the last [period], there were X activities"
2. List recent activities chronologically (newest first):
   - [Time] - [User] [action] [entity]
3. Group by type if many activities (creates, updates, deletes)
4. Highlight any unusual patterns or significant changes
5. End with **Notable:** calling out anything requiring attention
""",

    QueryIntent.DETAIL: """
**Response Format for Detail Request:**
1. Start with the entity name/title prominently
2. Show all relevant fields in organized sections:
   - Status & Priority
   - People (assigned, owner, created by)
   - Dates (created, due, completed)
   - Description/Details
3. Include related items (linked tasks, related meetings)
4. End with **Actions:** listing what can be done with this item
""",
}


def _get_response_template(intent: QueryIntent) -> str:
    """Get the response template for a given intent type."""
    return RESPONSE_TEMPLATES.get(intent, "")


def _generate_action_hints(classified: ClassifiedIntent, item_count: int) -> str:
    """
    Generate action hints for AI context based on query intent and data.
    These hints help the AI provide more actionable responses.
    Phase 1.7: Add action hints to AI context for improved actionability.
    """
    hints = []
    intent = classified.intent
    entities = classified.entities
    params = classified.parameters

    if intent == QueryIntent.STATUS_CHECK:
        if params.get('status') in ['blocked', 'overdue']:
            hints.append("Suggest contacting the assigned person for blocked items")
            hints.append("Recommend prioritizing resolution of blockers")
        if 'risks' in str(params) or 'blockers' in str(classified):
            hints.append("Highlight any patterns in blocked items (same assignee, category)")
            hints.append("Suggest escalation if items have been blocked too long")

    elif intent == QueryIntent.ACTION_GUIDANCE:
        hints.append("Recommend specific tasks to start with (name them)")
        hints.append("Explain why these tasks are good starting points")
        if params.get('learning_friendly') or 'learning' in str(params) or 'beginner' in str(params):
            hints.append("Focus on tasks with learning_friendly=true or complexity='beginner' if available")
            hints.append("Suggest pairing with experienced team member if task seems complex")
            hints.append("Mention required skills (skills_required field) if present")

    elif intent == QueryIntent.OWNERSHIP:
        hints.append("Include contact information if available (owner_contact, assigned_to, owner)")
        hints.append("Mention team affiliation if present (team field)")
        hints.append("Suggest reaching out via team channel if owner unclear")
        if params.get('ownership_subject'):
            hints.append(f"User is asking specifically about: {params['ownership_subject']}")

    elif intent == QueryIntent.AGGREGATION:
        hints.append("Explain what the numbers mean for the team")
        hints.append("Highlight any concerning patterns (unbalanced workload, too many blocked)")
        if item_count > 10:
            hints.append("Suggest focusing on most impactful category first")

    elif intent == QueryIntent.COMPARISON:
        hints.append("Explain what changed and why it matters")
        hints.append("Suggest actions based on trend direction")

    elif intent == QueryIntent.LIST:
        if item_count > 5:
            hints.append("Highlight top 3 most urgent/important items")
        if item_count == 0:
            hints.append("Suggest how to create new items or broaden search")
        # Phase 2.4: Timeline hints for agent lists
        if params.get('show_timeline') and 'agents' in entities:
            hints.append("Order agents by target_deployment_date if available")
            hints.append("Highlight any deployment_blockers")
            hints.append("Show next_milestone for each agent")

    # Phase 2.4: Add general hints based on parameters
    if params.get('show_timeline'):
        hints.append("Include timeline information (target_deployment_date, next_milestone)")
        hints.append("Highlight any deployment blockers that might delay timeline")

    if not hints:
        return ""

    return "\n[Suggested Response Actions]: " + "; ".join(hints[:3])


def _extract_contact_info(items: List[Dict[str, Any]], classified: ClassifiedIntent) -> str:
    """
    Phase 4.2: Extract and format contact information from items.
    Returns a string with key contacts relevant to the query results.
    """
    if not items:
        return ""

    contacts = {}  # name -> {role, items they're connected to}

    for item in items:
        # Check multiple contact fields
        assignee = item.get('assigned_to') or item.get('assignee')
        owner = item.get('owner') or item.get('owner_name')
        owner_contact = item.get('owner_contact')
        facilitator = item.get('facilitator')
        made_by = item.get('made_by')
        created_by = item.get('created_by')
        team = item.get('team')

        item_title = item.get('title') or item.get('name') or 'Item'
        item_status = item.get('status', '')

        # Prioritize contacts for blocked/urgent items
        is_urgent = item_status.lower() in ['blocked', 'in-progress'] or item.get('priority', '').lower() in ['high', 'critical']

        if assignee:
            if assignee not in contacts:
                contacts[assignee] = {'role': 'Assignee', 'items': [], 'urgent': False, 'contact': None, 'team': None}
            contacts[assignee]['items'].append(item_title)
            if is_urgent:
                contacts[assignee]['urgent'] = True

        if owner and owner != assignee:
            if owner not in contacts:
                contacts[owner] = {'role': 'Owner', 'items': [], 'urgent': False, 'contact': owner_contact, 'team': team}
            contacts[owner]['items'].append(item_title)
            if is_urgent:
                contacts[owner]['urgent'] = True
            if owner_contact:
                contacts[owner]['contact'] = owner_contact
            if team:
                contacts[owner]['team'] = team

        if facilitator and facilitator not in contacts:
            contacts[facilitator] = {'role': 'Facilitator', 'items': [item_title], 'urgent': False, 'contact': None, 'team': None}

        if made_by and made_by not in contacts:
            contacts[made_by] = {'role': 'Decision Maker', 'items': [item_title], 'urgent': False, 'contact': None, 'team': None}

    if not contacts:
        return ""

    # Format contacts - prioritize urgent ones
    urgent_contacts = {k: v for k, v in contacts.items() if v['urgent']}
    other_contacts = {k: v for k, v in contacts.items() if not v['urgent']}

    lines = ["\n[Key Contacts]:"]

    # Show urgent contacts first (limit to top 3)
    for name, info in list(urgent_contacts.items())[:3]:
        contact_line = f"- {name} ({info['role']})"
        if info.get('contact'):
            contact_line += f" - {info['contact']}"
        if info.get('team'):
            contact_line += f" [{info['team']}]"
        contact_line += f" - {len(info['items'])} items (NEEDS ATTENTION)"
        lines.append(contact_line)

    # Then other contacts (limit to 2 more)
    remaining_slots = 5 - len(urgent_contacts)
    for name, info in list(other_contacts.items())[:remaining_slots]:
        contact_line = f"- {name} ({info['role']})"
        if info.get('contact'):
            contact_line += f" - {info['contact']}"
        if info.get('team'):
            contact_line += f" [{info['team']}]"
        contact_line += f" - {len(info['items'])} items"
        lines.append(contact_line)

    if len(contacts) > 5:
        lines.append(f"(+{len(contacts) - 5} more contacts in results)")

    return "\n".join(lines)


def _extract_date_references(query: str) -> Dict[str, Any]:
    """Extract date/time references from query and return date range parameters."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = {}

    # This week
    if re.search(r'\bthis week\b', query):
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        result['start_date'] = start_of_week.isoformat()
        result['end_date'] = end_of_week.isoformat()
        result['timeframe'] = 'this_week'

    # Last week
    elif re.search(r'\blast week\b', query):
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        result['start_date'] = start_of_last_week.isoformat()
        result['end_date'] = end_of_last_week.isoformat()
        result['timeframe'] = 'last_week'

    # Today
    elif re.search(r'\btoday\b', query):
        result['start_date'] = today.isoformat()
        result['end_date'] = (today + timedelta(days=1)).isoformat()
        result['timeframe'] = 'today'

    # Yesterday
    elif re.search(r'\byesterday\b', query):
        yesterday = today - timedelta(days=1)
        result['start_date'] = yesterday.isoformat()
        result['end_date'] = today.isoformat()
        result['timeframe'] = 'yesterday'

    # Tomorrow
    elif re.search(r'\btomorrow\b', query):
        tomorrow = today + timedelta(days=1)
        result['start_date'] = tomorrow.isoformat()
        result['end_date'] = (tomorrow + timedelta(days=1)).isoformat()
        result['timeframe'] = 'tomorrow'

    # This month
    elif re.search(r'\bthis month\b', query):
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        result['start_date'] = start_of_month.isoformat()
        result['end_date'] = end_of_month.isoformat()
        result['timeframe'] = 'this_month'

    # Last month (Phase 5.1)
    elif re.search(r'\blast month\b', query):
        if today.month == 1:
            start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
        else:
            start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
        result['start_date'] = start_of_last_month.isoformat()
        result['end_date'] = end_of_last_month.isoformat()
        result['timeframe'] = 'last_month'

    # This quarter (Phase 5.1)
    elif re.search(r'\bthis quarter\b', query):
        quarter = (today.month - 1) // 3
        start_of_quarter = today.replace(month=quarter * 3 + 1, day=1)
        if quarter == 3:
            end_of_quarter = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_quarter = today.replace(month=(quarter + 1) * 3 + 1, day=1) - timedelta(days=1)
        result['start_date'] = start_of_quarter.isoformat()
        result['end_date'] = end_of_quarter.isoformat()
        result['timeframe'] = 'this_quarter'

    # Last quarter (Phase 5.1)
    elif re.search(r'\blast quarter\b', query):
        quarter = (today.month - 1) // 3
        if quarter == 0:
            start_of_last_quarter = today.replace(year=today.year - 1, month=10, day=1)
            end_of_last_quarter = today.replace(year=today.year - 1, month=12, day=31)
        else:
            start_of_last_quarter = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            end_of_last_quarter = today.replace(month=quarter * 3 + 1, day=1) - timedelta(days=1)
        result['start_date'] = start_of_last_quarter.isoformat()
        result['end_date'] = end_of_last_quarter.isoformat()
        result['timeframe'] = 'last_quarter'

    # Overdue (due date before today)
    elif re.search(r'\b(overdue|past due|late)\b', query):
        result['before_date'] = today.isoformat()
        result['timeframe'] = 'overdue'

    # Due soon (within 3 days)
    elif re.search(r'\b(due soon|upcoming|coming up)\b', query):
        result['start_date'] = today.isoformat()
        result['end_date'] = (today + timedelta(days=3)).isoformat()
        result['timeframe'] = 'due_soon'

    # Next week
    elif re.search(r'\bnext week\b', query):
        start_of_next_week = today + timedelta(days=(7 - today.weekday()))
        end_of_next_week = start_of_next_week + timedelta(days=6)
        result['start_date'] = start_of_next_week.isoformat()
        result['end_date'] = end_of_next_week.isoformat()
        result['timeframe'] = 'next_week'

    # Last N days
    elif match := re.search(r'\blast\s+(\d+)\s+days?\b', query):
        days = int(match.group(1))
        result['start_date'] = (today - timedelta(days=days)).isoformat()
        result['end_date'] = today.isoformat()
        result['timeframe'] = f'last_{days}_days'

    # Next N days
    elif match := re.search(r'\bnext\s+(\d+)\s+days?\b', query):
        days = int(match.group(1))
        result['start_date'] = today.isoformat()
        result['end_date'] = (today + timedelta(days=days)).isoformat()
        result['timeframe'] = f'next_{days}_days'

    # End of week (Phase 5.1)
    elif re.search(r'\b(end of week|by friday|eow)\b', query):
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0 and today.weekday() > 4:
            days_until_friday = 7
        end_of_week = today + timedelta(days=days_until_friday)
        result['start_date'] = today.isoformat()
        result['end_date'] = end_of_week.isoformat()
        result['timeframe'] = 'end_of_week'

    # End of month (Phase 5.1)
    elif re.search(r'\b(end of month|by month end|eom)\b', query):
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        result['start_date'] = today.isoformat()
        result['end_date'] = end_of_month.isoformat()
        result['timeframe'] = 'end_of_month'

    # Specific weekday - "by Monday", "on Tuesday", etc. (Phase 5.1)
    elif match := re.search(r'\b(on|by|next|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', query):
        day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        target_day = day_names.index(match.group(2).lower())
        days_ahead = target_day - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        target_date = today + timedelta(days=days_ahead)
        result['start_date'] = target_date.isoformat()
        result['end_date'] = (target_date + timedelta(days=1)).isoformat()
        result['timeframe'] = f'on_{match.group(2).lower()}'

    return result


def _detect_query_entities(query: str) -> list[str]:
    """Detect which entity types the query is asking about."""
    query_lower = query.lower()
    entities = []

    task_keywords = ['task', 'tasks', 'todo', 'todos', 'action item', 'action items', 'assigned', 'pending', 'blocked', 'in-progress', 'done', 'due']
    meeting_keywords = ['meeting', 'meetings', 'session', 'sessions', 'transcript', 'discussed', 'agenda']
    agent_keywords = ['agent', 'agents', 'ai agent', 'bot', 'bots', 'assistant', 'integration', 'integrated', 'integrating']
    proposal_keywords = ['proposal', 'proposals', 'proposed', 'proposing']
    decision_keywords = ['decision', 'decisions', 'decided', 'approved', 'governance']
    audit_keywords = ['audit', 'activity', 'history', 'changes', 'modified', 'created', 'deleted', 'who changed', 'trail']

    if any(kw in query_lower for kw in audit_keywords):
        entities.append('audit_logs')
    if any(kw in query_lower for kw in task_keywords):
        entities.append('tasks')
    if any(kw in query_lower for kw in meeting_keywords):
        entities.append('meetings')
    if any(kw in query_lower for kw in agent_keywords):
        entities.append('agents')
    if any(kw in query_lower for kw in proposal_keywords):
        entities.append('proposals')
    if any(kw in query_lower for kw in decision_keywords):
        entities.append('decisions')

    return entities if entities else ['tasks', 'meetings', 'agents']


# =============================================================================
# STATUS/PRIORITY NORMALIZATION HELPERS (Task 7.15)
# =============================================================================

# Status normalization map - matches TaskStatus enum values
STATUS_NORMALIZATION_MAP = {
    'blocked': 'Blocked',
    'pending': 'Pending',
    'in-progress': 'In-Progress',
    'in progress': 'In-Progress',
    'inprogress': 'In-Progress',
    'completed': 'Done',
    'done': 'Done',
    'finished': 'Done',
    'closed': 'Done',
    'deferred': 'Deferred',
}

# Priority normalization map - matches TaskPriority enum values
PRIORITY_NORMALIZATION_MAP = {
    'critical': 'Critical',
    'high': 'High',
    'medium': 'Medium',
    'low': 'Low',
}


def _normalize_status(status: str) -> str:
    """Normalize extracted status values to match TaskStatus enum values."""
    return STATUS_NORMALIZATION_MAP.get(status.lower(), status)


def _normalize_priority(priority: str) -> str:
    """Normalize extracted priority values to match TaskPriority enum values."""
    return PRIORITY_NORMALIZATION_MAP.get(priority.lower(), priority)


# =============================================================================
# QUERY-SPECIFIC COSMOSDB QUERY GENERATOR (Task 16.2)
# =============================================================================

def _build_cosmos_query(
    entity_type: str,
    intent: QueryIntent,
    parameters: Dict[str, Any],
    limit: Optional[int] = 15
) -> Tuple[str, Dict[str, Any]]:
    """
    Build a targeted CosmosDB query based on intent and parameters.
    Returns (query_string, query_parameters) for parameterized queries.
    """
    conditions = []
    query_params: Dict[str, Any] = {}

    # Status filter
    if 'status' in parameters:
        status = parameters['status']
        if status == 'overdue':
            # Overdue means due_date is in the past and status is not completed
            conditions.append("c.due_date < @today AND c.status != 'Done'")
            query_params['@today'] = datetime.utcnow().strftime('%Y-%m-%d')
        else:
            # Map common status names to actual TaskStatus enum values
            # TaskStatus: Pending, In-Progress, Done, Blocked, Deferred
            mapped_status = _normalize_status(status)
            conditions.append("c.status = @status")
            query_params['@status'] = mapped_status

    # Priority filter
    if 'priority' in parameters:
        mapped_priority = _normalize_priority(parameters['priority'])
        conditions.append("c.priority = @priority")
        query_params['@priority'] = mapped_priority

    # Assignee filter
    if 'assignee' in parameters:
        conditions.append("CONTAINS(c.assigned_to, @assignee)")
        query_params['@assignee'] = parameters['assignee']

    # Integration status filter (for agents only)
    if 'integration_status' in parameters and entity_type == 'agents':
        conditions.append("c.integration_status = @integration_status")
        query_params['@integration_status'] = parameters['integration_status']

    # Date range filters - use entity-appropriate date field
    # decisions use decision_date, meetings use date, tasks use due_date
    date_field_map = {
        'decisions': 'decision_date',
        'meetings': 'date',
        'tasks': 'due_date',
        'proposals': 'created_at',
        'agents': 'created_at',
        'audit_logs': 'timestamp',
    }
    date_field = date_field_map.get(entity_type, 'due_date')

    if 'start_date' in parameters and 'end_date' in parameters:
        conditions.append(f"c.{date_field} >= @start_date AND c.{date_field} <= @end_date")
        query_params['@start_date'] = parameters['start_date'][:10]  # YYYY-MM-DD
        query_params['@end_date'] = parameters['end_date'][:10]

    # Before date (for overdue) - skip if status=overdue already handled it
    # Only applies to tasks with due_date
    if 'before_date' in parameters and parameters.get('status') != 'overdue' and entity_type == 'tasks':
        conditions.append("c.due_date < @before_date AND c.status != 'Done'")
        query_params['@before_date'] = parameters['before_date'][:10]

    # Selected IDs filter (from page context)
    if 'selected_ids' in parameters and parameters['selected_ids']:
        id_placeholders = []
        for i, item_id in enumerate(parameters['selected_ids']):
            placeholder = f"@id{i}"
            id_placeholders.append(placeholder)
            query_params[placeholder] = item_id
        conditions.append(f"c.id IN ({', '.join(id_placeholders)})")

    # Search term (text search in title/description)
    if 'search_term' in parameters:
        search_term = parameters['search_term'].lower()
        conditions.append(
            "(CONTAINS(LOWER(c.title), @search_term) OR CONTAINS(LOWER(c.description), @search_term))"
        )
        query_params['@search_term'] = search_term

    # Phase 2.4: Learning-friendly task filter
    if 'learning_friendly' in parameters and entity_type == 'tasks':
        conditions.append("c.learning_friendly = true")

    # Phase 2.4: Complexity filter for tasks
    if 'complexity' in parameters and entity_type == 'tasks':
        conditions.append("c.complexity = @complexity")
        query_params['@complexity'] = parameters['complexity']

    # Phase 2.4: Owner filter for ownership queries
    if 'owner' in parameters:
        # Search in owner, owner_name, and assigned_to fields
        conditions.append(
            "(CONTAINS(LOWER(c.owner), @owner) OR CONTAINS(LOWER(c.owner_name), @owner) OR CONTAINS(LOWER(c.assigned_to), @owner))"
        )
        query_params['@owner'] = parameters['owner'].lower()

    # Phase 2.4: Team filter
    if 'team' in parameters:
        conditions.append("CONTAINS(LOWER(c.team), @team)")
        query_params['@team'] = parameters['team'].lower()

    # For aggregation, fetch all items and aggregate client-side
    # (CosmosDB Gateway mode doesn't support GROUP BY with COUNT)
    if intent == QueryIntent.AGGREGATION:
        if conditions:
            where_clause = " AND ".join(conditions)
            query = f"SELECT c.status FROM c WHERE {where_clause}"
        else:
            query = "SELECT c.status FROM c"
        return query, query_params

    # Standard queries with results
    # If limit is None, fetch all items (for aggregation or when full data needed)
    if limit is not None:
        select_clause = f"SELECT TOP {limit} *"
    else:
        select_clause = "SELECT *"

    if conditions:
        where_clause = " AND ".join(conditions)
        query = f"{select_clause} FROM c WHERE {where_clause} ORDER BY c._ts DESC"
    else:
        query = f"{select_clause} FROM c ORDER BY c._ts DESC"

    return query, query_params


def _get_entity_total_count(container, entity_type: str, parameters: Dict[str, Any]) -> int:
    """Get total count of entities matching the filter criteria (without limit)."""
    try:
        conditions = []
        query_params = {}

        if parameters:
            if 'status' in parameters:
                conditions.append("c.status = @status")
                query_params["@status"] = _normalize_status(parameters['status'])
            if 'priority' in parameters:
                conditions.append("c.priority = @priority")
                query_params["@priority"] = _normalize_priority(parameters['priority'])
            if 'assignee' in parameters:
                conditions.append("c.assigned_to = @assignee")
                query_params["@assignee"] = parameters['assignee']

        if conditions:
            count_query = f"SELECT VALUE COUNT(1) FROM c WHERE {' AND '.join(conditions)}"
        else:
            count_query = "SELECT VALUE COUNT(1) FROM c"

        if query_params:
            result = list(container.query_items(
                query=count_query,
                parameters=[{"name": k, "value": v} for k, v in query_params.items()],
                enable_cross_partition_query=True
            ))
        else:
            result = list(container.query_items(
                query=count_query,
                enable_cross_partition_query=True
            ))

        return result[0] if result else 0
    except Exception as e:
        logger.warning(f"Failed to get total count for {entity_type}: {e}")
        return -1


def _get_live_context_with_intent(
    classified: ClassifiedIntent,
    limit: Optional[int] = 15
) -> Tuple[str, List[str], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Fetch live data from CosmosDB using intent-aware queries.
    Returns formatted context string, list of sources, raw items, and data_basis metadata.
    """
    context_parts = []
    sources = []
    all_items = []
    data_basis = {"items_shown": 0, "total_items": 0, "entity_types": []}

    for entity_type in classified.entities:
        try:
            container = db.get_container(entity_type)
            if not container:
                continue

            # Build targeted query based on intent and parameters
            query, query_params = _build_cosmos_query(
                entity_type=entity_type,
                intent=classified.intent,
                parameters=classified.parameters,
                limit=limit
            )

            logger.info(f"CosmosDB query for {entity_type}: {query} | Params: {query_params}")

            # Execute query with parameters
            if query_params:
                items = list(container.query_items(
                    query=query,
                    parameters=[{"name": k, "value": v} for k, v in query_params.items()],
                    enable_cross_partition_query=True
                ))
            else:
                items = list(container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))

            logger.info(f"Parameterized query returned {len(items)} items for {entity_type}")
            if query_params:
                statuses = [item.get('status', 'N/A') for item in items[:5]]
                logger.info(f"Sample statuses from results: {statuses}")

            # Get total count for "showing X of Y" context when limit is applied
            total_count = None
            if limit is not None and classified.intent != QueryIntent.AGGREGATION:
                total_count = _get_entity_total_count(container, entity_type, classified.parameters)
                if total_count >= 0:
                    logger.info(f"Total count for {entity_type}: {total_count} (showing {len(items)})")

            # Update data_basis metadata
            data_basis["items_shown"] += len(items)
            if total_count is not None and total_count >= 0:
                data_basis["total_items"] += total_count
            else:
                data_basis["total_items"] += len(items)
            if entity_type not in data_basis["entity_types"]:
                data_basis["entity_types"].append(entity_type)

            if not items:
                if classified.parameters:
                    context_parts.append(f"\n=== {entity_type.upper()} (0 matching filters) ===")
                    context_parts.append(f"No {entity_type} found matching: {classified.parameters}")
                continue

            # Collect raw items for action suggestions
            all_items.extend(items)

            # Format results based on entity type and intent
            context_parts.append(_format_entity_results(entity_type, items, classified, total_count))
            if classified.intent == QueryIntent.AGGREGATION:
                from collections import Counter
                status_counts = Counter(item.get('status', 'Unknown') for item in items)
                sources.append(f"Aggregation: {len(items)} {entity_type} in {len(status_counts)} status groups")
            else:
                sources.append(f"Live Data: {len(items)} {entity_type} from database")

        except Exception as e:
            logger.warning(f"Failed to fetch {entity_type} from CosmosDB: {e}")

    return "\n".join(context_parts), sources, all_items, data_basis


def _format_aggregation_results(entity_type: str, items: List[dict]) -> str:
    """Format aggregation query results (counts by status/group) with client-side aggregation."""
    lines = []

    from collections import Counter
    status_counts = Counter(item.get('status', 'Unknown') for item in items)
    total = len(items)

    lines.append(f"\n=== {entity_type.upper()} STATUS SUMMARY ===")
    lines.append(f"Total: {total}")
    lines.append("")

    for status, count in status_counts.most_common():
        pct = (count / total * 100) if total > 0 else 0
        lines.append(f"- {status}: {count} ({pct:.1f}%)")

    return "\n".join(lines)


def _format_entity_results(entity_type: str, items: List[dict], classified: ClassifiedIntent, total_count: Optional[int] = None) -> str:
    """Format entity results for context, highlighting relevant fields based on intent."""
    lines = []

    if classified.intent == QueryIntent.AGGREGATION:
        return _format_aggregation_results(entity_type, items)

    filter_desc = ""
    if classified.parameters:
        filter_parts = []
        if 'status' in classified.parameters:
            filter_parts.append(f"status={classified.parameters['status']}")
        if 'priority' in classified.parameters:
            filter_parts.append(f"priority={classified.parameters['priority']}")
        if 'assignee' in classified.parameters:
            filter_parts.append(f"assignee={classified.parameters['assignee']}")
        if 'timeframe' in classified.parameters:
            filter_parts.append(f"timeframe={classified.parameters['timeframe']}")
        if filter_parts:
            filter_desc = f" [filtered: {', '.join(filter_parts)}]"

    def _make_header(entity_name: str) -> str:
        """Create header with 'showing X of Y total' when applicable."""
        shown = len(items)
        if total_count is not None and total_count > 0 and total_count != shown:
            return f"\n=== {entity_name} (showing {shown} of {total_count} total){filter_desc} ==="
        else:
            return f"\n=== {entity_name} ({shown} results){filter_desc} ==="

    if entity_type == 'tasks':
        lines.append(_make_header("TASKS"))
        for item in items:
            status = item.get('status', 'Unknown')
            priority = item.get('priority', 'Unknown')
            assigned = item.get('assigned_to', 'Unassigned')
            due = item.get('due_date', 'No due date')
            lines.append(
                f"- [{status}] {item.get('title', 'Untitled')} "
                f"(Priority: {priority}, Assigned: {assigned}, Due: {due})"
            )
            if item.get('description'):
                lines.append(f"  Description: {item.get('description', '')[:200]}")

    elif entity_type == 'meetings':
        lines.append(_make_header("MEETINGS"))
        for item in items:
            status = item.get('status', 'Unknown')
            date = item.get('date', 'Unknown date')
            lines.append(
                f"- [{status}] {item.get('title', 'Untitled')} "
                f"(Date: {date}, Type: {item.get('type', 'Unknown')})"
            )
            if item.get('summary'):
                lines.append(f"  Summary: {item.get('summary', '')[:200]}")

    elif entity_type == 'agents':
        lines.append(_make_header("AI AGENTS"))
        for item in items:
            status = item.get('status', 'Unknown')
            tier = item.get('tier', 'Unknown')
            lines.append(
                f"- [{status}] {item.get('name', 'Untitled')} "
                f"(Tier: {tier}, Owner: {item.get('owner', 'Unknown')})"
            )
            if item.get('description'):
                lines.append(f"  Description: {item.get('description', '')[:200]}")

    elif entity_type == 'proposals':
        lines.append(_make_header("PROPOSALS"))
        for item in items:
            status = item.get('status', 'Unknown')
            lines.append(
                f"- [{status}] {item.get('title', 'Untitled')} "
                f"(Proposer: {item.get('proposer', 'Unknown')})"
            )

    elif entity_type == 'decisions':
        lines.append(_make_header("DECISIONS"))
        for item in items:
            lines.append(
                f"- {item.get('title', 'Untitled')} "
                f"(Date: {item.get('decision_date', 'Unknown')}, By: {item.get('decision_maker', 'Unknown')})"
            )

    elif entity_type == 'audit_logs':
        lines.append(_make_header("AUDIT TRAIL"))
        for item in items:
            action = item.get('action', 'unknown')
            entity = item.get('entity_type', 'unknown')
            entity_id = item.get('entity_id', 'N/A')
            user = item.get('user_name') or item.get('user_id', 'unknown')
            timestamp = item.get('timestamp', 'Unknown time')
            lines.append(
                f"- [{action.upper()}] {entity}/{entity_id} by {user} at {timestamp}"
            )
            if item.get('entity_title'):
                lines.append(f"  Title: {item.get('entity_title')}")

    return "\n".join(lines)


def _get_live_context(entities: list[str], limit: int = 10) -> tuple[str, list[str]]:
    """Fetch live data from CosmosDB for the specified entity types."""
    context_parts = []
    sources = []

    for entity_type in entities:
        try:
            container = db.get_container(entity_type)
            if not container:
                continue

            items = list(container.query_items(
                query=f"SELECT TOP {limit} * FROM c ORDER BY c._ts DESC",
                enable_cross_partition_query=True
            ))

            if not items:
                continue

            if entity_type == 'tasks':
                context_parts.append(f"\n=== CURRENT TASKS ({len(items)} most recent) ===")
                for item in items:
                    status = item.get('status', 'Unknown')
                    priority = item.get('priority', 'Unknown')
                    assigned = item.get('assigned_to', 'Unassigned')
                    due = item.get('due_date', 'No due date')
                    context_parts.append(
                        f"- [{status}] {item.get('title', 'Untitled')} (Priority: {priority}, Assigned: {assigned}, Due: {due})"
                    )
                    if item.get('description'):
                        context_parts.append(f"  Description: {item.get('description', '')[:200]}")
                sources.append(f"Live Data: {len(items)} tasks from database")

            elif entity_type == 'meetings':
                context_parts.append(f"\n=== RECENT MEETINGS ({len(items)} most recent) ===")
                for item in items:
                    status = item.get('status', 'Unknown')
                    date = item.get('date', 'Unknown date')
                    context_parts.append(
                        f"- [{status}] {item.get('title', 'Untitled')} (Date: {date}, Type: {item.get('type', 'Unknown')})"
                    )
                    if item.get('summary'):
                        context_parts.append(f"  Summary: {item.get('summary', '')[:200]}")
                sources.append(f"Live Data: {len(items)} meetings from database")

            elif entity_type == 'agents':
                context_parts.append(f"\n=== AI AGENTS ({len(items)} registered) ===")
                for item in items:
                    status = item.get('status', 'Unknown')
                    tier = item.get('tier', 'Unknown')
                    context_parts.append(
                        f"- [{status}] {item.get('name', 'Untitled')} (Tier: {tier}, Owner: {item.get('owner', 'Unknown')})"
                    )
                    if item.get('description'):
                        context_parts.append(f"  Description: {item.get('description', '')[:200]}")
                sources.append(f"Live Data: {len(items)} agents from database")

            elif entity_type == 'proposals':
                context_parts.append(f"\n=== PROPOSALS ({len(items)} most recent) ===")
                for item in items:
                    status = item.get('status', 'Unknown')
                    context_parts.append(
                        f"- [{status}] {item.get('title', 'Untitled')} (Proposer: {item.get('proposer', 'Unknown')})"
                    )
                sources.append(f"Live Data: {len(items)} proposals from database")

            elif entity_type == 'decisions':
                context_parts.append(f"\n=== DECISIONS ({len(items)} most recent) ===")
                for item in items:
                    context_parts.append(
                        f"- {item.get('title', 'Untitled')} (Date: {item.get('decision_date', 'Unknown')}, By: {item.get('decision_maker', 'Unknown')})"
                    )
                sources.append(f"Live Data: {len(items)} decisions from database")

            elif entity_type == 'audit_logs':
                context_parts.append(f"\n=== AUDIT TRAIL ({len(items)} recent entries) ===")
                for item in items:
                    action = item.get('action', 'unknown')
                    entity = item.get('entity_type', 'unknown')
                    entity_id = item.get('entity_id', 'N/A')
                    user = item.get('user_name') or item.get('user_id', 'unknown')
                    timestamp = item.get('timestamp', 'Unknown time')
                    context_parts.append(
                        f"- [{action.upper()}] {entity}/{entity_id} by {user} at {timestamp}"
                    )
                sources.append(f"Live Data: {len(items)} audit entries from database")

        except Exception as e:
            logger.warning(f"Failed to fetch {entity_type} from CosmosDB: {e}")

    return "\n".join(context_parts), sources


@app.post("/api/agent/query", response_model=AgentQueryResponse)
async def query_agent(request: AgentQueryRequest):
    """Query the Fourth AI Guide agent with intent classification, targeted queries, and RAG context."""
    try:
        context = request.context or ""
        sources = []
        session_id = request.session_id or "default"

        # Phase 5.2: Resolve pronouns and get context from conversation history
        query_to_process = request.query
        session_context_additions = {}
        if session_id != "default":
            query_to_process, session_context_additions = _resolve_pronouns(request.query, session_id)
            history_summary = conversation_memory.get_history_summary(session_id)
            if history_summary:
                context = f"{history_summary}\n\n{context}" if context else history_summary
                logger.info(f"Session {session_id[:8]}...: Added conversation history context")

        # Step 1: Classify query intent and extract parameters
        classified = _classify_intent(query_to_process)

        # Phase 5.2: Merge session context into classified parameters
        if session_context_additions:
            classified.parameters.update(session_context_additions)
            logger.info(f"Session context applied: {session_context_additions}")

        # Step 1b: Apply page context if provided
        if request.page_context:
            classified = _apply_page_context(classified, request.page_context)
            logger.info(f"Page context applied: page={request.page_context.current_page}, selected={len(request.page_context.selected_ids)} items")

        logger.info(
            f"Query: '{request.query[:50]}...' | Intent: {classified.intent.value} | "
            f"Entities: {classified.entities} | Params: {classified.parameters} | Confidence: {classified.confidence}"
        )

        # HMLR: Route query and get memory context
        hmlr_decision = None
        hmlr_context = None
        user_id = request.user_id or "anonymous"
        if settings.hmlr_enabled and session_id != "default":
            try:
                hmlr_decision, hmlr_hydrated = await hmlr_service.route_query(
                    user_id=user_id,
                    session_id=session_id,
                    query=request.query,
                    intent=classified.intent.value,
                    entities=classified.entities
                )
                hmlr_context = hmlr_hydrated.full_context
                if hmlr_context:
                    context = f"{hmlr_context}\n\n{context}" if context else hmlr_context
                    logger.info(f"HMLR: Added memory context ({hmlr_hydrated.token_estimate} tokens)")
            except Exception as hmlr_error:
                logger.warning(f"HMLR routing failed, continuing without memory: {hmlr_error}")

        # Add intent metadata to help AI understand query type
        intent_context = f"\n[Query Analysis]\nIntent: {classified.intent.value}\nTarget: {', '.join(classified.entities)}"
        if classified.parameters:
            intent_context += f"\nFilters: {classified.parameters}"

        # Step 2: Fetch LIVE data from CosmosDB using intent-aware targeted queries
        # Use intent-aware limits: AGGREGATION needs all items for accurate counts, LIST can be limited
        live_items = []
        data_basis_info = None
        if classified.intent == QueryIntent.AGGREGATION:
            query_limit = None  # No limit - need all items for accurate aggregation counts
        else:
            query_limit = 50  # Increased from 15 for better context coverage
        try:
            logger.info(f"Calling _get_live_context_with_intent with classified: {classified.intent.value}, params: {classified.parameters}, limit: {query_limit}")
            live_context, live_sources, live_items, data_basis_info = _get_live_context_with_intent(classified, limit=query_limit)
            if live_context:
                context = f"{context}\n\n{live_context}" if context else live_context
                sources.extend(live_sources)
                logger.info(f"Intent-aware query returned {len(live_sources)} sources, {len(live_items)} items")
        except Exception as db_error:
            logger.error(f"CosmosDB intent-aware query failed: {db_error}", exc_info=True)
            # Fallback to generic query if targeted query fails
            try:
                logger.info("Falling back to generic query")
                live_context, live_sources = _get_live_context(classified.entities, limit=15)
                if live_context:
                    context = f"{context}\n\n{live_context}" if context else live_context
                    sources.extend(live_sources)
            except Exception as fallback_error:
                logger.error(f"Fallback query also failed: {fallback_error}")

        # Step 2b: Handle COMPARISON intent with historical snapshots
        if classified.intent == QueryIntent.COMPARISON:
            try:
                from src.snapshot_service import snapshot_service
                query_lower = request.query.lower()

                # Determine comparison period
                if "last month" in query_lower or "previous month" in query_lower:
                    days_ago = 30
                elif "last week" in query_lower or "previous week" in query_lower:
                    days_ago = 7
                elif "yesterday" in query_lower:
                    days_ago = 1
                else:
                    days_ago = 7  # Default to week comparison

                # Get current snapshot (capture if doesn't exist)
                current_snapshot = await snapshot_service.capture_daily_snapshot()
                previous_snapshot = await snapshot_service.get_snapshot(days_ago=days_ago)

                if current_snapshot and previous_snapshot:
                    comparison_context = snapshot_service.format_comparison(
                        current_snapshot, previous_snapshot
                    )
                    context = f"{context}\n\n{comparison_context}" if context else comparison_context
                    sources.append(f"Historical Data: Comparison with {days_ago} days ago")
                    logger.info(f"Added comparison context for {days_ago} days ago")
                else:
                    context = f"{context}\n\n[Note: Historical data for comparison not yet available. Snapshots are captured daily.]"
                    logger.info("No historical snapshot available for comparison")

            except Exception as comparison_error:
                logger.warning(f"Failed to fetch comparison data: {comparison_error}")
                context = f"{context}\n\n[Note: Historical comparison data temporarily unavailable.]"

        # Step 3: Also fetch from semantic search for additional context (transcripts, docs)
        try:
            search_service = get_search_service()
            search_results = search_service.search(
                query=request.query,
                top=3,
                use_semantic_search=True,
            )

            if search_results:
                context_parts = ["\n=== RELATED DOCUMENTS ==="]
                for result in search_results:
                    context_parts.append(
                        f"[{result['type'].upper()}] {result['title']}: {result['content'][:300]}"
                    )
                    sources.append(f"{result['type']}: {result['title']}")
                context = f"{context}\n" + "\n".join(context_parts)

        except Exception as search_error:
            logger.warning(f"Search failed, proceeding without RAG context: {search_error}")

        # Step 4: Generate action hints based on query intent and data
        action_hints = _generate_action_hints(classified, len(live_items))

        # Step 4b: Get response template for this intent type (Phase 4.1)
        response_template = _get_response_template(classified.intent)

        # Step 4c: Extract contact information from results (Phase 4.2)
        contact_info = _extract_contact_info(live_items, classified)

        # Step 4d: Get platform documentation context for platform-related queries
        platform_context_result = None
        platform_intent = None
        try:
            page_ctx = None
            if request.page_context:
                page_ctx = {
                    "current_page": request.page_context.current_page,
                    "selected_ids": request.page_context.selected_ids,
                    "active_filters": request.page_context.active_filters,
                }
            platform_context_result = await context_service.get_context_for_query(
                request.query, page_context=page_ctx
            )
            if platform_context_result.sources:
                sources.extend(platform_context_result.sources)
                platform_intent = platform_context_result.intent.value
                logger.info(f"Platform docs context: intent={platform_intent}, sources={platform_context_result.sources}")
        except Exception as platform_error:
            logger.warning(f"Platform docs lookup failed: {platform_error}")

        # Step 5: Prepend intent context, response template, and action hints to help AI
        full_context = f"{intent_context}\n{context}" if context else intent_context
        if response_template:
            full_context = f"{full_context}\n{response_template}"
        if contact_info:
            full_context = f"{full_context}\n{contact_info}"
        if action_hints:
            full_context = f"{full_context}\n{action_hints}"

        # Step 6: Call AI with enriched context and platform docs
        platform_docs_context = platform_context_result.context if platform_context_result else None
        result = await ai_client.query_agent(
            query=request.query,
            context=full_context,
            platform_context=platform_docs_context,
            intent=platform_intent,
        )

        if 'sources' not in result or not result['sources']:
            result['sources'] = sources if sources else []

        # Add intent metadata to response for frontend use
        result['intent'] = classified.intent.value
        result['confidence'] = classified.confidence

        # Generate action suggestions based on query results (with HMLR personalization)
        page_type = request.page_context.visible_entity_type if request.page_context else None
        suggestions = await _generate_action_suggestions_with_hmlr(
            classified, live_items, result.get('response', ''),
            user_id=request.user_id, session_id=session_id, page_type=page_type
        )
        result['suggestions'] = [s.model_dump() for s in suggestions]

        # Add data basis metadata for UI confidence indicators
        if data_basis_info:
            result['data_basis'] = data_basis_info

        # Phase 5.2: Store conversation turn for multi-turn context
        if session_id != "default":
            extracted_context = {}
            if classified.parameters.get('assignee'):
                extracted_context['assignee'] = classified.parameters['assignee']
            if classified.parameters.get('status'):
                extracted_context['status'] = classified.parameters['status']
            if classified.parameters.get('priority'):
                extracted_context['priority'] = classified.parameters['priority']
            if classified.parameters.get('ownership_subject'):
                extracted_context['subject'] = classified.parameters['ownership_subject']

            conversation_memory.add_turn(
                session_id=session_id,
                query=request.query,
                response=result.get('response', '')[:500],  # Truncate for memory efficiency
                intent=classified.intent.value,
                entities=classified.entities,
                extracted_context=extracted_context
            )
            logger.info(f"Session {session_id[:8]}...: Stored conversation turn")

            # HMLR: Store turn for persistent memory (triggers background fact extraction)
            if settings.hmlr_enabled and hmlr_decision:
                try:
                    await hmlr_service.store_turn(
                        user_id=user_id,
                        session_id=session_id,
                        query=request.query,
                        response=result.get('response', ''),
                        decision=hmlr_decision,
                        intent=classified.intent.value,
                        entities=classified.entities
                    )
                    logger.info(f"HMLR: Stored turn in block (scenario={hmlr_decision.scenario})")
                except Exception as hmlr_store_error:
                    logger.warning(f"HMLR store_turn failed: {hmlr_store_error}")

        return AgentQueryResponse(**result)
    except Exception as e:
        logger.error(f"Error querying agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/query/stream")
async def query_agent_stream(request: AgentQueryRequest):
    """Stream query responses from the Fourth AI Guide agent with SSE."""
    import json as json_module

    try:
        context = request.context or ""
        sources = []
        session_id = request.session_id or "default"

        # Phase 5.2: Resolve pronouns and get context from conversation history
        query_to_process = request.query
        session_context_additions = {}
        if session_id != "default":
            query_to_process, session_context_additions = _resolve_pronouns(request.query, session_id)
            history_summary = conversation_memory.get_history_summary(session_id)
            if history_summary:
                context = f"{history_summary}\n\n{context}" if context else history_summary

        # Step 1: Classify query intent and extract parameters
        classified = _classify_intent(query_to_process)

        if session_context_additions:
            classified.parameters.update(session_context_additions)

        if request.page_context:
            classified = _apply_page_context(classified, request.page_context)

        logger.info(
            f"Stream Query: '{request.query[:50]}...' | Intent: {classified.intent.value} | "
            f"Entities: {classified.entities} | Confidence: {classified.confidence}"
        )

        intent_context = f"\n[Query Analysis]\nIntent: {classified.intent.value}\nTarget: {', '.join(classified.entities)}"
        if classified.parameters:
            intent_context += f"\nFilters: {classified.parameters}"

        # Step 2: Fetch LIVE data from CosmosDB
        live_items = []
        data_basis_info = None
        query_limit = None if classified.intent == QueryIntent.AGGREGATION else 50

        try:
            live_context, live_sources, live_items, data_basis_info = _get_live_context_with_intent(classified, limit=query_limit)
            if live_context:
                context = f"{context}\n\n{live_context}" if context else live_context
                sources.extend(live_sources)
        except Exception as db_error:
            logger.error(f"CosmosDB query failed: {db_error}")
            try:
                live_context, live_sources = _get_live_context(classified.entities, limit=15)
                if live_context:
                    context = f"{context}\n\n{live_context}" if context else live_context
                    sources.extend(live_sources)
            except Exception:
                pass

        # Step 3: Semantic search for additional context
        try:
            search_service = get_search_service()
            search_results = search_service.search(query=request.query, top=3, use_semantic_search=True)
            if search_results:
                context_parts = ["\n=== RELATED DOCUMENTS ==="]
                for result in search_results:
                    context_parts.append(f"[{result['type'].upper()}] {result['title']}: {result['content'][:300]}")
                    sources.append(f"{result['type']}: {result['title']}")
                context = f"{context}\n" + "\n".join(context_parts)
        except Exception:
            pass

        # Step 4: Generate action hints and response template
        action_hints = _generate_action_hints(classified, len(live_items))
        response_template = _get_response_template(classified.intent)
        contact_info = _extract_contact_info(live_items, classified)

        # Step 4d: Get platform documentation context
        platform_context_result = None
        platform_intent = None
        try:
            page_ctx = None
            if request.page_context:
                page_ctx = {
                    "current_page": request.page_context.current_page,
                    "selected_ids": request.page_context.selected_ids,
                    "active_filters": request.page_context.active_filters,
                }
            platform_context_result = await context_service.get_context_for_query(
                request.query, page_context=page_ctx
            )
            if platform_context_result.sources:
                sources.extend(platform_context_result.sources)
                platform_intent = platform_context_result.intent.value
        except Exception as platform_error:
            logger.warning(f"Platform docs lookup failed: {platform_error}")

        full_context = f"{intent_context}\n{context}" if context else intent_context
        if response_template:
            full_context = f"{full_context}\n{response_template}"
        if contact_info:
            full_context = f"{full_context}\n{contact_info}"
        if action_hints:
            full_context = f"{full_context}\n{action_hints}"

        # Generate suggestions (with HMLR personalization)
        page_type = request.page_context.visible_entity_type if request.page_context else None
        suggestions = await _generate_action_suggestions_with_hmlr(
            classified, live_items, "",
            user_id=request.user_id, session_id=session_id, page_type=page_type
        )
        platform_docs_context = platform_context_result.context if platform_context_result else None

        def generate():
            """Generator for SSE stream."""
            # First, send metadata
            # Handle data_basis - could be dict or Pydantic model
            data_basis_dict = None
            if data_basis_info:
                if hasattr(data_basis_info, 'model_dump'):
                    data_basis_dict = data_basis_info.model_dump()
                elif isinstance(data_basis_info, dict):
                    data_basis_dict = data_basis_info

            metadata = {
                "type": "metadata",
                "sources": sources,
                "intent": classified.intent.value,
                "confidence": classified.confidence,
                "suggestions": [s.model_dump() for s in suggestions],
                "data_basis": data_basis_dict,
            }
            yield f"data: {json_module.dumps(metadata)}\n\n"

            # Stream content from AI with platform docs context
            full_response = ""
            for token in ai_client.query_agent_streaming(
                query=request.query,
                context=full_context,
                platform_context=platform_docs_context,
                intent=platform_intent,
            ):
                full_response += token
                chunk_data = {"type": "content", "token": token}
                yield f"data: {json_module.dumps(chunk_data)}\n\n"

            # Store conversation turn for multi-turn context
            if session_id != "default":
                extracted_context = {}
                if classified.parameters.get('assignee'):
                    extracted_context['assignee'] = classified.parameters['assignee']
                if classified.parameters.get('status'):
                    extracted_context['status'] = classified.parameters['status']
                if classified.parameters.get('priority'):
                    extracted_context['priority'] = classified.parameters['priority']

                conversation_memory.add_turn(
                    session_id=session_id,
                    query=request.query,
                    response=full_response[:500],
                    intent=classified.intent.value,
                    entities=classified.entities,
                    extracted_context=extracted_context
                )

            # Send completion signal
            yield 'data: {"type": "done"}\n\n'

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        logger.error(f"Error in streaming query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# PROACTIVE INSIGHTS ENDPOINT (Phase 5.3)
# =============================================================================

class InsightItem(PydanticBaseModel):
    """A single proactive insight."""
    id: str
    type: str  # 'warning', 'info', 'action'
    title: str
    description: str
    count: Optional[int] = None
    action_label: Optional[str] = None
    action_query: Optional[str] = None  # Suggested query to run


class InsightsResponse(PydanticBaseModel):
    """Response containing page-specific insights."""
    page: str
    insights: List[InsightItem]
    generated_at: str


@app.get("/api/agent/insights")
async def get_proactive_insights(page: str = "dashboard"):
    """
    Get page-specific proactive insights for the AI Guide.
    Returns insights based on current data state.
    """
    try:
        insights = []
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        if page in ["tasks", "dashboard", "/"]:
            # Task-related insights
            tasks = list(db.tasks.find({}))

            # Overdue tasks
            overdue_count = sum(
                1 for t in tasks
                if t.get('due_date') and t.get('status') not in ['Done', 'Completed']
                and datetime.fromisoformat(str(t['due_date']).replace('Z', '+00:00').replace('+00:00', '')) < today
            )
            if overdue_count > 0:
                insights.append(InsightItem(
                    id="overdue_tasks",
                    type="warning",
                    title="Overdue Tasks",
                    description=f"You have {overdue_count} task{'s' if overdue_count != 1 else ''} past their due date",
                    count=overdue_count,
                    action_label="Show overdue",
                    action_query="Show me all overdue tasks"
                ))

            # Blocked tasks
            blocked_count = sum(1 for t in tasks if t.get('status') == 'Blocked')
            if blocked_count > 0:
                insights.append(InsightItem(
                    id="blocked_tasks",
                    type="warning",
                    title="Blocked Tasks",
                    description=f"{blocked_count} task{'s are' if blocked_count != 1 else ' is'} currently blocked",
                    count=blocked_count,
                    action_label="View blockers",
                    action_query="What tasks are blocked and why?"
                ))

            # Unassigned high priority
            unassigned_high = sum(
                1 for t in tasks
                if t.get('priority') in ['High', 'Critical']
                and not t.get('assigned_to')
                and t.get('status') not in ['Done', 'Completed']
            )
            if unassigned_high > 0:
                insights.append(InsightItem(
                    id="unassigned_high",
                    type="action",
                    title="Unassigned Priority Items",
                    description=f"{unassigned_high} high-priority task{'s need' if unassigned_high != 1 else ' needs'} assignment",
                    count=unassigned_high,
                    action_label="Assign tasks",
                    action_query="Show unassigned high priority tasks"
                ))

            # Due this week
            end_of_week = today + timedelta(days=(6 - today.weekday()))
            due_soon_count = sum(
                1 for t in tasks
                if t.get('due_date') and t.get('status') not in ['Done', 'Completed']
                and today <= datetime.fromisoformat(str(t['due_date']).replace('Z', '+00:00').replace('+00:00', '')) <= end_of_week
            )
            if due_soon_count > 0:
                insights.append(InsightItem(
                    id="due_this_week",
                    type="info",
                    title="Due This Week",
                    description=f"{due_soon_count} task{'s are' if due_soon_count != 1 else ' is'} due by end of week",
                    count=due_soon_count,
                    action_label="View schedule",
                    action_query="What tasks are due this week?"
                ))

        elif page in ["agents", "agents/"]:
            # Agent-related insights
            agents = list(db.agents.find({}))

            # Agents with integration issues
            integration_issues = sum(
                1 for a in agents
                if a.get('integration_status') in ['Integration Issues', 'Blocked']
            )
            if integration_issues > 0:
                insights.append(InsightItem(
                    id="integration_issues",
                    type="warning",
                    title="Integration Issues",
                    description=f"{integration_issues} agent{'s have' if integration_issues != 1 else ' has'} integration problems",
                    count=integration_issues,
                    action_label="View issues",
                    action_query="Which agents have integration issues?"
                ))

            # Agents in development
            in_dev = sum(1 for a in agents if a.get('status') in ['Development', 'Testing'])
            if in_dev > 0:
                insights.append(InsightItem(
                    id="agents_in_dev",
                    type="info",
                    title="In Development",
                    description=f"{in_dev} agent{'s are' if in_dev != 1 else ' is'} currently in development or testing",
                    count=in_dev,
                    action_label="Track progress",
                    action_query="Show me agents in development"
                ))

        elif page in ["meetings", "meetings/"]:
            # Meeting-related insights
            meetings = list(db.meetings.find({}))

            # Upcoming meetings
            upcoming = [
                m for m in meetings
                if m.get('date') and m.get('status') == 'Scheduled'
                and datetime.fromisoformat(str(m['date']).replace('Z', '+00:00').replace('+00:00', '')) >= today
            ]
            if upcoming:
                next_meeting = min(upcoming, key=lambda x: x.get('date', ''))
                insights.append(InsightItem(
                    id="next_meeting",
                    type="info",
                    title="Next Meeting",
                    description=f"'{next_meeting.get('title', 'Untitled')}' - {next_meeting.get('date', 'TBD')[:10]}",
                    action_label="View details",
                    action_query=f"Tell me about the meeting '{next_meeting.get('title', '')}'"
                ))

            # Unprocessed transcripts
            unprocessed = sum(
                1 for m in meetings
                if m.get('transcript_url') and not m.get('summary')
            )
            if unprocessed > 0:
                insights.append(InsightItem(
                    id="unprocessed_transcripts",
                    type="action",
                    title="Unprocessed Transcripts",
                    description=f"{unprocessed} meeting{'s have' if unprocessed != 1 else ' has'} transcripts pending processing",
                    count=unprocessed,
                    action_label="Process transcripts",
                    action_query="Which meetings have unprocessed transcripts?"
                ))

        elif page in ["governance", "governance/", "decisions"]:
            # Governance insights
            decisions = list(db.decisions.find({}))
            proposals = list(db.proposals.find({}))

            # Pending proposals
            pending_proposals = sum(1 for p in proposals if p.get('status') in ['Proposed', 'Reviewing'])
            if pending_proposals > 0:
                insights.append(InsightItem(
                    id="pending_proposals",
                    type="action",
                    title="Pending Proposals",
                    description=f"{pending_proposals} proposal{'s need' if pending_proposals != 1 else ' needs'} review",
                    count=pending_proposals,
                    action_label="Review proposals",
                    action_query="Show pending proposals that need review"
                ))

            # Recent decisions
            recent_decisions = sum(
                1 for d in decisions
                if d.get('decision_date') and (today - datetime.fromisoformat(str(d['decision_date']).replace('Z', '+00:00').replace('+00:00', ''))).days <= 7
            )
            if recent_decisions > 0:
                insights.append(InsightItem(
                    id="recent_decisions",
                    type="info",
                    title="Recent Decisions",
                    description=f"{recent_decisions} decision{'s were' if recent_decisions != 1 else ' was'} made this week",
                    count=recent_decisions,
                    action_label="View decisions",
                    action_query="What decisions were made this week?"
                ))

        return InsightsResponse(
            page=page,
            insights=insights,
            generated_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Error generating insights: {e}", exc_info=True)
        return InsightsResponse(page=page, insights=[], generated_at=datetime.utcnow().isoformat())


@app.get("/api/guide/suggestions")
async def get_personalized_suggestions(
    page_type: str = "dashboard",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
):
    """
    Get personalized suggestions for the AI Guide.
    Uses HMLR memory for personalization with static fallback.
    """
    from src.hmlr.suggestion_providers import VALID_PAGE_TYPES
    if page_type not in VALID_PAGE_TYPES:
        logger.warning(f"Invalid page_type '{page_type}', defaulting to 'unknown'")
        page_type = "unknown"

    def format_suggestion_response(result):
        return {
            "suggestions": [
                {
                    "id": f"suggestion-{i}",
                    "text": s.text,
                    "source": s.source,
                    "priority": s.priority,
                    "confidence": s.confidence,
                    "metadata": s.metadata
                }
                for i, s in enumerate(result.suggestions)
            ],
            "is_personalized": result.is_personalized,
            "fallback_reason": result.fallback_reason,
            "page_type": result.page_type
        }

    try:
        result = await suggestion_orchestrator.get_initial_suggestions(
            user_id=user_id,
            page_type=page_type,
            session_id=session_id
        )
        return format_suggestion_response(result)
    except Exception as e:
        logger.error(f"Error getting personalized suggestions: {e}", exc_info=True)
        result = suggestion_orchestrator._static_fallback(page_type, f"endpoint_error: {str(e)}")
        return format_suggestion_response(result)


class SearchRequest(PydanticBaseModel):
    """Request model for search."""
    query: str
    doc_type: Optional[str] = None
    top: int = 5


@app.post("/api/search")
async def search_documents(request: SearchRequest):
    """Search the knowledge base using semantic search."""
    try:
        search_service = get_search_service()
        results = search_service.search(
            query=request.query,
            doc_type=request.doc_type,
            top=request.top,
            use_semantic_search=True,
        )
        return results
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Snapshot Endpoints (Phase 3.3)
# =============================================================================

@app.post("/api/snapshots/capture")
async def capture_snapshot():
    """Manually trigger a daily snapshot capture."""
    try:
        from src.snapshot_service import snapshot_service
        snapshot = await snapshot_service.capture_daily_snapshot()
        return {"status": "success", "snapshot": snapshot}
    except Exception as e:
        logger.error(f"Error capturing snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/snapshots/{snapshot_id}")
async def get_snapshot(snapshot_id: str):
    """Get a specific snapshot by ID."""
    try:
        from src.snapshot_service import snapshot_service
        snapshot = await snapshot_service.get_snapshot_by_id(snapshot_id)
        if not snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        return snapshot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/snapshots/compare/{days_ago}")
async def compare_snapshots(days_ago: int = 7):
    """Compare current state with snapshot from N days ago."""
    try:
        from src.snapshot_service import snapshot_service

        current = await snapshot_service.capture_daily_snapshot()
        previous = await snapshot_service.get_snapshot(days_ago=days_ago)

        if not previous:
            return {
                "status": "partial",
                "message": f"No snapshot available from {days_ago} days ago",
                "current": current,
                "previous": None,
                "comparison": None,
            }

        comparison_text = snapshot_service.format_comparison(current, previous)

        return {
            "status": "success",
            "current": current,
            "previous": previous,
            "comparison": comparison_text,
            "days_compared": days_ago,
        }
    except Exception as e:
        logger.error(f"Error comparing snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/snapshots")
async def list_snapshots(limit: int = 30):
    """List recent snapshots."""
    try:
        from src.snapshot_service import snapshot_service
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=limit)

        snapshots = await snapshot_service.get_snapshots_range(start_date, end_date)
        return {"snapshots": snapshots, "count": len(snapshots)}
    except Exception as e:
        logger.error(f"Error listing snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/snapshots")
async def clear_snapshots():
    """Clear all snapshots (for resetting test data)."""
    try:
        from src.snapshot_service import snapshot_service

        deleted_count = await snapshot_service.clear_all_snapshots()
        logger.info(f"Cleared {deleted_count} snapshots")
        return {"status": "success", "deleted_count": deleted_count}
    except Exception as e:
        logger.error(f"Error clearing snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
