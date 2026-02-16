"""
Intent detection — keyword heuristics, code-switch aware (Tech Spec Section 6).
Intent names match playbook and benchmark: ask_payment, follow_up, request_senior,
say_no, cold_outreach, give_feedback, disagree, escalate, apologize, ai_prompt, general.
"""
from __future__ import annotations

# Intent names aligned with docs/Loma_Benchmark_v1.json and prompt playbook
INTENT_PATTERNS: dict[str, dict] = {
    "request_senior": {
        "vi_signals": ["anh ơi", "chị ơi", "xin phép", "cho em hỏi", "nhờ anh", "nhờ chị", "được không ạ", "gấp"],
        "en_signals": ["could you please", "would it be possible", "i was wondering if", "sorry to bother", "if you have time"],
        "en_business_signals": ["approve", "permission", "sign off", "greenlight", "review", "budget", "pr ", "pr#", "deploy", "sprint", "friday", "wednesday", "roi", "q1", "breakdown", "sign off giúp"],
        "context_signals": ["boss", "manager", "director", "lead"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "say_no": {
        "vi_signals": ["không được", "khó", "em nghĩ", "chưa phù hợp", "từ chối", "phải từ chối"],
        "en_signals": ["unfortunately", "not able to", "difficult to", "i don't think", "not sure if we can"],
        "en_business_signals": ["decline", "reject", "cannot accommodate", "pass on", "scope", "handle", "resource", "plan a", "timeline", "delay", "sprint", "suggest", "reduce scope", "push back", "deadline"],
        "context_signals": ["decline", "reject", "cannot"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "follow_up": {
        "vi_signals": ["chưa nhận được", "nhắc lại", "theo dõi", "gửi lại", "ping", "được chưa"],
        "en_signals": ["following up", "just checking", "any update", "circling back", "wanted to check", "haven't heard"],
        "en_business_signals": ["status", "eta", "timeline", "progress", "pending", "review", "submit", "deadline", "feedback", "finalize", "sprint planning", "headcount", "approval", "offer letter", "candidate", "end of week", "design mockup", "figma", "headcount request", "final approval"],
        "context_signals": ["reminder", "pending", "waiting"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "ask_payment": {
        "vi_signals": ["thanh toán", "hóa đơn", "chưa nhận", "quá hạn", "invoice", "payment"],
        "en_signals": ["invoice", "payment", "overdue", "outstanding", "balance due"],
        "en_business_signals": ["remittance", "wire transfer", "net 30", "past due", "accounts receivable", "process", "confirm", "payment date", "payment terms"],
        "context_signals": ["amount", "due date", "$", "usd", "vnd"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "ai_prompt": {
        "vi_signals": ["viết code", "tạo", "giải thích", "phân tích", "viết giúp", "phân tích giúp", "viết cái", "viết em", "em cần viết", "em muốn viết"],
        "en_signals": ["write a function", "create", "explain", "analyze", "generate", "help me", "build", "parse", "function", "python", "dataset", "insight", "output format", "technical spec"],
        "en_business_signals": ["github issue", "bug", "websocket", "requirements", "edge case", "parse csv", "json format", "revenue", "region", "real-time", "concurrent connections", "notification system"],
        "platform_signals": ["chatgpt", "claude"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "disagree": {
        "vi_signals": ["em nghĩ khác", "không đồng ý", "theo em", "em có concern", "em thấy"],
        "en_signals": ["i disagree", "i think differently", "not sure i agree", "my concern is", "i see it differently"],
        "en_business_signals": ["pushback", "counterpoint", "alternative view", "respectfully disagree", "align", "okr", "data", "conversion rate", "rollout", "retention", "feature", "acquisition", "split resource", "hit target", "respect decision", "a/b test", "full rollout", "strategy"],
        "context_signals": ["but", "however", "concern", "risk", "strategy"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "give_feedback": {
        "vi_signals": ["đánh giá", "nhận xét", "góp ý", "cải thiện"],
        "en_signals": ["feedback", "review", "performance", "improve", "suggestion", "you did", "your work"],
        "en_business_signals": ["kpi", "okr", "performance review", "360 feedback", "areas for improvement", "refactor", "consistent", "optimize", "exceed", "revenue", "client satisfaction", "develop", "delegation", "micromanage", "pr ", "naming convention", "code duplication", "n+1", "endpoint"],
        "context_signals": ["strengths", "areas", "development"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "cold_outreach": {
        "vi_signals": ["giới thiệu", "hợp tác", "liên hệ", "đề xuất", "em thấy", "muốn explore"],
        "en_signals": ["reaching out", "introduce", "partnership", "opportunity", "connect", "i came across"],
        "en_business_signals": ["collaboration", "synergy", "proposal", "explore", "profile", "founder", "build", "platform", "market", "distribution channel", "linkedin", "developer tools"],
        "context_signals": ["company", "product", "service"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "escalate": {
        "vi_signals": ["báo cáo", "vấn đề nghiêm trọng", "cần xử lý gấp", "escalate"],
        "en_signals": ["escalate", "urgent", "critical issue", "blocked", "needs attention", "raising this"],
        "en_business_signals": ["blocker", "showstopper", "p0", "sla breach", "at risk", "red flag", "production", "outage", "downtime", "breach", "investigate", "root cause", "authorize", "emergency", "devops"],
        "context_signals": ["impact", "deadline", "risk"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
    },
    "apologize": {
        "vi_signals": ["xin lỗi", "em rất tiếc", "lỗi của em", "sorry"],
        "en_signals": ["sorry", "apologize", "my mistake", "my fault", "oversight", "i should have"],
        "en_business_signals": ["accountability", "corrective action", "root cause", "won't happen again", "bug", "merge", "hotfix", "deploy", "test suite"],
        "context_signals": ["mistake", "error", "delayed", "missed"],
        "vi_weight": 1.5,
        "en_weight": 1.0,
        "confidence_threshold": 0.35,
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


def compute_intent_scores(
    input_text: str,
    language_mix: dict[str, float],
    platform: str | None,
) -> dict[str, str | float]:
    """
    Returns {"intent": str, "confidence": float}.
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
                score += vi_weight

        en_weight = patterns.get("en_weight", 1.0)
        all_en = list(patterns.get("en_signals", [])) + list(patterns.get("en_business_signals", []))
        for signal in all_en:
            total_possible += en_weight
            if signal.lower() in text_lower:
                score += en_weight

        for signal in patterns.get("context_signals", []):
            total_possible += 1.0
            if signal.lower() in text_lower:
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

    best_intent = max(scores, key=scores.get)
    confidence = scores[best_intent]
    threshold = INTENT_PATTERNS[best_intent]["confidence_threshold"]

    if confidence < threshold:
        return {"intent": "general", "confidence": confidence, "output_language": None}
    output_lang = INTENT_PATTERNS[best_intent].get("output_language")
    return {"intent": best_intent, "confidence": confidence, "output_language": output_lang}
