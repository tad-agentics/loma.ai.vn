"""Tests for loma.router — cost routing."""
from loma.router import route_rewrite


class TestRouteRewrite:
    def test_vi_admin_routes_to_rules(self):
        tier = route_rewrite("anything", {"vi_ratio": 1.0, "en_ratio": 0.0}, "write_to_gov", 0.9, "vi_admin")
        assert tier == "rules"

    def test_short_low_complexity_routes_to_rules(self):
        """With rules engine enabled, short low-complexity intents try rules first.
        The pipeline will fall through to LLM if no rule matches."""
        tier = route_rewrite("short text", {"vi_ratio": 0.0, "en_ratio": 1.0}, "general", 0.5, "en")
        assert tier == "rules"

    def test_complex_vietnamese_routes_to_sonnet(self):
        text = "A" * 200  # Longer text
        tier = route_rewrite(text, {"vi_ratio": 0.7, "en_ratio": 0.3}, "escalate", 0.8, "en")
        assert tier == "sonnet"

    def test_short_vi_casual_routes_to_rules(self):
        """Short low-complexity now tries rules first."""
        tier = route_rewrite("ngắn gọn", {"vi_ratio": 1.0, "en_ratio": 0.0}, "general", 0.5, "vi_casual")
        assert tier == "rules"

    def test_low_complexity_short_routes_to_rules(self):
        """Short follow_up tries rules first (falls through to LLM in pipeline)."""
        tier = route_rewrite("hello there", {"vi_ratio": 0.0, "en_ratio": 1.0}, "follow_up", 0.6, "en")
        assert tier == "rules"

    def test_long_text_never_routes_to_rules(self):
        """Long text should always go to sonnet, never rules."""
        text = "A" * 250
        tier = route_rewrite(text, {"vi_ratio": 0.5, "en_ratio": 0.5}, "say_no", 0.8, "en")
        assert tier == "sonnet"

    def test_short_vi_formal_routes_to_haiku(self):
        """Short text with vi_formal output should route to haiku for cost savings."""
        tier = route_rewrite("Viết email cho sếp", {"vi_ratio": 1.0, "en_ratio": 0.0}, "write_formal_vn", 0.7, "vi_formal")
        assert tier == "haiku"

    def test_long_vi_formal_routes_to_sonnet(self):
        """Long Vietnamese formal text should still route to sonnet."""
        text = "Viết báo cáo chi tiết " * 20
        tier = route_rewrite(text, {"vi_ratio": 1.0, "en_ratio": 0.0}, "write_formal_vn", 0.7, "vi_formal")
        assert tier == "sonnet"

    def test_short_write_report_vn_routes_to_haiku(self):
        """Short Vietnamese report intent routes to haiku."""
        tier = route_rewrite("Tổng kết Q2", {"vi_ratio": 1.0, "en_ratio": 0.0}, "write_report_vn", 0.7, "vi_formal")
        assert tier == "haiku"

    def test_short_write_proposal_vn_routes_to_haiku(self):
        """Short Vietnamese proposal intent routes to haiku."""
        tier = route_rewrite("Đề xuất ngân sách", {"vi_ratio": 1.0, "en_ratio": 0.0}, "write_proposal_vn", 0.7, "vi_formal")
        assert tier == "haiku"
