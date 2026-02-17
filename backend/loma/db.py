"""
Database layer — Supabase PostgreSQL via supabase-py.
Provides functions for users, rewrites, and events tables.
Falls back gracefully when Supabase is not configured (local dev).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import config

logger = logging.getLogger("loma.db")

_client = None


def _get_client():
    """Lazy-init Supabase client. Returns None if not configured."""
    global _client
    if _client is not None:
        return _client
    if not config.SUPABASE_URL or not config.SUPABASE_SERVICE_KEY:
        logger.warning("Supabase not configured — database operations will be skipped")
        return None
    try:
        from supabase import create_client

        _client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
        return _client
    except ImportError:
        logger.warning("supabase-py not installed — database operations will be skipped")
        return None
    except Exception as e:
        logger.error("Failed to create Supabase client: %s", e)
        return None


# ---------- Users ----------

def get_user_by_id(user_id: str) -> dict | None:
    client = _get_client()
    if not client:
        return None
    try:
        result = client.table("users").select("*").eq("id", user_id).single().execute()
        return result.data
    except Exception as e:
        logger.error("get_user_by_id failed: %s", e)
        return None


def upsert_user(user_id: str, email: str, auth_provider: str = "google") -> dict | None:
    client = _get_client()
    if not client:
        return None
    try:
        now = datetime.now(timezone.utc).isoformat()
        result = client.table("users").upsert(
            {
                "id": user_id,
                "email": email,
                "auth_provider": auth_provider,
                "updated_at": now,
            },
            on_conflict="id",
        ).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error("upsert_user failed: %s", e)
        return None


def get_user_subscription(user_id: str) -> dict:
    """Returns subscription info: tier, payg_balance, rewrites_today."""
    client = _get_client()
    if not client:
        return {"tier": "free", "payg_balance": 0, "rewrites_today": 0}
    try:
        result = client.table("users").select(
            "subscription_tier,payg_balance,rewrites_today,last_rewrite_date"
        ).eq("id", user_id).single().execute()
        data = result.data or {}
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rewrites_today = data.get("rewrites_today", 0)
        if data.get("last_rewrite_date") != today:
            rewrites_today = 0
        return {
            "tier": data.get("subscription_tier", "free"),
            "payg_balance": data.get("payg_balance", 0),
            "rewrites_today": rewrites_today,
        }
    except Exception as e:
        logger.error("get_user_subscription failed: %s", e)
        return {"tier": "free", "payg_balance": 0, "rewrites_today": 0}


def increment_rewrite_count(user_id: str) -> None:
    """Increment daily rewrite counter. Deduct PAYG credit atomically if applicable.

    Uses an RPC function for PAYG deduction to prevent race conditions.
    Falls back to read-then-write if the RPC is not available.
    """
    client = _get_client()
    if not client:
        return
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sub = get_user_subscription(user_id)
        new_count = sub["rewrites_today"] + 1

        if sub["tier"] == "payg" and sub["payg_balance"] > 0:
            # Atomic: decrement balance and update count in one operation
            # Uses Postgres: UPDATE ... SET payg_balance = GREATEST(payg_balance - 1, 0)
            try:
                client.rpc("decrement_payg_and_count", {
                    "p_user_id": user_id,
                    "p_new_count": new_count,
                    "p_date": today,
                }).execute()
                return
            except Exception:
                # RPC not available — fall back to conditional update
                client.table("users").update({
                    "rewrites_today": new_count,
                    "last_rewrite_date": today,
                    "payg_balance": max(sub["payg_balance"] - 1, 0),
                }).eq("id", user_id).gte("payg_balance", 1).execute()
                return

        client.table("users").update({
            "rewrites_today": new_count,
            "last_rewrite_date": today,
        }).eq("id", user_id).execute()
    except Exception as e:
        logger.error("increment_rewrite_count failed: %s", e)


# ---------- Rewrites ----------

def store_rewrite(user_id: str | None, rewrite_data: dict) -> None:
    """Persist a completed rewrite to the rewrites table."""
    client = _get_client()
    if not client:
        return
    try:
        row = {
            "id": rewrite_data.get("rewrite_id"),
            "user_id": user_id,
            "input_text": rewrite_data.get("original_text", ""),
            "output_text": rewrite_data.get("output_text", ""),
            "detected_intent": rewrite_data.get("detected_intent"),
            "intent_confidence": rewrite_data.get("intent_confidence"),
            "routing_tier": rewrite_data.get("routing_tier"),
            "output_language": rewrite_data.get("output_language"),
            "platform": rewrite_data.get("platform"),
            "tone": rewrite_data.get("tone"),
            "language_mix": rewrite_data.get("language_mix"),
            "scores": rewrite_data.get("scores"),
            "response_time_ms": rewrite_data.get("response_time_ms"),
        }
        client.table("rewrites").insert(row).execute()
    except Exception as e:
        logger.error("store_rewrite failed: %s", e)


# ---------- Events / Analytics ----------

def log_event(user_id: str | None, event_name: str, event_data: dict | None = None) -> None:
    """Store an analytics event."""
    client = _get_client()
    if not client:
        return
    try:
        client.table("events").insert(
            {
                "user_id": user_id,
                "event_name": event_name,
                "event_data": event_data or {},
            }
        ).execute()
    except Exception as e:
        logger.error("log_event failed: %s", e)
