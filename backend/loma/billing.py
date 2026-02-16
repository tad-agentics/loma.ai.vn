"""
Billing — tier enforcement, quota checking.
Tiers: free (5/day), payg (20 credits per pack), pro (unlimited).
"""
from __future__ import annotations

import logging
from typing import Any

import config
from . import db

logger = logging.getLogger("loma.billing")


def check_quota(user_id: str | None) -> dict[str, Any]:
    """
    Check if user can perform a rewrite.
    Returns: {"allowed": bool, "tier": str, "remaining": int|None, "reason": str|None}
    """
    if not user_id:
        # Anonymous: allow with daily limit (tracked client-side, soft enforcement)
        return {"allowed": True, "tier": "anonymous", "remaining": None, "reason": None}

    sub = db.get_user_subscription(user_id)
    tier = sub["tier"]

    if tier == "pro":
        return {"allowed": True, "tier": "pro", "remaining": None, "reason": None}

    if tier == "payg":
        balance = sub["payg_balance"]
        if balance > 0:
            return {"allowed": True, "tier": "payg", "remaining": balance, "reason": None}
        return {
            "allowed": False,
            "tier": "payg",
            "remaining": 0,
            "reason": "payg_exhausted",
        }

    # Free tier
    rewrites_today = sub["rewrites_today"]
    limit = config.FREE_REWRITES_PER_DAY
    if rewrites_today < limit:
        return {
            "allowed": True,
            "tier": "free",
            "remaining": limit - rewrites_today,
            "reason": None,
        }
    return {
        "allowed": False,
        "tier": "free",
        "remaining": 0,
        "reason": "free_limit_reached",
    }


def _add_payg_credits(user_id: str, credits: int) -> None:
    """Add PAYG credits to user's balance."""
    client = db._get_client()
    if not client:
        return
    try:
        sub = db.get_user_subscription(user_id)
        new_balance = sub["payg_balance"] + credits
        client.table("users").update(
            {"payg_balance": new_balance, "subscription_tier": "payg"}
        ).eq("id", user_id).execute()
    except Exception as e:
        logger.error("_add_payg_credits failed: %s", e)


def _set_subscription_tier(user_id: str, tier: str) -> None:
    """Update user's subscription tier."""
    client = db._get_client()
    if not client:
        return
    try:
        client.table("users").update({"subscription_tier": tier}).eq("id", user_id).execute()
    except Exception as e:
        logger.error("_set_subscription_tier failed: %s", e)
