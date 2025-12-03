"""Submissions router for internal ticketing and idea submissions."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
from src.database import db
from src.models import (
    Submission,
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionComment,
    CommentCreate,
    SubmissionStats,
    SubmissionStatus,
    SubmissionCategory,
    SubmissionPriority,
    Task,
    TaskStatus,
    TaskPriority,
    TaskCategory,
)
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


def get_submissions_container():
    container = db.get_container("submissions")
    if not container:
        raise HTTPException(status_code=500, detail="Submissions container not initialized")
    return container


def get_tasks_container():
    container = db.get_container("tasks")
    if not container:
        raise HTTPException(status_code=500, detail="Tasks container not initialized")
    return container


@router.get("", response_model=List[dict])
async def list_submissions(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by assignee"),
    submitted_by: Optional[str] = Query(None, description="Filter by submitter"),
    sort_by: Optional[str] = Query("date", description="Sort by: upvotes, date, priority"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all submissions with optional filters."""
    try:
        container = get_submissions_container()

        conditions = []
        params = []

        if status:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status})
        if category:
            conditions.append("c.category = @category")
            params.append({"name": "@category", "value": category})
        if priority:
            conditions.append("c.priority = @priority")
            params.append({"name": "@priority", "value": priority})
        if assigned_to:
            conditions.append("c.assigned_to = @assigned_to")
            params.append({"name": "@assigned_to", "value": assigned_to})
        if submitted_by:
            conditions.append("c.submitted_by = @submitted_by")
            params.append({"name": "@submitted_by", "value": submitted_by})

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        order_map = {
            "upvotes": "c.upvote_count DESC",
            "date": "c.submitted_at DESC",
            "priority": "c.priority ASC",
        }
        order_clause = order_map.get(sort_by, "c.submitted_at DESC")

        query = f"SELECT * FROM c WHERE {where_clause} ORDER BY {order_clause} OFFSET @offset LIMIT @limit"
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
        logger.error(f"Error listing submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=SubmissionStats)
async def get_submission_stats():
    """Get dashboard statistics for submissions."""
    try:
        container = get_submissions_container()

        items = list(container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))

        stats = {
            "total": len(items),
            "by_status": {},
            "by_category": {},
            "by_priority": {},
        }

        for item in items:
            status = item.get("status", "Unknown")
            category = item.get("category", "Unknown")
            priority = item.get("priority", "Unknown")

            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

        return stats
    except Exception as e:
        logger.error(f"Error getting submission stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{submission_id}")
async def get_submission(submission_id: str):
    """Get a single submission by ID."""
    try:
        container = get_submissions_container()

        try:
            item = container.read_item(item=submission_id, partition_key=submission_id)
            return item
        except Exception:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_submission(submission: SubmissionCreate):
    """Create a new submission."""
    try:
        container = get_submissions_container()

        submission_id = str(uuid.uuid4())
        now = datetime.utcnow()

        new_submission = Submission(
            id=submission_id,
            title=submission.title,
            description=submission.description,
            category=submission.category,
            priority=submission.priority,
            submitted_by=submission.submitted_by,
            submitted_at=now,
            tags=submission.tags,
            updated_at=now,
        )

        item = new_submission.model_dump(mode="json")
        container.create_item(body=item)

        logger.info(f"Created submission: {submission_id}")
        return item
    except Exception as e:
        logger.error(f"Error creating submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{submission_id}")
