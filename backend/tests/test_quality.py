"""Tests for loma.quality — quality scoring."""
from loma.quality import compute_length_reduction_pct, score_rewrite


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


class TestScoreRewrite:
    def test_returns_dict(self):
        result = score_rewrite("original text here", "shorter")
        assert isinstance(result, dict)
        assert "length_reduction_pct" in result

    def test_positive_reduction(self):
        result = score_rewrite("This is a much longer original text", "Short")
        assert result["length_reduction_pct"] > 0
