"""Data models for the application."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MeetingType(str, Enum):
    """Meeting type enum."""

    GOVERNANCE = "Governance"
    AI_ARCHITECT = "AI Architect"
    LICENSING = "Licensing"
    TECHNICAL = "Technical"
    REVIEW = "Review"


class MeetingStatus(str, Enum):
    """Meeting status enum."""

    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class TaskStatus(str, Enum):
    """Task status enum."""

    PENDING = "Pending"
    IN_PROGRESS = "In-Progress"
    DONE = "Done"
    BLOCKED = "Blocked"
    DEFERRED = "Deferred"


class TaskPriority(str, Enum):
    """Task priority enum."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TaskCategory(str, Enum):
    """Task category enum - aligned with ProposalCategory."""

    AGENT = "Agent"
    GOVERNANCE = "Governance"
    TECHNICAL = "Technical"
    LICENSING = "Licensing"
    AI_ARCHITECT = "AI Architect"


class AgentTier(str, Enum):
    """Agent tier enum."""

    TIER1_INDIVIDUAL = "Tier1_Individual"
    TIER2_DEPARTMENT = "Tier2_Department"
    TIER3_ENTERPRISE = "Tier3_Enterprise"


class AgentStatus(str, Enum):
    """Agent status enum."""

    IDEA = "Idea"
    DESIGN = "Design"
    DEVELOPMENT = "Development"
    TESTING = "Testing"
    STAGING = "Staging"
    PRODUCTION = "Production"
    DEPRECATED = "Deprecated"


class IntegrationStatus(str, Enum):
    """Agent integration status enum for tracking system integration state."""

    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    PARTIALLY_INTEGRATED = "Partially Integrated"
    FULLY_INTEGRATED = "Fully Integrated"
    INTEGRATION_ISSUES = "Integration Issues"


class ChecklistItem(BaseModel):
    """Pre-work checklist item."""

    item: str
    completed: bool = False


