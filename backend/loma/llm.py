"""
LLM integration — Claude Haiku / Sonnet (Tech Spec 3.5).
Requires ANTHROPIC_API_KEY in env. Includes timeout, retry, and error handling.
"""
from __future__ import annotations

import logging
import os
import time

logger = logging.getLogger("loma.llm")

USER_MESSAGE_TEMPLATE = "Rewrite this:\n\n{input_text}"

# Retry config
MAX_RETRIES = 1
RETRY_DELAY_S = 1.0
REQUEST_TIMEOUT_S = 15.0


def call_claude(
    system_prompt: str,
    input_text: str,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1024,
) -> str:
    """
    Call Claude API with timeout and retry.
    Returns the rewritten text only.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return f"[LLM placeholder — set ANTHROPIC_API_KEY to call {model}]\n\nInput length: {len(input_text)} chars."

    try:
        from anthropic import Anthropic, APITimeoutError, APIConnectionError, RateLimitError
    except ImportError:
        return "[LLM unavailable — install anthropic package]"

    client = Anthropic(api_key=api_key, timeout=REQUEST_TIMEOUT_S)
    user_message = USER_MESSAGE_TEMPLATE.format(input_text=input_text)

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            text = response.content[0].text if response.content else ""
            return text.strip()
        except RateLimitError as e:
            logger.warning("Claude rate limited (attempt %d): %s", attempt + 1, e)
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_S * (attempt + 1))
        except (APITimeoutError, APIConnectionError) as e:
            logger.warning("Claude connection error (attempt %d): %s", attempt + 1, e)
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_S)
        except Exception as e:
            logger.error("Claude API error: %s", e)
            last_error = e
            break

    logger.error("Claude API failed after %d attempts: %s", MAX_RETRIES + 1, last_error)
    raise RuntimeError(f"LLM call failed: {last_error}")
