"""Azure Resources Service - manages Azure resource tracking via SDK."""
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)


class AzureResourcesService:
    """Service for tracking Azure resources via Management SDKs."""

    def __init__(self):
        """Initialize Azure clients with DefaultAzureCredential."""
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

        if not self.subscription_id:
            logger.warning("AZURE_SUBSCRIPTION_ID not set - Azure resource tracking disabled")
            self.enabled = False
            return

        try:
            credential = DefaultAzureCredential()
            self.resource_client = ResourceManagementClient(credential, self.subscription_id)
            self.cost_client = CostManagementClient(credential)
            self.monitor_client = MonitorManagementClient(credential, self.subscription_id)
            self.enabled = True
            logger.info("Azure Resources Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure clients: {e}")
            self.enabled = False

        # Cache with expiry
        self.resource_cache: List[Dict[str, Any]] = []
        self.resource_cache_expiry: Optional[datetime] = None
        self.cost_cache: Dict[str, float] = {}
        self.cost_cache_expiry: Optional[datetime] = None

    def _is_cache_valid(self, expiry: Optional[datetime]) -> bool:
        """Check if cache is still valid."""
        if not expiry:
            return False
        return datetime.utcnow() < expiry

    async def list_resources(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """List all Azure resources with 5-minute caching."""
        if not self.enabled:
            logger.warning("Azure resource tracking is disabled")
            return []

        # Return cached data if valid
        if not force_refresh and self._is_cache_valid(self.resource_cache_expiry):
            logger.info("Returning cached resources")
            return self.resource_cache

        try:
            logger.info("Fetching resources from Azure...")
            resources = []

            for resource in self.resource_client.resources.list():
                resources.append({
                    "id": resource.id,
                    "name": resource.name,
                    "type": resource.type,
                    "location": resource.location,
                    "resource_group": resource.id.split('/')[4] if '/' in resource.id else "Unknown",
                    "tags": resource.tags or {},
                    "properties": dict(resource.properties) if resource.properties else {},
                })

            # Update cache
            self.resource_cache = resources
            self.resource_cache_expiry = datetime.utcnow() + timedelta(minutes=5)

            logger.info(f"Fetched {len(resources)} resources from Azure")
            return resources

        except Exception as e:
            logger.error(f"Error fetching Azure resources: {e}")
            # Return cached data if available, even if expired
            return self.resource_cache if self.resource_cache else []

    async def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific resource."""
        resources = await self.list_resources()
        return next((r for r in resources if r["id"] == resource_id), None)

    async def get_resource_cost(self, resource_id: str) -> Optional[float]:
        """Get current month cost for specific resource (with 1-hour caching)."""
        if not self.enabled:
            return None

        # Check cache
        if (self._is_cache_valid(self.cost_cache_expiry) and
            resource_id in self.cost_cache):
            return self.cost_cache[resource_id]

        try:
            # Note: Actual Cost Management API implementation would go here
            # For now, return None as cost tracking requires additional setup
            logger.warning("Cost tracking not yet implemented")
            return None
        except Exception as e:
            logger.error(f"Error fetching cost for {resource_id}: {e}")
            return None

    async def get_summary(self) -> Dict[str, Any]:
        """Get aggregation statistics for all resources."""
        resources = await self.list_resources()

        if not resources:
            return {
                "total_resources": 0,
                "running_services": 0,
                "regions": 0,
                "resource_groups": 0,
                "total_cost": None
            }

        # Calculate statistics
        unique_locations = set(r["location"] for r in resources)
        unique_resource_groups = set(r["resource_group"] for r in resources)

        # Estimate running services (resources that aren't purely storage/config)
        running_services = len([
            r for r in resources
            if any(keyword in r["type"].lower()
                   for keyword in ["compute", "app", "function", "container", "foundry"])
        ])

        return {
            "total_resources": len(resources),
            "running_services": running_services,
            "regions": len(unique_locations),
            "resource_groups": len(unique_resource_groups),
            "total_cost": None  # Will be implemented with Cost Management API
        }

    async def refresh_cache(self) -> int:
        """Force refresh all caches and return resource count."""
        resources = await self.list_resources(force_refresh=True)
        return len(resources)


# Singleton instance
azure_resources_service = AzureResourcesService()
