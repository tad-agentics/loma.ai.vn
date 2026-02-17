"""
Payment integration — PayOS (Vietnamese payment gateway).
Handles webhook verification, credit top-up, and subscription management.

PayOS docs: https://payos.vn/docs
Flow:
1. Extension opens PayOS checkout link (generated client-side or via API)
2. User pays via bank transfer / e-wallet / card
3. PayOS sends webhook POST to /api/v1/webhook/payos
4. We verify signature, credit the user's account
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from typing import Any

from . import billing, db

logger = logging.getLogger("loma.payment")

# PayOS configuration
PAYOS_CLIENT_ID = os.environ.get("PAYOS_CLIENT_ID", "")
PAYOS_API_KEY = os.environ.get("PAYOS_API_KEY", "")
PAYOS_CHECKSUM_KEY = os.environ.get("PAYOS_CHECKSUM_KEY", "")

# Product mapping: PayOS order description → credits/tier
PRODUCTS = {
    "loma_payg_20": {"type": "payg", "credits": 20, "amount": 49000},      # ~$2 USD
    "loma_payg_100": {"type": "payg", "credits": 100, "amount": 199000},    # ~$8 USD
    "loma_pro_monthly": {"type": "pro", "credits": 0, "amount": 149000},    # ~$6 USD/mo
}


def verify_webhook_signature(data: dict, signature: str) -> bool:
    """
    Verify PayOS webhook signature using HMAC-SHA256.
    PayOS signs: orderCode + amount + description + ... sorted alphabetically.
    """
    if not PAYOS_CHECKSUM_KEY:
        logger.warning("PAYOS_CHECKSUM_KEY not configured — skipping signature check")
        return False

    # PayOS checksum: sort data keys, concatenate values, HMAC-SHA256
    sorted_data = sorted(data.items())
    raw = "&".join(f"{k}={v}" for k, v in sorted_data if k != "signature")
    computed = hmac.new(
        PAYOS_CHECKSUM_KEY.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, signature)


def process_webhook(payload: dict) -> dict[str, Any]:
    """
    Process a PayOS webhook event.
    Returns {"ok": bool, "message": str, "action": str|None}.

    Payload structure (PayOS v2):
    {
        "code": "00",           # "00" = success
        "desc": "success",
        "data": {
            "orderCode": 123456,
            "amount": 49000,
            "description": "loma_payg_20",
            "accountNumber": "...",
            "reference": "...",
            "transactionDateTime": "...",
            "paymentLinkId": "...",
            "counterAccountBankId": "...",
            "counterAccountBankName": "...",
            "counterAccountName": "...",
            "counterAccountNumber": "...",
            "virtualAccountName": "...",
            "virtualAccountNumber": "...",
        },
        "signature": "..."
    }
    """
    code = payload.get("code")
    if code != "00":
        return {"ok": True, "message": f"Non-success code: {code}", "action": None}

    data = payload.get("data", {})
    signature = payload.get("signature", "")

    # Verify signature — reject with 401-triggering flag on mismatch
    if PAYOS_CHECKSUM_KEY and not verify_webhook_signature(data, signature):
        logger.warning("Invalid PayOS webhook signature for order %s", data.get("orderCode"))
        return {"ok": False, "message": "Invalid signature", "action": None, "signature_invalid": True}

    description = data.get("description", "")
    order_code = data.get("orderCode")
    amount = data.get("amount", 0)

    # Extract user_id from order reference (format: "loma_{product}_{user_id}")
    reference = data.get("reference", "")
    user_id = _extract_user_id(reference, description)

    if not user_id:
        logger.error("Cannot extract user_id from PayOS webhook: ref=%s, desc=%s", reference, description)
        return {"ok": False, "message": "Cannot identify user", "action": None}

    # Match product
    product = PRODUCTS.get(description)
    if not product:
        # Try matching by amount as fallback
        product = _match_by_amount(amount)

    if not product:
        logger.warning("Unknown product in PayOS webhook: desc=%s, amount=%s", description, amount)
        return {"ok": False, "message": f"Unknown product: {description}", "action": None}

    # Apply credits or subscription
    if product["type"] == "payg":
        billing._add_payg_credits(user_id, product["credits"])
        logger.info("Added %d PAYG credits to user %s (order %s)", product["credits"], user_id, order_code)
        return {
            "ok": True,
            "message": f"Added {product['credits']} credits",
            "action": "payg_credit",
            "user_id": user_id,
            "credits": product["credits"],
        }
    elif product["type"] == "pro":
        billing._set_subscription_tier(user_id, "pro")
        logger.info("Upgraded user %s to Pro (order %s)", user_id, order_code)
        return {
            "ok": True,
            "message": "Upgraded to Pro",
            "action": "pro_upgrade",
            "user_id": user_id,
        }

    return {"ok": False, "message": "Unhandled product type", "action": None}


def _extract_user_id(reference: str, description: str) -> str | None:
    """Extract user_id from PayOS reference field. Format: userId_orderCode."""
    if not reference:
        return None
    # PayOS reference format we set: "{user_id}_{timestamp}"
    parts = reference.split("_")
    if len(parts) >= 1 and len(parts[0]) > 10:
        return parts[0]
    return None


def _match_by_amount(amount: int) -> dict | None:
    """Fallback: match product by payment amount."""
    for product in PRODUCTS.values():
        if product["amount"] == amount:
            return product
    return None


def create_payment_link(
    user_id: str,
    product_key: str,
    return_url: str = "",
    cancel_url: str = "",
) -> dict | None:
    """
    Create a PayOS payment link for a product.
    Returns {"checkout_url": str, "order_code": int} or None on failure.

    This uses the PayOS REST API directly (no SDK dependency).
    """
    import time

    if not PAYOS_CLIENT_ID or not PAYOS_API_KEY:
        logger.warning("PayOS not configured — cannot create payment link")
        return None

    product = PRODUCTS.get(product_key)
    if not product:
        return None

    order_code = int(time.time() * 1000) % 2147483647  # PayOS requires int32
    reference = f"{user_id}_{order_code}"

    body = {
        "orderCode": order_code,
        "amount": product["amount"],
        "description": product_key,
        "cancelUrl": cancel_url or "https://loma.app/payment/cancel",
        "returnUrl": return_url or "https://loma.app/payment/success",
        "buyerName": "",
        "buyerEmail": "",
        "buyerPhone": "",
        "items": [
            {
                "name": f"Loma {'PAYG' if product['type'] == 'payg' else 'Pro'} - {product.get('credits', 'unlimited')} credits",
                "quantity": 1,
                "price": product["amount"],
            }
        ],
    }

    # Generate checksum
    sorted_items = sorted(body.items())
    raw = "&".join(f"{k}={v}" for k, v in sorted_items if k not in ("items",))
    checksum = hmac.new(
        PAYOS_CHECKSUM_KEY.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest() if PAYOS_CHECKSUM_KEY else ""
    body["signature"] = checksum

    try:
        import urllib.request
        req = urllib.request.Request(
            "https://api-merchant.payos.vn/v2/payment-requests",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-client-id": PAYOS_CLIENT_ID,
                "x-api-key": PAYOS_API_KEY,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == "00":
                return {
                    "checkout_url": result["data"]["checkoutUrl"],
                    "order_code": order_code,
                }
            logger.error("PayOS create link failed: %s", result)
            return None
    except Exception as e:
        logger.error("PayOS API call failed: %s", e)
        return None
