"""Shared Access Key authentication middleware."""
from fastapi import Header, HTTPException, status
from src.config import settings
import logging

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

    # Verify token matches configured API key
    if token != settings.api_access_key:
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True
