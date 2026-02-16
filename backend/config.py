"""
Loma backend configuration — dev / staging / prod.
Reads from environment variables with sane defaults for local development.
"""
from __future__ import annotations

import os

ENV = os.environ.get("LOMA_ENV", "development")  # development | staging | production


def _bool(val: str | None) -> bool:
    return (val or "").lower() in ("1", "true", "yes")


# --- Anthropic ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# --- Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

# --- CORS ---
ALLOWED_ORIGINS: list[str] = [
    o.strip()
    for o in os.environ.get(
        "ALLOWED_ORIGINS",
        "chrome-extension://,http://localhost:3000,https://loma.app",
    ).split(",")
    if o.strip()
]

# --- Rate Limits ---
FREE_REWRITES_PER_DAY = int(os.environ.get("FREE_REWRITES_PER_DAY", "5"))
PAYG_PACK_SIZE = int(os.environ.get("PAYG_PACK_SIZE", "20"))

# --- Logging ---
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO" if ENV == "production" else "DEBUG")

# --- API ---
API_PORT = int(os.environ.get("PORT", "3000"))
