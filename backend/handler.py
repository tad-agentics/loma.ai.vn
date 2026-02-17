"""
Lambda entry for Loma rewrite API.
Event: API Gateway HTTP API (payload v2) or direct invoke with body.
Includes: auth, billing quota check, analytics, error handling.
"""
from __future__ import annotations

import json
import logging

from loma import analytics, auth, billing, db
from loma.pipeline import run_rewrite

logger = logging.getLogger("loma.handler")

_JSON_HEADERS = {"Content-Type": "application/json"}


def handler(event: dict, context: object) -> dict:
    """Route API requests."""
    path = event.get("rawPath", "") or event.get("path", "")

    # Health check
    if path.endswith("/health"):
        return _json_response(200, {"ok": True, "service": "loma-rewrite"})

    # Analytics event
    if path.endswith("/events"):
        return _handle_event(event)

    # User edit tracking (post-accept correction capture)
    if path.endswith("/user-edit"):
        return _handle_user_edit(event)

    # Acceptance rates (analytics dashboard)
    if path.endswith("/stats/acceptance"):
        return _handle_acceptance_rates(event)

    # Rewrite endpoint (default)
    return _handle_rewrite(event)


def _handle_rewrite(event: dict) -> dict:
    """Handle POST /api/v1/rewrite."""
    # Parse body
    try:
        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)
    except json.JSONDecodeError:
        return _json_response(400, {
            "error": "invalid_json",
            "message": "Invalid JSON body.",
            "message_vi": "Dữ liệu gửi lên không đúng định dạng.",
        })

    # Auth (optional — anonymous users get limited free tier)
    headers = event.get("headers") or {}
    token = auth.get_bearer_token(headers)
    user_id = auth.extract_user_id(token)

    # Quota check
    quota = billing.check_quota(user_id)
    if not quota["allowed"]:
        analytics.track(analytics.EVENT_QUOTA_HIT, user_id=user_id, properties={"reason": quota["reason"]})
        msg = "Free limit reached. Add credit to continue."
        msg_vi = "Bạn đã dùng hết lượt miễn phí. Nạp tiền để tiếp tục."
        if quota["reason"] == "payg_exhausted":
            msg = "PAYG credits exhausted. Purchase more credits."
            msg_vi = "Đã hết lượt PAYG. Mua thêm để tiếp tục."
        return _json_response(429, {
            "error": quota["reason"],
            "message": msg,
            "message_vi": msg_vi,
            "tier": quota["tier"],
            "remaining": quota["remaining"],
        })

    # Extract params
    input_text = body.get("input_text") or ""
    platform = body.get("platform")
    tone = body.get("tone") or "professional"
    language_mix = body.get("language_mix")
    intent_override = body.get("intent")
    output_language = body.get("output_language")
    output_language_source = body.get("output_language_source")

    # Run pipeline
    try:
        result = run_rewrite(
            input_text=input_text,
            platform=platform,
            tone=tone,
            language_mix_in=language_mix,
            intent_override=intent_override,
            output_language_in=output_language,
            output_language_source_in=output_language_source,
        )
    except Exception as e:
        logger.exception("Pipeline error: %s", e)
        analytics.track(analytics.EVENT_ERROR, user_id=user_id, properties={"error": str(e)})
        return _json_response(500, {
            "error": "pipeline_error",
            "message": "Something went wrong. Please try again.",
            "message_vi": "Có lỗi xảy ra. Vui lòng thử lại.",
        })

    if "error" in result:
        status = 400 if result["error"] in ("text_too_short", "text_too_long") else 500
        return _json_response(status, result)

    # Success — increment usage, store rewrite, track analytics
    if user_id:
        db.increment_rewrite_count(user_id)
    result["payg_balance_remaining"] = quota.get("remaining")
    result["tier"] = quota.get("tier")

    db.store_rewrite(user_id, result)
    analytics.track_rewrite(user_id, result)

    return _json_response(200, result)


def _handle_event(event: dict) -> dict:
    """Handle POST /api/v1/events — client-side analytics."""
    try:
        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)
    except json.JSONDecodeError:
        return _json_response(400, {"error": "invalid_json"})

    headers = event.get("headers") or {}
    token = auth.get_bearer_token(headers)
    user_id = auth.extract_user_id(token)

    event_name = body.get("event_name", "")
    event_data = body.get("event_data", {})
    if event_name:
        analytics.track(event_name, user_id=user_id, properties=event_data)
    return _json_response(200, {"ok": True})


def _handle_user_edit(event: dict) -> dict:
    """Handle POST /api/v1/user-edit — capture post-accept text edits."""
    try:
        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)
    except json.JSONDecodeError:
        return _json_response(400, {"error": "invalid_json"})

    headers = event.get("headers") or {}
    token = auth.get_bearer_token(headers)
    user_id = auth.extract_user_id(token)

    analytics.track_user_edit(
        user_id=user_id,
        rewrite_id=body.get("rewrite_id", ""),
        original_output=body.get("original_output", ""),
        edited_output=body.get("edited_output", ""),
        detected_intent=body.get("detected_intent", ""),
        platform=body.get("platform"),
    )
    return _json_response(200, {"ok": True})


def _handle_acceptance_rates(event: dict) -> dict:
    """Handle GET /api/v1/stats/acceptance — return acceptance rate metrics."""
    rates = analytics.compute_acceptance_rates()
    if rates is None:
        return _json_response(200, {
            "ok": False,
            "message": "Database not configured — acceptance rates unavailable.",
        })
    return _json_response(200, {"ok": True, **rates})


def _json_response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": _JSON_HEADERS,
        "body": json.dumps(body, ensure_ascii=False),
    }
