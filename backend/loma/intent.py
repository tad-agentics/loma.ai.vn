"""
Intent detection — keyword heuristics, code-switch aware (Tech Spec Section 6).
Intent names match playbook and benchmark: ask_payment, follow_up, request_senior,
say_no, cold_outreach, give_feedback, disagree, escalate, apologize, ai_prompt, general.

Improvements over v1:
- Per-intent confidence thresholds (calibrated against benchmark scenarios)
- Negation-aware signal matching (skips signals preceded by negators,
  but exempts Vietnamese hedging phrases like "em không biết", "em sợ")
- Disambiguation tiebreaker (first-signal-position when top 2 are within margin)
"""
from __future__ import annotations

import re

# Negation words — if a signal is preceded (within 3 words) by one of these,
# the match is suppressed.
_NEGATION_VI = {"không", "chẳng", "đừng", "khỏi"}
# Note: "chưa" removed from negation — in Vietnamese, "chưa" often indicates
# waiting/pending state which is the core signal, not negation.
_NEGATION_EN = {"not", "no", "never", "don't", "doesn't", "didn't", "won't",
                "can't", "cannot", "isn't", "aren't", "wasn't", "weren't",
                "shouldn't", "wouldn't", "couldn't"}
_NEGATION_ALL = _NEGATION_VI | _NEGATION_EN

# Vietnamese hedging phrases — these look like negation but are actually
# softening/politeness markers. When these appear before a signal, do NOT
# treat as negation.
_HEDGING_PREFIXES = [
    "em không biết",    # "I'm not sure" (= hedging, not negation)
    "em sợ",            # "I'm afraid" (= hedging)
    "em ngại",          # "I'm reluctant" (= hedging)
    "em không muốn nói nặng",  # "I don't want to say harshly" (= hedging)
    "em không muốn làm lớn",   # "I don't want to make a big deal" (= hedging)
    "em không muốn mách",      # "I don't want to tattle" (= hedging)
    "không biết",       # "not sure if" (= hedging)
]

_NEGATION_WINDOW = 3  # words

