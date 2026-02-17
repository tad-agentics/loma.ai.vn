"""
Quality scorer — length reduction, entity preservation check, and semantic scoring.

Improvements over v1:
- Entity post-check: verifies names, numbers, amounts survive the rewrite
- Semantic quality score via Haiku (optional, background)
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger("loma.quality")


def compute_length_reduction_pct(original: str, rewritten: str) -> int:
    """Returns percentage (0-100) by which output is shorter. Can be negative if output is longer."""
    if not original:
        return 0
    orig_len = len(original)
    new_len = len(rewritten)
    if orig_len == 0:
        return 0
    reduction = (orig_len - new_len) / orig_len * 100
    return int(round(reduction))


# Patterns for extracting entities that must be preserved
_MONEY_PATTERN = re.compile(
    r"(?:\$[\d,.]+|[\d,.]+\s*(?:USD|VND|EUR|GBP)|\d+[\d,.]*\s*(?:đồng|triệu|tỷ))",
    re.IGNORECASE,
)
_NUMBER_PATTERN = re.compile(
    r"\b\d+(?:[.,]\d+)*%?\b"
)
_DATE_PATTERN = re.compile(
    r"\b(?:"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}"
    r"|(?:tháng\s+\d{1,2})"
    r"|Q[1-4]"
    r"|\d{1,2}/\d{1,2}(?:/\d{2,4})?"
    r")\b",
    re.IGNORECASE,
)
# Vietnamese proper names: capitalized sequences with possible diacritics
_PROPER_NAME_PATTERN = re.compile(
    r"\b[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ]"
    r"[a-zàáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]*"
    r"(?:\s+[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬĐÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ]"
    r"[a-zàáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]*){1,4}"
)
# Technical identifiers: PR #123, INV-2024-031, etc.
_IDENTIFIER_PATTERN = re.compile(
    r"(?:PR\s*#?\d+|#\d+|INV-[\w-]+|[A-Z]{2,}-\d+[\w-]*)",
    re.IGNORECASE,
)

# Common English words to exclude from "missing entity" checks
_COMMON_WORDS = frozenset({
    "The", "This", "That", "Here", "There", "What", "When", "Where", "How",
    "Please", "Thank", "Dear", "Best", "Kind", "Good", "Great",
    "Hi", "Hello", "Sorry", "Thanks",
})


def extract_entities(text: str) -> dict[str, list[str]]:
    """Extract entities that should be preserved through rewriting."""
    entities: dict[str, list[str]] = {
        "money": [],
        "numbers": [],
        "dates": [],
        "names": [],
        "identifiers": [],
    }
    entities["money"] = _MONEY_PATTERN.findall(text)
    entities["numbers"] = [n for n in _NUMBER_PATTERN.findall(text) if len(n) > 1]
    entities["dates"] = _DATE_PATTERN.findall(text)

    # Names: filter out common English words and very short matches
    raw_names = _PROPER_NAME_PATTERN.findall(text)
    entities["names"] = [
        n for n in raw_names
        if n.split()[0] not in _COMMON_WORDS and len(n) > 2
    ]

    entities["identifiers"] = _IDENTIFIER_PATTERN.findall(text)
    return entities


def check_entity_preservation(
    original_text: str, output_text: str
) -> dict:
    """
    Check which entities from the original are missing in the output.
    Returns {"missing": [...], "total_checked": int, "preserved_pct": float}.
    """
    entities = extract_entities(original_text)
    output_lower = output_text.lower()
    missing = []
    total = 0

    for category, items in entities.items():
        for item in items:
            total += 1
            # Normalize for comparison: strip whitespace, lowercase
            normalized = item.strip().lower()
            if normalized not in output_lower:
                # For money: also check without comma formatting
                alt = normalized.replace(",", "")
                if alt not in output_lower:
                    missing.append(f"{category}:{item}")

    preserved_pct = ((total - len(missing)) / total * 100) if total > 0 else 100.0
    return {
        "missing": missing,
        "total_checked": total,
        "preserved_pct": round(preserved_pct, 1),
    }


def score_rewrite(original_text: str, output_text: str) -> dict:
    """
    Returns quality metrics:
    - length_reduction_pct: percentage shorter (negative = longer)
    - entity_preserved_pct: percentage of entities preserved (0-100)
    - entity_missing: list of missing entities (empty = good)
    """
    entity_check = check_entity_preservation(original_text, output_text)

    return {
        "length_reduction_pct": compute_length_reduction_pct(original_text, output_text),
        "entity_preserved_pct": entity_check["preserved_pct"],
        "entity_missing": entity_check["missing"],
    }


def score_semantic_quality(
    original_text: str,
    output_text: str,
    intent: str,
) -> dict | None:
    """
    Use Haiku to score semantic preservation (1-5).
    Returns {"meaning_score": int, "tone_score": int, "issues": [str]} or None on failure.
    This is optional and designed to run as a background check, not blocking the response.
    """
    import os

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        from anthropic import Anthropic
    except ImportError:
        return None

    prompt = (
        f"You are a quality checker for a Vietnamese-to-English rewriting tool.\n\n"
        f"Original (Vietnamese/mixed): {original_text}\n\n"
        f"Rewrite (English): {output_text}\n\n"
        f"Detected intent: {intent}\n\n"
        f"Score the rewrite on two dimensions (1-5 each):\n"
        f"1. meaning_score: Did the rewrite preserve all key information and intent? "
        f"(5=perfect, 1=lost critical info)\n"
        f"2. tone_score: Is the tone appropriate for the intent? "
        f"(5=perfect, 1=completely wrong tone)\n\n"
        f"Also list any specific issues (max 3).\n\n"
        f"Respond in JSON only: "
        f'{{"meaning_score": N, "tone_score": N, "issues": ["...", ...]}}'
    )

    try:
        client = Anthropic(api_key=api_key, timeout=10.0)
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        import json
        text = response.content[0].text.strip()
        return json.loads(text)
    except Exception as e:
        logger.warning("Semantic quality scoring failed: %s", e)
        return None
