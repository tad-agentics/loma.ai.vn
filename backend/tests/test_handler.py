"""Tests for handler.py — request routing, input validation, security headers, rate limiting."""
import json
from unittest.mock import patch, MagicMock

import handler
from handler import _json_response, _check_anon_rate_limit, _extract_client_ip, _anon_ip_counts


class TestJsonResponse:
    def test_basic_response_shape(self):
        resp = _json_response(200, {"ok": True})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["ok"] is True

    def test_security_headers_present(self):
        resp = _json_response(200, {"ok": True})
        h = resp["headers"]
        assert h["X-Content-Type-Options"] == "nosniff"
        assert h["X-Frame-Options"] == "DENY"
        assert "max-age=" in h["Strict-Transport-Security"]

    def test_content_type_json(self):
        resp = _json_response(200, {})
        assert resp["headers"]["Content-Type"] == "application/json"

    def test_unicode_body(self):
        resp = _json_response(200, {"msg": "Xin chào"})
        assert "Xin chào" in resp["body"]


class TestHealthEndpoint:
    def test_health_returns_200(self):
        event = {"rawPath": "/health", "headers": {}}
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["ok"] is True
        assert body["service"] == "loma-rewrite"


class TestInputValidation:
    def _make_event(self, body_dict):
        return {
            "rawPath": "/api/v1/rewrite",
            "headers": {},
            "body": json.dumps(body_dict),
        }

    @patch("handler.billing")
    @patch("handler.auth")
    def test_invalid_tone_returns_400(self, mock_auth, mock_billing):
        mock_auth.get_bearer_token.return_value = None
        mock_auth.extract_user_id.return_value = None
        mock_billing.check_quota.return_value = {"allowed": True, "tier": "anonymous", "remaining": None, "reason": None}

        event = self._make_event({"input_text": "hello", "tone": "aggressive"})
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"] == "invalid_tone"

    @patch("handler.billing")
    @patch("handler.auth")
    def test_invalid_platform_returns_400(self, mock_auth, mock_billing):
        mock_auth.get_bearer_token.return_value = None
        mock_auth.extract_user_id.return_value = None
        mock_billing.check_quota.return_value = {"allowed": True, "tier": "anonymous", "remaining": None, "reason": None}

        event = self._make_event({"input_text": "hello", "platform": "fakebook"})
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"] == "invalid_platform"

    @patch("handler.billing")
    @patch("handler.auth")
    def test_invalid_intent_returns_400(self, mock_auth, mock_billing):
        mock_auth.get_bearer_token.return_value = None
        mock_auth.extract_user_id.return_value = None
        mock_billing.check_quota.return_value = {"allowed": True, "tier": "anonymous", "remaining": None, "reason": None}

        event = self._make_event({"input_text": "hello", "intent": "nonexistent_intent"})
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"] == "invalid_intent"

    @patch("handler.billing")
    @patch("handler.auth")
    def test_valid_tone_passes(self, mock_auth, mock_billing):
        mock_auth.get_bearer_token.return_value = None
        mock_auth.extract_user_id.return_value = None
        mock_billing.check_quota.return_value = {"allowed": True, "tier": "anonymous", "remaining": None, "reason": None}

        for tone in ("professional", "direct", "warm", "formal"):
            event = self._make_event({"input_text": "Anh ơi cho em hỏi", "tone": tone})
            resp = handler.handler(event, None)
            # Should not be 400 for tone validation
            assert resp["statusCode"] != 400 or "invalid_tone" not in resp["body"]

    @patch("handler.billing")
    @patch("handler.auth")
    def test_valid_platform_passes(self, mock_auth, mock_billing):
        mock_auth.get_bearer_token.return_value = None
        mock_auth.extract_user_id.return_value = None
        mock_billing.check_quota.return_value = {"allowed": True, "tier": "anonymous", "remaining": None, "reason": None}

        event = self._make_event({"input_text": "hello world test text", "platform": "gmail"})
        resp = handler.handler(event, None)
        assert resp["statusCode"] != 400 or "invalid_platform" not in resp["body"]

    @patch("handler.billing")
    @patch("handler.auth")
    def test_none_platform_passes(self, mock_auth, mock_billing):
        mock_auth.get_bearer_token.return_value = None
        mock_auth.extract_user_id.return_value = None
        mock_billing.check_quota.return_value = {"allowed": True, "tier": "anonymous", "remaining": None, "reason": None}

        event = self._make_event({"input_text": "hello world test"})
        resp = handler.handler(event, None)
        assert resp["statusCode"] != 400 or "invalid_platform" not in resp["body"]


class TestInvalidJson:
    def test_invalid_json_body(self):
        event = {"rawPath": "/api/v1/rewrite", "headers": {}, "body": "not json{"}
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 400
        body = json.loads(resp["body"])
        assert body["error"] == "invalid_json"


