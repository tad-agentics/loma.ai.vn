"""
Cost router — route to rules | haiku | sonnet (Tech Spec 3.5, v1.5 output_language).
"""
from __future__ import annotations

# Intents that can be handled by rules for very short/simple text
LOW_COMPLEXITY_INTENTS = frozenset({"follow_up", "say_no", "apologize", "general"})


def can_rules_handle(input_text: str, intent: str) -> bool:
    """
    Rules engine for high-confidence, short, simple cases that match cultural patterns.
    When in doubt, route up (Haiku/Sonnet).
    """
    if len(input_text) > 200:
        return False
    if intent not in LOW_COMPLEXITY_INTENTS:
        return False
    # Enable rules matching for short, low-complexity intents.
    # The rules engine returns None if no pattern matches, so pipeline
    # will fall through to LLM automatically.
    return True


def route_rewrite(
    input_text: str,
    language_mix: dict[str, float],
    intent: str,
    intent_confidence: float,
    output_language: str | None = None,
) -> str:
    """
    Returns "rules" | "haiku" | "sonnet".
    output_language: "en" | "vi_casual" | "vi_formal" | "vi_admin" (Tech Spec v1.5).
    """
    # Vietnamese admin (công văn) → rules engine, template-driven, zero LLM
    if output_language == "vi_admin":
        return "rules"

    if can_rules_handle(input_text, intent):
        return "rules"

    vi_ratio = language_mix.get("vi_ratio", 0.0)

    # Vietnamese casual/formal short text → Haiku (Tech Spec v1.5)
    if output_language in ("vi_casual", "vi_formal") and len(input_text) < 150:
        return "haiku"

    # Pure English rough text → Haiku
    if vi_ratio < 0.1 and intent == "general":
        return "haiku"
    # Short, low-complexity
    if len(input_text) < 100 and intent in LOW_COMPLEXITY_INTENTS:
        return "haiku"

    # Vietnamese or code-switched, or complex intents → Sonnet
    return "sonnet"
