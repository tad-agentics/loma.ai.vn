#!/usr/bin/env python3
"""
Local API server for the Loma extension.
Serves POST /api/v1/rewrite (calls Lambda handler). Loads backend/.env.
Run: cd backend && python server.py
Default: http://127.0.0.1:3000 (extension uses http://localhost:3000)
"""
from __future__ import annotations

import os
import sys

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
os.chdir(_backend_dir)

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, Response
from flask_cors import CORS

from handler import handler

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"])


@app.route("/api/v1/rewrite", methods=["POST", "OPTIONS"])
def rewrite():
    if request.method == "OPTIONS":
        return "", 204
    body = request.get_data(as_text=True) or "{}"
    event = {"body": body}
    result = handler(event, None)
    status = result.get("statusCode", 200)
    return Response(
        result.get("body", "{}"),
        status=status,
        mimetype="application/json",
    )


@app.route("/health", methods=["GET"])
def health():
    return {"ok": True, "service": "loma-rewrite"}, 200


def main() -> None:
    port = int(os.environ.get("PORT", "3000"))
    print(f"Loma API: http://127.0.0.1:{port}/api/v1/rewrite")
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()
