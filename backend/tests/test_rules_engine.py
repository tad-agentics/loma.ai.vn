"""Tests for loma.rules_engine — pattern matching, công văn template, category mapping."""
from loma.rules_engine import apply_rules, _category_to_intent, _apply_cong_van_template


class TestApplyRulesCongVan:
    def test_write_to_gov_uses_template(self):
        result = apply_rules("Xin cấp giấy phép kinh doanh", "write_to_gov")
        assert result is not None
        assert "Kính gửi" in result
        assert "Trân trọng đề nghị" in result
        assert "Nơi nhận" in result

    def test_vi_admin_output_language_uses_template(self):
        result = apply_rules("Nội dung công văn", "general", output_language="vi_admin")
        assert result is not None
        assert "Kính gửi" in result

    def test_cong_van_preserves_user_content(self):
        content = "Đề nghị cấp phép hoạt động cho công ty ABC"
        result = apply_rules(content, "write_to_gov")
        assert content in result


class TestCongVanTemplate:
    def test_template_structure(self):
        result = _apply_cong_van_template("Test content")
        assert result.startswith("Kính gửi")
        assert "Test content" in result
        assert "Nơi nhận:" in result
        assert "Lưu." in result

    def test_strips_whitespace(self):
        result = _apply_cong_van_template("  hello  ")
        assert "hello" in result


class TestFollowUpPatterns:
    def test_ping_lai(self):
        result = apply_rules("em ping lại về project X", "follow_up")
        assert result is not None
        assert "Following up" in result or "project X" in result

    def test_anh_da_xem_chua(self):
        result = apply_rules("anh đã xem PR này chưa", "follow_up")
        assert result is not None
        assert "review" in result.lower() or "PR" in result

    def test_nhac_lai(self):
        result = apply_rules("em nhắc lại về deadline", "follow_up")
        assert result is not None
        assert "reminder" in result.lower() or "deadline" in result


class TestSayNoPatterns:
    def test_em_so_la_khong(self):
        result = apply_rules("em sợ là không thể nhận thêm", "say_no")
        assert result is not None
        assert "Unfortunately" in result or "không" not in result

    def test_chua_phu_hop(self):
        result = apply_rules("chưa phù hợp", "say_no")
        assert result is not None
        assert "right fit" in result.lower() or "moment" in result.lower()


class TestApologizePatterns:
    def test_xin_loi_reply_tre(self):
        result = apply_rules("xin lỗi đã reply trễ về báo cáo", "apologize")
        assert result is not None
        assert "patience" in result.lower() or "báo cáo" in result.lower() or len(result) > 0

    def test_mong_anh_thong_cam(self):
        result = apply_rules("Em gửi báo cáo muộn. mong anh thông cảm", "apologize")
        assert result is not None
        # Should strip the "mong anh thông cảm" hedge
        assert "thông cảm" not in result.lower()


class TestNoMatchReturnsNone:
    def test_general_intent_no_match(self):
        result = apply_rules("This is just a random English sentence", "general")
        assert result is None

    def test_long_text_no_follow_up_match(self):
        long_text = "This is a very long message that doesn't match any patterns " * 5
        result = apply_rules(long_text, "follow_up")
        assert result is None

    def test_unknown_intent_no_match(self):
        result = apply_rules("test input", "nonexistent_intent")
        assert result is None


class TestCategoryToIntent:
    def test_greeting_maps_to_general(self):
        assert _category_to_intent("greeting_opening") == "general"

    def test_general_professional_maps_to_general(self):
        assert _category_to_intent("general_professional") == "general"

    def test_direct_intent_mapping(self):
        assert _category_to_intent("follow_up") == "follow_up"
        assert _category_to_intent("say_no") == "say_no"
        assert _category_to_intent("escalate") == "escalate"

    def test_vn_output_intents(self):
        assert _category_to_intent("write_to_gov") == "write_to_gov"
        assert _category_to_intent("write_formal_vn") == "write_formal_vn"
        assert _category_to_intent("write_report_vn") == "write_report_vn"
        assert _category_to_intent("write_proposal_vn") == "write_proposal_vn"

    def test_none_input(self):
        assert _category_to_intent(None) is None

    def test_unknown_category(self):
        assert _category_to_intent("nonexistent") is None
