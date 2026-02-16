#!/usr/bin/env python3
"""
Spike A — Text isolation: extract user-written text from 20 scenarios (UX Spec 2.4).
Gate: ≥18/20 correct extractions.
"""
from __future__ import annotations

import json
import os
import sys

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
os.chdir(_backend_dir)

from loma.text_isolation import extract_user_text


def normalize(s: str) -> str:
    return " ".join(s.split()) if s else ""


def main() -> int:
    scenarios_path = os.path.join(_backend_dir, "..", "docs", "Loma_TextIsolation_Spike_Scenarios.json")
    if not os.path.isfile(scenarios_path):
        print("Scenarios file not found:", scenarios_path, file=sys.stderr)
        return 1
    with open(scenarios_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data.get("scenarios", [])
    expected = data.get("expected_user_text", {})
    if not scenarios or not expected:
        print("Missing scenarios or expected_user_text.", file=sys.stderr)
        return 1
    passed = 0
    for s in scenarios:
        sid = s.get("id", "")
        full_text = s.get("full_text", "")
        want = expected.get(sid, "")
        user_text, method = extract_user_text(full_text)
        ok = normalize(user_text) == normalize(want)
        if ok:
            passed += 1
        else:
            print(f"  [{sid}] FAIL expected {len(want)} chars, got {len(user_text)} chars (method={method})")
            print(f"       want: {repr(want[:80])}...")
            print(f"       got:  {repr(user_text[:80])}...")
    total = len(scenarios)
    pct = 100 * passed / total if total else 0
    print(f"Text isolation: {passed}/{total} ({pct:.0f}%)")
    print("Gate: ≥18/20")
    return 0 if passed >= 18 else 1


if __name__ == "__main__":
    sys.exit(main())
