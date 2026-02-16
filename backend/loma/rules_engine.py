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
    Wraps user content in standard header/footer. Phase 2: expand with real templates.
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


def apply_rules(
    input_text: str, intent: str, output_language: str | None = None
) -> str | None:
    """
    If a high-confidence pattern match exists, return rewritten text; else None.
    When output_language is vi_admin (or intent is write_to_gov), use công văn template.
    """
    if output_language == "vi_admin" or intent == "write_to_gov":
        return _apply_cong_van_template(input_text)

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
    }
    return m.get(category)
