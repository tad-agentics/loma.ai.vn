#!/usr/bin/env python3
"""
Run rewrite pipeline locally (no Lambda).
Usage: python run_local.py "Anh ơi, em muốn nhờ anh xem giúp em cái báo cáo Q4 được không ạ?"
"""
import json
import sys

# Ensure backend dir is on path (run from repo root or backend/)
import os
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
os.chdir(_backend_dir)

from dotenv import load_dotenv
load_dotenv()

from handler import handler


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python run_local.py \"<input text>\" [platform] [tone] [output_language]")
        print("Example: python run_local.py \"Anh ơi, em xin phép hỏi...\" gmail")
        print("Example: python run_local.py \"Kính gửi Sở, căn cứ nghị định...\" generic professional vi_admin")
        sys.exit(1)
    input_text = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else None
    tone = sys.argv[3] if len(sys.argv) > 3 else "professional"
    output_language = sys.argv[4] if len(sys.argv) > 4 else None
    payload = {"input_text": input_text, "platform": platform, "tone": tone}
    if output_language:
        payload["output_language"] = output_language
    event = {"body": json.dumps(payload)}
    result = handler(event, None)
    body = json.loads(result["body"])
    if "error" in body:
        print("Error:", body.get("message", body["error"]))
        sys.exit(1)
    print("Intent:", body.get("detected_intent"), "| Confidence:", body.get("intent_confidence"))
    print("Output language:", body.get("output_language"), "| Source:", body.get("output_language_source"))
    print("Routing:", body.get("routing_tier"))
    print("Length reduction:", body.get("scores", {}).get("length_reduction_pct"), "%")
    print("\n--- Output ---\n")
    print(body.get("output_text", ""))


if __name__ == "__main__":
    main()
