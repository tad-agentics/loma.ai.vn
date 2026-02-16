"""Tests for loma.router — cost routing."""
from loma.router import route_rewrite


class TestRouteRewrite:
    def test_vi_admin_routes_to_rules(self):
        tier = route_rewrite("anything", {"vi_ratio": 1.0, "en_ratio": 0.0}, "write_to_gov", 0.9, "vi_admin")
        assert tier == "rules"

    def test_short_english_general_routes_to_haiku(self):
        tier = route_rewrite("short text", {"vi_ratio": 0.0, "en_ratio": 1.0}, "general", 0.5, "en")
        assert tier == "haiku"

    def test_complex_vietnamese_routes_to_sonnet(self):
        text = "A" * 200  # Longer text
        tier = route_rewrite(text, {"vi_ratio": 0.7, "en_ratio": 0.3}, "escalate", 0.8, "en")
        assert tier == "sonnet"

    def test_short_vi_casual_routes_to_haiku(self):
        tier = route_rewrite("ngắn gọn", {"vi_ratio": 1.0, "en_ratio": 0.0}, "general", 0.5, "vi_casual")
        assert tier == "haiku"

    def test_low_complexity_short_routes_to_haiku(self):
        tier = route_rewrite("hello there", {"vi_ratio": 0.0, "en_ratio": 1.0}, "follow_up", 0.6, "en")
        assert tier == "haiku"
