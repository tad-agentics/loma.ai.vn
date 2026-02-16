#!/usr/bin/env python3
"""
Spike B — Code-switching: intent accuracy on benchmark code-switched scenarios.
Gate: intent accuracy >65% for vi_ratio 0.3–0.7 (Tech Spec 3.1).
"""
from __future__ import annotations

import json
import os
import sys

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
os.chdir(_backend_dir)

from loma.intent import compute_intent_scores
from loma.language import compute_language_mix


def main() -> None:
    benchmark_path = os.path.join(_backend_dir, "..", "docs", "Loma_Benchmark_v1.json")
    if not os.path.isfile(benchmark_path):
        print("Benchmark file not found:", benchmark_path, file=sys.stderr)
        sys.exit(1)
    with open(benchmark_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenarios = [s for s in data.get("scenarios", []) if s.get("code_switched") is True]
    print(f"Code-switched scenarios: {len(scenarios)}")
    if not scenarios:
        print("No code-switched scenarios in benchmark.")
        sys.exit(0)
    correct = 0
    for s in scenarios:
        expected = s.get("intent", "")
        text = s.get("input", "")
        platform = s.get("platform") or "generic"
        lang_mix = compute_language_mix(text)
        result = compute_intent_scores(text, lang_mix, platform)
        detected = result.get("intent", "")
        if detected == expected:
            correct += 1
        else:
            print(f"  [{s.get('id')}] expected={expected} got={detected} (vi_ratio={lang_mix.get('vi_ratio')})")
    pct = 100 * correct / len(scenarios) if scenarios else 0
    print(f"Intent match: {correct}/{len(scenarios)} ({pct:.0f}%)")
    print("Gate: >65% for code-switched (vi_ratio 0.3–0.7)")
    sys.exit(0 if pct > 65 else 1)


if __name__ == "__main__":
    main()
