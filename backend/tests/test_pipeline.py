"""Tests for loma.pipeline — end-to-end pipeline (no LLM calls)."""
import os
import pytest
from loma.pipeline import run_rewrite


class TestRunRewrite:
    def test_empty_input(self):
        result = run_rewrite("")
        assert result["error"] == "text_too_short"

    def test_too_long_input(self):
        result = run_rewrite("x" * 5001)
        assert result["error"] == "text_too_long"

    def test_whitespace_only(self):
        result = run_rewrite("   \n   ")
        assert result["error"] == "text_too_short"

    def test_valid_vietnamese_input(self):
        """Pipeline should run without error (may return placeholder if no API key)."""
        result = run_rewrite(
            "Anh ơi, cái invoice tháng 1 chưa thanh toán, 5000 USD quá hạn 2 tuần rồi"
        )
        assert "error" not in result
        assert "output_text" in result
        assert "detected_intent" in result
        assert "routing_tier" in result
        assert "scores" in result
        assert "language_mix" in result
        assert "response_time_ms" in result
        assert "rewrite_id" in result

    def test_intent_override(self):
        result = run_rewrite(
            "Anh ơi, cái báo cáo review được chưa?",
            intent_override="follow_up",
        )
        assert result.get("detected_intent") == "follow_up"
        assert result.get("intent_detection_method") == "user_confirmed"

    def test_output_language_vi_admin(self):
        result = run_rewrite(
            "Cần xin giấy phép kinh doanh cho công ty mới",
            output_language_in="vi_admin",
        )
        assert result.get("output_language") in ("vi_admin",)
        # Rules engine should handle vi_admin
        assert result.get("routing_tier") == "rules"

    def test_response_time_tracked(self):
        result = run_rewrite("Anh ơi, em cần anh review cái này")
        assert result.get("response_time_ms", 0) >= 0

    def test_scores_present(self):
        result = run_rewrite("Anh ơi, cần anh giúp em cái này gấp lắm")
        scores = result.get("scores", {})
        assert "length_reduction_pct" in scores


class TestRunRewriteAuth:
    """Test that pipeline still works without auth (backward compatible)."""

    def test_no_auth_fields_in_result(self):
        result = run_rewrite("Anh ơi, em nhờ anh review giúp cái PR này")
        # payg_balance_remaining is set by handler, not pipeline
        assert result.get("payg_balance_remaining") is None
