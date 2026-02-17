"""Tests for loma.language — Vietnamese detection with romanized support and language mix."""
import pytest
from loma.language import contains_vietnamese, compute_language_mix


class TestContainsVietnamese:
    def test_pure_vietnamese(self):
        assert contains_vietnamese("Anh ơi, cái invoice tháng 1 chưa thanh toán") is True

    def test_pure_english(self):
        assert contains_vietnamese("Please send me the report by Friday") is False

    def test_mixed_code_switch(self):
        assert contains_vietnamese("Anh ơi, cái KPI report Q4 đã review chưa?") is True

    def test_short_text_below_threshold(self):
        assert contains_vietnamese("hi") is False

    def test_empty_text(self):
        assert contains_vietnamese("") is False

    def test_none_text(self):
        assert contains_vietnamese(None) is False

    def test_diacritics_only(self):
        assert contains_vietnamese("văn bản hành chính đúng format thông báo kết quả") is True

    def test_function_words_only(self):
        assert contains_vietnamese("cái này của cho với được không") is True

    def test_english_with_single_vi_word(self):
        # Should not trigger with just 1 function word
        assert contains_vietnamese("Please send the report chưa finish") is False


class TestRomanizedVietnamese:
    """Test detection of Vietnamese typed without diacritics."""

    def test_romanized_bigram_thanh_toan(self):
        assert contains_vietnamese("anh oi, thanh toan invoice thang 1 di") is True

    def test_romanized_bigram_xin_chao(self):
        assert contains_vietnamese("xin chao anh, em muon hoi ve project") is True

    def test_romanized_bigram_bao_cao(self):
        assert contains_vietnamese("em gui bao cao cho anh review nhe") is True

    def test_romanized_multiple_words(self):
        """Three romanized single words should trigger detection."""
        assert contains_vietnamese("khong duoc roi, chua xong, gui lai") is True

    def test_romanized_false_positive_guard(self):
        """Normal English should not trigger romanized detection."""
        assert contains_vietnamese("The quick brown fox jumps over the lazy dog") is False

    def test_romanized_de_xuat(self):
        assert contains_vietnamese("em co de xuat moi cho project nay anh") is True


class TestComputeLanguageMix:
    def test_pure_vietnamese(self):
        mix = compute_language_mix("Anh ơi em cần gửi báo cáo cho anh tháng này nhé")
        assert mix["vi_ratio"] >= 0.5

    def test_pure_english(self):
        mix = compute_language_mix("Please send me the invoice by Friday")
        assert mix["en_ratio"] > 0.8

    def test_mixed(self):
        mix = compute_language_mix("Anh ơi cái KPI report Q4 đã review chưa")
        assert 0.2 < mix["vi_ratio"] < 0.9
        assert 0.1 < mix["en_ratio"] < 0.8

    def test_empty(self):
        mix = compute_language_mix("")
        assert mix["vi_ratio"] == 0.0
        assert mix["en_ratio"] == 0.0
