"""
Authentication — verify Supabase JWT tokens.
Extension sends Authorization: Bearer <token> on every API request.
Anonymous/unauthenticated users get a limited free tier (tracked by IP fallback).
"""
from __future__ import annotations

import logging
from typing import Any

import config

logger = logging.getLogger("loma.auth")


def verify_token(token: str | None) -> dict[str, Any] | None:
    """
    Verify a Supabase JWT and return the decoded payload.
    Returns None if token is missing or invalid.
    Payload includes: sub (user_id), email, exp, etc.
    """
    if not token:
        return None

    jwt_secret = config.SUPABASE_JWT_SECRET
    if not jwt_secret:
        logger.warning("SUPABASE_JWT_SECRET not configured — skipping token verification")
        return None

    try:
        import jwt as pyjwt

        payload = pyjwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except ImportError:
        logger.warning("PyJWT not installed — skipping token verification")
        return None
    except Exception as e:
        logger.debug("Token verification failed: %s", e)
        return None


def extract_user_id(token: str | None) -> str | None:
    """Extract user_id (sub) from a valid JWT. Returns None for anonymous."""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def get_bearer_token(headers: dict) -> str | None:
    """Extract Bearer token from request headers."""
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None