async def update_submission(submission_id: str, update: SubmissionUpdate):
    """Update a submission (admin only for status/assignee)."""
    try:
        container = get_submissions_container()

        try:
            existing = container.read_item(item=submission_id, partition_key=submission_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        update_data = update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if value is not None:
                if hasattr(value, 'value'):
                    existing[key] = value.value
                else:
                    existing[key] = value

        existing["updated_at"] = datetime.utcnow().isoformat()

        if update.status == SubmissionStatus.COMPLETED or update.status == SubmissionStatus.DECLINED:
            existing["resolved_at"] = datetime.utcnow().isoformat()

        container.replace_item(item=submission_id, body=existing)

        logger.info(f"Updated submission: {submission_id}")
        return existing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{submission_id}")
async def delete_submission(submission_id: str):
    """Delete a submission (admin only)."""
    try:
        container = get_submissions_container()

        try:
            container.delete_item(item=submission_id, partition_key=submission_id)
            logger.info(f"Deleted submission: {submission_id}")
            return {"message": f"Submission {submission_id} deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{submission_id}/upvote")
async def toggle_upvote(submission_id: str, user: str = Query(..., description="User performing the upvote")):
    """Toggle upvote on a submission."""
    try:
        container = get_submissions_container()

        try:
            existing = container.read_item(item=submission_id, partition_key=submission_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        upvotes = existing.get("upvotes", [])

        if user in upvotes:
            upvotes.remove(user)
            action = "removed"
        else:
            upvotes.append(user)
            action = "added"

        existing["upvotes"] = upvotes
        existing["upvote_count"] = len(upvotes)
        existing["updated_at"] = datetime.utcnow().isoformat()

        container.replace_item(item=submission_id, body=existing)

        logger.info(f"Upvote {action} for submission {submission_id} by {user}")
        return existing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling upvote: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{submission_id}/comments")
async def add_comment(submission_id: str, comment: CommentCreate):
    """Add a comment to a submission."""
    try:
        container = get_submissions_container()

        try:
            existing = container.read_item(item=submission_id, partition_key=submission_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        comment_id = str(uuid.uuid4())
        now = datetime.utcnow()

        new_comment = SubmissionComment(
            id=comment_id,
            user=comment.user,
            content=comment.content,
            created_at=now,
        )

        comments = existing.get("comments", [])
        comments.append(new_comment.model_dump(mode="json"))

        existing["comments"] = comments
        existing["updated_at"] = now.isoformat()

        container.replace_item(item=submission_id, body=existing)

        logger.info(f"Added comment {comment_id} to submission {submission_id}")
        return existing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{submission_id}/comments/{comment_id}")
async def update_comment(submission_id: str, comment_id: str, content: str = Query(...)):
    """Update a comment on a submission."""
    try:
        container = get_submissions_container()

        try:
            existing = container.read_item(item=submission_id, partition_key=submission_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        comments = existing.get("comments", [])
        comment_found = False

        for comment in comments:
            if comment.get("id") == comment_id:
                comment["content"] = content
                comment["updated_at"] = datetime.utcnow().isoformat()
                comment_found = True
                break

        if not comment_found:
            raise HTTPException(status_code=404, detail=f"Comment {comment_id} not found")

        existing["comments"] = comments
        existing["updated_at"] = datetime.utcnow().isoformat()

        container.replace_item(item=submission_id, body=existing)

        logger.info(f"Updated comment {comment_id} on submission {submission_id}")
        return existing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{submission_id}/comments/{comment_id}")
async def delete_comment(submission_id: str, comment_id: str):
    """Delete a comment from a submission."""
    try:
        container = get_submissions_container()

        try:
            existing = container.read_item(item=submission_id, partition_key=submission_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        comments = existing.get("comments", [])
        original_count = len(comments)
        comments = [c for c in comments if c.get("id") != comment_id]

        if len(comments) == original_count:
            raise HTTPException(status_code=404, detail=f"Comment {comment_id} not found")

        existing["comments"] = comments
        existing["updated_at"] = datetime.utcnow().isoformat()

        container.replace_item(item=submission_id, body=existing)

        logger.info(f"Deleted comment {comment_id} from submission {submission_id}")
        return existing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{submission_id}/convert-to-task")
async def convert_to_task(
    submission_id: str,
    category: Optional[str] = Query(None, description="Task category override"),
):
    """Convert a submission to a task."""
    try:
        submissions_container = get_submissions_container()
        tasks_container = get_tasks_container()

        try:
            submission = submissions_container.read_item(item=submission_id, partition_key=submission_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        if submission.get("linked_task_id"):
            raise HTTPException(status_code=400, detail="Submission already converted to task")

        priority_map = {
            "Critical": TaskPriority.CRITICAL,
            "High": TaskPriority.HIGH,
            "Medium": TaskPriority.MEDIUM,
            "Low": TaskPriority.LOW,
        }

        task_priority = priority_map.get(submission.get("priority"), TaskPriority.MEDIUM)

        if category:
            try:
                task_category = TaskCategory(category)
            except ValueError:
                task_category = TaskCategory.GOVERNANCE
        else:
            task_category = TaskCategory.GOVERNANCE

        task_id = str(uuid.uuid4())
        now = datetime.utcnow()

        task_description = f"{submission.get('description', '')}\n\n---\nConverted from submission: {submission_id}"

        new_task = Task(
            id=task_id,
            title=submission.get("title"),
            description=task_description,
            status=TaskStatus.PENDING,
            priority=task_priority,
            category=task_category,
            assigned_to=submission.get("assigned_to"),
            notes=f"Created from feedback submission by {submission.get('submitted_by')}",
            from_submission_id=submission_id,
            created_at=now,
            updated_at=now,
        )

        task_item = new_task.model_dump(mode="json")
        tasks_container.create_item(body=task_item)

        submission["linked_task_id"] = task_id
        submission["status"] = SubmissionStatus.IN_PROGRESS.value
        submission["updated_at"] = now.isoformat()

        submissions_container.replace_item(item=submission_id, body=submission)

        logger.info(f"Converted submission {submission_id} to task {task_id}")
        return {
            "submission": submission,
            "task": task_item,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting submission to task: {e}")
        raise HTTPException(status_code=500, detail=str(e))
