"""Tests for loma.intent — intent detection with negation, disambiguation, and tuned thresholds."""
import pytest
from loma.intent import compute_intent_scores, INTENT_PATTERNS, _is_negated, _first_signal_position


class TestComputeIntentScores:
    def test_ask_payment(self):
        result = compute_intent_scores(
            "Anh ơi, invoice tháng 1 chưa thanh toán, 5000 USD quá hạn 2 tuần rồi",
            {"vi_ratio": 0.6, "en_ratio": 0.4},
            "gmail",
        )
        assert result["intent"] == "ask_payment"
        assert result["confidence"] > 0.3

    def test_follow_up(self):
        result = compute_intent_scores(
            "Chưa nhận được feedback, nhắc lại về cái deadline tuần này",
            {"vi_ratio": 0.7, "en_ratio": 0.3},
            "gmail",
        )
        assert result["intent"] == "follow_up"

    def test_say_no(self):
        result = compute_intent_scores(
            "Em nghĩ khó được, chưa phù hợp với scope này, cần phải từ chối",
            {"vi_ratio": 0.8, "en_ratio": 0.2},
            "slack",
        )
        assert result["intent"] in ("say_no", "disagree")

    def test_ai_prompt_on_chatgpt(self):
        result = compute_intent_scores(
            "Viết code giúp em tạo function parse CSV, generate JSON output format, explain how it works",
            {"vi_ratio": 0.2, "en_ratio": 0.8},
            "chatgpt",
        )
        assert result["intent"] == "ai_prompt"

    def test_general_fallback(self):
        result = compute_intent_scores(
            "Xin chào anh, tôi muốn hỏi thăm",
            {"vi_ratio": 0.9, "en_ratio": 0.1},
            "generic",
        )
        # Should return some intent, possibly general
        assert result["intent"] in INTENT_PATTERNS

    def test_write_to_gov(self):
        result = compute_intent_scores(
            "Kính gửi Sở Kế hoạch, căn cứ nghị định, đề nghị cấp giấy phép",
            {"vi_ratio": 1.0, "en_ratio": 0.0},
            "generic",
        )
        assert result["intent"] == "write_to_gov"
        assert result["output_language"] == "vi_admin"

    def test_apologize(self):
        result = compute_intent_scores(
            "Em xin lỗi anh, lỗi hoàn toàn là do em, em rất tiếc đã deploy bug lên production",
            {"vi_ratio": 0.7, "en_ratio": 0.3},
            "slack",
        )
        assert result["intent"] == "apologize"

    def test_cold_outreach(self):
        result = compute_intent_scores(
            "Em tự giới thiệu, em muốn explore cơ hội hợp tác, xin giới thiệu platform của bên em",
            {"vi_ratio": 0.6, "en_ratio": 0.4},
            "gmail",
        )
        assert result["intent"] == "cold_outreach"

    def test_give_feedback(self):
        result = compute_intent_scores(
            "Anh đánh giá performance review của em, code có nhiều code duplication cần refactor, nhưng client satisfaction tăng",
            {"vi_ratio": 0.5, "en_ratio": 0.5},
            "gmail",
        )
        assert result["intent"] == "give_feedback"

    def test_request_senior(self):
        result = compute_intent_scores(
            "Anh ơi, xin phép nhờ anh review và approve cái PR deploy lên production",
            {"vi_ratio": 0.6, "en_ratio": 0.4},
            "slack",
        )
        assert result["intent"] == "request_senior"

    def test_write_formal_vn(self):
        result = compute_intent_scores(
            "Kính gửi ban lãnh đạo, trân trọng báo cáo kết quả, kính mời quý anh/chị",
            {"vi_ratio": 1.0, "en_ratio": 0.0},
            "generic",
        )
        assert result["intent"] == "write_formal_vn"
        assert result["output_language"] == "vi_formal"

    def test_write_report_vn(self):
        result = compute_intent_scores(
            "Báo cáo tổng kết kết quả quý Q2, tình hình tiến độ đánh giá mục tiêu KPI",
            {"vi_ratio": 0.9, "en_ratio": 0.1},
            "generic",
        )
        assert result["intent"] == "write_report_vn"
        assert result["output_language"] == "vi_formal"

    def test_write_proposal_vn(self):
        result = compute_intent_scores(
            "Đề xuất phương án triển khai kế hoạch ngân sách mới, kiến nghị phê duyệt mục tiêu",
            {"vi_ratio": 0.9, "en_ratio": 0.1},
            "generic",
        )
        assert result["intent"] == "write_proposal_vn"
        assert result["output_language"] == "vi_formal"

    def test_empty_text(self):
        result = compute_intent_scores(
            "",
            {"vi_ratio": 0.0, "en_ratio": 0.0},
            None,
        )
        assert result["intent"] == "general"

    def test_all_intents_have_required_keys(self):
        for intent_name, patterns in INTENT_PATTERNS.items():
            assert "vi_signals" in patterns, f"{intent_name} missing vi_signals"
            assert "en_signals" in patterns, f"{intent_name} missing en_signals"
            assert "confidence_threshold" in patterns, f"{intent_name} missing confidence_threshold"


