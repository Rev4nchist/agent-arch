"""Audit logging service for tracking user actions."""
import uuid
import logging
from datetime import datetime
from typing import List, Optional
from src.database import db
from src.models import (
    AuditLog,
    AuditAction,
    AuditEntityType,
    AuditLogQueryParams,
)

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit log operations."""

    def __init__(self):
        self.container_name = "audit_logs"

    def _get_container(self):
        return db.get_container(self.container_name)

    async def log_action(
        self,
        user_id: str,
        action: AuditAction,
        entity_type: AuditEntityType,
        entity_id: str,
        user_name: Optional[str] = None,
        entity_title: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
    ) -> AuditLog:
        """Log an audit action."""
        try:
            audit_entry = AuditLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                user_name=user_name,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_title=entity_title,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                old_value=old_value,
                new_value=new_value,
            )

            container = self._get_container()
            if container:
                container.create_item(body=audit_entry.model_dump(mode="json"))
                logger.info(
                    f"Audit logged: {action.value} {entity_type.value}/{entity_id} by {user_id}"
                )
            return audit_entry

        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
            raise

    async def query_logs(
        self, params: AuditLogQueryParams
    ) -> tuple[List[AuditLog], int]:
        """Query audit logs with filters."""
        try:
            container = self._get_container()
            if not container:
                return [], 0

            conditions = ["1=1"]
            query_params = []

            if params.user_id:
                conditions.append("c.user_id = @user_id")
                query_params.append({"name": "@user_id", "value": params.user_id})

            if params.entity_type:
                conditions.append("c.entity_type = @entity_type")
                query_params.append(
                    {"name": "@entity_type", "value": params.entity_type.value}
                )

            if params.entity_id:
                conditions.append("c.entity_id = @entity_id")
                query_params.append({"name": "@entity_id", "value": params.entity_id})

            if params.action:
                conditions.append("c.action = @action")
                query_params.append({"name": "@action", "value": params.action.value})

            if params.start_date:
                conditions.append("c.timestamp >= @start_date")
                query_params.append(
                    {"name": "@start_date", "value": params.start_date.isoformat()}
                )

            if params.end_date:
                conditions.append("c.timestamp <= @end_date")
                query_params.append(
                    {"name": "@end_date", "value": params.end_date.isoformat()}
                )

            where_clause = " AND ".join(conditions)

            count_query = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"
            count_result = list(
                container.query_items(
                    query=count_query,
                    parameters=query_params,
                    enable_cross_partition_query=True,
                )
            )
            total_count = count_result[0] if count_result else 0

            query = f"""
                SELECT * FROM c
                WHERE {where_clause}
                ORDER BY c.timestamp DESC
                OFFSET {params.offset} LIMIT {params.limit}
            """

            items = list(
                container.query_items(
                    query=query,
                    parameters=query_params,
                    enable_cross_partition_query=True,
                )
            )

            logs = [AuditLog(**item) for item in items]
            return logs, total_count

        except Exception as e:
            logger.error(f"Failed to query audit logs: {e}")
            raise

    async def get_entity_history(
        self, entity_type: AuditEntityType, entity_id: str, limit: int = 50
    ) -> List[AuditLog]:
        """Get change history for a specific entity."""
        params = AuditLogQueryParams(
            entity_type=entity_type, entity_id=entity_id, limit=limit
        )
        logs, _ = await self.query_logs(params)
        return logs

    async def get_user_activity(
        self, user_id: str, limit: int = 50
    ) -> List[AuditLog]:
        """Get recent activity for a specific user."""
        params = AuditLogQueryParams(user_id=user_id, limit=limit)
        logs, _ = await self.query_logs(params)
        return logs

    async def get_recent_activity(self, limit: int = 100) -> List[AuditLog]:
        """Get recent activity across all entities."""
        params = AuditLogQueryParams(limit=limit)
        logs, _ = await self.query_logs(params)
        return logs


audit_service = AuditService()
