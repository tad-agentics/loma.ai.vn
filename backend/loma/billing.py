"""
Billing — Stripe + PayOS integration, tier enforcement, webhook handling.
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


def handle_stripe_webhook(payload: bytes, sig_header: str) -> dict[str, Any]:
    """
    Process Stripe webhook events.
    Returns {"ok": True} on success, {"error": str} on failure.
    """
    if not config.STRIPE_SECRET_KEY or not config.STRIPE_WEBHOOK_SECRET:
        return {"error": "Stripe not configured"}

    try:
        import stripe

        stripe.api_key = config.STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(
            payload, sig_header, config.STRIPE_WEBHOOK_SECRET
        )
    except ImportError:
        return {"error": "stripe package not installed"}
    except Exception as e:
        logger.error("Stripe webhook verification failed: %s", e)
        return {"error": "webhook_verification_failed"}

    event_type = event.get("type", "")
    data_object = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(data_object)
    elif event_type == "customer.subscription.updated":
        _handle_subscription_updated(data_object)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(data_object)

    return {"ok": True}


def _handle_checkout_completed(session: dict) -> None:
    """Handle successful checkout — PAYG pack or Pro subscription."""
    user_id = session.get("client_reference_id")
    if not user_id:
        return

    mode = session.get("mode")
    if mode == "payment":
        # PAYG pack purchase
        _add_payg_credits(user_id, config.PAYG_PACK_SIZE)
    elif mode == "subscription":
        # Pro subscription started
        _set_subscription_tier(user_id, "pro")


def _handle_subscription_updated(subscription: dict) -> None:
    """Handle subscription status changes."""
    user_id = subscription.get("metadata", {}).get("user_id")
    if not user_id:
        return
    status = subscription.get("status")
    if status == "active":
        _set_subscription_tier(user_id, "pro")
    elif status in ("past_due", "canceled", "unpaid"):
        _set_subscription_tier(user_id, "free")


def _handle_subscription_deleted(subscription: dict) -> None:
    """Handle subscription cancellation."""
    user_id = subscription.get("metadata", {}).get("user_id")
    if user_id:
        _set_subscription_tier(user_id, "free")


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