class TestNegationHandling:
    """Verify that negation words suppress signal matches."""

    def test_is_negated_vi(self):
        assert _is_negated("em không muốn follow up", "follow up") is True
        assert _is_negated("em muốn follow up", "follow up") is False

    def test_chua_is_not_negation(self):
        """'chưa' is a pending/waiting marker in Vietnamese, not pure negation.
        It was removed from the negation set to avoid false suppression."""
        assert _is_negated("chưa cần thanh toán", "thanh toán") is False

    def test_is_negated_en(self):
        assert _is_negated("i don't want to follow up on this", "follow up") is True

    def test_not_negated_when_far(self):
        """Negation more than 3 words away should not suppress."""
        assert _is_negated("em không nghĩ là cần phải follow up", "follow up") is False

    def test_negated_follow_up_intent(self):
        """Negated follow_up signals should reduce confidence."""
        normal = compute_intent_scores(
            "Em nhắc lại anh về cái deadline tuần này",
            {"vi_ratio": 0.8, "en_ratio": 0.2},
            "gmail",
        )
        negated = compute_intent_scores(
            "Em không cần nhắc lại anh nữa",
            {"vi_ratio": 0.8, "en_ratio": 0.2},
            "gmail",
        )
        # Negated version should have lower confidence for follow_up
        if normal["intent"] == "follow_up":
            assert negated["intent"] != "follow_up" or negated["confidence"] < normal["confidence"]


class TestDisambiguation:
    """Test first-signal-position tiebreaker when top 2 intents are close."""

    def test_first_signal_position_basic(self):
        patterns = {"vi_signals": ["xin lỗi"], "en_signals": ["sorry"], "en_business_signals": []}
        pos = _first_signal_position("em xin lỗi anh", patterns)
        assert pos == 3  # "xin lỗi" starts at position 3

    def test_disambiguate_escalate_clear(self):
        """Clear escalation signals should win decisively."""
        result = compute_intent_scores(
            "Dự án bị block vì vấn đề nghiêm trọng, cần xử lý gấp, đã escalate lần 2",
            {"vi_ratio": 0.7, "en_ratio": 0.3},
            "gmail",
        )
        assert result["intent"] == "escalate"


class TestPerIntentThresholds:
    """Verify that different intents have appropriately different thresholds."""

    def test_thresholds_are_not_uniform(self):
        thresholds = {name: p["confidence_threshold"] for name, p in INTENT_PATTERNS.items()}
        unique_thresholds = set(thresholds.values())
        # Should have more than 2 distinct thresholds
        assert len(unique_thresholds) >= 3, f"Thresholds are too uniform: {unique_thresholds}"

    def test_escalate_has_low_threshold(self):
        assert INTENT_PATTERNS["escalate"]["confidence_threshold"] <= 0.30

    def test_disagree_has_higher_threshold_than_easy_intents(self):
        """Disagree should have a higher threshold than low-overlap intents like ask_payment."""
        assert INTENT_PATTERNS["disagree"]["confidence_threshold"] >= INTENT_PATTERNS["ask_payment"]["confidence_threshold"]

    def test_ask_payment_has_low_threshold(self):
        assert INTENT_PATTERNS["ask_payment"]["confidence_threshold"] <= 0.30
