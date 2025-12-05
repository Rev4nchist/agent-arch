"""Cost Management Service - Azure Cost Management API integration."""
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import (
    QueryDefinition,
    QueryTimePeriod,
    QueryDataset,
    QueryAggregation,
    QueryGrouping,
    TimeframeType,
    GranularityType,
    ExportType,
)
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

RESOURCE_GROUPS = [
    "rg-agent-architecture",
    "mb-ai-foundry",
    "mb-ai-foundry-hub",
    "fourth-ai-prod",
    "ai-dev-education",
    "personal-agent-rg",
    "boyan-ai-experiments",
]


class CostManagementService:
    """Service for querying Azure Cost Management API."""

    def __init__(self):
        """Initialize Azure Cost Management client."""
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

        if not self.subscription_id:
            logger.warning("AZURE_SUBSCRIPTION_ID not set - cost tracking disabled")
            self.enabled = False
            return

        try:
            credential = DefaultAzureCredential()
            self.client = CostManagementClient(credential)
            self.enabled = True
            logger.info("Cost Management Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cost Management client: {e}")
            self.enabled = False

        self._cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._cache_duration = timedelta(hours=1)

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid."""
        expiry = self._cache_expiry.get(key)
        if not expiry:
            return False
        return datetime.utcnow() < expiry

    def _set_cache(self, key: str, value: Any):
        """Set cache entry with expiry."""
        self._cache[key] = value
        self._cache_expiry[key] = datetime.utcnow() + self._cache_duration

    async def get_resource_group_costs(
        self,
        resource_group: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Query costs for a specific resource group."""
        if not self.enabled:
            return {"resource_group": resource_group, "total_cost": 0, "services": []}

        cache_key = f"rg_costs:{resource_group}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]

        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        scope = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}"

        try:
            query = QueryDefinition(
                type=ExportType.ACTUAL_COST,
                timeframe=TimeframeType.CUSTOM,
                time_period=QueryTimePeriod(
                    from_property=start_date,
                    to=end_date
                ),
                dataset=QueryDataset(
                    granularity=GranularityType.NONE,
                    aggregation={
                        "totalCost": QueryAggregation(name="Cost", function="Sum"),
                        "totalCostUSD": QueryAggregation(name="CostUSD", function="Sum"),
                    },
                    grouping=[
                        QueryGrouping(type="Dimension", name="ServiceName"),
                    ]
                )
            )

            result = self.client.query.usage(scope=scope, parameters=query)
            parsed = self._parse_cost_response(result, resource_group)
            self._set_cache(cache_key, parsed)
            return parsed

        except Exception as e:
            logger.error(f"Error querying costs for {resource_group}: {e}")
            return {"resource_group": resource_group, "total_cost": 0, "services": [], "error": str(e)}

    def _parse_cost_response(self, response, resource_group: str) -> Dict[str, Any]:
        """Parse Azure Cost Management API response."""
        services = []
        total_cost = 0.0

        if hasattr(response, 'rows') and response.rows:
            columns = [col.name.lower() for col in response.columns] if response.columns else []

            for row in response.rows:
                cost = float(row[0]) if row[0] else 0.0
                cost_usd = float(row[1]) if len(row) > 1 and row[1] else cost
                service_name = row[2] if len(row) > 2 else "Unknown"

                total_cost += cost_usd
                services.append({
                    "name": service_name,
                    "cost": round(cost_usd, 2),
                    "currency": "USD"
                })

        services.sort(key=lambda x: x["cost"], reverse=True)

        return {
            "resource_group": resource_group,
            "total_cost": round(total_cost, 2),
            "currency": "USD",
            "services": services,
            "period_start": datetime.utcnow().replace(day=1).isoformat(),
            "period_end": datetime.utcnow().isoformat(),
        }

    async def get_all_resource_group_costs(
        self,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Get costs for all configured resource groups."""
        if not self.enabled:
            return [{"resource_group": rg, "total_cost": 0, "services": []} for rg in RESOURCE_GROUPS]

        cache_key = "all_rg_costs"
        if not force_refresh and self._is_cache_valid(cache_key):
            return self._cache[cache_key]

        results = []
        for rg in RESOURCE_GROUPS:
            rg_costs = await self.get_resource_group_costs(rg)
            results.append(rg_costs)

        self._set_cache(cache_key, results)
        return results

    async def get_costs_by_service(self) -> Dict[str, float]:
        """Aggregate costs by Azure service type across all RGs."""
        all_costs = await self.get_all_resource_group_costs()

        service_totals: Dict[str, float] = {}
        for rg_data in all_costs:
            for service in rg_data.get("services", []):
                name = service["name"]
                cost = service["cost"]
                service_totals[name] = service_totals.get(name, 0) + cost

        return dict(sorted(service_totals.items(), key=lambda x: x[1], reverse=True))

    async def get_summary(self) -> Dict[str, Any]:
        """Get overall cost summary across all resource groups."""
        all_costs = await self.get_all_resource_group_costs()

        total = sum(rg["total_cost"] for rg in all_costs)
        service_breakdown = await self.get_costs_by_service()

        top_services = list(service_breakdown.items())[:5]

        return {
            "total_cost": round(total, 2),
            "currency": "USD",
            "resource_groups_count": len(RESOURCE_GROUPS),
            "period": "current_month",
            "period_start": datetime.utcnow().replace(day=1).isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "by_resource_group": [
                {"name": rg["resource_group"], "cost": rg["total_cost"]}
                for rg in sorted(all_costs, key=lambda x: x["total_cost"], reverse=True)
            ],
            "top_services": [
                {"name": name, "cost": round(cost, 2)}
                for name, cost in top_services
            ]
        }

    async def get_daily_trend(
        self,
        resource_group: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get daily cost trend for specified period."""
        if not self.enabled:
            return []

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        if resource_group:
            scope = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}"
        else:
            scope = f"/subscriptions/{self.subscription_id}"

        cache_key = f"trend:{resource_group or 'all'}:{days}"
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]

        try:
            query = QueryDefinition(
                type=ExportType.ACTUAL_COST,
                timeframe=TimeframeType.CUSTOM,
                time_period=QueryTimePeriod(
                    from_property=start_date,
                    to=end_date
                ),
                dataset=QueryDataset(
                    granularity=GranularityType.DAILY,
                    aggregation={
                        "totalCostUSD": QueryAggregation(name="CostUSD", function="Sum"),
                    }
                )
            )

            result = self.client.query.usage(scope=scope, parameters=query)

            trend = []
            if hasattr(result, 'rows') and result.rows:
                for row in result.rows:
                    cost = float(row[0]) if row[0] else 0.0
                    date_val = row[1] if len(row) > 1 else datetime.utcnow()
                    if isinstance(date_val, int):
                        date_str = str(date_val)
                        date_val = datetime.strptime(date_str, "%Y%m%d")
                    trend.append({
                        "date": date_val.isoformat() if hasattr(date_val, 'isoformat') else str(date_val),
                        "cost": round(cost, 2)
                    })

            trend.sort(key=lambda x: x["date"])
            self._set_cache(cache_key, trend)
            return trend

        except Exception as e:
            logger.error(f"Error fetching daily trend: {e}")
            return []

    def get_resource_groups(self) -> List[str]:
        """Return list of tracked resource groups."""
        return RESOURCE_GROUPS.copy()


cost_management_service = CostManagementService()