INTENT_PATTERNS: dict[str, dict] = {
    "request_senior": {
        "vi_signals": [
            "anh ơi", "chị ơi", "xin phép", "cho em hỏi", "nhờ anh", "nhờ chị",
            "được không ạ", "gấp", "đề xuất với", "cho em tham gia", "cho em nghỉ",
            "em muốn đề xuất",
        ],
        "en_signals": ["could you please", "would it be possible", "i was wondering if", "sorry to bother", "if you have time"],
        "en_business_signals": ["approve", "permission", "sign off", "greenlight", "review", "budget", "pr ", "pr#", "deploy", "sprint", "friday", "wednesday", "roi", "q1", "breakdown", "sign off giúp"],
        "context_signals": ["boss", "manager", "director", "lead"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.25,
    },
    "say_no": {
        "vi_signals": [
            "không được", "khó", "em nghĩ", "chưa phù hợp", "từ chối", "phải từ chối",
            "em sợ là", "quá tải", "không thể nhận", "chưa sẵn sàng", "không khả thi",
            "chưa phù hợp lắm",
        ],
        "en_signals": ["unfortunately", "not able to", "difficult to", "i don't think", "not sure if we can"],
        "en_business_signals": [
            "decline", "reject", "cannot accommodate", "pass on", "reduce scope",
            "push back", "scope", "handle", "resource", "plan a", "timeline",
            "delay", "sprint", "suggest", "deadline",
        ],
        "context_signals": ["decline", "reject", "cannot"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.20,
    },
    "follow_up": {
        "vi_signals": [
            "chưa nhận được", "nhắc lại", "theo dõi", "gửi lại", "ping", "được chưa",
            "phản hồi gì", "đã xem email", "share trên", "feedback được chưa",
            "gửi 2 tuần", "gửi tuần trước",
        ],
        "en_signals": ["following up", "just checking", "any update", "circling back", "wanted to check", "haven't heard"],
        "en_business_signals": [
            "status", "eta", "pending", "finalize", "sprint planning",
            "headcount request", "final approval", "review", "submit",
            "deadline", "feedback", "end of week", "design mockup", "figma",
            "offer letter", "candidate", "approval",
        ],
        "context_signals": ["reminder", "pending", "waiting"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.20,
    },
    "ask_payment": {
        "vi_signals": [
            "thanh toán", "hóa đơn", "chưa nhận", "quá hạn", "invoice", "payment",
            "khoản tiền",
        ],
        "en_signals": ["invoice", "payment", "overdue", "outstanding", "balance due"],
        "en_business_signals": ["remittance", "wire transfer", "net 30", "past due", "accounts receivable", "process", "confirm", "payment date", "payment terms"],
        "context_signals": ["amount", "due date", "$", "usd", "vnd"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.25,
    },
    "ai_prompt": {
        "vi_signals": [
            "viết code", "tạo", "giải thích", "phân tích", "viết giúp",
            "phân tích giúp", "viết cái", "viết em", "em cần viết", "em muốn viết",
        ],
        "en_signals": [
            "write a function", "create", "explain", "analyze", "generate",
            "help me", "build", "parse", "function", "python", "dataset",
            "insight", "output format", "technical spec",
        ],
        "en_business_signals": [
            "github issue", "bug", "websocket", "requirements", "edge case",
            "parse csv", "json format", "revenue", "region", "real-time",
            "concurrent connections", "notification system", "upload", "resize",
            "file >",
        ],
        "platform_signals": ["chatgpt", "claude"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.20,
    },
    "disagree": {
        "vi_signals": [
            "em nghĩ khác", "không đồng ý", "theo em", "em có concern", "em thấy",
            "cần xem lại", "có vấn đề",
        ],
        "en_signals": ["i disagree", "i think differently", "not sure i agree", "my concern is", "i see it differently"],
        "en_business_signals": [
            "pushback", "counterpoint", "alternative view", "respectfully disagree",
            "a/b test", "full rollout", "align", "okr", "data", "conversion rate",
            "rollout", "retention", "feature", "acquisition", "split resource",
            "hit target", "respect decision", "strategy",
        ],
        "context_signals": ["however", "concern", "risk", "but"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.25,
    },
    "give_feedback": {
        "vi_signals": [
            "đánh giá", "nhận xét", "góp ý", "cải thiện",
            "làm tốt", "chưa đạt yêu cầu", "cần cố gắng", "rất tốt",
            "tuy nhiên",
        ],
        "en_signals": ["feedback", "performance", "improve", "suggestion", "you did", "your work"],
        "en_business_signals": [
            "kpi", "okr", "performance review", "360 feedback",
            "areas for improvement", "refactor", "consistent", "optimize",
            "exceed", "client satisfaction", "delegation", "micromanage",
            "naming convention", "code duplication", "n+1", "revenue",
            "endpoint",
        ],
        "context_signals": ["strengths", "areas", "development"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.20,
    },
    "cold_outreach": {
        "vi_signals": [
            "giới thiệu", "hợp tác", "liên hệ", "đề xuất", "muốn explore",
            "tự giới thiệu", "xin giới thiệu", "mời anh", "mời chị",
        ],
        "en_signals": ["reaching out", "introduce", "partnership", "opportunity", "connect", "i came across"],
        "en_business_signals": [
            "collaboration", "synergy", "proposal", "explore", "profile",
            "founder", "build", "platform", "market", "distribution channel",
            "linkedin", "developer tools",
        ],
        "context_signals": ["company", "product", "service", "diễn giả", "hội thảo"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.20,
    },
    "escalate": {
        "vi_signals": [
            "báo cáo", "vấn đề nghiêm trọng", "cần xử lý gấp", "escalate",
            "bị block", "hủy hợp đồng", "than phiền", "bị lỗi",
        ],
        "en_signals": ["escalate", "urgent", "critical issue", "blocked", "needs attention", "raising this"],
        "en_business_signals": [
            "blocker", "showstopper", "p0", "sla breach", "at risk",
            "red flag", "production", "outage", "downtime", "breach",
            "investigate", "root cause", "authorize", "emergency", "devops",
        ],
        "context_signals": ["impact", "deadline", "risk"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.20,
    },
    "apologize": {
        "vi_signals": [
            "xin lỗi", "em rất tiếc", "lỗi của em", "sorry",
            "em biết em sai", "thông cảm", "bỏ qua cho em", "hứa sẽ không",
            "em mong anh thông cảm", "reply trễ",
        ],
        "en_signals": ["sorry", "apologize", "my mistake", "my fault", "oversight", "i should have"],
        "en_business_signals": [
            "accountability", "corrective action", "root cause",
            "won't happen again", "hotfix", "bug", "merge", "deploy",
            "test suite",
        ],
        "context_signals": ["mistake", "error", "delayed", "missed"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.20,
    },
    # Fallback when no intent meets threshold
    "general": {
        "vi_signals": [],
        "en_signals": [],
        "en_business_signals": [],
        "context_signals": [],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.2,
    },
    # Vietnamese output intents (Tech Spec v1.5) — trigger Vietnamese output
    "write_to_gov": {
        "vi_signals": ["kính gửi", "căn cứ", "đề nghị", "sở", "ủy ban", "giấy phép", "đăng ký", "cơ quan", "nghị định", "thông tư"],
        "en_signals": [],
        "en_business_signals": [],
        "context_signals": [".gov.vn"],
        "vi_weight": 2.0,
        "en_weight": 0,
        "confidence_threshold": 0.5,
        "output_language": "vi_admin",
    },
    "write_formal_vn": {
        "vi_signals": ["kính gửi", "trân trọng", "xin phép", "báo cáo", "kính mời", "thưa", "quý anh/chị"],
        "en_signals": [],
        "en_business_signals": [],
        "context_signals": ["sếp", "giám đốc", "trưởng phòng", "ban lãnh đạo"],
        "vi_weight": 2.0,
        "en_weight": 0,
        "confidence_threshold": 0.5,
        "output_language": "vi_formal",
    },
    "write_report_vn": {
        "vi_signals": ["báo cáo", "tổng kết", "kết quả", "tình hình", "đánh giá", "phân tích", "quý", "tháng"],
        "en_signals": [],
        "en_business_signals": ["kpi", "okr", "q1", "q2", "q3", "q4"],
        "context_signals": ["kết quả", "mục tiêu", "tiến độ"],
        "vi_weight": 1.5,
        "en_weight": 0.5,
        "confidence_threshold": 0.6,
        "output_language": "vi_formal",
    },
    "write_proposal_vn": {
        "vi_signals": ["đề xuất", "kiến nghị", "phương án", "kế hoạch", "ngân sách", "triển khai", "mục tiêu"],
        "en_signals": [],
        "en_business_signals": ["budget", "timeline", "roi", "headcount"],
        "context_signals": ["duyệt", "phê duyệt", "xin ý kiến"],
        "vi_weight": 1.5,
        "en_weight": 0.5,
        "confidence_threshold": 0.6,
        "output_language": "vi_formal",
    },
}


def _is_negated(text_lower: str, signal: str) -> bool:
    """
    Check if a signal match is preceded by a negation word within a window.
    Exempts Vietnamese hedging phrases (e.g., "em không biết" = "I'm not sure")
    which look like negation but are actually politeness/softening markers.
    """
    idx = text_lower.find(signal.lower())
    if idx < 0:
        return False

    # Check if the context matches a known hedging phrase
    # Look at the text before the signal for hedging prefixes
    prefix = text_lower[:idx + len(signal)].strip()
    for hedge in _HEDGING_PREFIXES:
        if hedge in prefix:
            return False  # This is hedging, not negation

    # Get the text before the signal, split into words, check last N
    prefix_text = text_lower[:idx].strip()
    if not prefix_text:
        return False
    prefix_words = prefix_text.split()
    window = prefix_words[-_NEGATION_WINDOW:]
    return any(w in _NEGATION_ALL for w in window)


def _first_signal_position(text_lower: str, patterns: dict) -> int:
    """Return character position of the earliest signal match. Used for disambiguation."""
    earliest = len(text_lower)
    for key in ("vi_signals", "en_signals", "en_business_signals"):
        for signal in patterns.get(key, []):
            pos = text_lower.find(signal.lower())
            if 0 <= pos < earliest:
                earliest = pos
    return earliest


def compute_intent_scores(
    input_text: str,
    language_mix: dict[str, float],
    platform: str | None,
) -> dict[str, str | float]:
    """
    Returns {"intent": str, "confidence": float, "output_language": str | None}.
    Falls back to "general" if best score is below that intent's confidence_threshold.
    """
    text_lower = input_text.lower()
    platform_lower = (platform or "").lower()
    scores: dict[str, float] = {}

    for intent, patterns in INTENT_PATTERNS.items():
        score = 0.0
        total_possible = 0.0

        vi_weight = patterns.get("vi_weight", 1.5)
        for signal in patterns.get("vi_signals", []):
            total_possible += vi_weight
            if signal.lower() in text_lower:
                if not _is_negated(text_lower, signal):
                    score += vi_weight

        en_weight = patterns.get("en_weight", 1.0)
        all_en = list(patterns.get("en_signals", [])) + list(patterns.get("en_business_signals", []))
        for signal in all_en:
            total_possible += en_weight
            if signal.lower() in text_lower:
                if not _is_negated(text_lower, signal):
                    score += en_weight

        for signal in patterns.get("context_signals", []):
            total_possible += 1.0
            if signal.lower() in text_lower:
                if not _is_negated(text_lower, signal):
                    score += 1.0

        if intent == "ai_prompt" and platform_lower in ("chatgpt", "claude"):
            score += 2.0
            total_possible += 2.0

        # Code-switched text: cap total so a few strong matches can pass threshold (Tech Spec 3.1)
        vi_ratio = (language_mix or {}).get("vi_ratio", 0.0)
        if 0.2 <= vi_ratio <= 0.8 and total_possible > 12:
            total_possible = min(total_possible, 12.0)
        normalized = score / max(total_possible, 1.0)
        scores[intent] = normalized

    # Sort by score descending
    sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_intent, best_score = sorted_intents[0]

    # Disambiguation: if top 2 are within 0.1 margin, use first-signal-position tiebreaker
    if len(sorted_intents) > 1:
        second_intent, second_score = sorted_intents[1]
        margin = best_score - second_score
        if 0 < margin < 0.1 and best_score > 0:
            pos_best = _first_signal_position(text_lower, INTENT_PATTERNS[best_intent])
            pos_second = _first_signal_position(text_lower, INTENT_PATTERNS[second_intent])
            if pos_second < pos_best:
                best_intent, best_score = second_intent, second_score

    confidence = best_score
    threshold = INTENT_PATTERNS[best_intent]["confidence_threshold"]

    if confidence < threshold:
        return {"intent": "general", "confidence": confidence, "output_language": None}
    output_lang = INTENT_PATTERNS[best_intent].get("output_language")
    return {"intent": best_intent, "confidence": confidence, "output_language": output_lang}
