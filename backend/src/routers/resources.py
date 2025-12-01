"""Resource library API endpoints."""
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
from typing import List, Optional
import uuid
import json
from datetime import datetime
import logging

from src.models import Resource, ResourceType, ResourceCategory
from src.resource_library_service import ResourceLibraryService
from src.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/resources", tags=["resources"])
resource_service = ResourceLibraryService()


@router.post("/", response_model=Resource)
async def create_resource(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    tags: str = Form("[]"),
    uploaded_by: str = Form("system"),
):
    """Create a new resource (upload document or add web link)."""

    if not file and not url:
        raise HTTPException(
            status_code=400, detail="Either file or url must be provided"
        )

    if file and url:
        raise HTTPException(
            status_code=400, detail="Cannot provide both file and url"
        )

    # Validate category
    try:
        ResourceCategory(category)
    except ValueError:
        valid_categories = [c.value for c in ResourceCategory]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )

    resource_id = str(uuid.uuid4())
    tags_list = json.loads(tags) if tags else []

    resource_data = {
        "id": resource_id,
        "title": title,
        "description": description,
        "category": category,
        "tags": tags_list,
        "uploaded_by": uploaded_by,
        "uploaded_at": datetime.utcnow().isoformat(),
        "view_count": 0,
        "related_resources": [],
    }

    try:
        if file:
            # Handle document upload
            file_content = await file.read()
            file_info = await resource_service.upload_document(
                file_content, file.filename, resource_id
            )

            resource_data.update(
                {
                    "type": ResourceType.PDF
                    if file_info["file_type"] == "pdf"
                    else ResourceType.DOCUMENT,
                    "file_type": file_info["file_type"],
                    "file_size_bytes": file_info["file_size_bytes"],
                    "blob_url": file_info["blob_url"],
                    "thumbnail_url": file_info.get("thumbnail_url"),
                }
            )

            # Extract text preview and page count for PDFs
            if file_info["file_type"] == "pdf":
                preview_text = await resource_service.extract_pdf_text_preview(
                    file_content
                )
                page_count = resource_service.get_page_count(file_content)
                resource_data["preview_text"] = preview_text
                resource_data["page_count"] = page_count

        elif url:
            # Handle web link
            og_metadata = await resource_service.fetch_og_metadata(url)

            resource_data.update(
                {
                    "type": ResourceType.LINK,
                    "url": url,
                    "og_title": og_metadata.get("og_title"),
                    "og_description": og_metadata.get("og_description"),
                    "og_image": og_metadata.get("og_image"),
                }
            )

            # Use OG metadata if title/description not provided
            if not resource_data["title"]:
                resource_data["title"] = og_metadata.get("og_title", url)
            if not resource_data["description"]:
                resource_data["description"] = og_metadata.get("og_description", "")

        # Store in database
        container = db.get_container("resources")
        created_item = container.create_item(resource_data)

        return Resource(**created_item)

    except Exception as e:
        logger.error(f"Error creating resource: {e}")
        # Cleanup uploaded files if database storage fails
        if file:
            await resource_service.delete_resource_files(resource_id)
        raise HTTPException(status_code=500, detail=f"Failed to create resource: {e}")


@router.get("/", response_model=List[Resource])
async def list_resources(
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    sort_by: str = Query("uploaded_at"),
    sort_order: str = Query("desc"),
):
    """List resources with optional filtering and search."""

    try:
        container = db.get_container("resources")

        # Build query
        query = "SELECT * FROM c WHERE c.type != 'undefined'"
        parameters = []

        if category:
            query += " AND c.category = @category"
            parameters.append({"name": "@category", "value": category})

        if type:
            query += " AND c.type = @type"
            parameters.append({"name": "@type", "value": type})

        if tags:
            tags_list = tags.split(",")
            for i, tag in enumerate(tags_list):
                query += f" AND ARRAY_CONTAINS(c.tags, @tag{i})"
                parameters.append({"name": f"@tag{i}", "value": tag.strip()})

        if search:
            query += " AND (CONTAINS(LOWER(c.title), LOWER(@search)) OR CONTAINS(LOWER(c.description), LOWER(@search)))"
            parameters.append({"name": "@search", "value": search})

        # Add sorting
        sort_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
        query += f" ORDER BY c.{sort_by} {sort_direction}"

        # Execute query
        items = list(
            container.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )

        return [Resource(**item) for item in items]

    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list resources: {e}")


@router.get("/{resource_id}", response_model=Resource)
async def get_resource(resource_id: str):
    """Get a specific resource by ID."""

    try:
        container = db.get_container("resources")

        item = container.read_item(item=resource_id, partition_key=resource_id)
        return Resource(**item)

    except Exception as e:
        logger.error(f"Error getting resource {resource_id}: {e}")
        raise HTTPException(status_code=404, detail="Resource not found")


@router.patch("/{resource_id}", response_model=Resource)
async def update_resource(
    resource_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
):
    """Update resource metadata."""

    # Validate category if provided
    if category:
        try:
            ResourceCategory(category)
        except ValueError:
            valid_categories = [c.value for c in ResourceCategory]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )

    try:
        container = db.get_container("resources")

        # Get existing resource
        item = container.read_item(item=resource_id, partition_key=resource_id)

        # Update fields
        if title:
            item["title"] = title
        if description:
            item["description"] = description
        if category:
            item["category"] = category
        if tags:
            item["tags"] = json.loads(tags)

        # Save changes
        updated_item = container.replace_item(item=resource_id, body=item)
        return Resource(**updated_item)

    except Exception as e:
        logger.error(f"Error updating resource {resource_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update resource: {e}"
        )


@router.delete("/{resource_id}")
async def delete_resource(resource_id: str):
    """Delete a resource and its associated files."""

    try:
        container = db.get_container("resources")

        # Get resource to check if it has files
        item = container.read_item(item=resource_id, partition_key=resource_id)

        # Delete files from Blob Storage if document type
        if item.get("blob_url"):
            await resource_service.delete_resource_files(resource_id)

        # Delete from database
        container.delete_item(item=resource_id, partition_key=resource_id)

        return {"message": "Resource deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting resource {resource_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete resource: {e}"
        )


@router.post("/{resource_id}/view")
async def increment_view_count(resource_id: str):
    """Increment view count when resource is accessed."""

    try:
        container = db.get_container("resources")

        item = container.read_item(item=resource_id, partition_key=resource_id)

        # Update view count and last accessed
        item["view_count"] = item.get("view_count", 0) + 1
        item["last_accessed"] = datetime.utcnow().isoformat()

        updated_item = container.replace_item(item=resource_id, body=item)

        return {
            "view_count": updated_item["view_count"],
            "last_accessed": updated_item["last_accessed"],
        }

    except Exception as e:
        logger.error(f"Error incrementing view count for {resource_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to increment view count: {e}"
        )


@router.get("/categories/list")
async def list_categories():
    """List all available resource categories from predefined enum."""
    return {"categories": [category.value for category in ResourceCategory]}


@router.get("/tags/list")
async def list_tags():
    """List all tags with usage count."""

    try:
        container = db.get_container("resources")

        # Get all resources
        query = "SELECT c.tags FROM c WHERE IS_DEFINED(c.tags)"
        items = list(
            container.query_items(query=query, enable_cross_partition_query=True)
        )

        # Count tag usage
        tag_counts = {}
        for item in items:
            for tag in item.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Sort by usage count
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "tags": [{"tag": tag, "count": count} for tag, count in sorted_tags]
        }

    except Exception as e:
        logger.error(f"Error listing tags: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tags: {e}")
