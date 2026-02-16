"""Tests for loma.auth — token handling."""
from loma.auth import get_bearer_token, extract_user_id


class TestGetBearerToken:
    def test_valid_bearer(self):
        token = get_bearer_token({"Authorization": "Bearer abc123"})
        assert token == "abc123"

    def test_lowercase_header(self):
        token = get_bearer_token({"authorization": "Bearer xyz789"})
        assert token == "xyz789"

    def test_no_auth_header(self):
        token = get_bearer_token({})
        assert token is None

    def test_non_bearer_scheme(self):
        token = get_bearer_token({"Authorization": "Basic abc123"})
        assert token is None


class TestExtractUserId:
    def test_none_token(self):
        assert extract_user_id(None) is None

    def test_empty_token(self):
        assert extract_user_id("") is None

    def test_invalid_token(self):
        # Without JWT secret configured, should return None
        assert extract_user_id("not.a.real.token") is None
