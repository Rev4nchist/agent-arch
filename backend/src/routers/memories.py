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
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

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


@router.get("/facts", response_model=FactsListResponse)
async def get_facts(
    user_id: str = Query(..., description="User ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in key/value"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    if not settings.hmlr_enabled:
        raise HTTPException(status_code=503, detail="HMLR not enabled")

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