class TestQuotaCheck:
    @patch("handler.analytics")
    @patch("handler.billing")
    @patch("handler.auth")
    def test_quota_exhausted_returns_429(self, mock_auth, mock_billing, mock_analytics):
        mock_auth.get_bearer_token.return_value = "token"
        mock_auth.extract_user_id.return_value = "user-123"
        mock_billing.check_quota.return_value = {
            "allowed": False,
            "tier": "free",
            "remaining": 0,
            "reason": "free_limit_reached",
        }

        event = {
            "rawPath": "/api/v1/rewrite",
            "headers": {"Authorization": "Bearer token"},
            "body": json.dumps({"input_text": "hello"}),
        }
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 429

    @patch("handler.analytics")
    @patch("handler.billing")
    @patch("handler.auth")
    def test_payg_exhausted_message(self, mock_auth, mock_billing, mock_analytics):
        mock_auth.get_bearer_token.return_value = "token"
        mock_auth.extract_user_id.return_value = "user-123"
        mock_billing.check_quota.return_value = {
            "allowed": False,
            "tier": "payg",
            "remaining": 0,
            "reason": "payg_exhausted",
        }

        event = {
            "rawPath": "/api/v1/rewrite",
            "headers": {"Authorization": "Bearer token"},
            "body": json.dumps({"input_text": "hello"}),
        }
        resp = handler.handler(event, None)
        body = json.loads(resp["body"])
        assert "PAYG" in body["message"]


class TestExtractClientIp:
    def test_http_api_v2_format(self):
        event = {"requestContext": {"http": {"sourceIp": "1.2.3.4"}}}
        assert _extract_client_ip(event) == "1.2.3.4"

    def test_rest_api_v1_format(self):
        event = {"requestContext": {"identity": {"sourceIp": "5.6.7.8"}}}
        assert _extract_client_ip(event) == "5.6.7.8"

    def test_no_request_context(self):
        assert _extract_client_ip({}) is None


class TestAnonRateLimit:
    def setup_method(self):
        _anon_ip_counts.clear()

    def test_first_request_allowed(self):
        assert _check_anon_rate_limit("10.0.0.1") is True

    def test_under_limit_allowed(self):
        for _ in range(19):
            _check_anon_rate_limit("10.0.0.2")
        assert _check_anon_rate_limit("10.0.0.2") is True

    def test_over_limit_blocked(self):
        for _ in range(20):
            _check_anon_rate_limit("10.0.0.3")
        assert _check_anon_rate_limit("10.0.0.3") is False

    def test_different_ips_independent(self):
        for _ in range(20):
            _check_anon_rate_limit("10.0.0.4")
        assert _check_anon_rate_limit("10.0.0.4") is False
        assert _check_anon_rate_limit("10.0.0.5") is True


class TestWebhookEndpoint:
    @patch("handler.analytics")
    @patch("handler.payment")
    def test_invalid_signature_returns_401(self, mock_payment, mock_analytics):
        mock_payment.process_webhook.return_value = {
            "ok": False,
            "message": "Invalid signature",
            "action": None,
            "signature_invalid": True,
        }
        event = {
            "rawPath": "/api/v1/webhook/payos",
            "headers": {},
            "body": json.dumps({"code": "00", "data": {}, "signature": "bad"}),
        }
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 401

    @patch("handler.analytics")
    @patch("handler.payment")
    def test_valid_webhook_returns_200(self, mock_payment, mock_analytics):
        mock_payment.process_webhook.return_value = {
            "ok": True,
            "message": "Added 20 credits",
            "action": "payg_credit",
            "user_id": "user-1",
            "credits": 20,
        }
        event = {
            "rawPath": "/api/v1/webhook/payos",
            "headers": {},
            "body": json.dumps({"code": "00", "data": {}, "signature": "good"}),
        }
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 200


class TestEventsEndpoint:
    @patch("handler.analytics")
    @patch("handler.auth")
    def test_events_returns_ok(self, mock_auth, mock_analytics):
        mock_auth.get_bearer_token.return_value = None
        mock_auth.extract_user_id.return_value = None

        event = {
            "rawPath": "/api/v1/events",
            "headers": {},
            "body": json.dumps({"event_name": "loma_test", "event_data": {}}),
        }
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 200


class TestCreatePaymentEndpoint:
    @patch("handler.payment")
    @patch("handler.auth")
    def test_unauthenticated_returns_401(self, mock_auth, mock_payment):
        mock_auth.get_bearer_token.return_value = None
        mock_auth.extract_user_id.return_value = None

        event = {
            "rawPath": "/api/v1/payment/create",
            "headers": {},
            "body": json.dumps({"product": "loma_payg_20"}),
        }
        resp = handler.handler(event, None)
        assert resp["statusCode"] == 401
        body = json.loads(resp["body"])
        assert body["error"] == "auth_required"
