"""HMLR (Hierarchical Memory Lookup & Routing) Service Module.

This module implements a persistent memory system for the Azure Agent,
inspired by the HMLR-Agentic-AI-Memory-System architecture.

Components:
- Governor: Routes conversations using 4 scenarios (continue, resume, new, shift)
- BridgeBlockManager: Topic-based conversation organization (Cosmos DB)
- FactScrubber: Extracts hard facts from conversations (Azure SQL)
- Hydrator: Assembles context for LLM prompts
- Scribe: Async user profile updates
- LatticeCrawler: Vector search for semantic memory retrieval (Azure AI Search)
- HMLRService: Main orchestrator

Memory Scope:
- Bridge Blocks: Per-Session (conversation flow resets each session)
- Facts: Per-User (entities/relationships persist forever)
- User Profiles: Per-User (preferences build over time)
- Lattice Index: Per-User (semantic search over facts + block summaries)
"""

from src.hmlr.models import (
    BridgeBlock,
    Fact,
    UserProfile,
    GovernorDecision,
    HydratedContext,
    Turn,
    CandidateMemory,
    MemoryType,
)
from src.hmlr.service import HMLRService
from src.hmlr.lattice_crawler import LatticeCrawler, get_lattice_crawler, initialize_lattice
from src.hmlr.suggestion_models import (
    SuggestionSource,
    PersonalizedSuggestion,
    SuggestionData,
    SuggestionResponse
)
from src.hmlr.suggestion_orchestrator import SuggestionOrchestrator
from src.hmlr.memory_accessor import HMLRMemoryAccessor

__all__ = [
    "HMLRService",
    "BridgeBlock",
    "Fact",
    "UserProfile",
    "GovernorDecision",
    "HydratedContext",
    "Turn",
    "CandidateMemory",
    "MemoryType",
    "LatticeCrawler",
    "get_lattice_crawler",
    "initialize_lattice",
    "SuggestionSource",
    "PersonalizedSuggestion",
    "SuggestionData",
    "SuggestionResponse",
    "SuggestionOrchestrator",
    "HMLRMemoryAccessor"
]
