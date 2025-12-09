"""Feature updates router for What's New page."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
from src.database import db
from src.models import (
    FeatureUpdate,
    FeatureUpdateCreate,
    FeatureUpdateUpdate,
    FeatureUpdateCategory,
)
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feature-updates", tags=["feature-updates"])


def get_feature_updates_container():
    container = db.get_container("feature_updates")
    if not container:
        raise HTTPException(status_code=500, detail="Feature updates container not initialized")
    return container


@router.get("")
async def list_feature_updates(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all feature updates, newest first."""
    try:
        container = get_feature_updates_container()

        conditions = []
        params = []

        if category:
            conditions.append("c.category = @category")
            params.append({"name": "@category", "value": category})

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"SELECT * FROM c WHERE {where_clause} ORDER BY c.published_at DESC OFFSET @offset LIMIT @limit"
        params.extend([
            {"name": "@offset", "value": offset},
            {"name": "@limit", "value": limit},
        ])

        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

        count_query = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"
        count_params = [p for p in params if p["name"] not in ["@offset", "@limit"]]
        total_count = list(container.query_items(query=count_query, parameters=count_params, enable_cross_partition_query=True))[0]

        return JSONResponse(
            content={"items": items, "total": total_count},
            headers={"X-Total-Count": str(total_count)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing feature updates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{update_id}")
async def get_feature_update(update_id: str):
    """Get a single feature update by ID."""
    try:
        container = get_feature_updates_container()

        try:
            item = container.read_item(item=update_id, partition_key=update_id)
            return item
        except Exception:
            raise HTTPException(status_code=404, detail=f"Feature update {update_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_feature_update(update: FeatureUpdateCreate):
    """Create a new feature update (admin only)."""
    try:
        container = get_feature_updates_container()

        update_id = str(uuid.uuid4())
        now = datetime.utcnow()

        new_update = FeatureUpdate(
            id=update_id,
            title=update.title,
            description=update.description,
            category=update.category,
            version=update.version,
            related_pages=update.related_pages,
            published_at=update.published_at or now,
            created_by=update.created_by,
            created_at=now,
            updated_at=now,
        )

        item = new_update.model_dump(mode="json")
        container.create_item(body=item)

        logger.info(f"Created feature update: {update_id}")
        return item
    except Exception as e:
        logger.error(f"Error creating feature update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{update_id}")
async def update_feature_update(update_id: str, update: FeatureUpdateUpdate):
    """Update a feature update (admin only)."""
    try:
        container = get_feature_updates_container()

        try:
            existing = container.read_item(item=update_id, partition_key=update_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Feature update {update_id} not found")

        update_data = update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if value is not None:
                if hasattr(value, 'value'):
                    existing[key] = value.value
                else:
                    existing[key] = value

        existing["updated_at"] = datetime.utcnow().isoformat()

        container.replace_item(item=update_id, body=existing)

        logger.info(f"Updated feature update: {update_id}")
        return existing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feature update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{update_id}")
async def delete_feature_update(update_id: str):
    """Delete a feature update (admin only)."""
    try:
        container = get_feature_updates_container()

        try:
            container.delete_item(item=update_id, partition_key=update_id)
            logger.info(f"Deleted feature update: {update_id}")
            return {"message": f"Feature update {update_id} deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail=f"Feature update {update_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feature update: {e}")
        raise HTTPException(status_code=500, detail=str(e))
