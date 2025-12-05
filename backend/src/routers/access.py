"""Access control router for user authorization and management."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
from src.database import db
from src.models import (
    AllowedUser,
    AllowedUserCreate,
    AllowedUserUpdate,
    AccessRequest,
    AccessRequestCreate,
    AccessVerifyResponse,
    UserRole,
    UserStatus,
    AccessRequestStatus,
)
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/access", tags=["access"])

INITIAL_ADMIN_USERS = [
    {"email": "alaster.sagar@fourth.com", "name": "Alaster Sagar"},
    {"email": "bernard.poostchi@fourth.com", "name": "Bernard Poostchi"},
    {"email": "borja.soler@fourth.com", "name": "Borja Soler"},
    {"email": "boyan.asenov@fourth.com", "name": "Boyan Asenov"},
    {"email": "carly.hodges@fourth.com", "name": "Carly Hodges"},
    {"email": "christian.berthelsen@fourth.com", "name": "Christian Berthelsen"},
    {"email": "danny.shine@fourth.com", "name": "Danny Shine"},
    {"email": "denis.brooker@fourth.com", "name": "Denis Brooker"},
    {"email": "jeffrey.rosser@fourth.com", "name": "Jeffrey Rosser"},
    {"email": "mark.beynon@fourth.com", "name": "Mark Beynon"},
    {"email": "dimitar.stoynev@fourth.com", "name": "Dimitar Stoynev"},
    {"email": "david.hayes@fourth.com", "name": "David Hayes"},
]


def get_allowed_users_container():
    container = db.get_container("allowed_users")
    if not container:
        raise HTTPException(status_code=500, detail="Allowed users container not initialized")
    return container


def get_access_requests_container():
    container = db.get_container("access_requests")
    if not container:
        raise HTTPException(status_code=500, detail="Access requests container not initialized")
    return container


@router.get("/verify", response_model=AccessVerifyResponse)
async def verify_access(email: str = Query(..., description="User email to verify")):
    """Check if user is authorized to access the platform."""
    try:
        container = get_allowed_users_container()
        email_lower = email.lower()

        query = "SELECT * FROM c WHERE LOWER(c.email) = @email AND c.status = @status"
        params = [
            {"name": "@email", "value": email_lower},
            {"name": "@status", "value": UserStatus.ACTIVE.value},
        ]

        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

        if items:
            user = items[0]
            return AccessVerifyResponse(
                authorized=True,
                role=user.get("role"),
                user_id=user.get("id"),
                name=user.get("name"),
            )

        return AccessVerifyResponse(authorized=False)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying access: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request")
async def create_access_request(request: AccessRequestCreate):
    """Submit a new access request."""
    try:
        container = get_access_requests_container()
        users_container = get_allowed_users_container()
        email_lower = request.email.lower()

        existing_user_query = "SELECT * FROM c WHERE LOWER(c.email) = @email"
        existing_users = list(users_container.query_items(
            query=existing_user_query,
            parameters=[{"name": "@email", "value": email_lower}],
            enable_cross_partition_query=True
        ))

        if existing_users:
            raise HTTPException(status_code=400, detail="User already has access or is pending approval")

        pending_query = "SELECT * FROM c WHERE LOWER(c.email) = @email AND c.status = @status"
        pending_requests = list(container.query_items(
            query=pending_query,
            parameters=[
                {"name": "@email", "value": email_lower},
                {"name": "@status", "value": AccessRequestStatus.PENDING.value},
            ],
            enable_cross_partition_query=True
        ))

        if pending_requests:
            raise HTTPException(status_code=400, detail="Access request already pending")

        request_id = str(uuid.uuid4())
        now = datetime.utcnow()

        new_request = AccessRequest(
            id=request_id,
            email=request.email,
            name=request.name,
            reason=request.reason,
            status=AccessRequestStatus.PENDING,
            created_at=now,
        )

        item = new_request.model_dump(mode="json")
        container.create_item(body=item)

        logger.info(f"Created access request: {request_id} for {request.email}")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating access request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requests", response_model=List[dict])
async def list_access_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all access requests (admin only)."""
    try:
        container = get_access_requests_container()

        conditions = []
        params = []

        if status:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status})

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"SELECT * FROM c WHERE {where_clause} ORDER BY c.created_at DESC OFFSET @offset LIMIT @limit"
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
        logger.error(f"Error listing access requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/requests/{request_id}/approve")
