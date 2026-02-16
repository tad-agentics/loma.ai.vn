"""
Analytics — track loma_* events server-side.
Events are stored in Supabase `events` table via db module.
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
