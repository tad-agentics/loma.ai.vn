"""
Rules engine — regex + cultural pattern hints (Tech Spec 3.2).
Handles ~30% at $0 when confident; otherwise pipeline routes to LLM.
Công văn (vi_admin) template for write_to_gov (Tech Spec v1.5).
"""
from __future__ import annotations

import json
from pathlib import Path


def _load_patterns() -> list[dict]:
    """Load cultural patterns from repo docs (or bundled copy)."""
    root = Path(__file__).resolve().parent.parent.parent
    paths = [
        root / "docs" / "Loma_Cultural_Patterns_v0.1.json",
        root / "backend" / "docs" / "Loma_Cultural_Patterns_v0.1.json",
    ]
    for p in paths:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("patterns", [])
    return []


def _apply_cong_van_template(input_text: str) -> str:
    """
    Minimal công văn (administrative Vietnamese) template — rules-based, zero LLM.
    Wraps user content in standard header/footer.
    """
    content = input_text.strip()
    return (
        "Kính gửi: [Cơ quan nhận]\n\n"
        "Căn cứ [quy định có liên quan], [Đơn vị] trình bày nội dung như sau:\n\n"
        f"{content}\n\n"
        "Trân trọng đề nghị Quý cơ quan xem xét, giải quyết.\n\n"
        "Nơi nhận:\n"
        "- Như trên;\n"
        "- Lưu.\n\n"
        "[Trưởng phòng/Ký tên]\n"
    )


# Pattern-based rewrite templates for short, common messages.
# Each maps a regex pattern to a rewrite template with optional captures.
import re as _re

_FOLLOW_UP_PATTERNS = [
    # "ping lại về X" → "Following up on X"
    (_re.compile(r"(?:em\s+)?ping\s+lại\s+(?:về\s+)?(.+)", _re.IGNORECASE),
     lambda m: f"Following up on {m.group(1).strip().rstrip('.')}. Could you provide an update?"),
    # "anh đã xem ... chưa" → "Have you had a chance to review ...?"
    (_re.compile(r".*(?:đã\s+xem|xem\s+giúp|review)\s+(.+?)\s*(?:chưa|được không|chưa ạ).*", _re.IGNORECASE),
     lambda m: f"Have you had a chance to review {m.group(1).strip().rstrip('.')}?"),
    # "nhắc lại" → "Just a reminder about"
    (_re.compile(r"(?:em\s+)?nhắc\s+lại\s+(?:về\s+)?(.+)", _re.IGNORECASE),
     lambda m: f"Just a reminder about {m.group(1).strip().rstrip('.')}."),
]

_SAY_NO_PATTERNS = [
    # "em sợ là không thể / không được" → "Unfortunately, I won't be able to..."
    (_re.compile(r".*(?:em\s+sợ\s+là|em\s+sợ)\s+(.+)", _re.IGNORECASE),
     lambda m: f"Unfortunately, {m.group(1).strip().rstrip('.')}." if "không" in m.group(1) else None),
    # "chưa phù hợp" → "This isn't the right fit at the moment."
    (_re.compile(r".*chưa\s+(?:phù hợp|sẵn sàng).*", _re.IGNORECASE),
     lambda _: "This isn't the right fit at the moment. I'll reach out if things change."),
]

_APOLOGIZE_PATTERNS = [
    # "xin lỗi đã reply trễ" → "Thanks for your patience. Regarding..."
    (_re.compile(r".*xin\s+lỗi\s+(?:đã\s+)?reply\s+trễ.*(?:về\s+)?(.+)?", _re.IGNORECASE),
     lambda m: f"Thanks for your patience. {m.group(1).strip().capitalize() if m.group(1) else ''}".strip()),
    # "mong anh thông cảm" → strip it (this is a closing hedge, not content)
    (_re.compile(r"(.+?)\s*\.?\s*(?:em\s+)?mong\s+anh\s+thông\s+cảm.*", _re.IGNORECASE),
     lambda m: m.group(1).strip()),
]

_INTENT_TEMPLATES = {
    "follow_up": _FOLLOW_UP_PATTERNS,
    "say_no": _SAY_NO_PATTERNS,
    "apologize": _APOLOGIZE_PATTERNS,
}


def apply_rules(
    input_text: str, intent: str, output_language: str | None = None
) -> str | None:
    """
    If a high-confidence pattern match exists, return rewritten text; else None.
    When output_language is vi_admin (or intent is write_to_gov), use công văn template.
    """
    if output_language == "vi_admin" or intent == "write_to_gov":
        return _apply_cong_van_template(input_text)

    # Try pattern-based templates for common short messages
    templates = _INTENT_TEMPLATES.get(intent, [])
    for pattern, formatter in templates:
        match = pattern.match(input_text.strip())
        if match:
            result = formatter(match)
            if result:
                return result

    patterns = _load_patterns()
    text_stripped = input_text.strip().lower()
    for p in patterns:
        if p.get("category") != intent and _category_to_intent(p.get("category")) != intent:
            continue
        vi = (p.get("vietnamese_pattern") or "").lower()
        if not vi:
            continue
        # Exact match: use loma_mapping (may contain [name], [date], etc. — keep as-is for now)
        if vi in text_stripped or text_stripped in vi:
            mapping = p.get("loma_mapping") or ""
            if mapping and mapping != "[Omit — start with the actual message]":
                return mapping
        # Substring match for common openings (e.g. "Anh ơi, " → "Hi [name], ")
        if text_stripped.startswith(vi[: min(20, len(vi))]):
            mapping = p.get("loma_mapping") or ""
            if mapping and not mapping.startswith("["):
                return mapping
    return None


def _category_to_intent(category: str | None) -> str | None:
    """Map cultural pattern category to intent name."""
    if not category:
        return None
    m = {
        "greeting_opening": "general",
        "request_senior": "request_senior",
        "ask_payment": "ask_payment",
        "follow_up": "follow_up",
        "say_no": "say_no",
        "cold_outreach": "cold_outreach",
        "give_feedback": "give_feedback",
        "disagree": "disagree",
        "escalate": "escalate",
        "apologize": "apologize",
        "general_professional": "general",
        "write_to_gov": "write_to_gov",
        "write_formal_vn": "write_formal_vn",
        "write_report_vn": "write_report_vn",
        "write_proposal_vn": "write_proposal_vn",
    }
    return m.get(category)