async def approve_access_request(
    request_id: str,
    role: UserRole = Query(UserRole.USER, description="Role to assign"),
    reviewer_email: str = Query(..., description="Email of the admin approving"),
):
    """Approve an access request and create allowed user (admin only)."""
    try:
        requests_container = get_access_requests_container()
        users_container = get_allowed_users_container()

        try:
            request = requests_container.read_item(item=request_id, partition_key=request_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Access request {request_id} not found")

        if request.get("status") != AccessRequestStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Request already processed")

        now = datetime.utcnow()
        user_id = str(uuid.uuid4())

        new_user = AllowedUser(
            id=user_id,
            email=request.get("email"),
            name=request.get("name"),
            role=role,
            status=UserStatus.ACTIVE,
            approved_by=reviewer_email,
            approved_at=now,
            created_at=now,
        )

        user_item = new_user.model_dump(mode="json")
        users_container.create_item(body=user_item)

        request["status"] = AccessRequestStatus.APPROVED.value
        request["reviewed_by"] = reviewer_email
        request["reviewed_at"] = now.isoformat()
        requests_container.replace_item(item=request_id, body=request)

        logger.info(f"Approved access request {request_id}, created user {user_id}")
        return {"request": request, "user": user_item}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving access request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/requests/{request_id}/deny")
async def deny_access_request(
    request_id: str,
    reviewer_email: str = Query(..., description="Email of the admin denying"),
):
    """Deny an access request (admin only)."""
    try:
        container = get_access_requests_container()

        try:
            request = container.read_item(item=request_id, partition_key=request_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Access request {request_id} not found")

        if request.get("status") != AccessRequestStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Request already processed")

        now = datetime.utcnow()
        request["status"] = AccessRequestStatus.DENIED.value
        request["reviewed_by"] = reviewer_email
        request["reviewed_at"] = now.isoformat()

        container.replace_item(item=request_id, body=request)

        logger.info(f"Denied access request {request_id}")
        return request
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error denying access request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", response_model=List[dict])
async def list_allowed_users(
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all allowed users (admin only)."""
    try:
        container = get_allowed_users_container()

        conditions = []
        params = []

        if role:
            conditions.append("c.role = @role")
            params.append({"name": "@role", "value": role})
        if status:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status})

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"SELECT * FROM c WHERE {where_clause} ORDER BY c.created_at DESC OFFSET @offset LIMIT @limit"
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
        logger.error(f"Error listing allowed users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users")
async def create_allowed_user(user: AllowedUserCreate, approver_email: str = Query(...)):
    """Add a new allowed user directly (admin only)."""
    try:
        container = get_allowed_users_container()
        email_lower = user.email.lower()

        existing_query = "SELECT * FROM c WHERE LOWER(c.email) = @email"
        existing = list(container.query_items(
            query=existing_query,
            parameters=[{"name": "@email", "value": email_lower}],
            enable_cross_partition_query=True
        ))

        if existing:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        user_id = str(uuid.uuid4())
        now = datetime.utcnow()

        new_user = AllowedUser(
            id=user_id,
            email=user.email,
            name=user.name,
            role=user.role,
            status=UserStatus.ACTIVE,
            approved_by=approver_email,
            approved_at=now,
            created_at=now,
        )

        item = new_user.model_dump(mode="json")
        container.create_item(body=item)

        logger.info(f"Created allowed user: {user_id}")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating allowed user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/users/{user_id}")
async def update_allowed_user(user_id: str, update: AllowedUserUpdate):
    """Update an allowed user (admin only)."""
    try:
        container = get_allowed_users_container()

        try:
            existing = container.read_item(item=user_id, partition_key=user_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

        update_data = update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if value is not None:
                if hasattr(value, 'value'):
                    existing[key] = value.value
                else:
                    existing[key] = value

        container.replace_item(item=user_id, body=existing)

        logger.info(f"Updated allowed user: {user_id}")
        return existing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating allowed user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_allowed_user(user_id: str):
    """Remove an allowed user (admin only)."""
    try:
        container = get_allowed_users_container()

        try:
            container.delete_item(item=user_id, partition_key=user_id)
            logger.info(f"Deleted allowed user: {user_id}")
            return {"message": f"User {user_id} deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting allowed user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seed-admins")
async def seed_initial_admins():
    """Seed initial admin users. Only works if no users exist."""
    try:
        container = get_allowed_users_container()

        existing = list(container.query_items(
            query="SELECT VALUE COUNT(1) FROM c",
            enable_cross_partition_query=True
        ))

        if existing and existing[0] > 0:
            return {"message": "Users already exist, skipping seed", "existing_count": existing[0]}

        now = datetime.utcnow()
        created_users = []

        for admin in INITIAL_ADMIN_USERS:
            user_id = str(uuid.uuid4())
            new_user = AllowedUser(
                id=user_id,
                email=admin["email"],
                name=admin["name"],
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                approved_by="system",
                approved_at=now,
                created_at=now,
            )

            item = new_user.model_dump(mode="json")
            container.create_item(body=item)
            created_users.append(admin["email"])

        logger.info(f"Seeded {len(created_users)} initial admin users")
        return {"message": f"Created {len(created_users)} admin users", "users": created_users}
    except Exception as e:
        logger.error(f"Error seeding admin users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-count")
async def get_pending_request_count():
    """Get count of pending access requests (for sidebar badge)."""
    try:
        container = get_access_requests_container()

        query = "SELECT VALUE COUNT(1) FROM c WHERE c.status = @status"
        params = [{"name": "@status", "value": AccessRequestStatus.PENDING.value}]

        result = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        count = result[0] if result else 0

        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting pending count: {e}")
        raise HTTPException(status_code=500, detail=str(e))
