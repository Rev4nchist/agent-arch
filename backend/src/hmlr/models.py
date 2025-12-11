"""HMLR Data Models.

Pydantic models for the HMLR memory system components.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
from enum import Enum


class BlockStatus(str, Enum):
    """Bridge Block status states."""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"


class MemoryType(str, Enum):
    """Memory types for vector index."""
    FACT = "fact"
    BLOCK_SUMMARY = "block_summary"


class FactCategory(str, Enum):
    """Fact classification categories."""
    DEFINITION = "Definition"
    ACRONYM = "Acronym"
    SECRET = "Secret"
    ENTITY = "Entity"


class RoutingScenario(int, Enum):
    """Governor routing scenarios (from HMLR)."""
    TOPIC_CONTINUATION = 1  # Same block, continue conversation
    TOPIC_RESUMPTION = 2    # Reactivate paused block
    NEW_TOPIC_FIRST = 3     # First topic today (no active blocks)
    TOPIC_SHIFT = 4         # New topic, pause current block


class Turn(BaseModel):
    """Single conversation turn within a Bridge Block."""
    index: int
    query: str
    response_summary: str
    intent: Optional[str] = None
    entities: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BridgeBlock(BaseModel):
    """Bridge Block - Topic-based conversation unit (per-session).

    Bridge Blocks organize conversations by topic within a session.
    Only ONE block can be ACTIVE at a time; others are PAUSED.
    """
    id: str
    session_id: str
    user_id: str
    topic_label: str
    summary: str = ""
    keywords: List[str] = Field(default_factory=list)
    turns: List[Turn] = Field(default_factory=list)
    open_loops: List[str] = Field(default_factory=list)
    decisions_made: List[str] = Field(default_factory=list)
    status: BlockStatus = BlockStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class Fact(BaseModel):
    """Extracted fact with provenance (per-user, persistent).

    Facts are hard information extracted from conversations:
    - Definitions: "X is Y"
    - Acronyms: "API stands for Application Programming Interface"
    - Entities: "David owns the backend service"
    - Secrets: User preferences, rules, credentials
    """
    fact_id: Optional[int] = None
    user_id: str
    key: str
    value: str
    category: FactCategory
    source_block_id: Optional[str] = None
    source_chunk_id: Optional[str] = None
    evidence_snippet: Optional[str] = None
    confidence: float = 1.0
    verified: bool = False
    created_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class UserProfile(BaseModel):
    """User profile built over time (per-user, persistent).

    Tracks user preferences, common queries, known entities,
    and interaction patterns for personalization.
    """
    user_id: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    common_queries: List[str] = Field(default_factory=list)
    known_entities: List[Dict[str, str]] = Field(default_factory=list)
    interaction_patterns: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class GovernorDecision(BaseModel):
    """Routing decision from the Governor.

    Contains the selected scenario, target block, and retrieved context.
    """
    scenario: RoutingScenario
    matched_block_id: Optional[str] = None
    is_new_topic: bool = False
    suggested_label: str = ""
    active_block: Optional[BridgeBlock] = None
    relevant_facts: List[Fact] = Field(default_factory=list)
    memories: List[Dict[str, Any]] = Field(default_factory=list)
    topic_similarity: float = 0.0

    class Config:
        use_enum_values = True


class HydratedContext(BaseModel):
    """Assembled context for LLM prompts.

    Output of the Hydrator, ready to be prepended to the AI query.
    """
    block_summary: str = ""
    block_history: str = ""
    relevant_facts_text: str = ""
    user_preferences_text: str = ""
    open_loops_text: str = ""
    full_context: str = ""
    token_estimate: int = 0


class FactExtractionResult(BaseModel):
    """Result of fact extraction from a message."""
    facts: List[Fact] = Field(default_factory=list)
    extraction_method: str = "llm"
    processing_time_ms: int = 0


class ScribeUpdate(BaseModel):
    """Profile update from the Scribe agent."""
    user_id: str
    updates: Dict[str, Any]
    source_block_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CandidateMemory(BaseModel):
    """Candidate memory from LatticeCrawler vector search.

    Represents a raw candidate retrieved via semantic search (Key 1),
    before Governor applies contextual filtering (Key 2).
    """
    id: str
    user_id: str
    content: str
    memory_type: MemoryType
    source_id: str
    score: float
    category: Optional[str] = None
    topic_label: Optional[str] = None
    confidence: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        use_enum_values = True
