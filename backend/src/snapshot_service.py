"""
Snapshot Service for capturing daily/weekly metrics snapshots.
Phase 3.1: Enable historical trend analysis and comparison queries.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from azure.cosmos import CosmosClient
from src.config import settings
import logging

logger = logging.getLogger(__name__)

SNAPSHOTS_CONTAINER = "snapshots"


class SnapshotService:
    """Service for capturing and retrieving metric snapshots."""

    def __init__(self):
        """Initialize Cosmos DB client."""
        self.client = CosmosClient(settings.cosmos_endpoint, settings.cosmos_key)
        self.database = self.client.get_database_client(settings.cosmos_database_name)
        self._ensure_container()

    def _ensure_container(self):
        """Ensure snapshots container exists."""
        try:
            self.database.create_container_if_not_exists(
                id=SNAPSHOTS_CONTAINER,
                partition_key={"paths": ["/snapshot_type"], "kind": "Hash"}
            )
        except Exception as e:
            logger.warning(f"Could not create snapshots container: {e}")

    def _get_container(self, name: str):
        """Get a container by name."""
        return self.database.get_container_client(name)

    async def capture_daily_snapshot(self) -> Dict[str, Any]:
        """
        Capture a daily snapshot of all entity counts by status.
        Returns the snapshot data.
        """
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        snapshot_id = f"daily_{today.strftime('%Y-%m-%d')}"

        # Check if snapshot already exists for today
        existing = await self.get_snapshot_by_id(snapshot_id)
        if existing:
            logger.info(f"Snapshot {snapshot_id} already exists, skipping capture")
            return existing

        snapshot = {
            "id": snapshot_id,
            "snapshot_type": "daily",
            "date": today.isoformat(),
            "captured_at": datetime.utcnow().isoformat(),
            "tasks": await self._get_task_metrics(),
            "agents": await self._get_agent_metrics(),
            "decisions": await self._get_decision_metrics(),
            "meetings": await self._get_meeting_metrics(),
        }

        # Store snapshot
        container = self._get_container(SNAPSHOTS_CONTAINER)
        container.upsert_item(snapshot)
        logger.info(f"Captured daily snapshot: {snapshot_id}")

        return snapshot

    async def _get_task_metrics(self) -> Dict[str, Any]:
        """Get task counts by status and priority."""
        container = self._get_container("tasks")

        by_status = {"Pending": 0, "In-Progress": 0, "Done": 0, "Blocked": 0, "Deferred": 0}
        by_priority = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        total = 0
        overdue = 0
        today = datetime.utcnow().strftime('%Y-%m-%d')

        query = "SELECT c.status, c.priority, c.due_date FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        for item in items:
            total += 1
            status = item.get("status", "Pending")
            priority = item.get("priority", "Medium")
            due_date = item.get("due_date")

            if status in by_status:
                by_status[status] += 1
            if priority in by_priority:
                by_priority[priority] += 1
            if due_date and due_date < today and status != "Done":
                overdue += 1

        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "overdue": overdue,
            "completed": by_status.get("Done", 0),
            "blocked": by_status.get("Blocked", 0),
        }

    async def _get_agent_metrics(self) -> Dict[str, Any]:
        """Get agent counts by status."""
        container = self._get_container("agents")

        by_status = {
            "Idea": 0, "Design": 0, "Development": 0, "Testing": 0,
            "Staging": 0, "Production": 0, "Deprecated": 0
        }
        by_tier = {"Tier1_Individual": 0, "Tier2_Department": 0, "Tier3_Enterprise": 0}
        total = 0

        query = "SELECT c.status, c.tier FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        for item in items:
            total += 1
            status = item.get("status", "Idea")
            tier = item.get("tier", "Tier1_Individual")

            if status in by_status:
                by_status[status] += 1
            if tier in by_tier:
                by_tier[tier] += 1

        return {
            "total": total,
            "by_status": by_status,
            "by_tier": by_tier,
            "in_production": by_status.get("Production", 0),
            "in_development": by_status.get("Development", 0) + by_status.get("Testing", 0),
        }

    async def _get_decision_metrics(self) -> Dict[str, Any]:
        """Get decision counts by category."""
        container = self._get_container("decisions")

        by_category = {
            "Governance": 0, "Architecture": 0, "Licensing": 0,
            "Budget": 0, "Security": 0
        }
        total = 0

        query = "SELECT c.category FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        for item in items:
            total += 1
            category = item.get("category", "Governance")
            if category in by_category:
                by_category[category] += 1

        return {
            "total": total,
            "by_category": by_category,
        }

    async def _get_meeting_metrics(self) -> Dict[str, Any]:
        """Get meeting counts by status."""
        container = self._get_container("meetings")

        by_status = {"Scheduled": 0, "Completed": 0, "Cancelled": 0}
        total = 0

        query = "SELECT c.status FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        for item in items:
            total += 1
            status = item.get("status", "Scheduled")
            if status in by_status:
                by_status[status] += 1

        return {
            "total": total,
            "by_status": by_status,
            "completed": by_status.get("Completed", 0),
        }

    async def get_snapshot_by_id(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific snapshot by ID."""
        container = self._get_container(SNAPSHOTS_CONTAINER)
        try:
            query = "SELECT * FROM c WHERE c.id = @id"
            params = [{"name": "@id", "value": snapshot_id}]
            items = list(container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True
            ))
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Error fetching snapshot {snapshot_id}: {e}")
            return None

    async def get_snapshot(self, days_ago: int = 0) -> Optional[Dict[str, Any]]:
        """Get snapshot from N days ago."""
        target_date = datetime.utcnow() - timedelta(days=days_ago)
        snapshot_id = f"daily_{target_date.strftime('%Y-%m-%d')}"
        return await self.get_snapshot_by_id(snapshot_id)

    async def get_snapshots_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get all snapshots within a date range."""
        container = self._get_container(SNAPSHOTS_CONTAINER)

        query = """
            SELECT * FROM c
            WHERE c.snapshot_type = 'daily'
            AND c.date >= @start_date
            AND c.date <= @end_date
            ORDER BY c.date DESC
        """
        params = [
            {"name": "@start_date", "value": start_date.isoformat()},
            {"name": "@end_date", "value": end_date.isoformat()},
        ]

        items = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        return items

    async def clear_all_snapshots(self) -> int:
        """Delete all snapshots. Returns count of deleted items."""
        container = self._get_container(SNAPSHOTS_CONTAINER)
        deleted_count = 0

        query = "SELECT c.id, c.snapshot_type FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        for item in items:
            try:
                container.delete_item(item=item["id"], partition_key=item["snapshot_type"])
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete snapshot {item['id']}: {e}")

        logger.info(f"Cleared {deleted_count} snapshots from container")
        return deleted_count

    def format_comparison(
        self, current: Dict[str, Any], previous: Dict[str, Any]
    ) -> str:
        """Format comparison between two snapshots for AI context."""
        if not current or not previous:
            return "Historical comparison data not available."

        lines = ["**Comparison with Previous Period:**\n"]

        # Task comparison
        curr_tasks = current.get("tasks", {})
        prev_tasks = previous.get("tasks", {})

        task_total_delta = curr_tasks.get("total", 0) - prev_tasks.get("total", 0)
        task_completed_delta = curr_tasks.get("completed", 0) - prev_tasks.get("completed", 0)
        task_blocked_delta = curr_tasks.get("blocked", 0) - prev_tasks.get("blocked", 0)

        lines.append("**Tasks:**")
        lines.append(f"- Total: {curr_tasks.get('total', 0)} ({'+' if task_total_delta >= 0 else ''}{task_total_delta} from previous)")
        lines.append(f"- Completed: {curr_tasks.get('completed', 0)} ({'+' if task_completed_delta >= 0 else ''}{task_completed_delta})")
        lines.append(f"- Blocked: {curr_tasks.get('blocked', 0)} ({'+' if task_blocked_delta >= 0 else ''}{task_blocked_delta})")

        # Agent comparison
        curr_agents = current.get("agents", {})
        prev_agents = previous.get("agents", {})

        agent_total_delta = curr_agents.get("total", 0) - prev_agents.get("total", 0)
        agent_prod_delta = curr_agents.get("in_production", 0) - prev_agents.get("in_production", 0)

        lines.append("\n**Agents:**")
        lines.append(f"- Total: {curr_agents.get('total', 0)} ({'+' if agent_total_delta >= 0 else ''}{agent_total_delta})")
        lines.append(f"- In Production: {curr_agents.get('in_production', 0)} ({'+' if agent_prod_delta >= 0 else ''}{agent_prod_delta})")

        # Status breakdown comparison
        curr_by_status = curr_agents.get("by_status", {})
        prev_by_status = prev_agents.get("by_status", {})

        lines.append("\n**Agent Status Breakdown:**")
        for status in ["Development", "Testing", "Production"]:
            curr_val = curr_by_status.get(status, 0)
            prev_val = prev_by_status.get(status, 0)
            delta = curr_val - prev_val
            lines.append(f"- {status}: {curr_val} ({'+' if delta >= 0 else ''}{delta})")

        return "\n".join(lines)


# Global instance
snapshot_service = SnapshotService()
