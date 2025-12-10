"""Shared Access Key authentication middleware."""
from fastapi import Header, HTTPException, status, Depends
from src.config import settings
import logging
import secrets

logger = logging.getLogger(__name__)


async def verify_api_key(authorization: str = Header(None)) -> bool:
    """
    Verify API access key from Authorization header.

    Args:
        authorization: Authorization header (format: "Bearer {key}")

    Returns:
        True if valid

    Raises:
        HTTPException: If key is missing or invalid
    """
    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer {token}" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        logger.warning(f"Invalid Authorization header format: {authorization}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token matches configured API key using timing-safe comparison
    if not secrets.compare_digest(token.encode('utf-8'), settings.api_access_key.encode('utf-8')):
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


async def verify_admin_role(
    x_user_email: str = Header(None, alias="X-User-Email"),
    _api_key_valid: bool = Depends(verify_api_key)
) -> str:
    """
    Verify caller has admin role. Requires X-User-Email header.

    Args:
        x_user_email: Email of the calling user from header

    Returns:
        The verified admin email

    Raises:
        HTTPException: If email missing, user not found, or not admin
    """
    if not x_user_email:
        logger.warning("Missing X-User-Email header for admin endpoint")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Email header required for admin operations",
        )

    from src.database import db

    container = db.get_container("allowed_users")
    if not container:
        raise HTTPException(status_code=500, detail="Database not initialized")

    email_lower = x_user_email.lower()
    query = "SELECT * FROM c WHERE LOWER(c.email) = @email AND c.status = @status"
    params = [
        {"name": "@email", "value": email_lower},
        {"name": "@status", "value": "active"},
    ]

    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    if not items:
        logger.warning(f"Admin verification failed: user {x_user_email} not found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized",
        )

    user = items[0]
    if user.get("role") != "admin":
        logger.warning(f"Admin verification failed: user {x_user_email} is not admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )

    logger.debug(f"Admin verified: {x_user_email}")
    return x_user_email
