"""Tests for loma.quality — quality scoring with entity preservation."""
from loma.quality import (
    compute_length_reduction_pct,
    score_rewrite,
    extract_entities,
    check_entity_preservation,
)


class TestLengthReduction:
    def test_shorter_output(self):
        pct = compute_length_reduction_pct("a" * 100, "a" * 70)
        assert pct == 30

    def test_longer_output(self):
        pct = compute_length_reduction_pct("a" * 50, "a" * 75)
        assert pct == -50

    def test_same_length(self):
        pct = compute_length_reduction_pct("hello", "world")
        assert pct == 0

    def test_empty_original(self):
        pct = compute_length_reduction_pct("", "something")
        assert pct == 0


class TestExtractEntities:
    def test_money_usd(self):
        entities = extract_entities("Invoice for $5,000 USD is overdue")
        assert len(entities["money"]) >= 1

    def test_money_vnd(self):
        entities = extract_entities("Số tiền 15.000 USD từ hợp đồng")
        assert len(entities["money"]) >= 1

    def test_dates_q4(self):
        entities = extract_entities("Q4 report is ready for review")
        assert any("Q4" in d for d in entities["dates"])

    def test_identifiers_pr(self):
        entities = extract_entities("PR #347 needs review before deploy")
        assert len(entities["identifiers"]) >= 1

    def test_identifiers_invoice(self):
        entities = extract_entities("Invoice #INV-2024-031 amount $8,500")
        assert len(entities["identifiers"]) >= 1

    def test_names_vietnamese(self):
        entities = extract_entities("Anh Hùng ơi, em nhờ Nguyễn Văn Đức review")
        assert len(entities["names"]) >= 1

    def test_no_common_words_as_names(self):
        entities = extract_entities("The report is ready. Please review.")
        # "The" and "Please" should be filtered out
        for name in entities["names"]:
            assert name.split()[0] not in ("The", "Please")


class TestEntityPreservation:
    def test_all_preserved(self):
        original = "Invoice $5,000 from Nguyễn Văn Đức for Q4"
        output = "Invoice for $5,000 from Nguyễn Văn Đức regarding Q4 deliverables"
        result = check_entity_preservation(original, output)
        assert result["preserved_pct"] == 100.0
        assert len(result["missing"]) == 0

    def test_missing_amount(self):
        original = "Invoice $5,000 for Q4"
        output = "Invoice for the quarterly report"
        result = check_entity_preservation(original, output)
        assert result["preserved_pct"] < 100.0
        assert len(result["missing"]) > 0

    def test_empty_entities(self):
        original = "em muốn hỏi thăm anh"
        output = "I wanted to check in"
        result = check_entity_preservation(original, output)
        # No entities to check = 100% preserved
        assert result["preserved_pct"] == 100.0


class TestScoreRewrite:
    def test_returns_dict(self):
        result = score_rewrite("original text here", "shorter")
        assert isinstance(result, dict)
        assert "length_reduction_pct" in result
        assert "entity_preserved_pct" in result
        assert "entity_missing" in result

    def test_positive_reduction(self):
        result = score_rewrite("This is a much longer original text", "Short")
        assert result["length_reduction_pct"] > 0

    def test_entity_fields_present(self):
        result = score_rewrite(
            "Anh Hùng ơi, invoice $5,000 quá hạn",
            "Hi Hùng, the $5,000 invoice is overdue",
        )
        assert isinstance(result["entity_preserved_pct"], float)
        assert isinstance(result["entity_missing"], list)
