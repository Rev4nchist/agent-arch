"""Audit logging middleware for automatic action tracking."""
import asyncio
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from src.audit_service import audit_service
from src.models import AuditAction, AuditEntityType

logger = logging.getLogger(__name__)

ENTITY_ROUTE_MAP = {
    "/api/tasks": AuditEntityType.TASK,
    "/api/meetings": AuditEntityType.MEETING,
    "/api/agents": AuditEntityType.AGENT,
    "/api/decisions": AuditEntityType.DECISION,
    "/api/proposals": AuditEntityType.PROPOSAL,
    "/api/resources": AuditEntityType.RESOURCE,
    "/api/tech-radar": AuditEntityType.TECH_RADAR,
    "/api/code-patterns": AuditEntityType.CODE_PATTERN,
}

METHOD_TO_ACTION = {
    "GET": AuditAction.VIEW,
    "POST": AuditAction.CREATE,
    "PUT": AuditAction.UPDATE,
    "PATCH": AuditAction.UPDATE,
    "DELETE": AuditAction.DELETE,
}

EXCLUDED_ROUTES = {
    "/health",
    "/api/audit",
    "/api/search",
    "/docs",
    "/openapi.json",
    "/redoc",
}


def _should_audit(path: str, method: str) -> bool:
    """Determine if the request should be audited."""
    if any(path.startswith(excluded) for excluded in EXCLUDED_ROUTES):
        return False

    for route_prefix in ENTITY_ROUTE_MAP.keys():
        if path.startswith(route_prefix):
            return True

    if path == "/api/agent/query":
        return True

    return False


def _extract_entity_info(path: str) -> tuple[Optional[AuditEntityType], Optional[str]]:
    """Extract entity type and ID from the request path."""
    for route_prefix, entity_type in ENTITY_ROUTE_MAP.items():
        if path.startswith(route_prefix):
            remainder = path[len(route_prefix):]
            entity_id = None
            if remainder.startswith("/") and len(remainder) > 1:
                parts = remainder.split("/")
                if len(parts) >= 2 and parts[1]:
                    entity_id = parts[1]
            return entity_type, entity_id
    return None, None


def _get_user_from_request(request: Request) -> tuple[str, Optional[str]]:
    """Extract user ID and name from request headers or auth."""
    user_id = request.headers.get("X-User-ID", "anonymous")
    user_name = request.headers.get("X-User-Name")

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        pass

    return user_id, user_name


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log API actions to audit trail."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method

        if not _should_audit(path, method):
            return await call_next(request)

        user_id, user_name = _get_user_from_request(request)
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")

        response = await call_next(request)

        if response.status_code >= 400:
            return response

        try:
            entity_type, entity_id = _extract_entity_info(path)
            action = METHOD_TO_ACTION.get(method)

            if path == "/api/agent/query":
                entity_type = AuditEntityType.TASK
                action = AuditAction.QUERY
                entity_id = "ai_guide_query"

            if entity_type and action:
                asyncio.create_task(
                    audit_service.log_action(
                        user_id=user_id,
                        user_name=user_name,
                        action=action,
                        entity_type=entity_type,
                        entity_id=entity_id or "collection",
                        ip_address=ip_address,
                        user_agent=user_agent,
                        details={
                            "path": path,
                            "method": method,
                            "status_code": response.status_code,
                        },
                    )
                )

        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")

        return response


def audit_log_decorator(
    action: AuditAction,
    entity_type: AuditEntityType,
    get_entity_id: Optional[Callable] = None,
    get_entity_title: Optional[Callable] = None,
):
    """
    Decorator for explicit audit logging on specific endpoints.

    Usage:
        @audit_log_decorator(
            action=AuditAction.UPDATE,
            entity_type=AuditEntityType.TASK,
            get_entity_id=lambda task_id, **kwargs: task_id,
        )
        async def update_task(task_id: str, task: Task):
            ...
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            request: Optional[Request] = kwargs.get("request")

            result = await func(*args, **kwargs)

            try:
                entity_id = get_entity_id(*args, **kwargs) if get_entity_id else None
                entity_title = get_entity_title(*args, **kwargs) if get_entity_title else None

                user_id = "anonymous"
                user_name = None
                ip_address = None
                user_agent = None

                if request:
                    user_id, user_name = _get_user_from_request(request)
                    ip_address = request.client.host if request.client else None
                    user_agent = request.headers.get("User-Agent")

                asyncio.create_task(
                    audit_service.log_action(
                        user_id=user_id,
                        user_name=user_name,
                        action=action,
                        entity_type=entity_type,
                        entity_id=entity_id or "unknown",
                        entity_title=entity_title,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                )
            except Exception as e:
                logger.error(f"Audit decorator logging failed: {e}")

            return result

        return wrapper
    return decorator
