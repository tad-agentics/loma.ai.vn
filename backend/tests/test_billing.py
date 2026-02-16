"""Tests for loma.billing — quota checking."""
from loma.billing import check_quota


class TestCheckQuota:
    def test_anonymous_user_allowed(self):
        result = check_quota(None)
        assert result["allowed"] is True
        assert result["tier"] == "anonymous"

    def test_returns_dict(self):
        result = check_quota(None)
        assert "allowed" in result
        assert "tier" in result
        assert "remaining" in result
        assert "reason" in result
