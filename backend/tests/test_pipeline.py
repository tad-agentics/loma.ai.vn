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

    def test_entity_scores_present(self):
        result = run_rewrite("Anh ơi, invoice $5,000 quá hạn từ Nguyễn Văn Đức")
        scores = result.get("scores", {})
        assert "entity_preserved_pct" in scores
        assert "entity_missing" in scores

    def test_risk_flags_present(self):
        result = run_rewrite("Anh ơi, em nhờ anh review giúp cái PR #347")
        assert "risk_flags" in result
        assert isinstance(result["risk_flags"], list)


class TestVietnameseOutputIntents:
    """Test Vietnamese output intent pipeline: write_to_gov, write_formal_vn, write_report_vn, write_proposal_vn."""

    def test_write_to_gov_auto_detection(self):
        """write_to_gov triggers vi_admin output_language and routes to rules."""
        result = run_rewrite(
            "Kính gửi Sở Kế hoạch và Đầu tư, căn cứ nghị định 01, đề nghị cấp giấy phép kinh doanh",
        )
        assert "error" not in result
        assert result.get("output_language") == "vi_admin"
        assert result.get("routing_tier") == "rules"
        assert "Kính gửi" in result.get("output_text", "")

    def test_write_to_gov_with_override(self):
        """Explicit intent override for write_to_gov."""
        result = run_rewrite(
            "Xin cấp giấy phép cho công ty mới",
            intent_override="write_to_gov",
        )
        assert result.get("detected_intent") == "write_to_gov"
        assert result.get("output_language") == "vi_admin"
        assert result.get("routing_tier") == "rules"

    def test_output_language_vi_formal(self):
        """Client-specified vi_formal output language is respected."""
        result = run_rewrite(
            "Viết email cho giám đốc về tiến độ dự án",
            output_language_in="vi_formal",
        )
        assert result.get("output_language") == "vi_formal"

    def test_output_language_vi_casual(self):
        """Client-specified vi_casual output language is respected."""
        result = run_rewrite(
            "Nhắn team về buổi họp mai",
            output_language_in="vi_casual",
        )
        assert result.get("output_language") == "vi_casual"

    def test_vi_output_response_shape(self):
        """Vietnamese output responses have the same shape as English rewrites."""
        result = run_rewrite(
            "Cần xin giấy phép kinh doanh",
            output_language_in="vi_admin",
        )
        for key in ("rewrite_id", "output_text", "original_text", "detected_intent",
                     "intent_confidence", "routing_tier", "scores", "language_mix",
                     "response_time_ms", "output_language", "output_language_source"):
            assert key in result, f"Missing key: {key}"


class TestRunRewriteAuth:
    """Test that pipeline still works without auth (backward compatible)."""

    def test_no_auth_fields_in_result(self):
        result = run_rewrite("Anh ơi, em nhờ anh review giúp cái PR này")
        # payg_balance_remaining is set by handler, not pipeline
        assert result.get("payg_balance_remaining") is None
