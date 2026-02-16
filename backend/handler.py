"""
Lambda entry for Loma rewrite API.
Event: API Gateway HTTP API (payload v2) or direct invoke with body.
"""
from __future__ import annotations

import json

from loma.pipeline import run_rewrite


def handler(event: dict, context: object) -> dict:
    """
    Handle POST /api/v1/rewrite.
    Expects event["body"] as JSON string with input_text, platform?, tone?, language_mix?, intent?.
    """
    status = 200
    headers = {"Content-Type": "application/json"}

    try:
        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({
                "error": "invalid_json",
                "message": "Invalid JSON body.",
                "message_vi": "Dữ liệu gửi lên không đúng định dạng.",
            }),
        }

    input_text = body.get("input_text") or ""
    platform = body.get("platform")
    tone = body.get("tone") or "professional"
    language_mix = body.get("language_mix")
    intent_override = body.get("intent")
    output_language = body.get("output_language")  # en | vi_casual | vi_formal | vi_admin (Tech Spec v1.5)
    output_language_source = body.get("output_language_source")  # auto_domain | auto_intent | user_override | stored_pref

    result = run_rewrite(
        input_text=input_text,
        platform=platform,
        tone=tone,
        language_mix_in=language_mix,
        intent_override=intent_override,
        output_language_in=output_language,
        output_language_source_in=output_language_source,
    )

    if "error" in result:
        status = 400 if result["error"] in ("text_too_short", "text_too_long") else 500

    return {
        "statusCode": status,
        "headers": headers,
        "body": json.dumps(result, ensure_ascii=False),
    }
