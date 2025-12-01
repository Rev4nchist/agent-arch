"""Add Proposal model and update Decision model."""
import re

with open('src/models.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Proposal enums and model before DecisionCategory
proposal_models = '''class ProposalStatus(str, Enum):
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

    id: str
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


'''

# Insert Proposal models before DecisionCategory
content = content.replace(
    'class DecisionCategory(str, Enum):',
    proposal_models + 'class DecisionCategory(str, Enum):'
)

# Update Decision model to add impact and proposal_id fields
old_decision = '''class Decision(BaseModel):
    """Decision data model."""

    id: str
    title: str
    description: str
    category: DecisionCategory
    decision_date: datetime
    decision_maker: str
    rationale: Optional[str] = None
    meeting: Optional[str] = None  # Meeting ID
    created_at: datetime = Field(default_factory=datetime.utcnow)'''

new_decision = '''class Decision(BaseModel):
    """Decision data model."""

    id: str
    title: str
    description: str
    category: DecisionCategory
    decision_date: datetime
    decision_maker: str
    rationale: Optional[str] = None
    impact: Optional[str] = None
    meeting: Optional[str] = None  # Meeting ID
    proposal_id: Optional[str] = None  # Proposal ID
    created_at: datetime = Field(default_factory=datetime.utcnow)'''

content = content.replace(old_decision, new_decision)

with open('src/models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added Proposal model and updated Decision model")
