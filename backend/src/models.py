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
    # Feedback integration
    from_submission_id: Optional[str] = None  # Submission ID if created from feedback
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


class SubmissionCategory(str, Enum):
    """Submission category enum."""

    BUG_REPORT = "Bug Report"
    FEATURE_REQUEST = "Feature Request"
    IMPROVEMENT_IDEA = "Improvement Idea"
    QUESTION = "Question"


class SubmissionStatus(str, Enum):
    """Submission status enum."""

    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DECLINED = "Declined"


class SubmissionPriority(str, Enum):
    """Submission priority enum."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class SubmissionComment(BaseModel):
    """Comment on a submission."""

    id: str
    user: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class Submission(BaseModel):
    """Internal ticketing/idea submission data model."""

    id: Optional[str] = None
    title: str
    description: str
    category: SubmissionCategory
    priority: SubmissionPriority
    status: SubmissionStatus = SubmissionStatus.SUBMITTED
    submitted_by: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    upvotes: List[str] = []
    upvote_count: int = 0
    comments: List[SubmissionComment] = []
    assigned_to: Optional[str] = None
    tags: List[str] = []
    linked_task_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionCreate(BaseModel):
    """Request model for creating a submission."""

    title: str
    description: str
    category: SubmissionCategory
    priority: SubmissionPriority
    submitted_by: str
    tags: List[str] = []


class SubmissionUpdate(BaseModel):
    """Request model for updating a submission (admin)."""

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[SubmissionCategory] = None
    priority: Optional[SubmissionPriority] = None
    status: Optional[SubmissionStatus] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    resolution_notes: Optional[str] = None


class CommentCreate(BaseModel):
    """Request model for creating a comment."""

    user: str
    content: str


class SubmissionStats(BaseModel):
    """Dashboard statistics for submissions."""

    total: int = 0
    by_status: dict = Field(default_factory=dict)
    by_category: dict = Field(default_factory=dict)
    by_priority: dict = Field(default_factory=dict)


class PlatformDocCategory(str, Enum):
    """Platform documentation category enum."""

    NAVIGATION = "navigation"
    FEATURE = "feature"
    WORKFLOW = "workflow"
    FAQ = "faq"


class PlatformDoc(BaseModel):
    """Platform documentation for AI Guide context."""

    id: Optional[str] = None
    category: PlatformDocCategory
    title: str
    content: str
    keywords: List[str] = []
    related_features: List[str] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlatformDocCreate(BaseModel):
    """Request model for creating platform documentation."""

    category: PlatformDocCategory
    title: str
    content: str
    keywords: List[str] = []
    related_features: List[str] = []


class PlatformDocUpdate(BaseModel):
    """Request model for updating platform documentation."""

    category: Optional[PlatformDocCategory] = None
    title: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[List[str]] = None
    related_features: Optional[List[str]] = None


class QueryIntent(str, Enum):
    """Query intent classification for AI Guide."""

    PLATFORM_HELP = "platform_help"
    DATA_QUERY = "data_query"
    NAVIGATION = "navigation"
    GENERAL = "general"


class ContextResult(BaseModel):
    """Result from context retrieval."""

    context: str
    sources: List[str] = []
    intent: QueryIntent = QueryIntent.GENERAL


class UserRole(str, Enum):
    """User role enum for access control."""

    ADMIN = "admin"
    USER = "user"


class UserStatus(str, Enum):
    """User status enum."""

    ACTIVE = "active"
    PENDING = "pending"
    DENIED = "denied"


class AccessRequestStatus(str, Enum):
    """Access request status enum."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class AllowedUser(BaseModel):
    """Allowed user for platform access control."""

    id: Optional[str] = None
    email: str
    name: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AllowedUserCreate(BaseModel):
    """Request model for creating an allowed user."""

    email: str
    name: str
    role: UserRole = UserRole.USER


class AllowedUserUpdate(BaseModel):
    """Request model for updating an allowed user."""

    name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class AccessRequest(BaseModel):
    """Access request for users requesting platform access."""

    id: Optional[str] = None
    email: str
    name: str
    reason: Optional[str] = None
    status: AccessRequestStatus = AccessRequestStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AccessRequestCreate(BaseModel):
    """Request model for creating an access request."""

    email: str
    name: str
    reason: Optional[str] = None


class AccessVerifyResponse(BaseModel):
    """Response model for access verification."""

    authorized: bool
    role: Optional[str] = None
    user_id: Optional[str] = None
    name: Optional[str] = None


class BudgetCategory(str, Enum):
    """Budget category enum."""

    AZURE_SERVICE = "Azure Service"
    SOFTWARE_LICENSE = "Software License"
    CUSTOM_ALLOCATION = "Custom Allocation"


class BudgetStatus(str, Enum):
    """Budget status enum."""

    ON_TRACK = "On Track"
    WARNING = "Warning"
    CRITICAL = "Critical"
    EXCEEDED = "Exceeded"


class LicenseType(str, Enum):
    """License type enum."""

    SUBSCRIPTION = "Subscription"
    PAY_AS_YOU_GO = "Pay-as-you-go"
    PERPETUAL = "Perpetual"
    ENTERPRISE = "Enterprise"


class LicenseStatus(str, Enum):
    """License status enum."""

    ACTIVE = "Active"
    EXPIRING = "Expiring"
    EXPIRED = "Expired"
    SUSPENDED = "Suspended"


class Budget(BaseModel):
    """Budget allocation model."""

    id: Optional[str] = None
    name: str
    category: BudgetCategory
    resource_groups: List[str] = Field(default_factory=list)
    azure_service_type: Optional[str] = None
    amount: float
    spent: float = 0.0
    currency: str = "USD"
    period: str = "monthly"
    status: BudgetStatus = BudgetStatus.ON_TRACK
    threshold_warning: float = 75.0
    threshold_critical: float = 90.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    owner: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BudgetCreate(BaseModel):
    """Request model for creating a budget."""

    name: str
    category: BudgetCategory
    resource_groups: List[str] = Field(default_factory=list)
    azure_service_type: Optional[str] = None
    amount: float
    currency: str = "USD"
    period: str = "monthly"
    threshold_warning: float = 75.0
    threshold_critical: float = 90.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    owner: Optional[str] = None


class License(BaseModel):
    """Software license model."""

    id: Optional[str] = None
    name: str
    vendor: str
    license_type: LicenseType
    seats: Optional[int] = None
    cost_per_seat: Optional[float] = None
    monthly_cost: float
    annual_cost: Optional[float] = None
    renewal_date: Optional[datetime] = None
    status: LicenseStatus = LicenseStatus.ACTIVE
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LicenseCreate(BaseModel):
    """Request model for creating a license."""

    name: str
    vendor: str
    license_type: LicenseType
    seats: Optional[int] = None
    cost_per_seat: Optional[float] = None
    monthly_cost: float
    annual_cost: Optional[float] = None
    renewal_date: Optional[datetime] = None
    notes: Optional[str] = None


class CostSummary(BaseModel):
    """Cost summary model."""

    total_cost: float
    currency: str = "USD"
    resource_groups_count: int
    period: str
    period_start: str
    period_end: str
    by_resource_group: List[dict]
    top_services: List[dict]


class ResourceGroupCost(BaseModel):
    """Resource group cost model."""

    resource_group: str
    total_cost: float
    currency: str = "USD"
    services: List[dict]
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    error: Optional[str] = None
