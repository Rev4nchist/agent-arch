"""Audit log router for tracking and querying user actions."""
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
from src.audit_service import audit_service
from src.models import (
    AuditLog,
    AuditAction,
    AuditEntityType,
    AuditLogQueryParams,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/audit", tags=["audit"])


class AuditLogResponse:
    """Response wrapper for audit log queries."""
    pass


@router.get("", response_model=List[dict])
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by specific entity ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    start_date: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    limit: int = Query(100, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    Query audit logs with optional filters.

    - **user_id**: Filter logs by the user who performed the action
    - **entity_type**: Filter by entity (task, agent, meeting, decision, etc.)
    - **entity_id**: Filter by specific entity ID
    - **action**: Filter by action type (view, create, update, delete, query)
    - **start_date**: Filter logs from this date (ISO format)
    - **end_date**: Filter logs until this date (ISO format)
    - **limit**: Maximum number of results (default 100, max 500)
    - **offset**: Pagination offset
    """
    try:
        parsed_entity_type = None
        if entity_type:
            try:
                parsed_entity_type = AuditEntityType(entity_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid entity_type: {entity_type}. Valid values: {[e.value for e in AuditEntityType]}"
                )

        parsed_action = None
        if action:
            try:
                parsed_action = AuditAction(action.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {action}. Valid values: {[a.value for a in AuditAction]}"
                )

        parsed_start = None
        if start_date:
            try:
                parsed_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")

        parsed_end = None
        if end_date:
            try:
                parsed_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")

        params = AuditLogQueryParams(
            user_id=user_id,
            entity_type=parsed_entity_type,
            entity_id=entity_id,
            action=parsed_action,
            start_date=parsed_start,
            end_date=parsed_end,
            limit=limit,
            offset=offset,
        )

        logs, total_count = await audit_service.query_logs(params)

        return JSONResponse(
            content={
                "items": [log.model_dump(mode="json") for log in logs],
                "total": total_count,
                "limit": limit,
                "offset": offset,
            },
            headers={
                "X-Total-Count": str(total_count),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_history(
    entity_type: str,
    entity_id: str,
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get the change history for a specific entity.

    Returns all audit logs for the specified entity, ordered by timestamp descending.
    """
    try:
        try:
            parsed_entity_type = AuditEntityType(entity_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid entity_type: {entity_type}"
            )

        logs = await audit_service.get_entity_history(
            entity_type=parsed_entity_type,
            entity_id=entity_id,
            limit=limit,
        )

        return [log.model_dump(mode="json") for log in logs]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_activity(
    user_id: str,
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get recent activity for a specific user.

    Returns all audit logs for the specified user, ordered by timestamp descending.
    """
    try:
        logs = await audit_service.get_user_activity(user_id=user_id, limit=limit)
        return [log.model_dump(mode="json") for log in logs]

    except Exception as e:
        logger.error(f"Error getting user activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_activity(
    limit: int = Query(100, ge=1, le=500),
):
    """
    Get the most recent activity across all entities.

    Returns recent audit logs ordered by timestamp descending.
    """
    try:
        logs = await audit_service.get_recent_activity(limit=limit)
        return [log.model_dump(mode="json") for log in logs]

    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_audit_summary():
    """
    Get a summary of audit activity.

    Returns counts by action type, entity type, and recent user activity.
    """
    try:
        recent_logs = await audit_service.get_recent_activity(limit=500)

        action_counts = {}
        entity_counts = {}
        user_counts = {}

        for log in recent_logs:
            action = log.action.value
            action_counts[action] = action_counts.get(action, 0) + 1

            entity = log.entity_type.value
            entity_counts[entity] = entity_counts.get(entity, 0) + 1

            user = log.user_id
            user_counts[user] = user_counts.get(user, 0) + 1

        return {
            "total_logs": len(recent_logs),
            "by_action": action_counts,
            "by_entity": entity_counts,
            "by_user": dict(sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        }

    except Exception as e:
        logger.error(f"Error getting audit summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
