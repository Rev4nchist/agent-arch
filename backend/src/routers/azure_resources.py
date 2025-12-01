"""Azure Resources Router - API endpoints for Azure resource tracking."""
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from src.azure_resources_service import azure_resources_service
from src.models import AzureResource, AzureResourceSummary
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/azure", tags=["azure-resources"])


@router.get("/resources", response_model=List[AzureResource])
async def list_resources(
    type_filter: Optional[str] = Query(None, description="Filter by resource type (partial match)"),
    region: Optional[str] = Query(None, description="Filter by region/location"),
    resource_group: Optional[str] = Query(None, description="Filter by resource group"),
    force_refresh: bool = Query(False, description="Force refresh cache")
):
    """List all Azure resources with optional filtering."""
    try:
        resources = await azure_resources_service.list_resources(force_refresh=force_refresh)

        # Apply filters
        if type_filter:
            resources = [r for r in resources if type_filter.lower() in r["type"].lower()]

        if region:
            resources = [r for r in resources if r["location"].lower() == region.lower()]

        if resource_group:
            resources = [r for r in resources if r["resource_group"].lower() == resource_group.lower()]

        # Convert to Pydantic models
        return [AzureResource(**r) for r in resources]

    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch resources: {str(e)}")


@router.get("/resources/summary", response_model=AzureResourceSummary)
async def get_summary():
    """Get aggregation statistics for all resources."""
    try:
        summary = await azure_resources_service.get_summary()
        return AzureResourceSummary(**summary)
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.get("/resources/{resource_id:path}", response_model=AzureResource)
async def get_resource(resource_id: str):
    """Get detailed information for a specific resource."""
    try:
        resource = await azure_resources_service.get_resource(resource_id)

        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        # Enrich with cost data if available
        cost = await azure_resources_service.get_resource_cost(resource_id)
        if cost is not None:
            resource["current_month_cost"] = cost

        return AzureResource(**resource)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resource {resource_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resource: {str(e)}")


@router.post("/resources/refresh")
async def refresh_cache():
    """Force refresh resource cache."""
    try:
        count = await azure_resources_service.refresh_cache()
        return {"message": "Cache refreshed successfully", "resource_count": count}
    except Exception as e:
        logger.error(f"Error refreshing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh cache: {str(e)}")
