"""Suggestion Models for HMLR-driven personalization."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class SuggestionSource(str, Enum):
    STATIC = "static"
    INTENT = "intent"
    OPEN_LOOP = "open_loop"
    COMMON_QUERY = "common_query"
    TOPIC_INTEREST = "topic_interest"
    ENTITY = "entity"
    CONTEXT = "context"


class PersonalizedSuggestion(BaseModel):
    text: str
    source: SuggestionSource
    priority: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class SuggestionData(BaseModel):
    open_loops: List[Dict[str, Any]] = Field(default_factory=list)
    common_queries: List[str] = Field(default_factory=list)
    topic_interests: List[str] = Field(default_factory=list)
    known_entities: List[Dict[str, str]] = Field(default_factory=list)
    expertise_level: str = "intermediate"
    recent_topics: List[str] = Field(default_factory=list)
    relevant_facts: List[Dict[str, Any]] = Field(default_factory=list)


class SuggestionResponse(BaseModel):
    suggestions: List[PersonalizedSuggestion]
    is_personalized: bool = False
    fallback_reason: Optional[str] = None
    user_id: Optional[str] = None
    page_type: str = "unknown"
