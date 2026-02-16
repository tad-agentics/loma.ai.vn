#!/usr/bin/env python3
"""
Run Loma benchmark: all 50 scenarios through the rewrite pipeline.
Updates each scenario with loma_output, detected_intent, routing_tier, response_time_ms.
Optionally writes results to a new JSON file.

Usage:
  cd backend && python run_benchmark.py
  python run_benchmark.py --limit 5
  python run_benchmark.py --output ../docs/Loma_Benchmark_v1_results.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Ensure backend is on path
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
os.chdir(_backend_dir)

from dotenv import load_dotenv
load_dotenv()

from handler import handler


def main() -> None:
    ap = argparse.ArgumentParser(description="Run Loma benchmark (50 scenarios)")
    ap.add_argument("--benchmark", default=None, help="Path to benchmark JSON (default: ../docs/Loma_Benchmark_v1.json)")
    ap.add_argument("--output", "-o", default=None, help="Write updated scenarios to this JSON file")
    ap.add_argument("--limit", "-n", type=int, default=0, help="Run only first N scenarios (0 = all)")
    ap.add_argument("--quiet", "-q", action="store_true", help="Less stdout")
    args = ap.parse_args()

    benchmark_path = args.benchmark or os.path.join(_backend_dir, "..", "docs", "Loma_Benchmark_v1.json")
    if not os.path.isfile(benchmark_path):
        print("Benchmark file not found:", benchmark_path, file=sys.stderr)
        sys.exit(1)

    with open(benchmark_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenarios = data.get("scenarios", [])
    if args.limit:
        scenarios = scenarios[: args.limit]
    total = len(scenarios)
    intent_match = 0
    errors = 0
    total_ms = 0

    for i, scenario in enumerate(scenarios):
        sid = scenario.get("id", "?")
        expected_intent = scenario.get("intent", "")
        input_text = scenario.get("input", "")
        platform = scenario.get("platform") or "gmail"

        payload = {
            "input_text": input_text,
            "platform": platform,
            "tone": scenario.get("tone", "professional"),
        }
        if scenario.get("output_language"):
            payload["output_language"] = scenario["output_language"]
        event = {"body": json.dumps(payload)}
        try:
            result = handler(event, None)
            body = json.loads(result["body"])
        except Exception as e:
            if not args.quiet:
                print(f"[{sid}] ERROR: {e}", file=sys.stderr)
            scenario["loma_output"] = ""
            scenario["loma_error"] = str(e)
            errors += 1
            continue

        if "error" in body:
            if not args.quiet:
                print(f"[{sid}] API error: {body.get('message', body['error'])}", file=sys.stderr)
            scenario["loma_output"] = ""
            scenario["loma_error"] = body.get("message", body["error"])
            errors += 1
            continue

        scenario["loma_output"] = body.get("output_text", "")
        scenario["loma_detected_intent"] = body.get("detected_intent", "")
        scenario["loma_routing_tier"] = body.get("routing_tier", "")
        scenario["loma_response_time_ms"] = body.get("response_time_ms", 0)
        scenario["loma_length_reduction_pct"] = (body.get("scores") or {}).get("length_reduction_pct")

        if scenario["loma_detected_intent"] == expected_intent:
            intent_match += 1
        total_ms += scenario.get("loma_response_time_ms", 0)

        if not args.quiet:
            print(f"[{sid}] {scenario['loma_detected_intent']} ({scenario['loma_routing_tier']}) {scenario.get('loma_response_time_ms', 0)}ms")

    # Summary
    print()
    print("--- Summary ---")
    print(f"Scenarios run: {total}")
    print(f"Errors:        {errors}")
    if total - errors > 0:
        print(f"Intent match:  {intent_match}/{total} ({100 * intent_match / total:.0f}%)")
        print(f"Avg latency:   {total_ms / (total - errors):.0f} ms")
    print()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Wrote", args.output)


if __name__ == "__main__":
    main()
