"""Budget Router - API endpoints for cost tracking and budget management."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from src.cost_management_service import cost_management_service
from src.database import db
from src.models import (
    Budget,
    BudgetCreate,
    License,
    LicenseCreate,
    CostSummary,
    ResourceGroupCost,
    BudgetStatus,
)
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/budget", tags=["budget"])


@router.get("/costs/summary", response_model=CostSummary)
async def get_cost_summary():
    """Get overall cost summary from Azure Cost Management API."""
    try:
        summary = await cost_management_service.get_summary()
        return CostSummary(**summary)
    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/resource-groups", response_model=List[ResourceGroupCost])
async def get_resource_group_costs(force_refresh: bool = Query(False)):
    """Get costs for all tracked resource groups."""
    try:
        costs = await cost_management_service.get_all_resource_group_costs(force_refresh)
        return [ResourceGroupCost(**rg) for rg in costs]
    except Exception as e:
        logger.error(f"Error getting resource group costs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/resource-groups/{resource_group}", response_model=ResourceGroupCost)
async def get_resource_group_cost(resource_group: str):
    """Get costs for a specific resource group."""
    try:
        costs = await cost_management_service.get_resource_group_costs(resource_group)
        return ResourceGroupCost(**costs)
    except Exception as e:
        logger.error(f"Error getting costs for {resource_group}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/by-service")
async def get_costs_by_service():
    """Get costs aggregated by Azure service type."""
    try:
        service_costs = await cost_management_service.get_costs_by_service()
        return {
            "services": [
                {"name": name, "cost": round(cost, 2)}
                for name, cost in service_costs.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error getting costs by service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/trend")
async def get_cost_trend(
    resource_group: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=90)
):
    """Get daily cost trend for specified period."""
    try:
        trend = await cost_management_service.get_daily_trend(resource_group, days)
        return {"trend": trend, "days": days, "resource_group": resource_group}
    except Exception as e:
        logger.error(f"Error getting cost trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource-groups")
async def list_resource_groups():
    """List all tracked resource groups."""
    return {"resource_groups": cost_management_service.get_resource_groups()}


@router.get("/budgets", response_model=List[Budget])
async def list_budgets():
    """List all budget allocations."""
    try:
        container = db.get_container("budgets")
        if not container:
            return []

        items = list(container.query_items(
            query="SELECT * FROM c ORDER BY c.created_at DESC",
            enable_cross_partition_query=True
        ))
        return [Budget(**item) for item in items]
    except Exception as e:
        logger.error(f"Error listing budgets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/budgets", response_model=Budget)
async def create_budget(budget: BudgetCreate):
    """Create a new budget allocation."""
    try:
        container = db.get_container("budgets")
        if not container:
            raise HTTPException(status_code=500, detail="Database not initialized")

        budget_dict = budget.dict()
        budget_dict["id"] = str(uuid.uuid4())
        budget_dict["spent"] = 0.0
        budget_dict["status"] = BudgetStatus.ON_TRACK.value
        budget_dict["created_at"] = datetime.utcnow().isoformat()
        budget_dict["updated_at"] = datetime.utcnow().isoformat()

        if budget_dict.get("start_date"):
            budget_dict["start_date"] = budget_dict["start_date"].isoformat()
        if budget_dict.get("end_date"):
            budget_dict["end_date"] = budget_dict["end_date"].isoformat()

        container.create_item(body=budget_dict)
        return Budget(**budget_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budgets/{budget_id}", response_model=Budget)
async def get_budget(budget_id: str):
    """Get a specific budget by ID."""
    try:
        container = db.get_container("budgets")
        if not container:
            raise HTTPException(status_code=500, detail="Database not initialized")

        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": budget_id}],
            enable_cross_partition_query=True
        ))

        if not items:
            raise HTTPException(status_code=404, detail="Budget not found")

        return Budget(**items[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/budgets/{budget_id}", response_model=Budget)
async def update_budget(budget_id: str, budget: BudgetCreate):
    """Update an existing budget."""
    try:
        container = db.get_container("budgets")
        if not container:
            raise HTTPException(status_code=500, detail="Database not initialized")

        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": budget_id}],
            enable_cross_partition_query=True
        ))

        if not items:
            raise HTTPException(status_code=404, detail="Budget not found")

        existing = items[0]
        update_data = budget.dict()
        update_data["id"] = budget_id
        update_data["spent"] = existing.get("spent", 0.0)
        update_data["status"] = existing.get("status", BudgetStatus.ON_TRACK.value)
        update_data["created_at"] = existing.get("created_at")
        update_data["updated_at"] = datetime.utcnow().isoformat()

        if update_data.get("start_date"):
            update_data["start_date"] = update_data["start_date"].isoformat()
        if update_data.get("end_date"):
            update_data["end_date"] = update_data["end_date"].isoformat()

        container.upsert_item(body=update_data)
        return Budget(**update_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/budgets/{budget_id}")
async def delete_budget(budget_id: str):
    """Delete a budget."""
    try:
        container = db.get_container("budgets")
        if not container:
            raise HTTPException(status_code=500, detail="Database not initialized")

        container.delete_item(item=budget_id, partition_key=budget_id)
        return {"message": "Budget deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/licenses", response_model=List[License])
async def list_licenses():
    """List all software licenses."""
    try:
        container = db.get_container("licenses")
        if not container:
            return []

        items = list(container.query_items(
            query="SELECT * FROM c ORDER BY c.name",
            enable_cross_partition_query=True
        ))
        return [License(**item) for item in items]
    except Exception as e:
        logger.error(f"Error listing licenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/licenses", response_model=License)
async def create_license(license: LicenseCreate):
    """Create a new license entry."""
    try:
        container = db.get_container("licenses")
        if not container:
            raise HTTPException(status_code=500, detail="Database not initialized")

        license_dict = license.dict()
        license_dict["id"] = str(uuid.uuid4())
        license_dict["status"] = "Active"
        license_dict["created_at"] = datetime.utcnow().isoformat()
        license_dict["updated_at"] = datetime.utcnow().isoformat()

        if license_dict.get("renewal_date"):
            license_dict["renewal_date"] = license_dict["renewal_date"].isoformat()

        container.create_item(body=license_dict)
        return License(**license_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/licenses/{license_id}", response_model=License)
async def get_license(license_id: str):
    """Get a specific license by ID."""
    try:
        container = db.get_container("licenses")
        if not container:
            raise HTTPException(status_code=500, detail="Database not initialized")

        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": license_id}],
            enable_cross_partition_query=True
        ))

        if not items:
            raise HTTPException(status_code=404, detail="License not found")

        return License(**items[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/licenses/{license_id}", response_model=License)
async def update_license(license_id: str, license: LicenseCreate):
    """Update an existing license."""
    try:
        container = db.get_container("licenses")
        if not container:
            raise HTTPException(status_code=500, detail="Database not initialized")

        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.id = @id",
            parameters=[{"name": "@id", "value": license_id}],
            enable_cross_partition_query=True
        ))

        if not items:
            raise HTTPException(status_code=404, detail="License not found")

        existing = items[0]
        update_data = license.dict()
        update_data["id"] = license_id
        update_data["status"] = existing.get("status", "Active")
        update_data["created_at"] = existing.get("created_at")
        update_data["updated_at"] = datetime.utcnow().isoformat()

        if update_data.get("renewal_date"):
            update_data["renewal_date"] = update_data["renewal_date"].isoformat()

        container.upsert_item(body=update_data)
        return License(**update_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/licenses/{license_id}")
async def delete_license(license_id: str):
    """Delete a license."""
    try:
        container = db.get_container("licenses")
        if not container:
            raise HTTPException(status_code=500, detail="Database not initialized")

        container.delete_item(item=license_id, partition_key=license_id)
        return {"message": "License deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting license: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard():
    """Get combined dashboard data with costs, budgets, and licenses."""
    try:
        cost_summary = await cost_management_service.get_summary()

        budgets = []
        budget_container = db.get_container("budgets")
        if budget_container:
            budgets = list(budget_container.query_items(
                query="SELECT * FROM c ORDER BY c.created_at DESC",
                enable_cross_partition_query=True
            ))

        licenses = []
        license_container = db.get_container("licenses")
        if license_container:
            licenses = list(license_container.query_items(
                query="SELECT * FROM c ORDER BY c.name",
                enable_cross_partition_query=True
            ))

        total_license_cost = sum(lic.get("monthly_cost", 0) for lic in licenses)
        total_budget_amount = sum(b.get("amount", 0) for b in budgets)

        return {
            "azure_costs": cost_summary,
            "budgets": budgets,
            "licenses": licenses,
            "totals": {
                "azure_spend": cost_summary.get("total_cost", 0),
                "license_spend": total_license_cost,
                "total_monthly": cost_summary.get("total_cost", 0) + total_license_cost,
                "total_budget": total_budget_amount,
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
