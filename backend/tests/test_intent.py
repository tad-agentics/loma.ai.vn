"""Tests for loma.intent — intent detection."""
import pytest
from loma.intent import compute_intent_scores, INTENT_PATTERNS


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
            "Em nghĩ khó được, không đồng ý với scope này, cần phải từ chối",
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
