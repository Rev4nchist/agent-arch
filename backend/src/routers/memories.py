"""User Memories Router for HMLR data management."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging

from src.hmlr.sql_client import HMLRSQLClient
from src.hmlr.bridge_block_mgr import BridgeBlockManager
from src.hmlr.models import Fact, UserProfile, BridgeBlock, FactCategory
from src.config import settings

logger = logging.getLogger(__name__)

# In-memory fallback for demo mode when SQL is unavailable
_demo_facts_store: Dict[str, List[Dict[str, Any]]] = {}
_demo_mode_enabled = False

router = APIRouter(prefix="/api/memories", tags=["memories"])


class MemorySummary(BaseModel):
    total_facts: int
    verified_facts: int
    active_topics: int
    open_loops: int


class FactResponse(BaseModel):
    fact_id: int
    key: str
    value: str
    category: str
    confidence: float
    verified: bool
    evidence_snippet: Optional[str] = None
    created_at: Optional[str] = None


class FactsListResponse(BaseModel):
    facts: List[FactResponse]
    total: int


class TopicSummary(BaseModel):
    id: str
    session_id: str
    topic_label: str
    status: str
    turn_count: int
    open_loops: List[str]
    last_activity: str


class TopicDetail(BaseModel):
    id: str
    session_id: str
    topic_label: str
    summary: str
    status: str
    keywords: List[str]
    open_loops: List[str]
    decisions_made: List[str]
    turn_count: int
    turns: List[Dict[str, Any]]
    created_at: str
    last_activity: str


class TopicsListResponse(BaseModel):
    topics: List[TopicSummary]
    total: int


class ProfileResponse(BaseModel):
    user_id: str
    preferences: Dict[str, Any]
    common_queries: List[str]
    known_entities: List[Dict[str, str]]
    interaction_patterns: Dict[str, Any]
    last_updated: Optional[str] = None


class PreferencesUpdate(BaseModel):
    preferences: Dict[str, Any]


def _get_sql_client() -> HMLRSQLClient:
    return HMLRSQLClient()


def _get_block_manager() -> BridgeBlockManager:
    return BridgeBlockManager()


@router.get("/summary", response_model=MemorySummary)
async def get_memory_summary(user_id: str = Query(..., description="User ID")):
    global _demo_mode_enabled
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    # Try SQL first, fall back to demo mode
    try:
        sql_client = _get_sql_client()
        block_manager = _get_block_manager()

        try:
            facts = await sql_client.get_facts_by_user(user_id, limit=500)
            blocks = await block_manager.get_user_blocks(user_id, limit=100)

            total_open_loops = sum(len(b.open_loops) for b in blocks)
            active_topics = len([b for b in blocks if b.status == "ACTIVE"])

            return MemorySummary(
                total_facts=len(facts),
                verified_facts=len([f for f in facts if f.verified]),
                active_topics=active_topics,
                open_loops=total_open_loops
            )
        finally:
            sql_client.close()
    except Exception as e:
        logger.warning(f"SQL unavailable, using demo mode: {e}")
        _demo_mode_enabled = True
        user_facts = _demo_facts_store.get(user_id, [])
        return MemorySummary(
            total_facts=len(user_facts),
            verified_facts=len([f for f in user_facts if f.get("verified", False)]),
            active_topics=1,
            open_loops=10
        )


@router.get("/facts", response_model=FactsListResponse)
async def get_facts(
    user_id: str = Query(..., description="User ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in key/value"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    global _demo_mode_enabled
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    # Try SQL first, fall back to demo mode
    try:
        sql_client = _get_sql_client()

        try:
            if search:
                facts = await sql_client.search_facts(user_id, search.split(), limit=limit + offset)
            else:
                facts = await sql_client.get_facts_by_user(user_id, limit=limit + offset)

            if category:
                facts = [f for f in facts if f.category == category]

            total = len(facts)
            facts = facts[offset:offset + limit]

            return FactsListResponse(
                facts=[
                    FactResponse(
                        fact_id=f.fact_id or 0,
                        key=f.key,
                        value=f.value,
                        category=f.category if isinstance(f.category, str) else f.category.value,
                        confidence=f.confidence,
                        verified=f.verified,
                        evidence_snippet=f.evidence_snippet,
                        created_at=f.created_at.isoformat() if f.created_at else None
                    )
                    for f in facts
                ],
                total=total
            )
        finally:
            sql_client.close()
    except Exception as e:
        logger.warning(f"SQL unavailable for facts, using demo mode: {e}")
        _demo_mode_enabled = True
        user_facts = _demo_facts_store.get(user_id, [])

        if category:
            user_facts = [f for f in user_facts if f.get("category") == category]
        if search:
            search_lower = search.lower()
            user_facts = [f for f in user_facts if search_lower in f.get("key", "").lower() or search_lower in f.get("value", "").lower()]

        total = len(user_facts)
        user_facts = user_facts[offset:offset + limit]

        return FactsListResponse(
            facts=[
                FactResponse(
                    fact_id=f.get("fact_id", idx),
                    key=f.get("key", ""),
                    value=f.get("value", ""),
                    category=f.get("category", "GENERAL"),
                    confidence=f.get("confidence", 0.9),
                    verified=f.get("verified", False),
                    evidence_snippet=f.get("evidence_snippet"),
                    created_at=f.get("created_at")
                )
                for idx, f in enumerate(user_facts)
            ],
            total=total
        )


class FactCreate(BaseModel):
    key: str
    value: str
    category: str = "GENERAL"
    confidence: float = 0.9
    verified: bool = False
    evidence_snippet: Optional[str] = None


@router.post("/facts", response_model=FactResponse)
async def create_fact(
    fact_data: FactCreate,
    user_id: str = Query(..., description="User ID")
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    sql_client = _get_sql_client()

    try:
        fact = Fact(
            user_id=user_id,
            key=fact_data.key,
            value=fact_data.value,
            category=fact_data.category,
            confidence=fact_data.confidence,
            verified=fact_data.verified,
            evidence_snippet=fact_data.evidence_snippet
        )
        fact_id = await sql_client.save_fact(fact)
        return FactResponse(
            fact_id=fact_id,
            key=fact_data.key,
            value=fact_data.value,
            category=fact_data.category,
            confidence=fact_data.confidence,
            verified=fact_data.verified,
            evidence_snippet=fact_data.evidence_snippet
        )
    finally:
        sql_client.close()


@router.post("/seed-demo")
async def seed_demo_facts(user_id: str = Query(..., description="User ID")):
    """Seed demo facts for platform showcase. Falls back to in-memory if SQL unavailable."""
    global _demo_mode_enabled
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    # Valid categories: Definition, Acronym, Secret, Entity
    demo_facts = [
        {"fact_id": 1, "key": "Tech Stack", "value": "React 19, TypeScript, Next.js 16, Tailwind CSS", "category": "Definition", "confidence": 1.0, "verified": True},
        {"fact_id": 2, "key": "Backend Framework", "value": "FastAPI with Python 3.11, async/await patterns", "category": "Definition", "confidence": 1.0, "verified": True},
        {"fact_id": 3, "key": "Database", "value": "Azure Cosmos DB for documents, Azure SQL for structured data", "category": "Definition", "confidence": 1.0, "verified": True},
        {"fact_id": 4, "key": "Deployment", "value": "Azure Static Web Apps (frontend), Azure Container Apps (backend)", "category": "Definition", "confidence": 1.0, "verified": True},
        {"fact_id": 5, "key": "Fourth AI", "value": "Agent Architecture Platform for intelligent workflow automation", "category": "Entity", "confidence": 1.0, "verified": True},
        {"fact_id": 6, "key": "David Hayes", "value": "Platform Architect and Lead Developer", "category": "Entity", "confidence": 0.95, "verified": True},
        {"fact_id": 7, "key": "Claude Code", "value": "AI-powered coding assistant from Anthropic", "category": "Entity", "confidence": 0.9, "verified": False},
        {"fact_id": 8, "key": "HMLR", "value": "Hierarchical Memory with Linked Retrieval - the memory system powering this platform", "category": "Acronym", "confidence": 1.0, "verified": True},
        {"fact_id": 9, "key": "SWA", "value": "Azure Static Web Apps - serverless hosting for frontend", "category": "Acronym", "confidence": 1.0, "verified": True},
        {"fact_id": 10, "key": "ACA", "value": "Azure Container Apps - managed container hosting for backend", "category": "Acronym", "confidence": 1.0, "verified": True},
        {"fact_id": 11, "key": "MSAL", "value": "Microsoft Authentication Library for Azure AD integration", "category": "Acronym", "confidence": 0.95, "verified": True},
        {"fact_id": 12, "key": "API Key", "value": "dev-test-key-123 (development environment only)", "category": "Secret", "confidence": 1.0, "verified": True},
    ]

    # Try SQL first
    try:
        sql_client = _get_sql_client()
        created = 0

        try:
            for fd in demo_facts:
                fact = Fact(
                    user_id=user_id,
                    key=fd["key"],
                    value=fd["value"],
                    category=fd["category"],
                    confidence=fd["confidence"],
                    verified=fd["verified"]
                )
                await sql_client.save_fact(fact)
                created += 1
            return {"success": True, "facts_created": created, "mode": "sql"}
        finally:
            sql_client.close()
    except Exception as e:
        # Fall back to in-memory store
        logger.warning(f"SQL unavailable for seeding, using in-memory: {e}")
        _demo_mode_enabled = True
        _demo_facts_store[user_id] = demo_facts
        return {"success": True, "facts_created": len(demo_facts), "mode": "in-memory"}


@router.put("/facts/{fact_id}/verify")
async def verify_fact(
    fact_id: int,
    user_id: str = Query(..., description="User ID for authorization")
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    sql_client = _get_sql_client()

    try:
        success = await sql_client.verify_fact(fact_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Fact not found or unauthorized")
        return {"success": True, "fact_id": fact_id, "verified": True}
    finally:
        sql_client.close()


@router.delete("/facts/{fact_id}")
async def delete_fact(
    fact_id: int,
    user_id: str = Query(..., description="User ID for authorization")
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    sql_client = _get_sql_client()

    try:
        success = await sql_client.delete_fact_for_user(fact_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Fact not found or unauthorized")
        return {"success": True, "fact_id": fact_id}
    finally:
        sql_client.close()


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user_id: str = Query(..., description="User ID")):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    sql_client = _get_sql_client()

    try:
        profile = await sql_client.get_user_profile(user_id)
        if not profile:
            return ProfileResponse(
                user_id=user_id,
                preferences={},
                common_queries=[],
                known_entities=[],
                interaction_patterns={}
            )

        return ProfileResponse(
            user_id=profile.user_id,
            preferences=profile.preferences,
            common_queries=profile.common_queries,
            known_entities=profile.known_entities,
            interaction_patterns=profile.interaction_patterns,
            last_updated=profile.last_updated.isoformat() if profile.last_updated else None
        )
    finally:
        sql_client.close()


@router.patch("/profile/preferences")
async def update_preferences(
    update: PreferencesUpdate,
    user_id: str = Query(..., description="User ID")
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    sql_client = _get_sql_client()

    try:
        success = await sql_client.update_profile_field(user_id, "preferences", update.preferences)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        return {"success": True}
    finally:
        sql_client.close()


@router.delete("/profile/common-queries/{idx}")
async def delete_common_query(
    idx: int,
    user_id: str = Query(..., description="User ID")
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    sql_client = _get_sql_client()

    try:
        profile = await sql_client.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        if idx < 0 or idx >= len(profile.common_queries):
            raise HTTPException(status_code=400, detail="Invalid index")

        profile.common_queries.pop(idx)
        success = await sql_client.save_user_profile(profile)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        return {"success": True}
    finally:
        sql_client.close()


@router.delete("/profile/known-entities/{idx}")
async def delete_known_entity(
    idx: int,
    user_id: str = Query(..., description="User ID")
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    sql_client = _get_sql_client()

    try:
        profile = await sql_client.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        if idx < 0 or idx >= len(profile.known_entities):
            raise HTTPException(status_code=400, detail="Invalid index")

        profile.known_entities.pop(idx)
        success = await sql_client.save_user_profile(profile)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        return {"success": True}
    finally:
        sql_client.close()


@router.get("/topics", response_model=TopicsListResponse)
async def get_topics(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    block_manager = _get_block_manager()

    try:
        blocks = await block_manager.get_user_blocks(user_id, limit=limit + offset)
        total = len(blocks)
        blocks = blocks[offset:offset + limit]

        return TopicsListResponse(
            topics=[
                TopicSummary(
                    id=b.id,
                    session_id=b.session_id,
                    topic_label=b.topic_label,
                    status=b.status if isinstance(b.status, str) else b.status.value,
                    turn_count=len(b.turns),
                    open_loops=b.open_loops,
                    last_activity=b.last_activity.isoformat() if b.last_activity else ""
                )
                for b in blocks
            ],
            total=total
        )
    except Exception as e:
        logger.error(f"Failed to get topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics/{topic_id}", response_model=TopicDetail)
async def get_topic_detail(
    topic_id: str,
    session_id: str = Query(..., description="Session ID (partition key)")
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    block_manager = _get_block_manager()

    try:
        block = await block_manager.get_block(topic_id, session_id)
        if not block:
            raise HTTPException(status_code=404, detail="Topic not found")

        return TopicDetail(
            id=block.id,
            session_id=block.session_id,
            topic_label=block.topic_label,
            summary=block.summary,
            status=block.status if isinstance(block.status, str) else block.status.value,
            keywords=block.keywords,
            open_loops=block.open_loops,
            decisions_made=block.decisions_made,
            turn_count=len(block.turns),
            turns=[
                {
                    "index": t.index,
                    "query": t.query,
                    "response_summary": t.response_summary,
                    "intent": t.intent,
                    "entities": t.entities,
                    "timestamp": t.timestamp.isoformat() if t.timestamp else None
                }
                for t in block.turns
            ],
            created_at=block.created_at.isoformat() if block.created_at else "",
            last_activity=block.last_activity.isoformat() if block.last_activity else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get topic detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/topics/{topic_id}/open-loops/{idx}")
async def delete_open_loop(
    topic_id: str,
    idx: int,
    session_id: str = Query(..., description="Session ID (partition key)")
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

    block_manager = _get_block_manager()

    try:
        block = await block_manager.get_block(topic_id, session_id)
        if not block:
            raise HTTPException(status_code=404, detail="Topic not found")

        if idx < 0 or idx >= len(block.open_loops):
            raise HTTPException(status_code=400, detail="Invalid index")

        block.open_loops.pop(idx)
        result = await block_manager.update_block(topic_id, session_id, {"open_loops": block.open_loops})
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update topic")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete open loop: {e}")
        raise HTTPException(status_code=500, detail=str(e))
