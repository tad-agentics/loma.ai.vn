#!/usr/bin/env python3
"""
Local API server for the Loma extension.
Serves POST /api/v1/rewrite, /api/v1/events, /api/v1/billing/webhook, GET /health.
Run: cd backend && python server.py
Default: http://127.0.0.1:3000
"""
from __future__ import annotations

import logging
import os
import sys

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
os.chdir(_backend_dir)

from dotenv import load_dotenv
load_dotenv()

import config as cfg
from flask import Flask, request, Response
from flask_cors import CORS
from handler import handler

# Logging
logging.basicConfig(
    level=getattr(logging, cfg.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("loma.server")

app = Flask(__name__)

# Restrict CORS to configured origins
CORS(app, origins=cfg.ALLOWED_ORIGINS, allow_headers=["Content-Type", "Authorization"])


def _dispatch():
    """Forward request to the Lambda handler."""
    if request.method == "OPTIONS":
        return "", 204
    body = request.get_data(as_text=True) or "{}"
    headers = dict(request.headers)
    event = {
        "body": body,
        "headers": headers,
        "rawPath": request.path,
        "path": request.path,
    }
    result = handler(event, None)
    status = result.get("statusCode", 200)
    return Response(
        result.get("body", "{}"),
        status=status,
        mimetype="application/json",
    )


@app.route("/api/v1/rewrite", methods=["POST", "OPTIONS"])
def rewrite():
    return _dispatch()


@app.route("/api/v1/events", methods=["POST", "OPTIONS"])
def events():
    return _dispatch()


@app.route("/api/v1/billing/webhook", methods=["POST"])
def billing_webhook():
    return _dispatch()


@app.route("/health", methods=["GET"])
def health():
    return {"ok": True, "service": "loma-rewrite", "env": cfg.ENV}, 200


@app.errorhandler(500)
def handle_500(e):
    logger.exception("Unhandled error: %s", e)
    return {"error": "internal_server_error", "message": "Something went wrong."}, 500


def main() -> None:
    port = cfg.API_PORT
    logger.info("Loma API: http://127.0.0.1:%d  [env=%s]", port, cfg.ENV)
    app.run(host="127.0.0.1", port=port, debug=(cfg.ENV == "development"))


if __name__ == "__main__":
    main()
