"""
LLM integration — Claude Haiku / Sonnet (Tech Spec 3.5).
Requires ANTHROPIC_API_KEY in env. No streaming at launch if p95 < 2s.
"""
from __future__ import annotations

import os

USER_MESSAGE_TEMPLATE = "Rewrite this:\n\n{input_text}"


def call_claude(
    system_prompt: str,
    input_text: str,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1024,
) -> str:
    """
    Call Claude API. model should be 'claude-3-5-haiku-...' or 'claude-sonnet-4-...'.
    Returns the rewritten text only.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback for local dev: return placeholder so pipeline still runs
        return f"[LLM placeholder — set ANTHROPIC_API_KEY to call {model}]\n\nInput length: {len(input_text)} chars."

    try:
        from anthropic import Anthropic
    except ImportError:
        return "[LLM unavailable — install anthropic package]"

    client = Anthropic(api_key=api_key)
    user_message = USER_MESSAGE_TEMPLATE.format(input_text=input_text)

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    text = response.content[0].text if response.content else ""
    return text.strip()
