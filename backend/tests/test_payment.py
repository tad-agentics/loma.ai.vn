"""Tests for loma.payment — webhook processing, signature verification, payment links."""
import hashlib
import hmac
from unittest.mock import patch, MagicMock

from loma.payment import (
    verify_webhook_signature,
    process_webhook,
    _extract_user_id,
    _match_by_amount,
    PRODUCTS,
)


class TestVerifyWebhookSignature:
    def test_valid_signature(self):
        data = {"amount": 49000, "orderCode": 123456, "description": "loma_payg_20"}
        # Compute expected signature
        sorted_data = sorted(data.items())
        raw = "&".join(f"{k}={v}" for k, v in sorted_data)
        key = "test-checksum-key"
        expected = hmac.new(key.encode(), raw.encode(), hashlib.sha256).hexdigest()

        with patch("loma.payment.PAYOS_CHECKSUM_KEY", key):
            assert verify_webhook_signature(data, expected) is True

    def test_invalid_signature(self):
        data = {"amount": 49000, "orderCode": 123456}
        with patch("loma.payment.PAYOS_CHECKSUM_KEY", "test-key"):
            assert verify_webhook_signature(data, "invalid-sig") is False

    def test_no_checksum_key_returns_false(self):
        with patch("loma.payment.PAYOS_CHECKSUM_KEY", ""):
            assert verify_webhook_signature({}, "any") is False

    def test_signature_excluded_from_raw(self):
        data = {"amount": 49000, "signature": "should-be-excluded", "orderCode": 1}
        key = "test-key"
        # Compute without signature field
        sorted_data = sorted(data.items())
        raw = "&".join(f"{k}={v}" for k, v in sorted_data if k != "signature")
        expected = hmac.new(key.encode(), raw.encode(), hashlib.sha256).hexdigest()

        with patch("loma.payment.PAYOS_CHECKSUM_KEY", key):
            assert verify_webhook_signature(data, expected) is True


class TestProcessWebhook:
    def test_non_success_code(self):
        result = process_webhook({"code": "01"})
        assert result["ok"] is True
        assert result["action"] is None

    def test_invalid_signature_returns_flag(self):
        payload = {
            "code": "00",
            "data": {"orderCode": 1, "amount": 49000, "description": "loma_payg_20"},
            "signature": "bad-sig",
        }
        with patch("loma.payment.PAYOS_CHECKSUM_KEY", "real-key"):
            result = process_webhook(payload)
            assert result["ok"] is False
            assert result.get("signature_invalid") is True

    def test_no_user_id_fails(self):
        payload = {
            "code": "00",
            "data": {
                "orderCode": 1,
                "amount": 49000,
                "description": "loma_payg_20",
                "reference": "",
            },
            "signature": "",
        }
        with patch("loma.payment.PAYOS_CHECKSUM_KEY", ""):
            result = process_webhook(payload)
            assert result["ok"] is False
            assert "Cannot identify user" in result["message"]

    @patch("loma.payment.billing")
    def test_payg_credit_success(self, mock_billing):
        payload = {
            "code": "00",
            "data": {
                "orderCode": 1,
                "amount": 49000,
                "description": "loma_payg_20",
                "reference": "user-abc-123_12345",
            },
            "signature": "",
        }
        with patch("loma.payment.PAYOS_CHECKSUM_KEY", ""):
            result = process_webhook(payload)
            assert result["ok"] is True
            assert result["action"] == "payg_credit"
            assert result["credits"] == 20
            mock_billing._add_payg_credits.assert_called_once()

    @patch("loma.payment.billing")
    def test_pro_upgrade_success(self, mock_billing):
        payload = {
            "code": "00",
            "data": {
                "orderCode": 2,
                "amount": 149000,
                "description": "loma_pro_monthly",
                "reference": "user-xyz-789_99999",
            },
            "signature": "",
        }
        with patch("loma.payment.PAYOS_CHECKSUM_KEY", ""):
            result = process_webhook(payload)
            assert result["ok"] is True
            assert result["action"] == "pro_upgrade"
            mock_billing._set_subscription_tier.assert_called_once()

    def test_unknown_product_fails(self):
        payload = {
            "code": "00",
            "data": {
                "orderCode": 3,
                "amount": 99999,
                "description": "unknown_product",
                "reference": "user-abc-12345-long-id_99999",
            },
            "signature": "",
        }
        with patch("loma.payment.PAYOS_CHECKSUM_KEY", ""):
            result = process_webhook(payload)
            assert result["ok"] is False
            assert "Unknown product" in result["message"]


class TestExtractUserId:
    def test_valid_reference(self):
        assert _extract_user_id("user-abc-12345_99999", "") == "user-abc-12345"

    def test_empty_reference(self):
        assert _extract_user_id("", "") is None

    def test_short_reference(self):
        assert _extract_user_id("short", "") is None


class TestMatchByAmount:
    def test_known_amount(self):
        product = _match_by_amount(49000)
        assert product is not None
        assert product["type"] == "payg"
        assert product["credits"] == 20

    def test_unknown_amount(self):
        assert _match_by_amount(12345) is None

    def test_pro_amount(self):
        product = _match_by_amount(149000)
        assert product is not None
        assert product["type"] == "pro"


class TestProducts:
    def test_payg_20_exists(self):
        assert "loma_payg_20" in PRODUCTS
        assert PRODUCTS["loma_payg_20"]["credits"] == 20

    def test_payg_100_exists(self):
        assert "loma_payg_100" in PRODUCTS
        assert PRODUCTS["loma_payg_100"]["credits"] == 100

    def test_pro_monthly_exists(self):
        assert "loma_pro_monthly" in PRODUCTS
        assert PRODUCTS["loma_pro_monthly"]["type"] == "pro"