class Meeting(BaseModel):
    """Meeting data model."""

    id: Optional[str] = None
    title: str
    date: datetime
    type: MeetingType
    facilitator: str
    attendees: List[str]
    agenda: Optional[str] = None
    transcript_url: Optional[str] = None
    transcript_text: Optional[str] = None
    summary: Optional[str] = None  # AI-generated meeting summary
    pre_work_checklist: List[ChecklistItem] = []
    decisions: List[str] = []  # List of decision IDs
    action_items: List[str] = []  # List of task IDs
    topics: List[str] = []  # AI-extracted topics
    status: MeetingStatus = MeetingStatus.SCHEDULED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskComplexity(str, Enum):
    """Task complexity level for learning/onboarding queries."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Task(BaseModel):
    """Task data model."""

    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    category: Optional[TaskCategory] = TaskCategory.GOVERNANCE
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    created_from_meeting: Optional[str] = None  # Meeting ID
    related_agent: Optional[str] = None  # Agent ID
    dependencies: List[str] = []  # List of task IDs
    notes: Optional[str] = None
    # Phase 2.1: Learning/starter task fields
    complexity: Optional[TaskComplexity] = None
    learning_friendly: bool = False
    skills_required: List[str] = []
    # Phase 2.3: Owner/contact fields
    owner_name: Optional[str] = None
    owner_contact: Optional[str] = None  # email or slack handle
    team: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Agent(BaseModel):
    """Agent data model."""

    id: Optional[str] = None
    name: str
    description: str
    tier: AgentTier
    status: AgentStatus = AgentStatus.IDEA
    integration_status: Optional[IntegrationStatus] = IntegrationStatus.NOT_STARTED
    owner: str
    department: Optional[str] = None
    data_sources: List[str] = []
    use_case: Optional[str] = None
    integration_notes: Optional[str] = None
    related_tasks: List[str] = []  # List of task IDs
    # Phase 2.2: Timeline/deployment fields
    target_deployment_date: Optional[datetime] = None
    deployment_blockers: List[str] = []
    next_milestone: Optional[str] = None
    # Phase 2.3: Owner/contact fields
    owner_contact: Optional[str] = None  # email or slack handle
    team: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProposalStatus(str, Enum):
    """Proposal status enum."""

    PROPOSED = "Proposed"
    REVIEWING = "Reviewing"
    AGREED = "Agreed"
    DEFERRED = "Deferred"


class ProposalCategory(str, Enum):
    """Proposal category enum."""

    AGENT = "Agent"
    GOVERNANCE = "Governance"
    TECHNICAL = "Technical"
    LICENSING = "Licensing"
    AI_ARCHITECT = "AI Architect"


class Proposal(BaseModel):
    """Proposal data model."""

    id: Optional[str] = None
    title: str
    description: str
    category: ProposalCategory
    status: ProposalStatus = ProposalStatus.PROPOSED
    proposer: str
    department: str
    team_member: Optional[str] = None
    rationale: Optional[str] = None
    impact: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProposalUpdate(BaseModel):
    """Proposal partial update model - all fields optional for PATCH."""

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ProposalCategory] = None
    status: Optional[ProposalStatus] = None
    proposer: Optional[str] = None
    department: Optional[str] = None
    team_member: Optional[str] = None
    rationale: Optional[str] = None
    impact: Optional[str] = None


class DecisionCategory(str, Enum):
    """Decision category enum."""

    GOVERNANCE = "Governance"
    ARCHITECTURE = "Architecture"
    LICENSING = "Licensing"
    BUDGET = "Budget"
    SECURITY = "Security"


class Decision(BaseModel):
    """Decision data model."""

    id: Optional[str] = None
    title: str
    description: str
    category: DecisionCategory
    decision_date: datetime
    decision_maker: str
    rationale: Optional[str] = None
    impact: Optional[str] = None
    meeting: Optional[str] = None  # Meeting ID
    proposal_id: Optional[str] = None  # Proposal ID
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ResourceType(str, Enum):
    """Resource type enum."""

    PDF = "PDF"
    DOCUMENT = "Document"
    LINK = "Link"
    VIDEO = "Video"
    IMAGE = "Image"


class ResourceCategory(str, Enum):
    """Resource category enum."""

    AGENT = "Agent"
    GOVERNANCE = "Governance"
    TECHNICAL = "Technical"
    LICENSING = "Licensing"
    AI_ARCHITECT = "AI Architect"
    ARCHITECTURE = "Architecture"
    BUDGET = "Budget"
    SECURITY = "Security"


class Resource(BaseModel):
    """Educational resource data model."""

    id: Optional[str] = None
    type: ResourceType
    title: str
    description: Optional[str] = None
    category: ResourceCategory
    tags: List[str] = []

    # Document fields
    file_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    blob_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_text: Optional[str] = None
    page_count: Optional[int] = None

    # Link fields
    url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None

    # Metadata
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    view_count: int = 0
    related_resources: List[str] = []


class TechRadarCategory(str, Enum):
    """Tech radar category enum."""

    ADOPT = "Adopt"
    TRIAL = "Trial"
    ASSESS = "Assess"
    HOLD = "Hold"


class TechRadarItem(BaseModel):
    """Tech radar item data model."""

    id: Optional[str] = None
    tool_name: str
    category: TechRadarCategory
    description: str
    status: str
    recommendation: Optional[str] = None
    docs_link: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PatternType(str, Enum):
    """Code pattern type enum."""

    CODE_FIRST = "Code-First"
    LOW_CODE = "Low-Code"


class CodePattern(BaseModel):
    """Code pattern data model."""

    id: Optional[str] = None
    title: str
    pattern_type: PatternType
    language: Optional[str] = None
    description: str
    code_snippet: str
    use_case: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AzureResource(BaseModel):
    """Azure resource data model."""

    id: Optional[str] = None
    name: str
    type: str
    location: str
    resource_group: str
    tags: dict = Field(default_factory=dict)
    properties: Optional[dict] = None
    current_month_cost: Optional[float] = None
    status: Optional[str] = None


class AzureResourceSummary(BaseModel):
    """Azure resource summary statistics."""

    total_resources: int
    running_services: int
    regions: int
    resource_groups: int
    total_cost: Optional[float] = None


# Request/Response models
class TranscriptProcessRequest(BaseModel):
    """Request model for transcript processing."""

    transcript_text: str
    meeting_id: Optional[str] = None


class TranscriptProcessResponse(BaseModel):
    """Response model for transcript processing."""

    action_items: List[Task]
    decisions: List[Decision]


class PageContext(BaseModel):
    """Context about the current page state in the frontend."""

    current_page: Optional[str] = None
    selected_ids: List[str] = []
    active_filters: dict = Field(default_factory=dict)
    visible_entity_type: Optional[str] = None


class AgentQueryRequest(BaseModel):
    """Request model for agent query."""

    query: str
    context: Optional[str] = None
    page_context: Optional[PageContext] = None
    session_id: Optional[str] = None  # Phase 5.2: Session-based conversation memory


class ActionSuggestion(BaseModel):
    """Suggested follow-up action."""

    label: str
    action_type: str
    params: dict = Field(default_factory=dict)


class DataBasis(BaseModel):
    """Metadata about the data used to generate a response."""

    items_shown: int = 0
    total_items: int = 0
    entity_types: List[str] = []


class AgentQueryResponse(BaseModel):
    """Response model for agent query."""

    response: str
    sources: List[str] = []
    intent: Optional[str] = None
    confidence: Optional[str] = None
    suggestions: List[ActionSuggestion] = []
    data_basis: Optional[DataBasis] = None


class AuditAction(str, Enum):
    """Audit action type enum."""

    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"


class AuditEntityType(str, Enum):
    """Auditable entity type enum."""

    TASK = "task"
    AGENT = "agent"
    MEETING = "meeting"
    DECISION = "decision"
    PROPOSAL = "proposal"
    RESOURCE = "resource"
    TECH_RADAR = "tech_radar"
    CODE_PATTERN = "code_pattern"


class AuditLog(BaseModel):
    """Audit log entry data model."""

    id: Optional[str] = None
    user_id: str
    user_name: Optional[str] = None
    action: AuditAction
    entity_type: AuditEntityType
    entity_id: str
    entity_title: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[dict] = None
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None


class AuditLogQueryParams(BaseModel):
    """Query parameters for audit log retrieval."""

    user_id: Optional[str] = None
    entity_type: Optional[AuditEntityType] = None
    entity_id: Optional[str] = None
    action: Optional[AuditAction] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0
