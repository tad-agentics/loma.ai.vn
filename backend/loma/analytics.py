"""
Analytics — track loma_* events server-side.
Events are stored in Supabase `events` table via db module.

Improvements over v1:
- Acceptance rate computation per intent and platform
- User correction capture (post-edit diff tracking)
"""
from __future__ import annotations

import logging
from typing import Any

from . import db

logger = logging.getLogger("loma.analytics")

# Standard event names (Tech Spec v1.5, Section 3.8)
EVENT_REWRITE = "loma_rewrite"
EVENT_USE = "loma_use"
EVENT_COPY = "loma_copy"
EVENT_DISMISS = "loma_dismiss"
EVENT_TONE_CHANGE = "loma_tone_change"
EVENT_INTENT_PICK = "loma_intent_pick"
EVENT_ORIGINAL_EXPANDED = "loma_original_expanded"
EVENT_QUOTA_HIT = "loma_quota_hit"
EVENT_ERROR = "loma_error"
# New events
EVENT_USER_EDIT = "loma_user_edit"  # User edited text after accepting


def track(
    event_name: str,
    user_id: str | None = None,
    properties: dict[str, Any] | None = None,
) -> None:
    """
    Record an analytics event. Non-blocking — failures are logged, not raised.
    """
    try:
        db.log_event(user_id=user_id, event_name=event_name, event_data=properties)
    except Exception as e:
        logger.error("analytics.track failed for %s: %s", event_name, e)


def track_rewrite(user_id: str | None, rewrite_result: dict) -> None:
    """Convenience: track a completed rewrite with standard properties."""
    track(
        EVENT_REWRITE,
        user_id=user_id,
        properties={
            "rewrite_id": rewrite_result.get("rewrite_id"),
            "detected_intent": rewrite_result.get("detected_intent"),
            "routing_tier": rewrite_result.get("routing_tier"),
            "output_language": rewrite_result.get("output_language"),
            "response_time_ms": rewrite_result.get("response_time_ms"),
            "language_mix": rewrite_result.get("language_mix"),
            "scores": rewrite_result.get("scores"),
        },
    )


def track_user_edit(
    user_id: str | None,
    rewrite_id: str,
    original_output: str,
    edited_output: str,
    detected_intent: str,
    platform: str | None = None,
) -> None:
    """
    Track when a user edits the rewrite output after accepting.
    Captures the diff as implicit feedback about rewrite quality.
    """
    if not original_output or not edited_output:
        return
    if original_output == edited_output:
        return  # No actual edit

    # Compute basic diff stats
    orig_words = set(original_output.lower().split())
    edited_words = set(edited_output.lower().split())
    added = edited_words - orig_words
    removed = orig_words - edited_words

    track(
        EVENT_USER_EDIT,
        user_id=user_id,
        properties={
            "rewrite_id": rewrite_id,
            "detected_intent": detected_intent,
            "platform": platform,
            "original_length": len(original_output),
            "edited_length": len(edited_output),
            "words_added": len(added),
            "words_removed": len(removed),
            "edit_distance_pct": round(
                (len(added) + len(removed)) / max(len(orig_words), 1) * 100, 1
            ),
        },
    )


def compute_acceptance_rates(
    user_id: str | None = None,
    days: int = 30,
) -> dict[str, Any] | None:
    """
    Compute acceptance rate (loma_use / loma_rewrite) per intent.
    Returns aggregate stats or None if DB is unavailable.

    Returns:
    - overall_rate: float (0.0-1.0)
    - by_intent: {intent_name: {"rewrites": N, "uses": N, "rate": float}}
    """
    client = db._get_client()
    if not client:
        return None

    try:
        # Fetch recent rewrite and use events
        rewrite_events = (
            client.table("events")
            .select("event_data")
            .eq("event_name", EVENT_REWRITE)
            .order("created_at", desc=True)
            .limit(1000)
            .execute()
        )
        use_events = (
            client.table("events")
            .select("event_data")
            .eq("event_name", EVENT_USE)
            .order("created_at", desc=True)
            .limit(1000)
            .execute()
        )

        # Count by intent
        rewrite_by_intent: dict[str, int] = {}
        total_rewrites = 0

        for row in (rewrite_events.data or []):
            data = row.get("event_data") or {}
            intent = data.get("detected_intent", "unknown")
            rewrite_by_intent[intent] = rewrite_by_intent.get(intent, 0) + 1
            total_rewrites += 1

        use_by_intent: dict[str, int] = {}
        total_uses = 0

        for row in (use_events.data or []):
            data = row.get("event_data") or {}
            intent = data.get("detected_intent", "unknown")
            use_by_intent[intent] = use_by_intent.get(intent, 0) + 1
            total_uses += 1

        overall_rate = total_uses / max(total_rewrites, 1)

        by_intent = {}
        for intent in set(list(rewrite_by_intent.keys()) + list(use_by_intent.keys())):
            r = rewrite_by_intent.get(intent, 0)
            u = use_by_intent.get(intent, 0)
            by_intent[intent] = {
                "rewrites": r,
                "uses": u,
                "rate": round(u / max(r, 1), 3),
            }

        return {
            "overall_rate": round(overall_rate, 3),
            "total_rewrites": total_rewrites,
            "total_uses": total_uses,
            "by_intent": by_intent,
        }
    except Exception as e:
        logger.error("compute_acceptance_rates failed: %s", e)
        return None
