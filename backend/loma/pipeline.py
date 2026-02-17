"""
Rewrite pipeline: language → intent → route → rules or LLM → quality score.
Single entry: run_rewrite(input_text, platform, tone, language_mix?, intent?).
"""
from __future__ import annotations

import time
import uuid

from . import intent as intent_module
from . import language, quality, router, rules_engine
from .intent import compute_intent_scores
from .language import compute_language_mix
from .llm import call_claude
from .prompt_assembly import build_system_prompt
from .quality import extract_entities, score_rewrite
from .router import route_rewrite

# Model IDs (adjust to latest if needed)
HAIKU_MODEL = "claude-3-5-haiku-20241022"
SONNET_MODEL = "claude-sonnet-4-20250514"


def run_rewrite(
    input_text: str,
    platform: str | None = None,
    tone: str = "professional",
    language_mix_in: dict | None = None,
    intent_override: str | None = None,
    output_language_in: str | None = None,
    output_language_source_in: str | None = None,
) -> dict:
    """
    Full pipeline. Returns dict matching API response shape:
    rewrite_id, output_text, original_text, detected_intent, intent_confidence,
    intent_detection_method, routing_tier, scores, language_mix, response_time_ms,
    output_language, output_language_source (Tech Spec v1.5).
    """
    start_ms = int(time.time() * 1000)
    original_text = (input_text or "").strip()
    if not original_text:
        return _error_response("text_too_short", start_ms)

    if len(original_text) > 5000:
        return _error_response("text_too_long", start_ms)

    # Language mix (server-side confirmation)
    language_mix = language_mix_in or compute_language_mix(original_text)

    # Intent
    if intent_override and intent_override in intent_module.INTENT_PATTERNS:
        detected_intent = intent_override
        intent_confidence = 1.0
        intent_method = "user_confirmed"
        intent_output_lang = intent_module.INTENT_PATTERNS.get(intent_override, {}).get("output_language")
    else:
        result = compute_intent_scores(original_text, language_mix, platform)
        detected_intent = result["intent"]
        intent_confidence = result["confidence"]
        intent_method = "heuristic_v1"
        intent_output_lang = result.get("output_language")

    # Output language: intent overrides client (Tech Spec 3.7)
    if intent_output_lang:
        output_language = intent_output_lang
        output_language_source = "auto_intent"
    elif output_language_in in ("en", "vi_casual", "vi_formal", "vi_admin"):
        output_language = output_language_in
        output_language_source = output_language_source_in or "stored_pref"
    else:
        output_language = "en"
        output_language_source = "default"

    # Routing (output_language-aware: vi_admin → rules)
    tier = route_rewrite(
        original_text, language_mix, detected_intent, intent_confidence, output_language
    )

    # Rewrite
    output_text: str | None = None
    if tier == "rules":
        output_text = rules_engine.apply_rules(
            original_text, detected_intent, output_language=output_language
        )
    if output_text is None:
        # Extract entities from input to inject into prompt for preservation
        raw_entities = extract_entities(original_text)
        entity_list = []
        for category, items in raw_entities.items():
            for item in items:
                entity_list.append({"text": item, "label": category})

        system_prompt = build_system_prompt(
            intent=detected_intent,
            tone=tone,
            language_mix=language_mix,
            platform=platform,
            entities=entity_list if entity_list else None,
            output_language=output_language,
        )
        model = SONNET_MODEL if tier == "sonnet" else HAIKU_MODEL
        output_text = call_claude(
            system_prompt=system_prompt,
            input_text=original_text,
            model=model,
        )
        if tier != "rules":
            tier = "sonnet" if model == SONNET_MODEL else "haiku"

    # Quality
    scores = score_rewrite(original_text, output_text)
    end_ms = int(time.time() * 1000)
    response_time_ms = end_ms - start_ms

    # Risk flags: surface entity preservation issues
    risk_flags = []
    if scores.get("entity_missing"):
        risk_flags.append({
            "type": "entity_missing",
            "details": scores["entity_missing"],
        })

    return {
        "rewrite_id": str(uuid.uuid4()),
        "output_text": output_text,
        "original_text": original_text,
        "detected_intent": detected_intent,
        "intent_confidence": round(intent_confidence, 4),
        "intent_detection_method": intent_method,
        "detected_slots": None,
        "ner_entities": None,
        "routing_tier": tier,
        "scores": scores,
        "risk_flags": risk_flags,
        "language_mix": language_mix,
        "response_time_ms": response_time_ms,
        "payg_balance_remaining": None,
        "output_language": output_language,
        "output_language_source": output_language_source,
    }


def _error_response(error: str, start_ms: int) -> dict:
    end_ms = int(time.time() * 1000)
    messages = {
        "text_too_short": ("Input text is required.", "Vui lòng nhập nội dung."),
        "text_too_long": ("Input text must be 5000 characters or less.", "Nội dung tối đa 5000 ký tự."),
    }
    msg, msg_vi = messages.get(error, ("Service error.", "Lỗi dịch vụ."))
    return {
        "error": error,
        "message": msg,
        "message_vi": msg_vi,
        "response_time_ms": end_ms - start_ms,
    }
